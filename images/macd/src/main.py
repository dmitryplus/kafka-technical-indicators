import json
import os
import logging
import time
from datetime import datetime, timedelta

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from kafka import KafkaConsumer, KafkaProducer

from macd import Macd
from params import Params

logging.basicConfig(level=logging.ERROR)

interval = int(os.environ.get('INTERVAL', 0))
exit_topic_prefix = os.environ.get('TOPIC_PREFIX_MACD', None)

figies: dict[str, dict[str, float]] = {}


def convert_macd_value(
        value: dict[str: str, str: float, str: float, str: float]) \
        -> dict[str: str, str: float, str: float, str: float]:
    return value


def main():
    if interval == 0:
        print("INTERVAL not find")
        return

    if exit_topic_prefix is None:
        raise RuntimeError("MACD values topic name not find")

    kafka_service = KafkaService()
    topic = (ConfigService()).get_candle_topic_name(interval)
    exit_topic = (ConfigService()).get_indicator_values_topic_name(exit_topic_prefix, interval)

    kafka_service.wait_topic_exists(topic)

    # собираем данные из истории
    consumer_history = KafkaConsumer(
        topic,
        bootstrap_servers=[(KafkaService()).get_bootstrap()],
        auto_offset_reset='earliest',
        key_deserializer=lambda m: m.decode('utf-8'),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=1000
    )

    for message in consumer_history:

        if 'time' not in message.value:
            raise RuntimeError("Field 'time' not find in message")

        if 'close' not in message.value:
            raise RuntimeError("Field 'close' not find in message")

        if message.key not in figies:
            figies[message.key] = {}

        figies[message.key][message.value['time']] = message.value['close']

    consumer_history.close()

    # вычисляем по последнем данным из истории
    for figi in figies:
        if len(figies[figi]) > Params().get_candles_count():

            producer = KafkaProducer(
                bootstrap_servers=kafka_service.get_bootstrap(),
                key_serializer=str.encode,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            )

            times = sorted(list(figies[figi].keys()), key=lambda x: x.lower())

            for i in range(Params().get_candles_count(), len(figies[figi])):

                start_key = i - Params().get_candles_count()
                stop_key = i + 1

                part_times = times[start_key:stop_key]

                part_figies = {}

                for time_key in part_times:
                    part_figies[time_key] = figies[figi][time_key]

                macd_last_value = convert_macd_value(Macd(figi, part_figies).get_last_value())
                if len(macd_last_value) > 0:
                    producer.send(exit_topic, key=figi, value=macd_last_value)

                print(figi, macd_last_value)

            producer.close()

    # дальше реалтайм поток
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[(KafkaService()).get_bootstrap()],
        auto_offset_reset='latest',
        key_deserializer=lambda m: m.decode('utf-8'),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )

    stop_time = 0

    for message in consumer:

        start_time = time.time()

        if 'time' not in message.value:
            raise RuntimeError("Field 'time' not find in message")

        if 'close' not in message.value:
            raise RuntimeError("Field 'close' not find in message")

        if message.key not in figies:
            figies[message.key] = {}

        figies[message.key][message.value['time']] = message.value['close']

        receive_time = float(f'{(start_time - stop_time):0.4f}')

        '''если задержка больше 5 сек то это уже реалтайм и можно вычислять'''
        if receive_time > 5 and len(figies[message.key]) > Params().get_candles_count():

            if len(figies[message.key]) > Params().get_candles_count():
                macd_last_value = convert_macd_value(Macd(message.key, figies[message.key]).get_last_value())

                if len(macd_last_value) > 0:
                    kafka_service.send(exit_topic, message.key, macd_last_value)

                    print(message.key, macd_last_value)

        stop_time = time.time()

    consumer.close()


if __name__ == '__main__':
    main()
