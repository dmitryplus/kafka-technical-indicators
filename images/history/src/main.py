import json
import logging
import os
from pathlib import Path

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from tinkoff.invest import (Client, CandleInterval)
from tinkoff.invest.caching.market_data_cache.cache import MarketDataCache
from tinkoff.invest.caching.market_data_cache.cache_settings import MarketDataCacheSettings

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from infrastructure.candle_helper import candle_converter, convert_history_to_candle
from infrastructure.time_helper import time_from_key_to_utc, get_period_by_interval, get_time_key_for_period

logging.basicConfig(level=logging.ERROR)

token = os.environ.get('TOKEN', None)


def get_market_candle_interval(interval: int) -> CandleInterval:
    # INTERVAL_FIVE_MIN = 2
    if interval == 2:
        return CandleInterval.CANDLE_INTERVAL_5_MIN

    # INTERVAL_FIFTEEN_MIN = 3
    if interval == 3:
        return CandleInterval.CANDLE_INTERVAL_15_MIN

    # INTERVAL_30_MIN = 9
    if interval == 9:
        return CandleInterval.CANDLE_INTERVAL_30_MIN

    # INTERVAL_ONE_HOUR = 4
    if interval == 4:
        return CandleInterval.CANDLE_INTERVAL_HOUR

    # INTERVAL_FOUR_HOUR = 11
    if interval == 11:
        return CandleInterval.CANDLE_INTERVAL_4_HOUR

    # INTERVAL_ONE_DAY = 5
    if interval == 5:
        return CandleInterval.CANDLE_INTERVAL_DAY

    # INTERVAL_ONE_MIN = 1
    return CandleInterval.CANDLE_INTERVAL_1_MIN


def main():
    if token is None:
        print("TOKEN not find")
        return

    kafka_service = KafkaService()
    topic = (ConfigService()).get_history_action_topic_name(0)

    kafka_service.wait_topic_exists(topic)

    while True:

        with Client(token) as client:

            try:

                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=[(KafkaService()).get_bootstrap()],
                    group_id='history-consumer',
                    auto_offset_reset='earliest',
                    key_deserializer=lambda m: m.decode('utf-8'),
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                )

                for message in consumer:

                    if 'start' not in message.value:
                        raise RuntimeError("Field 'start' not find in message")

                    if 'stop' not in message.value:
                        raise RuntimeError("Field 'stop' not find in message")

                    if 'figi' not in message.value:
                        raise RuntimeError("Field 'figi' not find in message")

                    if 'interval' not in message.value:
                        raise RuntimeError("Field 'interval' not find in message")

                    time_from = time_from_key_to_utc(message.value['start'])
                    time_to = time_from_key_to_utc(message.value['stop'])

                    interval = message.value['interval']

                    exit_topic = (ConfigService()).get_candle_topic_name(interval)

                    kafka_service.wait_topic_exists(exit_topic)

                    producer = KafkaProducer(
                        bootstrap_servers=[(KafkaService()).get_bootstrap()],
                        key_serializer=str.encode,
                        value_serializer=lambda v: json.dumps(v).encode('utf-8')
                    )

                    settings = MarketDataCacheSettings(base_cache_dir=Path('market_data_cache'))
                    market_data_cache = MarketDataCache(settings=settings, services=client)
                    for candle in market_data_cache.get_all_candles(
                            figi=message.value['figi'],
                            from_=time_from,
                            to=time_to,
                            interval=get_market_candle_interval(interval),
                    ):
                        if candle.is_complete:
                            current_candle = candle_converter(convert_history_to_candle(candle, message.value['figi']))

                            current_candle['time'] = get_time_key_for_period(candle.time, get_period_by_interval(interval))

                            producer.send(exit_topic, key=current_candle['figi'], value=current_candle)

                            print(current_candle)

                    producer.close()

                consumer.close()

            except (KafkaError, RuntimeError):
                pass


if __name__ == '__main__':
    main()
