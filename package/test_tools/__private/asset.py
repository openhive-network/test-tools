from copy import deepcopy
from typing import Final, Union
import warnings

import abstractcp as acp


class AssetBase(acp.Abstract):
    token: str = acp.abstract_class_property(str)
    precision: int = acp.abstract_class_property(int)
    nai: str = acp.abstract_class_property(str)

    def __init__(self, amount):
        self.amount = self.__convert_amount_to_internal_representation(amount, self.precision)

    @staticmethod
    def __convert_amount_to_internal_representation(amount: Union[int, float], precision: int) -> int:
        AssetBase.__warn_if_precision_might_be_lost(amount, precision)
        return int(round(amount, precision) * pow(10, precision))

    @staticmethod
    def __warn_if_precision_might_be_lost(amount: Union[int, float], precision: int):
        rounded_value = round(amount, precision)
        acceptable_error = 0.1**10

        if abs(amount - rounded_value) > acceptable_error:
            warnings.warn(
                f"Precision lost during asset creation.\n"
                f"\n"
                f"Asset with amount {amount} was requested, but this value was rounded to {rounded_value},\n"
                f"because precision of this asset is {precision} ({pow(0.1, precision):.3f})."
            )

    def as_nai(self):
        return {
            "amount": str(self.amount),
            "precision": self.precision,
            "nai": self.nai,
        }

    def __add__(self, other):
        self.__assert_same_operands_type(other, "Can't add assets with different tokens or nai")
        result = deepcopy(self)
        result.amount += other.amount
        return result

    def __neg__(self):
        result = deepcopy(self)
        result.amount = -self.amount
        return result

    def __sub__(self, other):
        self.__assert_same_operands_type(other, "Can't subtract assets with different tokens or nai")
        return self + -other

    def __iadd__(self, other):
        self.__assert_same_operands_type(other, "Can't add assets with different tokens or nai")
        self.amount += other.amount
        return self

    def __isub__(self, other):
        self.__assert_same_operands_type(other, "Can't subtract assets with different tokens or nai")
        self.amount -= other.amount
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
        if isinstance(other, AssetBase):
            self.__assert_same_operands_type(other, "Can't compare assets with different tokens or nai")
            return self.amount < other.amount

        if isinstance(other, str):
            amount, token = other.split()
            if self.token != token:
                raise TypeError(f"Can't compare assets with different tokens ({self.token} and {token}).")
            return self.amount < float(amount) * pow(10, self.precision)

        if isinstance(other, dict):
            self.__assert_same_keys(other)

            if self.nai != other["nai"]:
                raise TypeError(f"Can't compare assets with different NAIs ({self.nai} and {other['nai']}).")

            return self.amount < int(other["amount"])

        raise TypeError(f"Assets can't be compared with objects of type {type(other)}")

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self < other and self != other

    def __ge__(self, other):
        return self == other or self > other

    def __eq__(self, other):
        if isinstance(other, str):
            _amount, token = other.split()
            if self.token != token:
                raise TypeError(f"Can't compare assets with different tokens ({self.token} and {token}).")
            return str(self) == other

        if isinstance(other, AssetBase):
            self.__assert_same_operands_type(other, "Can't compare assets with different tokens or nai")
            return self.amount == other.amount

        if isinstance(other, dict):
            self.__assert_same_keys(other)

            if self.nai != other["nai"]:
                raise TypeError(f"Can't compare assets with different NAIs ({self.nai} and {other['nai']}).")

            return self.as_nai() == other

        raise TypeError(f"Assets can't be compared with objects of type {type(other)}")

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
