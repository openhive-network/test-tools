from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from schemas.fields.compound import Price

if TYPE_CHECKING:
    from helpy import Hf26Asset
    from schemas.apis.database_api import GetDynamicGlobalProperties


@dataclass
class VestPrice:
    base: Hf26Asset.VestsT | Hf26Asset.HiveT | Hf26Asset.HbdT
    quote: Hf26Asset.VestsT | Hf26Asset.HiveT | Hf26Asset.HbdT

    def __str__(self) -> str:
        ratio = int(self.quote.amount) / int(self.base.amount) / 10 ** int(self.base.precision)
        return f"{ratio} {self.quote.get_asset_information().get_symbol()} per 1 {self.base.get_asset_information().get_symbol()}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_nai()})"

    @classmethod
    def from_dgpo(cls, dgpo: GetDynamicGlobalProperties) -> VestPrice:
        return cls(quote=dgpo.total_vesting_shares, base=dgpo.total_vesting_fund_hive)

    def as_nai(self) -> dict[str, dict[str, str]]:
        return {"quote": self.quote.dict(), "base": self.base.dict()}

    def as_schema(self) -> Price[Hf26Asset.HiveT, Hf26Asset.HbdT, Hf26Asset.VestsT]:
        return Price(base=self.base, quote=self.quote)
