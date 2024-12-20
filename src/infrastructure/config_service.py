import json
import os
from time import sleep

from kafka import KafkaConsumer
from tinkoff.invest import SubscriptionInterval

from .kafka_service import KafkaService

from .SingletonMeta import SingletonMeta


class ConfigService(metaclass=SingletonMeta):
    '''
    Класс для работы с конфигурацией
    '''

    __configs: dict[str, str | dict] = {}

    INSTRUMENT_KEY: str = 'instruments'
    CONFIG_TOPIC_NAME: str = os.environ.get('TOPIC_CONFIG', None)

    CONFIG_TOPIC_1_NAME: str = 'candles-1-min'
    CONFIG_TOPIC_5_NAME: str = 'candles-5-min'
    CONFIG_TOPIC_15_NAME: str = 'candles-15-min'
    CONFIG_TOPIC_30_NAME: str = 'candles-30-min'
    CONFIG_TOPIC_1_HOUR_NAME: str = 'candles-1-hour'
    CONFIG_TOPIC_4_HOUR_NAME: str = 'candles-4-hour'
    CONFIG_TOPIC_DAY_NAME: str = 'candles-1-day'

    @classmethod
    def __init__(cls):

        if cls.get_config_topic_name() is None:
            raise RuntimeError("TOPIC_CONFIG not find")

        need_reinit = False

        while not need_reinit:

            print("Wait init configuration")

            cls.init_config_from_kafka()

            if cls.INSTRUMENT_KEY in cls.__configs:
                need_reinit = True

            if not need_reinit:
                sleep(5)


    @classmethod
    def get_config_topic_name(cls):
        return cls.CONFIG_TOPIC_NAME

    @classmethod
    def get_instrument_key(cls):
        return cls.INSTRUMENT_KEY

    @classmethod
    def get_config(cls):
        return cls.__configs

    @classmethod
    def init_config_from_kafka(cls):

        (KafkaService()).wait_topic_exists(cls.get_config_topic_name())

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

        if cls.INSTRUMENT_KEY not in cls.__configs:
            raise RuntimeError(f'Key "{cls.INSTRUMENT_KEY}" not found or empty ')

        return cls.__configs[cls.INSTRUMENT_KEY]

    @classmethod
    def get_candle_topic_name(cls, interval: int) -> str | RuntimeError:
        match interval:
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_DAY:
                return cls.CONFIG_TOPIC_DAY_NAME
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_4_HOUR:
                return cls.CONFIG_TOPIC_4_HOUR_NAME
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_HOUR:
                return cls.CONFIG_TOPIC_1_HOUR_NAME
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_30_MIN:
                return cls.CONFIG_TOPIC_30_NAME
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIFTEEN_MINUTES:
                return cls.CONFIG_TOPIC_15_NAME
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES:
                return cls.CONFIG_TOPIC_5_NAME
            case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE:
                return cls.CONFIG_TOPIC_1_NAME
            case _:
                raise RuntimeError("Interval not in range for topic name")
