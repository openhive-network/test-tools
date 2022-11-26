from decimal import Decimal
from typing import Optional, Union
import warnings


class DecimalConverter:
    @classmethod
    def convert(cls, amount: Union[int, float, str], *, precision: Optional[int] = None) -> Decimal:
        if precision is not None:
            cls.__warn_if_precision_might_be_lost(amount, precision)

        # We could not pass float variable directly to Decimal initializer as from the nature of floats it won't result
        # in the exact decimal value. We need to convert float to string first like https://stackoverflow.com/a/18886013
        # For example: `str(Decimal(0.1)) == '0.1000000000000000055511151231257827021181583404541015625'` is True
        if isinstance(amount, float):
            amount = repr(amount)

        if precision is None:
            return Decimal(amount).normalize()

        exponent = Decimal(10) ** (-1 * precision)
        return Decimal(amount).quantize(exponent).normalize()

    @staticmethod
    def __warn_if_precision_might_be_lost(amount: Union[int, float], precision: int) -> None:
        rounded_value = round(amount, precision)
        acceptable_error = 0.1**10

        if abs(amount - rounded_value) > acceptable_error:
            warnings.warn(
                f"Precision lost during asset creation.\n"
                f"\n"
                f"Asset with amount {amount} was requested, but this value was rounded to {rounded_value},\n"
                f"because precision of this asset is {precision} ({pow(0.1, precision):.3f})."
            )
