import json
import os
import logging
from time import sleep

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from kafka import KafkaConsumer

from macd import Macd

logging.basicConfig(level=logging.ERROR)

interval = int(os.environ.get('INTERVAL', 0))

figies: dict[str, dict[str, float]] = {}


def main():
    if interval == 0:
        print("INTERVAL not find")
        return

    kafka_service = KafkaService()
    topic = (ConfigService()).get_candle_topic_name(interval)

    kafka_service.wait_topic_exists(topic)

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[(KafkaService()).get_bootstrap()],
        auto_offset_reset='earliest',
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

        macd_last_value = Macd(message.key, figies[message.key]).get_last_value()

        print(macd_last_value)


if __name__ == '__main__':
    main()
