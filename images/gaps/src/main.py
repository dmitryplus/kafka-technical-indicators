import json
import os
import logging
import time
from datetime import datetime, timedelta
from logging import ERROR

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from infrastructure.time_helper import time_from_key_to_utc

logging.basicConfig(level=logging.ERROR)

interval = int(os.environ.get('INTERVAL', 0))

figies: dict[str, list[str]] = {}


def get_period():
    # INTERVAL_FIVE_MIN = 2
    if interval == 2:
        return 60 * 5

    # INTERVAL_FIFTEEN_MIN = 3
    if interval == 3:
        return 60 * 15

    # INTERVAL_30_MIN = 9
    if interval == 9:
        return 60 * 30

    # INTERVAL_ONE_HOUR = 4
    if interval == 4:
        return 60 * 60

    # INTERVAL_FOUR_HOUR = 11
    if interval == 11:
        return 60 * 60 * 4

    # INTERVAL_ONE_DAY = 5
    if interval == 5:
        return 60 * 60 * 24

    # INTERVAL_ONE_MIN = 1
    return 60


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

        consumer.close()

    except (KafkaError, RuntimeError):
        pass

    print(figies)

    for figi in figies:

        time_list = sorted(figies[figi], key=lambda x: x.lower())

        empty_gaps = []

        for i in range(len(time_list) - 1):

            start_time_key = time_list[i]
            stop_time_key = time_list[i + 1]

            start_time = time_from_key_to_utc(start_time_key)

            next_time = time_from_key_to_utc(stop_time_key)

            diff = next_time - start_time

            if int(diff.total_seconds()) != get_period():
                empty_gaps.append({
                    'start_key': start_time_key,
                    'stop_key': stop_time_key,
                })


        print(figi)


if __name__ == '__main__':
    main()
