import os
from tinkoff.invest import (Client)

from instruments_helper import get_instruments

token = os.environ.get('TOKEN', None)


def main():
    if token is None:
        print("TOKEN not find")
        return

    with Client(token) as client:
        figi = get_instruments(client)

        print(figi)


if __name__ == '__main__':
    main()
