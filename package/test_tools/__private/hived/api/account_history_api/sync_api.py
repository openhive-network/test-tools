from __future__ import annotations

from beekeepy.handle.remote import AbstractSyncApi

from schemas.apis import account_history_api


class AccountHistoryApi(AbstractSyncApi):
    api = AbstractSyncApi.endpoint_jsonrpc

    @api
    def get_account_history(
        self,
        *,
        account: str,
        start: int = -1,
        limit: int = 1_000,
        include_reversible: bool = True,
        operation_filter_low: int | None = None,
        operation_filter_high: int | None = None,
    ) -> account_history_api.GetAccountHistory:
        raise NotImplementedError

    @api
    def get_transaction(self, *, id_: str, include_reversible: bool = True) -> account_history_api.GetTransaction:
        raise NotImplementedError

    @api
    def enum_virtual_ops(
        self,
        *,
        block_range_begin: int,
        block_range_end: int,
        operation_begin: int | None = None,
        filter_: int | None = None,
        limit: int | None = None,
        include_reversible: bool = True,
        group_by_block: bool = False,
    ) -> account_history_api.EnumVirtualOps:
        raise NotImplementedError

    @api
    def get_ops_in_block(
        self, *, block_num: int, only_virtual: bool = False, include_reversible: bool = True
    ) -> account_history_api.GetOpsInBlock:
        raise NotImplementedError
