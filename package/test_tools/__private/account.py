from __future__ import annotations

from typing import List

from test_tools.__private.key_generator import KeyGenerator
from test_tools.__private.keys import PrivateKey, PublicKey


class Account:
    def __init__(self, name, secret='secret'):
        self.__name = name
        self.__secret = secret
        self.__private_key = PrivateKey(self.__name, secret=self.__secret)
        self.__public_key = PublicKey(self.__name, secret=self.__secret)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def secret(self) -> str:
        return self.__secret

    @property
    def private_key(self) -> PrivateKey:
        return self.__private_key

    @property
    def public_key(self) -> PublicKey:
        return self.__public_key

    @staticmethod
    def create_multiple(
        number_of_accounts: int, name_base: str = 'account', *, secret: str = 'secret'
    ) -> List[Account]:
        accounts = []
        for generated in KeyGenerator.generate_keys(name_base, number_of_accounts=number_of_accounts, secret=secret):
            account = Account(generated['account_name'], secret=secret)
            # pylint: disable=unused-private-member, protected-access
            account.__private_key._value = generated['private_key']
            account.__public_key._value = generated['public_key']
            # pylint: enable=unused-private-member, protected-access

            accounts.append(account)

        return accounts
