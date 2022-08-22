from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union


class KeyBase(ABC):
    def __init__(self, name: str, *, secret: str = 'secret'):
        self.__name = name
        self.__secret = secret
        self.__value: Optional[str] = None

    @property
    def _value(self) -> str:
        if not self.__is_generated():
            self.__value = self._generate_value(self.__name, self.__secret)

        return self.__value

    @_value.setter
    def _value(self, value: str) -> None:
        self.__value = value

    @abstractmethod
    def _generate_value(self, name: str, secret: str) -> str:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._value}')"

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: Union[str, KeyBase]) -> bool:
        if isinstance(other, KeyBase):
            return self._value == other._value

        if isinstance(other, str):
            return self._value == other

        raise TypeError(f'{self.__class__.__name__} can be compared only with keys and strings.')

    def __is_generated(self) -> bool:
        return self.__value is not None
