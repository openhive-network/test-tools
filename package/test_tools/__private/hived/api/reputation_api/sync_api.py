from __future__ import annotations

from beekeepy.handle.remote import AbstractSyncApi

from schemas.apis import reputation_api


class ReputationApi(AbstractSyncApi):
    @AbstractSyncApi.endpoint_jsonrpc
    def get_account_reputations(
        self, *, account_lower_bound: str, limit: int = 1_000
    ) -> reputation_api.GetAccountReputations:
        raise NotImplementedError
