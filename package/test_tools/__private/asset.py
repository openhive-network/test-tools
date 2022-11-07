from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import operator
from typing import Final, Union
import warnings

import abstractcp as acp


class AssetBase(acp.Abstract):
    token: str = acp.abstract_class_property(str)
    precision: int = acp.abstract_class_property(int)
    nai: str = acp.abstract_class_property(str)

    def __init__(self, amount: Union[int, float]):
        self.amount = self.__convert_amount_to_internal_representation(amount)

    def __convert_amount_to_internal_representation(self, amount: Union[int, float]) -> int:
        self.__warn_if_precision_might_be_lost(amount)

        amount_decimal = self.__convert_to_decimal(amount)
        return int(amount_decimal * Decimal(10) ** self.precision)

    def __convert_to_decimal(self, amount: Union[int, float, str]) -> Decimal:
        # We could not pass float variable directly to Decimal initializer as from the nature of floats it won't result
        # in the exact decimal value. We need to convert float to string first like https://stackoverflow.com/a/18886013
        # For example: `str(Decimal(0.1)) == '0.1000000000000000055511151231257827021181583404541015625'` is True
        if isinstance(amount, float):
            amount = repr(amount)

        precision = Decimal(10) ** (-1 * self.precision)
        return Decimal(amount).quantize(precision).normalize()

    def __warn_if_precision_might_be_lost(self, amount: Union[int, float]) -> None:
        rounded_value = round(amount, self.precision)
        acceptable_error = 0.1**10

        if abs(amount - rounded_value) > acceptable_error:
            warnings.warn(
                f"Precision lost during asset creation.\n"
                f"\n"
                f"Asset with amount {amount} was requested, but this value was rounded to {rounded_value},\n"
                f"because precision of this asset is {self.precision} ({pow(0.1, self.precision):.3f})."
            )

    def as_nai(self):
        return {
            "amount": str(self.amount),
            "precision": self.precision,
            "nai": self.nai,
        }

    @staticmethod
    def __operate_on_assets(
        first: AssetBase, second: Union[str, dict, AssetBase], operator_: Union[operator.add, operator.sub]
    ) -> AssetBase:
        if isinstance(second, dict):
            first.__assert_same_keys(second)
            if first.nai != second["nai"]:
                raise TypeError(f"Can't add assets with different NAIs ({first.nai} and {second['nai']}).")
            result = deepcopy(first)
            result.amount = operator_(result.amount, int(second["amount"]))
            return result

        if isinstance(second, str):
            second = Asset.convert_string_to_asset(second)

        if not isinstance(second, AssetBase):
            raise TypeError(f"Assets can't be added with objects of type {type(second)}")

        if first.token != second.token:
            raise TypeError(f"Can't add assets with different tokens ({first.token} and {second.token}).")
        result = deepcopy(first)
        result.amount = operator_(result.amount, second.amount)
        return result

    def __add__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        return self.__operate_on_assets(self, other, operator.add)

    def __neg__(self):
        result = deepcopy(self)
        result.amount = -self.amount
        return result

    def __sub__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        return self.__operate_on_assets(self, other, operator.sub)

    def __iadd__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        self.amount = self.__operate_on_assets(self, other, operator.add).amount
        return self

    def __isub__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        self.amount = self.__operate_on_assets(self, other, operator.sub).amount
        return self

    def __assert_same_operands_type(self, other, error):
        if type(self) is not type(other):
            raise TypeError(error)

    def __assert_same_keys(self, other):
        if set(self.as_nai().keys()) != set(other.keys()):
            raise TypeError(
                f"The keys did not match.\n"
                f"Expected: {set(self.as_nai().keys())}.\n"
                f"Actual: {set(other.keys())}"
            )  # fmt: skip

    def __lt__(self, other):
        if isinstance(other, dict):
            self.__assert_same_keys(other)
            if self.nai != other["nai"]:
                raise TypeError(f"Can't compare assets with different NAIs ({self.nai} and {other['nai']}).")
            return self.amount < int(other["amount"])

        if isinstance(other, str):
            other = Asset.convert_string_to_asset(other)

        if not isinstance(other, AssetBase):
            raise TypeError(f"Assets can't be compared with objects of type {type(other)}")

        if self.token != other.token:
            raise TypeError(f"Can't compare assets with different tokens ({self.token} and {other.token}).")
        return self.amount < other.amount

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self < other and self != other

    def __ge__(self, other):
        return self == other or self > other

    def __eq__(self, other):
        if isinstance(other, dict):
            self.__assert_same_keys(other)
            if self.nai != other["nai"]:
                raise TypeError(f"Can't compare assets with different NAIs ({self.nai} and {other['nai']}).")
            return self.as_nai() == other

        if isinstance(other, str):
            other = Asset.convert_string_to_asset(other)

        if not isinstance(other, AssetBase):
            raise TypeError(f"Assets can't be compared with objects of type {type(other)}")

        if self.token != other.token:
            raise TypeError(f"Can't compare assets with different tokens ({self.token} and {other.token}).")
        return self.amount == other.amount

    def __str__(self):
        if self.token is None:
            raise RuntimeError(f"Asset with nai={self.nai} hasn't string representaion")

        return f"{self.amount / (10 ** self.precision):.{self.precision}f} {self.token}"

    def __repr__(self):
        return f"Asset({self.as_nai()})"


class Asset:
    class Hbd(AssetBase):
        token: Final[str] = "HBD"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000013"

    class Tbd(AssetBase):
        token: Final[str] = "TBD"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000013"

    class Hive(AssetBase):
        token: Final[str] = "HIVE"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000021"

    class Test(AssetBase):
        token: Final[str] = "TESTS"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000021"

    class Vest(AssetBase):
        token: Final[str] = "VESTS"
        precision: Final[int] = 6
        nai: Final[str] = "@@000000037"

    @classmethod
    def convert_string_to_asset(cls, asset_as_string: str):
        amount, token = asset_as_string.split()
        assets = [Asset.Hbd, Asset.Hive, Asset.Vest, Asset.Tbd, Asset.Test]
        for asset in assets:
            if token == asset.token:
                return asset(float(amount))
        raise TypeError(f'Asset with token "{token}" do not exist.')
