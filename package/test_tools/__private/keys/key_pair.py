from __future__ import annotations

from test_tools.__private.keys.private_key import PrivateKey
from test_tools.__private.keys.public_key import PublicKey


class KeyPair:
    def __init__(
        self,
        name: str,
        *,
        secret: str = "secret",
        private_key: PrivateKey | None = None,
        public_key: PublicKey | None = None,
    ):
        self.__secret = secret
        self.__private_key = private_key or PrivateKey(name=name, secret=self.secret)
        self.__public_key = public_key or PublicKey(name=name, secret=self.secret)
        assert self.__private_key.secret == self.secret
        assert self.__public_key.secret == self.secret

    @property
    def secret(self) -> str:
        return self.__secret

    @property
    def private(self) -> PrivateKey:
        return self.__private_key

    @property
    def public(self) -> PublicKey:
        return self.__public_key
