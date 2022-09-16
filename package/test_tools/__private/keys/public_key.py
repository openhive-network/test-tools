from __future__ import annotations

from test_tools.__private.key_generator import KeyGenerator
from test_tools.__private.keys.key_base import KeyBase


class PublicKey(KeyBase):
    def _generate_value(self, name: str, secret: str) -> str:
        return KeyGenerator.generate_keys(name, secret=secret)[0]["public_key"]
