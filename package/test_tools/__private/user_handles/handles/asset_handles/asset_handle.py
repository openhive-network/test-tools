from __future__ import annotations

from typing import Final, Type, TYPE_CHECKING, Union

from test_tools.__private.asset.asset import Asset
from test_tools.__private.user_handles.handles.asset_handles.hbd_handle import HbdHandle
from test_tools.__private.user_handles.handles.asset_handles.hive_handle import HiveHandle
from test_tools.__private.user_handles.handles.asset_handles.tbd_handle import TbdHandle
from test_tools.__private.user_handles.handles.asset_handles.test_handle import TestHandle
from test_tools.__private.user_handles.handles.asset_handles.vest_handle import VestHandle
from test_tools.__private.user_handles.static_handle import StaticHandle

if TYPE_CHECKING:
    from test_tools.__private.asset.token import Token
    from test_tools.__private.user_handles.handles.asset_handles.token_handle import TokenHandleBase


class AssetHandle(StaticHandle):
    Hbd = HbdHandle
    Tbd = TbdHandle
    Hive = HiveHandle
    Test = TestHandle
    Vest = VestHandle

    _implementation = Asset
    __TOKENS: Final[str, Type[Token]] = {
        "HBD": HbdHandle,
        "TBD": TbdHandle,
        "HIVE": HiveHandle,
        "TESTS": TestHandle,
        "VESTS": VestHandle,
    }

    @classmethod
    def from_(cls, data: Union[str, dict], *, treat_dict_as_testnet_currencies: bool = True) -> TokenHandleBase:
        token = cls._implementation.from_(data=data, treat_dict_as_testnet_currencies=treat_dict_as_testnet_currencies)
        handle_type = cls.__TOKENS[token.token]
        handle = handle_type(__implementation=token)
        return handle
