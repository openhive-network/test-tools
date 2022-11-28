from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from functools import total_ordering
import operator
from typing import Any, NoReturn, Optional, TYPE_CHECKING, Union

import abstractcp as acp

from test_tools.__private.exceptions import ParseError
from test_tools.__private.user_handles.implementation import Implementation
from test_tools.__private.utilities.decimal_converter import DecimalConverter

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.asset_handles.token_handle import TokenHandleBase


@total_ordering
class Token(Implementation, acp.Abstract):
    token: str = acp.abstract_class_property(str)
    precision: int = acp.abstract_class_property(int)
    nai: str = acp.abstract_class_property(str)

    def __init__(self, amount: Union[int, float], handle: Optional[TokenHandleBase] = None) -> None:
        super().__init__(handle=handle)
        self.amount = self.__convert_amount_to_internal_representation(amount)

    def __str__(self) -> str:
        return f"{self.amount / (10 ** self.precision):.{self.precision}f} {self.token}"

    def __repr__(self) -> str:
        return f"Asset({self.as_nai()})"

    def __eq__(self, other: Any) -> bool:
        other: Token = self.__convert_to_asset(other, error_detail="compare")
        return self.amount == other.amount

    def __lt__(self, other: Any) -> bool:
        other: Token = self.__convert_to_asset(other, error_detail="compare")
        return self.amount < other.amount

    def __neg__(self) -> Token:
        result = deepcopy(self)
        result.amount = -self.amount
        return result

    def __add__(self, other: Any) -> Token:
        return self.__combine_with(other, operator.add)

    def __sub__(self, other: Any) -> Token:
        return self.__combine_with(other, operator.sub)

    def __iadd__(self, other: Any) -> Token:
        new_asset = self.__combine_with(other, operator.add)
        self.amount = new_asset.amount
        return self

    def __isub__(self, other: Any) -> Token:
        new_asset = self.__combine_with(other, operator.sub)
        self.amount = new_asset.amount
        return self

    @classmethod
    def __template(cls) -> dict:
        return {
            "amount": None,
            "precision": cls.precision,
            "nai": cls.nai,
        }

    def as_nai(self) -> dict:
        template = self.__template().copy()
        template["amount"] = str(self.amount)
        return template

    @classmethod
    def _from_dict(cls, asset_as_dict: dict) -> Token:
        cls.__assert_same_template(asset_as_dict)

        try:
            amount = int(asset_as_dict["amount"])
            precision = int(asset_as_dict["precision"])
        except ValueError as exception:
            raise ParseError("Amount and precision have to be integers.") from exception

        return cls(amount / 10**precision)

    def __convert_amount_to_internal_representation(self, amount: Union[int, float]) -> int:
        amount_decimal = DecimalConverter.convert(amount, precision=self.precision)
        return int(amount_decimal * Decimal(10) ** self.precision)

    def __combine_with(self, other: Any, operator_: Union[operator.add, operator.sub]) -> Token:
        other: Token = self.__convert_to_asset(other, error_detail=operator_.__name__)

        result = deepcopy(self)
        result.amount = operator_(result.amount, other.amount)
        return result

    def __convert_to_asset(self, other: Any, *, error_detail: Optional[str] = None) -> Token:
        error_detail = "operate on" if error_detail is None else error_detail

        try:
            other = self.__handle_asset_conversion(other, error_detail)
        except ParseError as exception:
            raise TypeError(f"Can't {error_detail} asset: `{self}` and `{other}`.") from exception

        self.__assert_same_token(other, error_detail=error_detail)
        return other

    def __handle_asset_conversion(self, other: Any, error_detail: str) -> Token:
        is_testnet = self.token in ("TESTS", "TBD")  # nai json does not store token info, so we assume it is our type

        if isinstance(other, (str, dict)):
            # Break import cycle
            from test_tools.__private.asset.asset import Asset  # pylint: disable=import-outside-toplevel, cyclic-import

            other = Asset.from_(other, treat_dict_as_testnet_currencies=is_testnet)

        if not isinstance(other, Token):
            raise TypeError(f"Can't {error_detail} objects of type `{type(other)}`.")
        return other

    @classmethod
    def __assert_same_template(cls, other: dict) -> Optional[NoReturn]:
        if cls.__template().keys() != other.keys():
            raise ParseError(f"Asset dict keys differ: {other.keys()}, when expected {cls.__template().keys()}.")

        if cls.nai != other["nai"]:
            raise ParseError(f"Asset dict nai differ: `{other['nai']}`, when expected `{cls.nai}`.")

        if cls.precision != other["precision"]:
            raise ParseError(f"Asset dict precision differ: `{other['precision']}`, when expected `{cls.precision}`.")

    def __assert_same_token(self, other: Token, *, error_detail: str) -> Optional[NoReturn]:
        if self.token != other.token:
            raise TypeError(f"Can't {error_detail} assets with different tokens: `{self.token}` and `{other.token}`.")
