from __future__ import annotations

from schemas._preconfigured_base_model import PreconfiguredBaseModel


class GetMetadata(PreconfiguredBaseModel, kw_only=True):
    json_metadata: str
    posting_json_metadata: str
