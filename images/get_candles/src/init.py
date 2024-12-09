from tinkoff.invest import (Client)

from instruments_helper import get_instruments

__all__ = ['init_data']


def init_data(token: str, figies: dict = {}):
    '''
    первоначальное заполнение данных, создание блоков, обновление архива свеч
    :param token: str
    :param figies: dict|none
    :return: figies: dict
    '''
    with Client(token) as client:
        figies = get_instruments(client)

        for key in figies:

            print('init data ', figies[key]['figi'])

    return figies