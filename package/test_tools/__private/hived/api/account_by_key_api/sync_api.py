from __future__ import annotations

from beekeepy.handle.remote import AbstractSyncApi

from schemas.apis import account_by_key_api


class AccountByKeyApi(AbstractSyncApi):
    @AbstractSyncApi.endpoint_jsonrpc
    def get_key_references(self, *, keys: list[str]) -> account_by_key_api.GetKeyReferences:
        raise NotImplementedError
