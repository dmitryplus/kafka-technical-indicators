import json
import os
import logging
import time

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from kafka import KafkaConsumer

from macd import Macd

logging.basicConfig(level=logging.ERROR)

interval = int(os.environ.get('INTERVAL', 0))
exit_topic_prefix = os.environ.get('TOPIC_PREFIX_MACD', None)

figies: dict[str, dict[str, float]] = {}


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

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[(KafkaService()).get_bootstrap()],
        auto_offset_reset='earliest',
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

        '''если задержка больше 30 сек то это уже реалтайм и можно вычислять'''
        if stop_time > 0 and receive_time > 30 and len(figies[message.key]) > 100:

            macd_last_value = Macd(message.key, figies[message.key]).get_last_value()

            if len(macd_last_value) > 0:
                kafka_service.send(exit_topic, message.key, macd_last_value)

            print(message.key, message.value['time'], macd_last_value)

        stop_time = time.time()


if __name__ == '__main__':
    main()
