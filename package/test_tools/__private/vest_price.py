from __future__ import annotations

from dataclasses import dataclass

from test_tools.__private.asset import Asset


@dataclass
class VestPrice:
    base: Asset.Vest
    quote: Asset.Test

    def __str__(self) -> str:
        ratio = self.quote.amount / self.base.amount / 10**self.base.precision
        return f"{ratio} {self.quote.token} per 1 {self.base.token}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_nai()})"

    @classmethod
    def from_dgpo(cls, dgpo: dict) -> VestPrice:
        vest: Asset.Vest = Asset.from_(dgpo["total_vesting_shares"])
        hive: Asset.Test = Asset.from_(dgpo["total_vesting_fund_hive"])
        return cls(quote=vest, base=hive)

    def as_nai(self) -> dict:
        return {"quote": self.quote.as_nai(), "base": self.base.as_nai()}
