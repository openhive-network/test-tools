from datetime import timedelta


class Time:
    def __new__(cls, *_args, **_kwargs):
        raise TypeError(f'Creation object of {Time.__name__} class is forbidden.')

    @staticmethod
    def seconds(amount: int) -> timedelta:
        return timedelta(seconds=amount)

    @staticmethod
    def minutes(amount: int) -> timedelta:
        return timedelta(minutes=amount)

    @staticmethod
    def hours(amount: int) -> timedelta:
        return timedelta(hours=amount)

    @staticmethod
    def days(amount: int) -> timedelta:
        return timedelta(days=amount)
