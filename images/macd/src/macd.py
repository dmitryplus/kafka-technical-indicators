import math

import numpy as np
import talib

from params import MinuteParams


class Macd(object):
    params: object = {}

    main_line: list = []
    signal_line: list = []
    histogram: list = []

    last_time_key: str = ""

    def __init__(self, figi: str, closes: dict):
        self.params = MinuteParams()
        self.set_values(figi, closes)

    def set_values(self, figi: str, closes: dict):

        keys = sorted(closes.keys(), key=lambda x: x.lower())
        keys = keys[-(self.params.get_candles_count()):]

        self.last_time_key = keys[-1:][0]

        sort_closes = []
        for key in keys:
            sort_closes.append(closes[key])

        self.main_line, self.signal_line, self.histogram = talib.MACD(
            np.real(np.asarray(sort_closes)),
            self.params.get_fast(),
            self.params.get_slow(),
            self.params.get_signal()
        )

    def get_last_value(self) -> dict[str, float]:

        last_main_line = self.main_line[-1:][0]
        last_signal_line = self.signal_line[-1:][0]
        last_histogram = self.histogram[-1:][0]

        if math.isnan(last_main_line):
            return {}

        return {
            'time': self.last_time_key,
            'main_line': float(last_main_line),
            'signal_line': float(last_signal_line),
            'histogram': float(last_histogram)
        }
