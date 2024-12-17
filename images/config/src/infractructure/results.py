import os
import json
import logging

from kafka import KafkaProducer

logging.basicConfig(level=logging.ERROR)

def on_send_success(record_metadata):
    print('Instrument send to config topic, offset', record_metadata.offset)


def on_send_error(excp):
    logging.error('Config send error', exc_info=excp)

def send_results(result):
    servers = os.environ.get('KAFKA_CONNECT', None)
    topic = os.environ.get('TOPIC_CONFIG', None)

    if servers is None:
        print("KAFKA CONNECT not find")
        return

    if topic is None:
        print("TOPIC_CONFIG not find")
        return

    producer = KafkaProducer(
        bootstrap_servers=servers,
        key_serializer=str.encode,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    producer.send(topic, key='instruments', value=json.dumps(result)).add_callback(on_send_success).add_errback(on_send_error)
