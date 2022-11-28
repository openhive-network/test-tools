from typing import Union

from test_tools.__private.asset.asset import Asset
from test_tools.__private.user_handles.handles.asset_handles.token_handle import TokenHandleBase


class TestHandle(TokenHandleBase):
    def __init__(self, amount: Union[int, float]) -> None:
        super().__init__(amount, token=Asset.Test)
