import os
import logging

from tinkoff.invest import (Client)

from instruments_helper import get_instruments
from src.infractructure.kafka_service import KafkaService

logging.basicConfig(level=logging.ERROR)

token = os.environ.get('TOKEN', None)


def main():
    if token is None:
        print("TOKEN not find")
        return

    with Client(token) as client:
        figi = get_instruments(client)

        print(figi)

        kafka_service = KafkaService()

        kafka_service.send(
            KafkaService.get_config_topic_name(),
            KafkaService.get_instrument_key(),
            figi
        )


if __name__ == '__main__':
    main()
