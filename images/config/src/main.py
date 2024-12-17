import os
import logging
from tinkoff.invest import (Client)

from instruments_helper import get_instruments
from infractructure.results import send_results

logging.basicConfig(level=logging.DEBUG)

token = os.environ.get('TOKEN', None)


def main():
    if token is None:
        print("TOKEN not find")
        return

    with Client(token) as client:
        figi = get_instruments(client)

        print(figi)

        send_results(figi)


if __name__ == '__main__':
    main()
