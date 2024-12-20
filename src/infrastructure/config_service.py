import json
import os

from kafka import KafkaConsumer

from .kafka_service import KafkaService

from .SingletonMeta import SingletonMeta

class ConfigService(metaclass=SingletonMeta):
    '''
    Класс для работы с конфигурацией
    '''

    __configs: dict[str, str | dict] = None

    __config_topic_name: str = None
    __instrument_key: str = 'instruments'

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

        kafka_service = KafkaService()

        consumer = KafkaConsumer(
            kafka_service.get_config_topic_name(),
            bootstrap_servers=[kafka_service.get_bootstrap()],
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            key_deserializer=lambda m: m.decode('utf-8'),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=3000
        )

        for message in consumer:
            cls.__configs[message.key] = message.value


