from tinkoff.invest import Candle, HistoricCandle
from tinkoff.invest.utils import quotation_to_decimal

__all__ = [
    'candle_converter',
    'convert_history_to_candle',
]


def candle_converter(candle: Candle):
    """
    Переводит свечу в список
    :param candle: Candle
    :return:
    """

    return {
        'figi': candle.figi,
        'high': float(quotation_to_decimal(candle.high)),
        'open': float(quotation_to_decimal(candle.open)),
        'close': float(quotation_to_decimal(candle.close)),
        'low': float(quotation_to_decimal(candle.low)),
        'volume': candle.volume
    }

def convert_history_to_candle(candle: HistoricCandle, figi: str):
    result = Candle()
    result.high = candle.high
    result.low = candle.low
    result.open = candle.open
    result.close = candle.close
    result.volume = candle.volume
    result.figi = figi
    result.time = candle.time

    return result
