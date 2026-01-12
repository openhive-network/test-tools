from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import Literal

from beekeepy.handle.remote import AbstractSyncApi
from database_api import database_api_description as database_api  # noqa: TCH002

from schemas.transaction import Transaction
from test_tools.__private.hived.api.database_api.common import DatabaseApiCommons
from wax.helpy._interfaces.asset import Hf26Asset


class DatabaseApi(AbstractSyncApi, DatabaseApiCommons):
    api = AbstractSyncApi.endpoint_jsonrpc

    @api
    def find_account_recovery_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindAccountRecoveryRequestsResponse:
        raise NotImplementedError

    @api
    def find_accounts(
        self, *, accounts: list[str], delayed_votes_active: bool | None = None
    ) -> database_api.FindAccountsResponse:
        raise NotImplementedError

    @api
    def find_change_recovery_account_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindChangeRecoveryAccountRequestsResponse:
        raise NotImplementedError

    @api
    def find_collateralized_conversion_requests(
        self, *, account: str
    ) -> database_api.FindCollateralizedConversionRequestsResponse:
        raise NotImplementedError

    @api
    def find_comments(self, *, comments: list[tuple[str, str]]) -> database_api.FindCommentsResponse:
        raise NotImplementedError

    @api
    def find_decline_voting_rights_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindDeclineVotingRightsRequestsResponse:
        raise NotImplementedError

    @api
    def find_escrows(self, *, from_: str = "") -> database_api.FindEscrowsResponse:
        raise NotImplementedError

    @api
    def find_hbd_conversion_requests(self, *, account: str) -> database_api.FindHbdConversionRequestsResponse:
        raise NotImplementedError

    @api
    def find_limit_orders(self, *, account: str) -> database_api.FindLimitOrdersResponse:
        raise NotImplementedError

    @api
    def find_owner_histories(self, *, owner: str = "") -> database_api.FindOwnerHistoriesResponse:
        raise NotImplementedError

    @api
    def find_proposals(self, *, proposal_ids: list[int]) -> database_api.FindProposalsResponse:
        raise NotImplementedError

    @api
    def find_recurrent_transfers(self, *, from_: str = "") -> database_api.FindRecurrentTransfersResponse:
        raise NotImplementedError

    @api
    def find_savings_withdrawals(self, *, account: str) -> database_api.FindSavingsWithdrawalsResponse:
        raise NotImplementedError

    @api
    def find_vesting_delegation_expirations(
        self, *, account: str
    ) -> database_api.FindVestingDelegationExpirationsResponse:
        raise NotImplementedError

    @api
    def find_vesting_delegations(self, *, account: str) -> database_api.FindVestingDelegationsResponse:
        raise NotImplementedError

    @api
    def find_withdraw_vesting_routes(
        self, *, account: str, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.FindWithdrawVestingRoutesResponse:
        raise NotImplementedError

    @api
    def find_witnesses(self, *, owners: list[str]) -> database_api.FindWitnessesResponse:
        raise NotImplementedError

    @api
    def get_active_witnesses(self, *, include_future: bool = False) -> database_api.GetActiveWitnessesResponse:
        raise NotImplementedError

    @api
    def get_comment_pending_payouts(
        self, *, comments: list[tuple[str, str]]
    ) -> database_api.GetCommentPendingPayoutsResponse:
        raise NotImplementedError

    @api
    def get_config(self) -> database_api.GetConfigResponse:
        raise NotImplementedError

    @api
    def get_current_price_feed(self) -> database_api.GetCurrentPriceFeedResponse:
        raise NotImplementedError

    @api
    def get_dynamic_global_properties(
        self,
    ) -> database_api.GetDynamicGlobalPropertiesResponse:
        raise NotImplementedError

    @api
    def get_feed_history(self) -> database_api.GetFeedHistoryResponse:
        raise NotImplementedError

    @api
    def get_hardfork_properties(self) -> database_api.GetHardforkPropertiesResponse:
        raise NotImplementedError

    @api
    def get_order_book(
        self, *, limit: int, base: Hf26Asset.HiveT, quote: Hf26Asset.HbdT
    ) -> database_api.GetOrderBookResponse:
        raise NotImplementedError

    @api
    def get_potential_signatures(self, *, trx: Transaction) -> database_api.GetPotentialSignaturesResponse:
        raise NotImplementedError

    @api
    def get_required_signatures(self, *, trx: Transaction) -> database_api.GetPotentialSignaturesResponse:
        raise NotImplementedError

    @api
    def get_reward_funds(self) -> database_api.GetRewardFundsResponse:
        raise NotImplementedError

    @api
    def get_transaction_hex(self, *, trx: Transaction) -> database_api.GetTransactionHexResponse:
        raise NotImplementedError

    @api
    def get_version(self) -> database_api.GetVersionResponse:
        raise NotImplementedError

    @api
    def get_witness_schedule(self) -> database_api.GetWitnessScheduleResponse:
        raise NotImplementedError

    @api
    def is_known_transaction(self, *, id_: str) -> database_api.IsKnownTransactionResponse:
        raise NotImplementedError

    @api
    def list_account_recovery_requests(
        self, *, account: str, limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListAccountRecoveryRequestsResponse:
        raise NotImplementedError

    @api
    def list_accounts(
        self,
        *,
        start: str | tuple[str, str] | tuple[datetime, str],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
        delayed_votes_active: bool = True,
    ) -> database_api.ListAccountsResponse:
        raise NotImplementedError

    @api
    def list_change_recovery_account_requests(
        self, *, start: str | tuple[datetime, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListChangeRecoveryAccountRequestsResponse:
        raise NotImplementedError

    @api
    def list_collateralized_conversion_requests(
        self, *, start: str | None, limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListCollateralizedConversionRequestsResponse:
        raise NotImplementedError

    @api
    def list_decline_voting_rights_requests(
        self, *, start: str | tuple[datetime, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListDeclineVotingRightsRequestsResponse:
        raise NotImplementedError

    @api
    def list_escrows(
        self, *, start: tuple[str, int] | tuple[bool, datetime, int], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListEscrowsResponse:
        raise NotImplementedError

    @api
    def list_hbd_conversion_requests(
        self, *, limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListHbdConversionRequestsResponse:
        raise NotImplementedError

    @api
    def list_limit_orders(
        self, *, start: tuple[str, int] | tuple[dict[Literal["base", "quote"], Hf26Asset.HiveT | Hf26Asset.HbdT], int]
    ) -> database_api.ListLimitOrdersResponse:
        raise NotImplementedError

    @api
    def list_owner_histories(
        self, *, start: tuple[str, datetime], limit: int
    ) -> database_api.ListOwnerHistoriesResponse:
        raise NotImplementedError

    @api
    def list_proposal_votes(
        self,
        *,
        start: list[str],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
        order_direction: DatabaseApiCommons.SORT_DIRECTION,
        status: DatabaseApiCommons.PROPOSAL_STATUS,
    ) -> database_api.ListProposalVotesResponse:
        raise NotImplementedError

    @api
    def list_proposals(
        self,
        *,
        start: list[str] | list[int] | list[datetime],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
        order_direction: DatabaseApiCommons.SORT_DIRECTION,
        status: DatabaseApiCommons.PROPOSAL_STATUS,
    ) -> database_api.ListProposalsResponse:
        raise NotImplementedError

    @api
    def list_savings_withdrawals(
        self,
        *,
        start: tuple[int] | tuple[datetime, str, int] | tuple[str, datetime, int],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
    ) -> database_api.ListSavingsWithdrawalsResponse:
        raise NotImplementedError

    @api
    def list_vesting_delegation_expirations(
        self,
        *,
        start: tuple[str, datetime, int] | tuple[datetime, int],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
    ) -> database_api.ListVestingDelegationExpirationsResponse:
        raise NotImplementedError

    @api
    def list_vesting_delegations(
        self, *, start: tuple[str, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListVestingDelegationsResponse:
        raise NotImplementedError

    @api
    def list_withdraw_vesting_routes(
        self, *, start: tuple[str, str] | tuple[str, int], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListWithdrawVestingRoutesResponse:
        raise NotImplementedError

    @api
    def list_witness_votes(
        self, *, start: tuple[str, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListWitnessVotesResponse:
        raise NotImplementedError

    @api
    def list_witnesses(
        self, *, start: str | tuple[int, str] | tuple[str | int, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListWitnessesResponse:
        raise NotImplementedError

    @api
    def verify_account_authority(
        self, *, account: str, signers: list[str]
    ) -> database_api.VerifyAccountAuthorityResponse:
        raise NotImplementedError

    @api
    def verify_authority(
        self, *, trx: Transaction, pack: DatabaseApiCommons.PACK_TYPES = "hf26"
    ) -> database_api.VerifyAuthorityResponse:
        raise NotImplementedError

    @api
    def verify_signatures(
        self,
        *,
        hash_: str,
        signatures: list[str],
        required_owner: list[str],
        required_active: list[str],
        required_posting: list[str],
        required_other: list[str],
    ) -> database_api.VerifySignaturesResponse:
        raise NotImplementedError
