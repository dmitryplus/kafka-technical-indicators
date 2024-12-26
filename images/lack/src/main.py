import json
import os
import logging
from datetime import datetime, timedelta

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from infrastructure.time_helper import get_period_by_interval
from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService

logging.basicConfig(level=logging.ERROR)

sleep_time = int(os.environ.get('SLEEP_TIME', 5))


def get_periods() -> list:
    # INTERVAL_ONE_MIN = 1
    # INTERVAL_FIVE_MIN = 2
    # INTERVAL_FIFTEEN_MIN = 3
    # INTERVAL_30_MIN = 9
    # INTERVAL_ONE_HOUR = 4
    # INTERVAL_FOUR_HOUR = 11
    # INTERVAL_ONE_DAY = 5
    return [1, 2, 3, 9, 4, 11, 5]


def get_need_candles_count(interval: int) -> int:
    # INTERVAL_FIVE_MIN = 2
    if interval == 2:
        return int(os.environ.get('CANDLES_FIVE_MIN', 200))

    # INTERVAL_FIFTEEN_MIN = 3
    if interval == 3:
        return int(os.environ.get('CANDLES_FIFTEEN_MIN', 200))

    # INTERVAL_30_MIN = 9
    if interval == 9:
        return int(os.environ.get('CANDLES_30_MIN', 200))

    # INTERVAL_ONE_HOUR = 4
    if interval == 4:
        return int(os.environ.get('CANDLES_ONE_HOUR', 200))

    # INTERVAL_FOUR_HOUR = 11
    if interval == 11:
        return int(os.environ.get('CANDLES_FOUR_HOUR', 200))

    # INTERVAL_ONE_DAY = 5
    if interval == 5:
        return int(os.environ.get('CANDLES_ONE_DAY', 200))

    # INTERVAL_ONE_MIN = 1
    return int(os.environ.get('CANDLES_ONE_MIN', 200))


def main():
    kafka_service = KafkaService()
    exit_topic = (ConfigService()).get_gaps_topic_name(0)

    instruments = (ConfigService()).get_instruments()


    for interval in get_periods():

        figies = {}

        for figi in list(instruments.values()):
            figies[figi] = []


        topic = (ConfigService()).get_candle_topic_name(interval)
        kafka_service.wait_topic_exists(topic)

        # читаем все данные из топика
        try:

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

                figies[message.key].append(message.value['time'])

            consumer.close()

        except (KafkaError, RuntimeError):
            pass

        for figi in figies:

            if len(figies[figi]) >= get_need_candles_count(interval):
                continue

            time_list = sorted(figies[figi], key=lambda x: x.lower())


            if len(time_list) > 0:
                stop_time_key = time_list[:1][0]
            else:
                stop_time_key = datetime.now().strftime('%Y-%m-%d %H:%M')

            stop_time = datetime.strptime(stop_time_key, '%Y-%m-%d %H:%M')

            minutes_count = get_period_by_interval(interval) * get_need_candles_count(interval) + 1

            start_time = datetime(
                stop_time.year,
                stop_time.month,
                stop_time.day,
                stop_time.hour,
                stop_time.minute,
                0
            ) - timedelta(minutes=minutes_count)

            start_time_key = f'{start_time:%Y-%m-%d %H:%M}'

            message = {
                'figi': figi,
                'interval': interval,
                'start': start_time_key,
                'stop': stop_time_key,
            }

            kafka_service.send(exit_topic, figi, message)

            print(figi, message)


if __name__ == '__main__':
    main()
