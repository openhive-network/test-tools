from decimal import Decimal
from typing import NoReturn, Optional, Union
import warnings


class DecimalConverter:
    @classmethod
    def convert(cls, amount: Union[int, float, str], *, precision: Optional[int] = None) -> Decimal:

        # We could not pass float variable directly to Decimal initializer as from the nature of floats it won't result
        # in the exact decimal value. We need to convert float to string first like https://stackoverflow.com/a/18886013
        # For example: `str(Decimal(0.1)) == '0.1000000000000000055511151231257827021181583404541015625'` is True
        if isinstance(amount, float):
            amount = repr(amount)

        converted = Decimal(amount)

        if precision is not None:
            cls.__assert_precision_is_positive(precision)
            cls.__warn_if_precision_might_be_lost(converted, precision)
            converted = cls.__round_to_precision(converted, precision)

        return converted.normalize()

    @staticmethod
    def __assert_precision_is_positive(precision: int) -> Optional[NoReturn]:
        if precision < 0:
            raise ValueError("Precision must be a positive integer.")

    @staticmethod
    def __round_to_precision(amount: Decimal, precision: int) -> Decimal:
        exponent = Decimal(10) ** (-1 * precision)
        return amount.quantize(exponent)

    @classmethod
    def __warn_if_precision_might_be_lost(cls, amount: Decimal, precision: int) -> None:
        rounded_amount = cls.__round_to_precision(amount, precision)
        if rounded_amount != amount:
            warnings.warn(
                f"Precision lost during value creation.\n"
                f"\n"
                f"Value of {amount} was requested, but it was rounded to {rounded_amount},\n"
                f"because precision of this value is {precision} ({pow(0.1, precision):.{precision}f})."
            )
