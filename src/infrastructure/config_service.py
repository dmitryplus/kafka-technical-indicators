import json
import os

from kafka import KafkaConsumer
from tinkoff.invest import SubscriptionInterval

from .kafka_service import KafkaService

from .SingletonMeta import SingletonMeta


class ConfigService(metaclass=SingletonMeta):
    '''
    Класс для работы с конфигурацией
    '''

    __configs: dict[str, str | dict] = {}

    __config_topic_name: str = None
    __instrument_key: str = 'instruments'

    __config_topic_1_name: str = 'candles-1-min'
    __config_topic_5_name: str = 'candles-5-min'
    __config_topic_15_name: str = 'candles-15-min'
    __config_topic_30_name: str = 'candles-30-min'
    __config_topic_1_hour_name: str = 'candles-1-hour'
    __config_topic_day_name: str = 'candles-1-day'

    @classmethod
    def __init__(cls):

        cls.__config_topic_name = os.environ.get('TOPIC_CONFIG', None)
        if cls.get_config_topic_name() is None:
            raise RuntimeError("TOPIC_CONFIG not find")

        cls.init_config_from_kafka()

    @classmethod
    def get_config_topic_name(cls):
        return cls.__config_topic_name

    @classmethod
    def get_instrument_key(cls):
        return cls.__instrument_key

    @classmethod
    def get_config(cls):
        return cls.__configs

    @classmethod
    def init_config_from_kafka(cls):

        consumer = KafkaConsumer(
            cls.get_config_topic_name(),
            bootstrap_servers=[(KafkaService()).get_bootstrap()],
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            key_deserializer=lambda m: m.decode('utf-8'),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=3000
        )

        for message in consumer:
            cls.__configs[message.key] = message.value

    @classmethod
    def get_instruments(cls) -> dict[str, str]:
        return cls.__configs[cls.__instrument_key]

    @classmethod
    def get_candle_topic_name(cls, interval: int) -> str | RuntimeError:
        match interval:
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_DAY:
                return cls.__config_topic_day_name
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_HOUR:
                return cls.__config_topic_1_hour_name
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_30_MIN:
                return cls.__config_topic_30_name
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIFTEEN_MINUTES:
                return cls.__config_topic_15_name
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES:
                return cls.__config_topic_5_name
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE:
                return cls.__config_topic_1_name
            case _:
                raise RuntimeError("Interval not in range for topic name")
