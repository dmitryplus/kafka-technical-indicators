import os.path
from tinkoff.invest.services import Services

__all__ = 'get_instruments'

good_tickers = []
bad_tickers = []


def get_need_tickers():
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/need_tickers.txt'

    if not os.path.exists(file_path):
        return

    with open(file_path) as file_tickers:
        for ticker in file_tickers:
            ticker = ticker.rstrip('\n')
            good_tickers.append(ticker)


def get_bad_tickers():
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/not_need_tickers.txt'

    if not os.path.exists(file_path):
        return

    with open(file_path) as file_tickers:
        for ticker in file_tickers:
            ticker = ticker.rstrip('\n')
            bad_tickers.append(ticker)


def check_instrument(instrument):
    common_check = (instrument.country_of_risk == 'RU'
                    and instrument.currency == 'rub'
                    and (instrument.exchange != 'spb_close' or instrument.exchange != 'otc_ncc')
                    and instrument.class_code == 'TQBR'
                    and instrument.ticker not in bad_tickers)

    if good_tickers:
        return common_check and instrument.ticker in good_tickers

    return common_check


def get_instruments(client: Services):
    figies = {}

    get_need_tickers()
    get_bad_tickers()

    instruments = client.instruments.shares().instruments

    for inst in instruments:
        if check_instrument(inst):
            figies[inst.ticker] = inst.figi

    return figies
