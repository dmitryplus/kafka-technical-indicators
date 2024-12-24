import os

class MinuteParams(object):
    __fast: int = int(os.environ.get("MACD_FAST", 12))
    __slow: int = int(os.environ.get("MACD_SLOW", 26))
    __signal: int = int(os.environ.get("MACD_SIGNAL", 9))

    __candles_count = int(os.environ.get("MACD_CANDLES_COUNT", 100))

    def get_fast(self) -> int:
        return self.__fast

    def get_slow(self) -> int:
        return self.__slow

    def get_signal(self) -> int:
        return self.__signal

    def get_candles_count(self) -> int:
        return self.__candles_count
