from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from functools import total_ordering
import operator
from typing import Any, Final, NoReturn, Optional, TypeVar, Union

import abstractcp as acp

from schemas.__private.hive_fields_basic_schemas import AssetHF26
from test_tools.__private.exceptions import ParseError
from test_tools.__private.utilities.decimal_converter import DecimalConverter

AssetLimitT = TypeVar("AssetLimitT", bound="AssetBase")


@total_ordering
class AssetBase(acp.Abstract):
    token: str = acp.abstract_class_property(str)
    precision: int = acp.abstract_class_property(int)
    nai: str = acp.abstract_class_property(str)

    def __init__(self, amount: Union[int, float]) -> None:
        self.amount = self.__convert_amount_to_internal_representation(amount)

    def __str__(self) -> str:
        return f"{self.amount / (10 ** self.precision):.{self.precision}f} {self.token}"

    def __repr__(self) -> str:
        return f"Asset({self.as_nai()})"

    def __eq__(self, other: Any) -> bool:
        other: AssetBase = self.__convert_to_asset(other, error_detail="compare")
        return self.amount == other.amount

    def __lt__(self, other: Any) -> bool:
        other: AssetBase = self.__convert_to_asset(other, error_detail="compare")
        return self.amount < other.amount

    def __neg__(self) -> AssetBase:
        result = deepcopy(self)
        result.amount = -self.amount
        return result

    def __add__(self, other: Any) -> AssetBase:
        return self.__combine_with(other, operator.add)

    def __sub__(self, other: Any) -> AssetBase:
        return self.__combine_with(other, operator.sub)

    def __iadd__(self, other: Any) -> AssetBase:
        new_asset = self.__combine_with(other, operator.add)
        self.amount = new_asset.amount
        return self

    def __isub__(self, other: Any) -> AssetBase:
        new_asset = self.__combine_with(other, operator.sub)
        self.amount = new_asset.amount
        return self

    def __mul__(self, other: Any) -> AssetBase:
        return self.__combine_with_numeric(other, operator.mul)

    def __rmul__(self, other: Any) -> AssetBase:
        return self.__combine_with_numeric(other, operator.mul)

    def __imul__(self, other: Any) -> AssetBase:
        new_asset = self.__combine_with_numeric(other, operator.mul)
        self.amount = new_asset.amount
        return self

    def __truediv__(self, other: Any) -> AssetBase:
        return self.__combine_with_numeric(other, operator.truediv)

    def __rtruediv__(self, other: Any) -> AssetBase:
        return self.__combine_with_numeric(other, operator.truediv)

    def __itruediv__(self, other: Any) -> AssetBase:
        new_asset = self.__combine_with_numeric(other, operator.itruediv)
        self.amount = new_asset.amount
        return self

    def as_nai(self) -> dict:
        return self.__nai_template(amount=str(self.amount))

    @classmethod
    def _from_dict(cls, asset_as_dict: dict) -> AssetBase:
        cls.__assert_same_template(asset_as_dict)

        try:
            amount = int(asset_as_dict["amount"])
            precision = int(asset_as_dict["precision"])
        except ValueError as exception:
            raise ParseError("Amount and precision have to be integers.") from exception

        return cls(amount / 10**precision)

    @classmethod
    def __nai_template(cls, *, amount: Optional[str] = None) -> dict:
        return {
            "amount": amount,
            "precision": cls.precision,
            "nai": cls.nai,
        }

    def __convert_amount_to_internal_representation(self, amount: Union[int, float, AssetHF26]) -> int:
        if isinstance(amount, AssetHF26):
            return amount.amount
        amount_decimal = DecimalConverter.convert(amount, precision=self.precision)
        return int(amount_decimal * Decimal(10) ** self.precision)

    def __combine_with(self, other: Any, operator_: Union[operator.add, operator.sub]) -> AssetBase:
        other: AssetBase = self.__convert_to_asset(other, error_detail=operator_.__name__)

        result = deepcopy(self)
        result.amount = operator_(result.amount, other.amount)
        return result

    def __combine_with_numeric(self, other: Any, operator_: Union[operator.mul, operator.truediv]) -> AssetBase:
        if not isinstance(other, (int, float)):
            raise TypeError(f"Asset {operator_.__name__} is only possible with numeric values.")

        result = deepcopy(self)
        result.amount = int(operator_(result.amount, other))
        return result

    def __convert_to_asset(self, other: Any, *, error_detail: Optional[str] = None) -> AssetBase:
        error_detail = "operate on" if error_detail is None else error_detail

        try:
            other = self.__handle_asset_conversion(other, error_detail)
        except ParseError as exception:
            raise TypeError(f"Can't {error_detail} asset: `{self}` and `{other}`.") from exception

        self.assert_same_token(self, other, error_detail=error_detail)
        return other

    def __handle_asset_conversion(self, other: Any, error_detail: str) -> AssetBase:
        is_testnet = self.token in ("TESTS", "TBD")  # nai json does not store token info, so we assume it is our type

        if isinstance(other, (str, dict, AssetHF26)):
            other = Asset.from_(other, treat_dict_as_testnet_currencies=is_testnet)

        self.assert_is_asset(other, error_detail=error_detail)
        return other

    @classmethod
    def __assert_same_template(cls, other: dict) -> Optional[NoReturn]:
        if cls.__nai_template().keys() != other.keys():
            raise ParseError(f"Asset dict keys differ: {other.keys()}, when expected {cls.__nai_template().keys()}.")

        if cls.nai != other["nai"]:
            raise ParseError(f"Asset dict nai differ: `{other['nai']}`, when expected `{cls.nai}`.")

        if cls.precision != other["precision"]:
            raise ParseError(f"Asset dict precision differ: `{other['precision']}`, when expected `{cls.precision}`.")

    @staticmethod
    def assert_same_token(first: AssetBase, other: AssetBase, *, error_detail: str) -> Optional[NoReturn]:
        if first.token != other.token:
            raise TypeError(f"Can't {error_detail} assets with different tokens: `{first.token}` and `{other.token}`.")

    @staticmethod
    def assert_is_asset(*other: Any, error_detail: str) -> Optional[NoReturn]:
        for asset in other:
            if not isinstance(asset, (AssetBase, AssetHF26)):
                raise TypeError(f"Can't {error_detail} objects of type `{type(asset)}`.")


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

    class Range:
        """
        Represents a range of assets by providing the upper and lower bounds for a given value.
        It functions similarly to the built-in python `range(100, 110)` function, providing a convenient way to
        represent a range of assets within a specified value range.

        Usage:
            tt.Asset.Range(lower_limit=tt.Asset.Hive(100), upper_limit=tt.Asset.Hive(110))

        :param lower_limit is required. When tolerance is given it acts as the value to which we refer when specifying
        the percentage range.
        :param tolerance: is defined as a positive number, which is a percentage of the upper and lower deviations e.g:
            asset = tt.Asset.Hive(100)
            tt.Asset.Range(asset, tolerance=10) -> the range of this asset is from tt.Asset.Hive(90) to inclusive (100)

        Upper limit and tolerance should be used interchangeably.
        """

        def __init__(
            self,
            lower_limit: AssetLimitT,
            upper_limit: Optional[AssetLimitT] = None,
            *,
            tolerance: Union[int, float, None] = None,
        ):
            if not upper_limit and not tolerance:
                raise TypeError("Range has to be specified with either `upper_limit` or `tolerance`")

            if upper_limit and tolerance:
                raise TypeError("Please choose only one option from `upper_limit` or `tolerance`")

            if tolerance and tolerance < 0:
                raise TypeError("`tolerance` should be given as an positive number")

            self.__lower_limit = lower_limit if upper_limit else lower_limit - (lower_limit * tolerance / 100)
            self.__upper_limit = upper_limit if upper_limit else lower_limit + (lower_limit * tolerance / 100)
            AssetBase.assert_is_asset(self.__lower_limit, self.__upper_limit, error_detail="create range on")
            AssetBase.assert_same_token(self.__lower_limit, self.__upper_limit, error_detail="create range on")
            assert self.__lower_limit < self.__upper_limit, "The upper limit cannot be greater than the lower limit"

        def __contains__(self, item: AssetBase):
            AssetBase.assert_is_asset(item, error_detail="check if asset is in range when")
            AssetBase.assert_same_token(item, self.__lower_limit, error_detail="check if asset is in range when")
            return self.__lower_limit <= item <= self.__upper_limit

    @classmethod
    def from_(cls, data: Union[str, dict], *, treat_dict_as_testnet_currencies: bool = True) -> AssetBase:
        """
        This function allows you to convert an asset from string or JSON format to the appropriate object of Asset type.

        * In case of dict:
            Nai dictionary does not hold the information about token type.

            By default, treat_dict_as_testnet_currencies parameter is set to True. As a result, an Asset object will be
            created in the testnet format. If you want to create an object in mainnet form, set it to False.
        """
        if isinstance(data, str):
            return cls.__from_sting(data)
        if isinstance(data, dict):
            return cls.__from_dict(data, testnet_currencies=treat_dict_as_testnet_currencies)
        if isinstance(data, AssetHF26):
            return cls.__from_dict(data.dict(by_alias=True))
        raise ParseError(f"Can't convert `{type(data)}` to Asset object.")

    @classmethod
    def __from_sting(cls, asset_as_string: str) -> AssetBase:
        amount, token = asset_as_string.split()
        assets = [cls.Hbd, cls.Hive, cls.Vest, cls.Tbd, cls.Test]
        for asset in assets:
            if token == asset.token:
                return asset(float(amount))
        raise ParseError(
            f"Asset with token `{token}` does not exist.\n"
            f"Supported tokens are: {[asset.token for asset in assets]}."
        )

    @classmethod
    def __from_dict(cls, asset_as_dict: dict, *, testnet_currencies: bool = True) -> AssetBase:
        if "nai" not in asset_as_dict:
            raise ParseError("Asset dictionary has no nai.")

        assets = [cls.Vest]
        assets += [cls.Tbd, cls.Test] if testnet_currencies else [cls.Hbd, cls.Hive]

        for asset in assets:
            if asset_as_dict["nai"] == asset.nai:
                # When it will be implemented according to the Handle's practice  should be removed
                return asset._from_dict(asset_as_dict)  # pylint: disable=protected-access
        raise ParseError(
            f"Asset with nai `{asset_as_dict['nai']}` does not exist.\n"
            f"Supported nai's are: {[asset.nai for asset in assets]}."
        )
