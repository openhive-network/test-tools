from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from test_tools.__private.asset import Asset

    AnyAsset = Union[
        Asset.Hive, Asset.Test,
        Asset.Hbd, Asset.Tbd,
        Asset.Vest,
    ]  # fmt: skip
