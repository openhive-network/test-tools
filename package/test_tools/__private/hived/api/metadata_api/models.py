from __future__ import annotations

from schemas._preconfigured_base_model import PreconfiguredBaseModel


class GetAccountMetadata(PreconfiguredBaseModel, kw_only=True):
    json_metadata: str
    posting_json_metadata: str


class AccountMetadataInfo(PreconfiguredBaseModel, kw_only=True):
    account: str
    json_metadata: str
    posting_json_metadata: str


class FindAccountMetadata(PreconfiguredBaseModel, kw_only=True):
    metadata: list[AccountMetadataInfo]
