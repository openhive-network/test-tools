from __future__ import annotations

from beekeepy import beekeeper_factory


def test_simply():
    with beekeeper_factory() as beekeeper:
        with beekeeper.create_session() as session:
            with session.create_wallet(name="wallet", password="password") as wallet:
                public_key = wallet.generate_key()
                assert public_key in wallet.public_keys

        beekeeper.delete()
