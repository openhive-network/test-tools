from __future__ import annotations

from typing import List

from test_tools.__private.key_generator import KeyGenerator
from test_tools.__private.keys.key_pair import KeyPair
from test_tools.__private.keys.private_key import PrivateKey
from test_tools.__private.keys.public_key import PublicKey


class Account:
    def __init__(self, name, *, secret: str = "secret", keys: KeyPair | None = None):
        self.__name = name
        self.__keys = keys or KeyPair(name=name, secret=secret)
        assert secret == self.keys.secret

    @property
    def name(self) -> str:
        return self.__name

    @property
    def keys(self) -> KeyPair:
        return self.__keys

    @staticmethod
    def create_multiple(
        number_of_accounts: int, name_base: str = "account", *, secret: str = "secret"
    ) -> List[Account]:
        return [
            Account(
                account_name := generated["account_name"],
                secret=secret,
                keys=KeyPair(
                    account_name,
                    secret=secret,
                    private_key=PrivateKey(name=account_name, secret=secret, key=generated["private_key"]),
                    public_key=PublicKey(name=account_name, secret=secret, key=generated["public_key"]),
                ),
            )
            for generated in KeyGenerator.generate_keys(name_base, number_of_accounts=number_of_accounts, secret=secret)
        ]
