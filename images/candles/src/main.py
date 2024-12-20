import asyncio
import json
import logging
import os

from tinkoff.invest import AsyncClient, CandleInstrument, SubscriptionInterval, MarketDataRequest, \
    SubscribeCandlesRequest, SubscriptionAction

from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService
from infrastructure.candle_helper import candle_converter
from infrastructure.time_helper import get_time_key_for_period, get_period_by_interval

logging.basicConfig(level=logging.ERROR)

token = os.environ.get('TOKEN', None)
interval = int(os.environ.get('INTERVAL', SubscriptionInterval.SUBSCRIPTION_INTERVAL_UNSPECIFIED))


def is_run():
    return True


def get_instruments_for_market_request(figies: list[str] = None) -> list[CandleInstrument]:
    if figies is None:
        figies = []

    results = []

    for figi in figies:
        results.append(CandleInstrument(figi=figi, interval=interval, ))

    return results


is_candles_received = False


async def main():
    if token is None:
        print("TOKEN not find")
        return

    if interval == SubscriptionInterval.SUBSCRIPTION_INTERVAL_UNSPECIFIED:
        print("INTERVAL not find")
        return

    figies = (ConfigService()).get_instruments()
    figie_codes = list(figies.values())

    async def request_iterator(codes: list[str] = None):

        global is_candles_received

        if codes is None or len(codes) == 0:
            return

        yield MarketDataRequest(
            subscribe_candles_request=SubscribeCandlesRequest(
                waiting_close=False,
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=get_instruments_for_market_request(codes),
            )
        )
        while is_run():
            is_candles_received = False

            await asyncio.sleep(5)

    async with AsyncClient(token) as client:

        global is_candles_received

        async for marketdata in client.market_data_stream.market_data_stream(
                request_iterator(figie_codes)
        ):
            if marketdata.candle:
                # для уведа что свеча пришла

                candler = candle_converter(marketdata.candle)

                candler['time'] = get_time_key_for_period(marketdata.candle.time, get_period_by_interval(interval))

                print(candler)

                is_candles_received = True


if __name__ == '__main__':
    asyncio.run(main())
