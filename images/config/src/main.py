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

        config_service = ConfigService()

        (KafkaService()).send(
            config_service.get_config_topic_name(),
            config_service.get_instrument_key(),
            figi
        )


if __name__ == '__main__':
    main()
