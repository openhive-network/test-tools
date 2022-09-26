from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union


class KeyBase(ABC):
    def __init__(self, name: str, *, secret: str = "secret"):
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

        raise TypeError(f"{self.__class__.__name__} can be compared only with keys and strings.")

    def __hash__(self) -> int:
        # Counting hash of string which holds hash seems stupid, but it covers a case, where we
        # have set of keys stored as strings, and we check if key object is contained by set.
        # In such case key object have to return same hash as string present in container.
        #
        # So hashes of key object and key expressed as string have to be equal:
        # hash(tt.PrivateKey('initminer')) == hash('5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n')
        return hash(self._value)

    def __is_generated(self) -> bool:
        return self.__value is not None
