import os
import logging

from tinkoff.invest import (Client)

from instruments_helper import get_instruments
from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService

logging.basicConfig(level=logging.ERROR)

token = os.environ.get('TOKEN', None)


def main():
    if token is None:
        print("TOKEN not find")
        return

    with Client(token) as client:
        figi = get_instruments(client)

        print(figi)

        (KafkaService()).send(
            ConfigService.CONFIG_TOPIC_NAME,
            ConfigService.INSTRUMENT_KEY,
            figi
        )


if __name__ == '__main__':
    main()
