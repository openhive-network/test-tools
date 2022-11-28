from typing import Union

from test_tools.__private.asset.asset import Asset
from test_tools.__private.user_handles.handles.asset_handles.token_handle import TokenHandleBase

# 1
# class HiveHandle(Handle):
#
#     def __init__(self, amount: Union[int, float]) -> None:
#         super().__init__(
#             implementation=Asset.Hive(
#                 amount,
#                 handle=self,
#             ),
#         )

# 2
# class HiveHandleExisting(HiveHandle):
#     def __init__(self, implementation: Token) -> None:
#         setattr(implementation, "_Token__handle", self)
#         setattr(self, "_Handle__implementation", implementation)


# 3
class HiveHandle(TokenHandleBase):
    def __init__(self, amount: Union[int, float]) -> None:
        super().__init__(amount, token=Asset.Hive)
