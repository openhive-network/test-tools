from __future__ import annotations

from beekeepy.handle.remote import AbstractSyncApi

from schemas.apis import rc_api


class RcApi(AbstractSyncApi):
    api = AbstractSyncApi.endpoint_jsonrpc

    @api
    def find_rc_accounts(self, *, accounts: list[str], refresh_mana: bool = False) -> rc_api.FindRcAccounts:
        raise NotImplementedError

    @api
    def get_resource_params(self) -> rc_api.GetResourceParams:
        raise NotImplementedError

    @api
    def get_resource_pool(self) -> rc_api.GetResourcePool:
        raise NotImplementedError

    @api
    def list_rc_accounts(self, *, accounts: list[str], refresh_mana: bool = False) -> rc_api.ListRcAccounts:
        raise NotImplementedError

    @api
    def list_rc_direct_delegations(self, *, start: tuple[str, str], limit: int) -> rc_api.ListRcDirectDelegations:
        raise NotImplementedError
