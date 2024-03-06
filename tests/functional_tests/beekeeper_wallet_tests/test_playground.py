# mypy: ignore-errors
# ruff: noqa

from __future__ import annotations

import pytest
import wax

from helpy._interfaces.wax import WaxOperationFailedError
from helpy.exceptions import HelpyError, RequestError
from schemas.operations.custom_json_operation import CustomJsonOperation
from schemas.operations.delegate_rc_operation import DelegateRcOperation
import test_tools as tt


# def test_keys() -> None:
#     node = tt.InitNode()
#     node.config.plugin.append("transaction_status_api")
#     node.config.plugin.append("market_history_api")

#     node.run()
#     wallet = tt.Wallet(attach_to=node)

#     # wallet.create_account("alice", hives=tt.Asset.Test(1000), vests=tt.Asset.Test(1000000), hbds=tt.Asset.Tbd(1000))
#     # wallet.create_account("bob", hives=tt.Asset.Test(1000), vests=tt.Asset.Test(1000000), hbds=tt.Asset.Tbd(1000))

#     # wallet.api.get_encrypted_memo("alice", "initminer", "#this is memo")

#     wallet.api.create_account("initminer", "alice", "{}")

#     dupa = wallet.is_running()
#     encrypted = wallet.api.get_encrypted_memo("initminer", "alice", "#this is memo")
#     decrypted = wallet.api.decrypt_memo(encrypted)
#     pass

#     #  '#11111111Df8FT8jSnUBfKXVu9Ybucim3yLp1XQB3i2FDnCWTLvFpFu9SkGq6dip3xkP45WTwuiWbb3gkWXW5YiFkET2pnYZKRkBHZLryGFwRwf5eWxJdM8CqNfgvKd6'


def test_dupa():
    main_encryption_key = "6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4"
    other_encryption_key = "5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW"
    encrypted_memo = "111111118N2MrWbLqudcbQR4EUziLoGAqR7XN"

    encoded_memo = wax.encode_encrypted_memo(
        encrypted_content=encrypted_memo.encode(),
        main_encryption_key=main_encryption_key.encode(),
        other_encryption_key=other_encryption_key.encode(),
    )
    # encoded_memo = wax.encode_encrypted_memo(encrypted_content=encrypted_memo.encode(), main_encryption_key=main_encryption_key.encode())
    decoded_memo = wax.decode_encrypted_memo(encoded_memo)

    pass
