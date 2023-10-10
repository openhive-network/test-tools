from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.key_generator import KeyGenerator, KeyGeneratorItem

if TYPE_CHECKING:
    from schemas.fields.basic import PrivateKey, PublicKey


class Account:
    def __init__(self, name_or_generated_item: str | KeyGeneratorItem, secret: str = "secret") -> None:
        self.__secret = secret
        self.__private_key: PrivateKey | None = None
        self.__public_key: PublicKey | None = None
        self.__name: str = ""

        if not isinstance(name_or_generated_item, str):
            self.__name = name_or_generated_item.account_name
            self.__private_key = name_or_generated_item.private_key
            self.__public_key = name_or_generated_item.public_key
        else:
            self.__name = name_or_generated_item

    @property
    def name(self) -> str:
        return self.__name

    @property
    def secret(self) -> str:
        return self.__secret

    @property
    def private_key(self) -> PrivateKey:
        if self.__private_key is None:
            self.__generate_keys()
        assert self.__private_key is not None  # mypy check
        return self.__private_key

    @property
    def public_key(self) -> PublicKey:
        if self.__public_key is None:
            self.__generate_keys()
        assert self.__public_key is not None  # mypy check
        return self.__public_key

    @staticmethod
    def create_multiple(
        number_of_accounts: int, name_base: str = "account", *, secret: str = "secret"
    ) -> list[Account]:
        return [
            Account(generated, secret=secret)
            for generated in KeyGenerator.generate_keys(name_base, number_of_accounts=number_of_accounts, secret=secret)
        ]

    def __generate_keys(self) -> None:
        keys = KeyGenerator.generate_keys(self.__name, secret=self.__secret)[0]
        self.__private_key = keys.private_key
        self.__public_key = keys.public_key

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Account)
        return (self.name, self.secret) == (__value.name, __value.secret)
