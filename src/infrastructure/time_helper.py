from datetime import datetime, timedelta
import pytz

__all__ = ['time_to_local', 'time_to_key', 'get_time_key_for_period', 'time_from_key_to_utc', 'get_period_by_interval']

from tinkoff.invest import SubscriptionInterval


def time_to_local(dt: datetime):
    return dt.astimezone(pytz.timezone('Europe/Moscow'))


def time_to_key(dt: datetime):
    return f'{time_to_local(dt):%Y-%m-%d %H:%M}'


def get_time_key_for_period(dt: datetime, period: int):
    minute = int(f'{time_to_local(dt):%M}')

    time_compose_key = 0

    if minute % period == 0:
        time_compose_key = time_to_key(dt)
    else:
        for i in range(1, period):
            if ((minute - i) % period) == 0:
                time_compose_key = time_to_key(dt - timedelta(minutes=i))

    return time_compose_key


def time_from_key_to_utc(time_key: str):
    test_time = datetime.strptime(time_key, '%Y-%m-%d %H:%M')

    result = datetime(
        test_time.year,
        test_time.month,
        test_time.day,
        test_time.hour,
        test_time.minute,
        0,
        tzinfo=pytz.utc
    ) - timedelta(hours=+3)

    return result


def get_period_by_interval(interval: int) -> int | RuntimeError:
    match interval:
        case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_DAY:
            return 60 * 24
        case SubscriptionInterval.SUBSCRIPTION_INTERVAL_4_HOUR:
            return 60 * 4
        case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_HOUR:
            return 60
        case SubscriptionInterval.SUBSCRIPTION_INTERVAL_30_MIN:
            return 30
        case SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIFTEEN_MINUTES:
            return 15
        case SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES:
            return 5
        case SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE:
            return 1
        case _:
            raise RuntimeError("Interval not in range for period")
