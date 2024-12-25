import json
import os
import logging

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from kafka import KafkaConsumer

from macd import Macd
from params import Params

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

    kafka_service.wait_topic_exists(topic)


    consumer_history = KafkaConsumer(
        topic,
        bootstrap_servers=[(KafkaService()).get_bootstrap()],
        auto_offset_reset='earliest',
        key_deserializer=lambda m: m.decode('utf-8'),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000
    )

    for message in consumer_history:

        if 'time' not in message.value:
            raise RuntimeError("Field 'time' not find in message")

        if 'close' not in message.value:
            raise RuntimeError("Field 'close' not find in message")

        if message.key not in figies:
            figies[message.key] = {}

        figies[message.key][message.value['time']] = message.value['close']

        print(message.key, message.value['time'], message)

    consumer_history.close()

    for figi in figies:
        if len(figies[figi]) > Params().get_candles_count():
            macd_last_value = Macd(figi, figies[figi]).get_last_value()
            if len(macd_last_value) > 0:
                kafka_service.send(exit_topic, figi, macd_last_value)
            print(figi, macd_last_value)


    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[(KafkaService()).get_bootstrap()],
        auto_offset_reset='latest',
        key_deserializer=lambda m: m.decode('utf-8'),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )

    for message in consumer:

        if 'time' not in message.value:
            raise RuntimeError("Field 'time' not find in message")

        if 'close' not in message.value:
            raise RuntimeError("Field 'close' not find in message")

        if message.key not in figies:
            figies[message.key] = {}

        figies[message.key][message.value['time']] = message.value['close']

        if len(figies[message.key]) > Params().get_candles_count():
            macd_last_value = Macd(message.key, figies[message.key]).get_last_value()

            if len(macd_last_value) > 0:
                kafka_service.send(exit_topic, message.key, macd_last_value)

        print(message.key, message.value['time'], macd_last_value)


    consumer.close()


if __name__ == '__main__':
    main()
