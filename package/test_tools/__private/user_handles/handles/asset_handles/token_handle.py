from __future__ import annotations

from functools import total_ordering
import typing
from typing import Any, Type, TYPE_CHECKING, Union

from test_tools.__private.asset.token import Token
from test_tools.__private.user_handles.get_implementation import get_handle, get_implementation
from test_tools.__private.user_handles.inside_static_handle import InsideStaticHandle

if TYPE_CHECKING:
    from test_tools.__private.type_annotations.typed_dicts.nai import NaiDict


@total_ordering
class TokenHandleBase(InsideStaticHandle):
    """Base class for all Token-like handles."""

    def __init__(self, amount: Union[int, float], token: Type[Token]) -> None:
        super().__init__(
            implementation=token(
                amount,
                handle=self,
            ),
        )

    def __eq__(self, other: Any) -> bool:
        other = self.__get_implementation_if_exists(other)
        return self.__implementation == other

    def __lt__(self, other: Any) -> bool:
        other = self.__get_implementation_if_exists(other)
        return self.__implementation < other

    def __neg__(self) -> TokenHandleBase:
        token = -self.__implementation
        return get_handle(token)

    def __add__(self, other: Any) -> TokenHandleBase:
        other = self.__get_implementation_if_exists(other)
        token = self.__implementation + other
        return get_handle(token)

    def __sub__(self, other: Any) -> TokenHandleBase:
        other = self.__get_implementation_if_exists(other)
        token = self.__implementation - other
        return get_handle(token)

    def __iadd__(self, other: Any) -> TokenHandleBase:
        other = self.__get_implementation_if_exists(other)
        self.__implementation += other
        return self

    def __isub__(self, other: Any) -> TokenHandleBase:
        other = self.__get_implementation_if_exists(other)
        self.__implementation -= other
        return self

    @property
    def __implementation(self) -> Token:
        return typing.cast(Token, get_implementation(self))

    @__implementation.setter
    def __implementation(self, value) -> None:
        setattr(self, "__implementation", value)  # default behaviour, just set the value

    @staticmethod
    def __get_implementation_if_exists(other: Any) -> Union[Token, Any]:
        if isinstance(other, TokenHandleBase):
            return get_implementation(other)
        return other

    def as_nai(self) -> NaiDict:
        """Returns the token in the NAI representation (JSON format as a dictionary)."""
        return self.__implementation.as_nai()
