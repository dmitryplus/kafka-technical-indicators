import json
import os

from kafka import KafkaAdminClient, KafkaProducer
from time import sleep

from .SingletonMeta import SingletonMeta

class KafkaService(metaclass=SingletonMeta):
    '''
    Класс для работы с kafka
    '''

    __bootstrap: str = None

    __config_topic_name: str = None
    __instrument_key: str = 'instruments'

    @classmethod
    def __init__(cls):

        cls.__bootstrap = os.environ.get('KAFKA_CONNECT', None)
        if cls.get_bootstrap() is None:
            raise RuntimeError("KAFKA CONNECT not find")

        cls.__config_topic_name = os.environ.get('TOPIC_CONFIG', None)
        if cls.get_config_topic_name() is None:
            raise RuntimeError("TOPIC_CONFIG not find")

    @classmethod
    def wait_topic_exists(cls, topic: str):

        kafka_available = False


        while not kafka_available:
            try:

                kafka_admin = KafkaAdminClient(bootstrap_servers=cls.get_bootstrap())

                if topic not in kafka_admin.list_topics():
                    raise Exception('topic not fund')

                kafka_available = True

            except Exception as e:
                print(e)
                sleep(3)


    @classmethod
    def get_bootstrap(cls):
        return cls.__bootstrap

    @classmethod
    def get_config_topic_name(cls):
        return cls.__config_topic_name
    @classmethod
    def get_instrument_key(cls):
        return cls.__instrument_key


    @classmethod
    def send(cls, topic: str, key: str, value: str):

        cls.wait_topic_exists(topic)

        producer = KafkaProducer(
            bootstrap_servers=cls.get_bootstrap(),
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        producer.send(topic, key=key, value=value)
        producer.close()


