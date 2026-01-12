from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from schemas.fields.compound import Price

# NAI to symbol mapping for generated asset types
_NAI_TO_SYMBOL = {
    "@@000000021": "HIVE",
    "@@000000013": "HBD",
    "@@000000037": "VESTS",
}


def _get_precision(asset: Any) -> int:
    """Get precision from asset, handling both method and attribute access."""
    if callable(getattr(asset, "precision", None)):
        return cast(int, asset.precision())
    return cast(int, asset.precision)


def _get_symbol(asset: Any) -> str:
    """Get symbol from asset, handling both Hf26Asset and generated types."""
    if hasattr(asset, "get_asset_information"):
        return cast(str, asset.get_asset_information().get_symbol())
    return _NAI_TO_SYMBOL.get(asset.nai, asset.nai)


def _as_nai(asset: Any) -> dict[str, Any]:
    """Get NAI representation from asset, handling both Hf26Asset and generated types."""
    if hasattr(asset, "as_nai"):
        return cast(dict[str, Any], asset.as_nai())
    # For generated types, use dict() method or manual construction
    if hasattr(asset, "dict"):
        return cast(dict[str, Any], asset.dict())
    return {"amount": asset.amount, "nai": asset.nai, "precision": asset.precision}


@dataclass
class VestPrice:
    base: Any
    quote: Any

    def __str__(self) -> str:
        ratio = int(self.quote.amount) / int(self.base.amount) / 10 ** _get_precision(self.base)
        return f"{ratio} {_get_symbol(self.quote)} per 1 {_get_symbol(self.base)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_nai()})"

    @classmethod
    def from_dgpo(cls, dgpo: Any) -> VestPrice:
        return cls(quote=dgpo.total_vesting_shares, base=dgpo.total_vesting_fund_hive)

    def as_nai(self) -> dict[str, dict[str, Any]]:
        return {"quote": _as_nai(self.quote), "base": _as_nai(self.base)}

    def as_schema(self) -> Price:
        return Price(base=self.base, quote=self.quote)
