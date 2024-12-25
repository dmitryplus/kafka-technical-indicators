import json
import os
import logging
import time
from datetime import datetime, timedelta
from logging import ERROR

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from kafka import KafkaConsumer

logging.basicConfig(level=logging.ERROR)

interval = int(os.environ.get('INTERVAL', 0))

# exit_topic_prefix = os.environ.get('TOPIC_PREFIX_MACD', None)
#

figies: dict[str, list[str]] = {}


def main():
    if interval == 0:
        print("INTERVAL not find")
        return

    try:

        kafka_service = KafkaService()
        topic = (ConfigService()).get_candle_topic_name(interval)

        kafka_service.wait_topic_exists(topic)

        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[(KafkaService()).get_bootstrap()],
            auto_offset_reset='earliest',
            key_deserializer=lambda m: m.decode('utf-8'),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=1000
        )

        for message in consumer:

            if 'time' not in message.value:
                raise RuntimeError("Field 'time' not find in message")

            if message.key not in figies:
                figies[message.key] = []

            figies[message.key].append(message.value['time'])

            print(message)

        consumer.close()

        print(figies)

    except RuntimeError:
        pass


if __name__ == '__main__':
    main()
