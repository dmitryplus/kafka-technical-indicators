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

    @classmethod
    def __init__(cls):

        cls.__bootstrap = os.environ.get('KAFKA_CONNECT', None)
        if cls.get_bootstrap() is None:
            raise RuntimeError("KAFKA CONNECT not find")

    @classmethod
    def wait_topic_exists(cls, topic: str):

        kafka_available = False

        while not kafka_available:
            try:

                kafka_admin = KafkaAdminClient(bootstrap_servers=cls.get_bootstrap())

                if topic not in kafka_admin.list_topics():
                    raise RuntimeError(f'Topic "{topic}" not found')

                kafka_available = True

            except Exception as e:
                print(e)
                sleep(3)

    @classmethod
    def get_bootstrap(cls):
        return cls.__bootstrap

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
