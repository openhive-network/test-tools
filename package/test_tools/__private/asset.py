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

    def __init__(self, amount: Union[int, float]) -> None:
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

    def as_nai(self) -> dict:
        return {
            "amount": str(self.amount),
            "precision": self.precision,
            "nai": self.nai,
        }

    def __combine_with(
        self, asset: Union[str, dict, AssetBase], operator_: Union[operator.add, operator.sub]
    ) -> AssetBase:
        if isinstance(asset, dict):
            asset = self.__convert_asset_from_dict(asset)

        if isinstance(asset, str):
            asset = Asset.from_string(asset)

        if not isinstance(asset, AssetBase):
            raise TypeError(f"Assets can't be added with objects of type {type(asset)}")

        if self.token != asset.token:
            raise TypeError(f"Can't add assets with different tokens ({self.token} and {asset.token}).")
        result = deepcopy(self)
        result.amount = operator_(result.amount, asset.amount)
        return result

    def __add__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        return self.__combine_with(other, operator.add)

    def __neg__(self) -> AssetBase:
        result = deepcopy(self)
        result.amount = -self.amount
        return result

    def __sub__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        return self.__combine_with(other, operator.sub)

    def __iadd__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        new_asset = self.__combine_with(other, operator.add)
        self.amount = new_asset.amount
        return self

    def __isub__(self, other: Union[str, dict, AssetBase]) -> AssetBase:
        new_asset = self.__combine_with(other, operator.sub)
        self.amount = new_asset.amount
        return self

    def __convert_asset_from_dict(self, asset_as_dict: dict):
        """
        The function detects whether the operation takes place in testnet or mainnet assets and automatically
        uses "from_dict" with testnet currencies or mainnet currencies.
        """
        if self.token in ("HIVE", "HBD"):
            return Asset.from_dict(asset_as_dict, testnet_currencies=False)
        return Asset.from_dict(asset_as_dict)

    def __lt__(self, other: Union[str, dict, AssetBase]) -> bool:
        if isinstance(other, dict):
            other = self.__convert_asset_from_dict(other)

        if isinstance(other, str):
            other = Asset.from_string(other)

        if not isinstance(other, AssetBase):
            raise TypeError(f"Assets can't be compared with objects of type {type(other)}")

        if self.token != other.token:
            raise TypeError(f"Can't compare assets with different tokens ({self.token} and {other.token}).")
        return self.amount < other.amount

    def __le__(self, other: Union[str, dict, AssetBase]) -> bool:
        return self == other or self < other

    def __gt__(self, other: Union[str, dict, AssetBase]) -> bool:
        return not self < other and self != other

    def __ge__(self, other: Union[str, dict, AssetBase]) -> bool:
        return self == other or self > other

    def __eq__(self, other: Union[str, dict, AssetBase]) -> bool:
        if isinstance(other, dict):
            other = self.__convert_asset_from_dict(other)

        if isinstance(other, str):
            other = Asset.from_string(other)

        if not isinstance(other, AssetBase):
            raise TypeError(f"Assets can't be compared with objects of type {type(other)}")

        if self.token != other.token:
            raise TypeError(f"Can't compare assets with different tokens ({self.token} and {other.token}).")
        return self.amount == other.amount

    def __str__(self) -> str:
        if self.token is None:
            raise RuntimeError(f"Asset with nai={self.nai} hasn't string representaion")

        return f"{self.amount / (10 ** self.precision):.{self.precision}f} {self.token}"

    def __repr__(self) -> str:
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
    def from_string(cls, asset_as_string: str) -> AssetBase:
        """
        The function allows you to convert an asset from string to the appropriate Asset type.
        """
        amount, token = asset_as_string.split()
        assets = [cls.Hbd, cls.Hive, cls.Vest, cls.Tbd, cls.Test]
        for asset in assets:
            if token == asset.token:
                return asset(float(amount))
        raise TypeError(f'Asset with token "{token}" do not exist.')

    @classmethod
    def from_dict(cls, asset_as_dict: dict, *, testnet_currencies: bool = True) -> AssetBase:
        """
        The function allows you to convert an asset from JSON to the appropriate Asset type.
        In default state of testnet_currencies parameter, function return Asset object in
        testnet form eg: Test, Tbd, Vest.
        """
        asset_as_dict_template = {"amount": None, "precision": None, "nai": None}
        if set(asset_as_dict.keys()) != set(asset_as_dict_template.keys()):
            raise TypeError(
                f"The keys did not match.\n"
                f"Expected: {set(asset_as_dict_template)}.\n"
                f"Actual: {set(asset_as_dict.keys())}"
            )  # fmt: skip
        try:
            asset_as_dict["amount"] = int(asset_as_dict["amount"])
        except ValueError as error:
            raise ValueError("Value of 'amount' have to be integer.") from error
        if testnet_currencies:
            assets = [cls.Tbd, cls.Test, cls.Vest]
        else:
            assets = [cls.Hbd, cls.Hive, cls.Vest]
        for asset in assets:
            if asset_as_dict["nai"] == asset.nai:
                return asset(asset_as_dict["amount"] / 10 ** asset_as_dict["precision"])
        raise TypeError(f'Asset with nai "{asset_as_dict["nai"]}" do not exist.')
