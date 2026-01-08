from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from schemas.fields.compound import Price

if TYPE_CHECKING:
    from database_api.database_api_description import GetDynamicGlobalPropertiesResponse as GetDynamicGlobalProperties
    from schemas.fields.assets._base import AssetNaiAmount
    from wax.helpy import Hf26Asset


@dataclass
class VestPrice:
    base: Hf26Asset.VestsT | Hf26Asset.HiveT | Hf26Asset.HbdT
    quote: Hf26Asset.VestsT | Hf26Asset.HiveT | Hf26Asset.HbdT

    def __str__(self) -> str:
        ratio = int(self.quote.amount) / int(self.base.amount) / 10 ** int(self.base.precision())
        return f"{ratio} {self.quote.get_asset_information().get_symbol()} per 1 {self.base.get_asset_information().get_symbol()}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_nai()})"

    @classmethod
    def from_dgpo(cls, dgpo: GetDynamicGlobalProperties) -> VestPrice:
        return cls(quote=dgpo.total_vesting_shares, base=dgpo.total_vesting_fund_hive)

    def as_nai(self) -> dict[str, dict[str, AssetNaiAmount | str]]:
        return {"quote": self.quote.as_nai(), "base": self.base.as_nai()}

    def as_schema(self) -> Price:
        return Price(base=self.base, quote=self.quote)
