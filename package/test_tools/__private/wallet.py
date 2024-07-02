# mypy: ignore-errors
# ruff: noqa
# file for deletion after cli_wallet deprecation
from __future__ import annotations

import concurrent.futures
from functools import wraps
import json
import os
import shutil
import sys
import threading
import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Callable, Final, Literal

import wax
from beekeepy import beekeeper_factory
from beekeepy._interface.synchronous.beekeeper import Beekeeper
from beekeepy._interface.synchronous.session import Session
from beekeepy._interface.synchronous.wallet import UnlockedWallet
from beekeepy.settings import Settings
from loguru import logger
import helpy
from helpy import wax as wax_helpy
from helpy._communication.request_communicator import RequestCommunicator
from helpy._handles.hived.api.wallet_bridge_api.sync_api import WalletBridgeApi
from helpy._interfaces.context import ContextSync
from schemas.apis.block_api.fundaments_of_responses import Hf26Block
from schemas.apis.wallet_bridge_api.response_schemas import (
    FindProposals,
    FindRcAccounts,
    FindRecurrentTransfers,
    GetAccount,
    GetAccountHistory,
    GetAccounts,
    GetActiveWitnesses,
    GetBlock,
    GetCollateralizedConversionRequests,
    GetConversionRequests,
    GetFeedHistory,
    GetOpenOrders,
    GetOpsInBlock,
    GetOrderBook,
    GetOwnerHistory,
    GetTransaction,
    GetWithdrawRoutes,
    GetWitness,
    ListAccounts,
    ListMyAccounts,
    ListProposalVotes,
    ListProposals,
    ListRcAccounts,
    ListRcDirectDelegations,
    ListWitnesses,
)
from schemas.fields.assets.hbd import AssetHbdHF26
from schemas.fields.assets.hive import AssetHiveHF26
from schemas.fields.assets.vests import AssetVestsHF26
from schemas.fields.basic import AccountName, EmptyList, EmptyString, PrivateKey, PublicKey, WitnessUrl
from schemas.fields.compound import Authority, HbdExchangeRate, Proposal
from schemas.fields.hex import Hex
from schemas.fields.hive_datetime import HiveDateTime
from schemas.fields.hive_int import HiveInt
from schemas.fields.hive_list import HiveList
from schemas.operations import AnyOperation
from schemas.operations.account_create_operation import AccountCreateOperation
from schemas.operations.account_create_with_delegation_operation import AccountCreateWithDelegationOperation
from schemas.operations.account_update_operation import AccountUpdateOperation
from schemas.operations.account_witness_proxy_operation import AccountWitnessProxyOperation
from schemas.operations.account_witness_vote_operation import AccountWitnessVoteOperation
from schemas.operations.cancel_transfer_from_savings_operation import CancelTransferFromSavingsOperation
from schemas.operations.change_recovery_account_operation import ChangeRecoveryAccountOperation
from schemas.operations.claim_account_operation import ClaimAccountOperation
from schemas.operations.claim_reward_balance_operation import ClaimRewardBalanceOperation
from schemas.operations.collateralized_convert_operation import CollateralizedConvertOperation
from schemas.operations.comment_operation import CommentOperation
from schemas.operations.convert_operation import ConvertOperation
from schemas.operations.create_claimed_account_operation import CreateClaimedAccountOperation
from schemas.operations.create_proposal_operation import CreateProposalOperation
from schemas.operations.custom_json_operation import CustomJsonOperation
from schemas.operations.decline_voting_rights_operation import DeclineVotingRightsOperation
from schemas.operations.delegate_rc_operation import DelegateRcOperation
from schemas.operations.delegate_vesting_shares_operation import DelegateVestingSharesOperation
from schemas.operations.escrow_approve_operation import EscrowApproveOperation
from schemas.operations.escrow_dispute_operation import EscrowDisputeOperation
from schemas.operations.escrow_release_operation import EscrowReleaseOperation
from schemas.operations.escrow_transfer_operation import EscrowTransferOperation
from schemas.operations.feed_publish_operation import FeedPublishOperation
from schemas.operations.follow_operation import FollowOperation
from schemas.operations.limit_order_cancel_operation import LimitOrderCancelOperation
from schemas.operations.limit_order_create_operation import LimitOrderCreateOperation
from schemas.operations.recover_account_operation import RecoverAccountOperation
from schemas.operations.recurrent_transfer_operation import RecurrentTransferOperation
from schemas.operations.remove_proposal_operation import RemoveProposalOperation
from schemas.operations.representations.hf26_representation import HF26Representation
from schemas.operations.request_account_recovery_operation import RequestAccountRecoveryOperation
from schemas.operations.set_withdraw_vesting_route_operation import SetWithdrawVestingRouteOperation
from schemas.operations.transfer_from_savings_operation import TransferFromSavingsOperation
from schemas.operations.transfer_operation import TransferOperation
from schemas.operations.transfer_to_savings_operation import TransferToSavingsOperation
from schemas.operations.transfer_to_vesting_operation import TransferToVestingOperation
from schemas.operations.update_proposal_operation import UpdateProposalOperation
from schemas.operations.update_proposal_votes_operation import UpdateProposalVotesOperation
from schemas.operations.vote_operation import VoteOperation
from schemas.operations.withdraw_vesting_operation import WithdrawVestingOperation
from schemas.operations.witness_update_operation import WitnessUpdateOperation
from schemas.transaction import Transaction
from test_tools.__private import exceptions
from test_tools.__private.account import Account
from test_tools.__private.node import Node
from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.scope import ScopedObject, context
from test_tools.__private.type_annotations.any_node import AnyNode
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation

from helpy import Hf26Asset as Asset

if TYPE_CHECKING:
    from pathlib import Path

    from test_tools.__private.user_handles.handles.wallet_handle import WalletHandle

HIVE_MAX_TIME_UNTIL_EXPIRATION = 60 * 60

AccountNameApiType = AccountName | str
EmptyStringApiType = EmptyString | str
HiveDateTimeApiType = HiveDateTime | datetime | str
PublicKeyApiType = PublicKey | str
WitnessUrlApiType = WitnessUrl | str
HbdExchangeRateApiType = HbdExchangeRate | dict


@dataclass
class AuthorityRequirementsHolder:
    active: set[str] = field(default_factory=set)
    owner: set[str] = field(default_factory=set)
    posting: set[str] = field(default_factory=set)

    def all(self) -> set[str]:
        return set([*self.active, *self.owner, *self.posting])


@dataclass
class AuthorityHolder:
    active: dict[PublicKey, PrivateKey] = field(default_factory=dict)
    owner: dict[PublicKey, PrivateKey] = field(default_factory=dict)
    posting: dict[PublicKey, PrivateKey] = field(default_factory=dict)

    def all(self) -> dict[PublicKey, PrivateKey]:
        result = self.active.copy()
        result.update(self.owner)
        result.update(self.posting)
        return result


AuthorityType = Literal["active", "owner", "posting"]


class SimpleTransaction(Transaction):
    def add_operation(self, operation: AnyOperation) -> None:
        self.operations.append(HF26Representation(type=operation.get_name_with_suffix(), value=operation))


class WalletResponseBase(SimpleTransaction):
    transaction_id: str


class WalletResponse(WalletResponseBase):
    block_num: int
    transaction_num: int
    rc_cost: None | int


class Wallet(UserHandleImplementation, ScopedObject):
    DEFAULT_RUN_TIMEOUT = 15
    DEFAULT_PASSWORD = "password"

    class Api:
        class __TransactionBuilder:
            """Helper class for sending multiple operations in single transaction."""

            def __init__(self) -> None:
                self.__operations: EmptyList | list[AnyOperation] = []

            def _append_operation(self, operation: AnyOperation) -> None:
                self.__operations.append(operation)

            @property
            def operations(self) -> EmptyList | list[AnyOperation]:
                return self.__operations

        def __init__(self, wallet: Wallet) -> None:
            self.__wallet: Wallet = wallet
            self.__transaction_builder: self | None = None

        @property
        def _transaction_builder(self) -> __TransactionBuilder:
            if self.__transaction_builder is None:
                raise RuntimeError("Transaction builder is not initialized.")
            return self.__transaction_builder

        def _start_gathering_operations_for_single_transaction(self) -> None:
            if self.__transaction_builder is not None:
                raise RuntimeError("You cannot create transaction inside another transaction")

            self.__transaction_builder = self.__TransactionBuilder()

        def _send_gathered_operations_as_single_transaction(
            self, *, broadcast: bool, blocking: bool
        ) -> WalletResponseBase | WalletResponse:
            transaction = self.__wallet._prepare_and_send_transaction(
                operations=self.__transaction_builder.operations, broadcast=broadcast, blocking=blocking
            )
            self.__transaction_builder = None
            return transaction

        def __send_one_op(
            self, operation: AnyOperation, broadcast: bool, blocking: bool = True
        ) -> None | WalletResponseBase | WalletResponse:
            return self._send([operation], broadcast, blocking)

        def _send(
            self, operations: list[AnyOperation], broadcast: bool, blocking: bool
        ) -> None | WalletResponseBase | WalletResponse:
            broadcast = self.__handle_broadcast_parameter(broadcast)

            if not self.__is_transaction_build_in_progress():
                return self.__wallet._prepare_and_send_transaction(operations, blocking, broadcast)
            else:
                for operation in operations:
                    self._transaction_builder._append_operation(operation)

        def __handle_broadcast_parameter(self, broadcast: bool) -> None:
            if broadcast is None:
                broadcast = self.__get_default_broadcast_value()
            elif self.__is_transaction_build_in_progress():
                if broadcast is True:
                    raise RuntimeError(
                        "You cannot broadcast api call during transaction building.\n"
                        "\n"
                        "Replace broadcast parameter with value False or better -- remove it\n"
                        "completely, because it is default value during transaction building."
                    )

                warnings.warn(
                    'Avoid explicit setting "broadcast" parameter to False during registering operations in\n'
                    "transaction. False is a default value in this context. It is considered bad practice,\n"
                    "because obscures code and decreases its readability.",
                    stacklevel=1,
                )
            elif broadcast is True and not self.__is_transaction_build_in_progress():
                warnings.warn(
                    'Avoid explicit setting "broadcast" parameter to True in this context, it is default value.\n'
                    "It is considered bad practice, because obscures code and decreases its readability.",
                    stacklevel=1,
                )
            return broadcast

        def __get_default_broadcast_value(self) -> bool:
            return not self.__is_transaction_build_in_progress()

        def __is_transaction_build_in_progress(self) -> bool:
            return self.__transaction_builder is not None

        def __check_memo(self, memo: str) -> None:
            if isinstance(memo, PublicKey):
                assert not self.__wallet.beekeeper_wallet.has_matching_private_key(
                    memo
                ).exists, "Detected public key with matching private key in memo field. Cancelling transaction."

        def warn_if_only_result_set() -> Callable:
            def decorator(func: Callable) -> Callable:
                @wraps(func)
                def wrapper(*args, **kwargs):
                    if "only_result" in kwargs and kwargs["only_result"] != None:
                        warnings.warn(
                            f'In function {func.__name__}, the "only_result" argument was set. Avoid setting the "only_result" argument. In the Beekeeper wallet, this option is deprecated and does nothing.',
                            stacklevel=1,
                        )
                    return func(*args, **kwargs)

                return wrapper

            return decorator

        @warn_if_only_result_set()
        def about(self, only_result: bool | None = None):
            """
            Deprecated method. Raises an exception indicating that the method is deprecated.

            :param only_result: This argument is no longer active and should not be provided.
            :raises: MethodDeprecatedInBeekeeperWalletError: Indicates that the method is deprecated.
            """
            raise exceptions.MethodDeprecatedInBeekeeperWalletError()

        @warn_if_only_result_set()
        def cancel_order(
            self,
            owner: AccountNameApiType,
            orderid: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Enable to sign and send a transaction to cancel a specific order.

            :param owner: The account name of the order owner.
            :param orderid: The ID of the order to cancel.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                LimitOrderCancelOperation(
                    owner=owner,
                    orderid=orderid,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def cancel_transfer_from_savings(
            self,
            from_: AccountNameApiType,
            request_id: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Enable to sign and send a transaction to cancel a transfer from savings.

            :param from_: The account name from which the transfer originates.
            :param request_id: The ID of the transfer request.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                CancelTransferFromSavingsOperation(from_=from_, request_id=request_id),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def change_recovery_account(
            self,
            owner: AccountNameApiType,
            new_recovery_account: AccountNameApiType,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Enable to sign and send a transaction to change the recovery account for an account.

            :param owner: The account name whose recovery account is being changed.
            :param new_recovery_account: The new recovery account name.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                ChangeRecoveryAccountOperation(account_to_recover=owner, new_recovery_account=new_recovery_account),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def claim_account_creation(
            self,
            creator: AccountNameApiType,
            fee: AssetHiveHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Enable to sign and send a transaction to claim account creation.

            :param creator: The account name of the creator claiming the account creation.
            :param fee: The fee associated with claiming the account creation.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(ClaimAccountOperation(creator=creator, fee=fee), broadcast=broadcast)

        @warn_if_only_result_set()
        def claim_account_creation_nonblocking(
            self,
            creator: AccountNameApiType,
            fee: AssetHiveHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponseBase:
            """
            Enable to sign and send a transaction to claim account creation credits and non-blocking broadcast.

            :param creator: The account name of the creator claiming the account creation.
            :param fee: The fee associated with claiming the account creation.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                ClaimAccountOperation(creator=creator, fee=fee),
                broadcast=broadcast,
                blocking=False,
            )

        @warn_if_only_result_set()
        def claim_reward_balance(
            self,
            account: AccountNameApiType,
            reward_hive: AssetHiveHF26,
            reward_hbd: AssetHbdHF26,
            reward_vests: AssetVestsHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Enable to sign and send a transaction to claim the reward balance.

            :param account: The account name claiming the reward balance.
            :param reward_hive: The amount of HIVE to claim.
            :param reward_hbd: The amount of HBD to claim.
            :param reward_vests: The amount of VESTS to claim.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                ClaimRewardBalanceOperation(
                    account=account, reward_hive=reward_hive, reward_hbd=reward_hbd, reward_vests=reward_vests
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def convert_hbd(
            self,
            from_: AccountNameApiType,
            amount: AssetHbdHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Enable to sign and send a transaction to convert HBD to HIVE.

            :param from_: The account name initiating the conversion.
            :param amount: The amount of HBD to convert.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                ConvertOperation(owner=from_, amount=amount, requestid=int(time.time())),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def convert_hive_with_collateral(
            self,
            from_: AccountNameApiType,
            collateral_amount: AssetHiveHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Enable to sign and send a transaction to convert HIVE with collateral.

            :param from_: The account name initiating the conversion.
            :param collateral_amount: The amount of HIVE to use as collateral.
            :param broadcast: If set to True, the transaction is broadcasted to the blockchain.
                If set to False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                CollateralizedConvertOperation(owner=from_, amount=collateral_amount, requestid=int(time.time())),
                broadcast=broadcast,
            )

        def get_authority(self, key: str) -> dict:
            return {"weight_threshold": 1, "account_auths": [], "key_auths": [[key, 1]]}

        @warn_if_only_result_set()
        def create_account(
            self,
            creator: AccountNameApiType,
            new_account_name: AccountNameApiType,
            json_meta: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Creates a new account.

            :param creator: The name of the account creating the new account.
            :param new_account_name: The name of the new account.
            :param json_meta: The JSON metadata associated with the new account.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()

            owner_key, active_key, posting_key, memo_key = [self.suggest_brain_key() for _ in range(4)]

            self.import_keys(
                [
                    owner_key["wif_priv_key"],
                    active_key["wif_priv_key"],
                    posting_key["wif_priv_key"],
                    memo_key["wif_priv_key"],
                ]
            )

            transaction = self.__send_one_op(
                AccountCreateOperation(
                    creator=creator,
                    new_account_name=new_account_name,
                    json_metadata=json_meta,
                    fee=self.__wallet.connected_node.api.wallet_bridge.get_chain_properties().account_creation_fee.as_nai(),
                    owner=self.get_authority(owner_key["pub_key"]),
                    active=self.get_authority(active_key["pub_key"]),
                    posting=self.get_authority(posting_key["pub_key"]),
                    memo_key=memo_key["pub_key"],
                ),
                broadcast=broadcast,
            )
            return transaction

        @warn_if_only_result_set()
        def create_account_delegated(
            self,
            creator: AccountNameApiType,
            hive_fee: AssetHiveHF26,
            delegated_vests: AssetVestsHF26,
            new_account_name: AccountNameApiType,
            json_meta: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Creates a new account with a delegation.

            :param creator: The name of the account creating the new account.
            :param hive_fee: The amount of HIVE to be paid for account creation.
            :param delegated_vests: The amount of VESTS to be delegated.
            :param new_account_name: The name of the new account.
            :param json_meta: The JSON metadata associated with the new account.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()

            owner_key, active_key, posting_key, memo_key = [self.suggest_brain_key() for _ in range(4)]

            self.import_keys(
                [
                    owner_key["wif_priv_key"],
                    active_key["wif_priv_key"],
                    posting_key["wif_priv_key"],
                    memo_key["wif_priv_key"],
                ]
            )

            return self.__send_one_op(
                AccountCreateWithDelegationOperation(
                    creator=creator,
                    new_account_name=new_account_name,
                    json_metadata=json_meta,
                    fee=hive_fee,
                    delegation=delegated_vests,
                    owner=self.get_authority(owner_key["pub_key"]),
                    active=self.get_authority(active_key["pub_key"]),
                    posting=self.get_authority(posting_key["pub_key"]),
                    memo_key=memo_key["pub_key"],
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def create_account_with_keys(
            self,
            creator: AccountNameApiType,
            newname: AccountNameApiType,
            json_meta: str,
            owner: PublicKeyApiType,
            active: PublicKeyApiType,
            posting: PublicKeyApiType,
            memo: PublicKeyApiType,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Creates a new account with specified keys.

            :param creator: The name of the account creating the new account.
            :param newname: The name of the new account.
            :param json_meta: The JSON metadata associated with the new account.
            :param owner: The owner public key.
            :param active: The active public key.
            :param posting: The posting public key.
            :param memo: The memo public key.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            transaction = self.__send_one_op(
                AccountCreateOperation(
                    creator=creator,
                    new_account_name=newname,
                    json_metadata=json_meta,
                    fee=self.__wallet.connected_node.api.wallet_bridge.get_chain_properties().account_creation_fee,
                    owner=self.get_authority(owner),
                    active=self.get_authority(active),
                    posting=self.get_authority(posting),
                    memo_key=memo,
                ),
                broadcast=broadcast,
            )
            return transaction

        @warn_if_only_result_set()
        def create_account_with_keys_delegated(
            self,
            creator: AccountNameApiType,
            hive_fee: AssetHiveHF26,
            delegated_vests: AssetVestsHF26,
            newname: AccountNameApiType,
            json_meta: str,
            owner: PublicKeyApiType,
            active: PublicKeyApiType,
            posting: PublicKeyApiType,
            memo: PublicKeyApiType,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Creates a new account with specified keys and a delegation.

            :param creator: The name of the account creating the new account.
            :param hive_fee: The amount of HIVE to be paid for account creation.
            :param delegated_vests: The amount of VESTS to be delegated.
            :param newname: The name of the new account.
            :param json_meta: The JSON metadata associated with the new account.
            :param owner: The owner public key.
            :param active: The active public key.
            :param posting: The posting public key.
            :param memo: The memo public key.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            transaction = self.__send_one_op(
                AccountCreateWithDelegationOperation(
                    creator=creator,
                    new_account_name=newname,
                    json_metadata=json_meta,
                    fee=hive_fee,
                    delegation=delegated_vests,
                    owner=self.get_authority(owner),
                    active=self.get_authority(active),
                    posting=self.get_authority(posting),
                    memo_key=memo,
                ),
                broadcast=broadcast,
            )
            return transaction

        @warn_if_only_result_set()
        def create_funded_account_with_keys(
            self,
            creator: AccountNameApiType,
            new_account_name: AccountNameApiType,
            initial_amount: AssetHiveHF26,
            memo: PublicKeyApiType,
            json_meta: str,
            owner_key: PublicKeyApiType,
            active_key: PublicKeyApiType,
            posting_key: PublicKeyApiType,
            memo_key: PublicKeyApiType,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Creates a new account with specified keys and funds it.

            :param creator: The name of the account creating the new account.
            :param new_account_name: The name of the new account.
            :param initial_amount: The initial amount to fund the new account.
            :param memo: The memo public key.
            :param json_meta: The JSON metadata associated with the new account.
            :param owner_key: The owner public key.
            :param active_key: The active public key.
            :param posting_key: The posting public key.
            :param memo_key: The memo public key.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            with self.__wallet.in_single_transaction(broadcast=broadcast) as trx:
                if self.get_account(creator).pending_claimed_accounts > 0:
                    self.__send_one_op(
                        CreateClaimedAccountOperation(
                            creator=creator,
                            new_account_name=new_account_name,
                            owner=self.get_authority(owner_key),
                            active=self.get_authority(active_key),
                            posting=self.get_authority(posting_key),
                            memo_key=memo_key,
                            json_metadata=json_meta,
                        ),
                        broadcast=broadcast,
                    )
                else:
                    self.__send_one_op(
                        AccountCreateOperation(
                            creator=creator,
                            new_account_name=new_account_name,
                            json_metadata=json_meta,
                            fee=self.__wallet.connected_node.api.wallet_bridge.get_chain_properties().account_creation_fee,
                            owner=self.get_authority(owner_key),
                            active=self.get_authority(active_key),
                            posting=self.get_authority(posting_key),
                            memo_key=memo_key,
                        ),
                        broadcast=broadcast,
                    )

                if initial_amount > Asset.Test(0):
                    self.transfer(from_=creator, to=new_account_name, amount=initial_amount, memo=memo)

            return trx

        @warn_if_only_result_set()
        def create_order(
            self,
            owner: AccountNameApiType,
            order_id: int,
            amount_to_sell: AssetHiveHF26 | AssetHbdHF26,
            min_to_receive: AssetHiveHF26 | AssetHbdHF26,
            fill_or_kill: bool,
            expiration: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Creates a new limit order.

            :param owner: The name of the account creating the order.
            :param order_id: The ID of the order.
            :param amount_to_sell: The amount of HIVE or HBD to sell.
            :param min_to_receive: The minimum amount of HIVE or HBD to receive.
            :param fill_or_kill: If True, the order is either fully filled or cancelled.
            :param expiration: The expiration time of the order in seconds.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                LimitOrderCreateOperation(
                    owner=owner,
                    orderid=order_id,
                    amount_to_sell=amount_to_sell,
                    min_to_receive=min_to_receive,
                    fill_or_kill=fill_or_kill,
                    expiration=self.__wallet.connected_node.api.database.get_dynamic_global_properties().time
                    + timedelta(seconds=expiration),
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def create_proposal(
            self,
            creator: AccountNameApiType,
            receiver: AccountNameApiType,
            start_date: HiveDateTimeApiType,
            end_date: HiveDateTimeApiType,
            daily_pay: AssetHbdHF26,
            subject: str,
            permlink: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Creates a new proposal.

            :param creator: The name of the account creating the proposal.
            :param receiver: The name of the account receiving the proposal.
            :param start_date: The start date of the proposal.
            :param end_date: The end date of the proposal.
            :param daily_pay: The daily payment amount in HBD.
            :param subject: The subject of the proposal.
            :param permlink: The permlink of the proposal.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                CreateProposalOperation(
                    creator=creator,
                    receiver=receiver,
                    start_date=start_date,
                    end_date=end_date,
                    daily_pay=daily_pay,
                    subject=subject,
                    permlink=permlink,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def decline_voting_rights(
            self,
            account: AccountNameApiType,
            decline: bool,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Declines or grant voting rights for an account.

            :param account: The name of the account.
            :param decline: If True, the voting rights are declined. If False, the voting rights are granted.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                DeclineVotingRightsOperation(account=account, decline=decline),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def decrypt_memo(self, memo: str, only_result: bool | None = None) -> str:
            """
            Decrypts a memo.

            :param memo: The memo to be decrypted.
            :param broadcast: This argument is no longer active and should not be provided.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The decrypted memo.
            """
            decrypt_memo = wax_helpy.decrypt_memo(
                content=memo, second_step_callback=self.__wallet.beekeeper_wallet.decrypt_data
            )
            if decrypt_memo.startswith("#"):
                return decrypt_memo[1:]

        @warn_if_only_result_set()
        def delegate_rc(
            self,
            from_: AccountNameApiType,
            delegatees: list[AccountNameApiType],
            max_rc: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ):
            """
            Delegates Resource Credits (RC) to specified accounts.

            :param from_: The account delegating the RC.
            :param delegatees: The list of accounts receiving the RC delegation.
            :param max_rc: The maximum amount of RC to delegate.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            delegate_rc_operation = DelegateRcOperation(from_=from_, delegatees=delegatees, max_rc=max_rc)
            operation = CustomJsonOperation(
                required_auths=[],
                required_posting_auths=[from_],
                id_="rc",
                json_=HF26Representation(
                    type=delegate_rc_operation.get_name_with_suffix(), value=delegate_rc_operation
                ),
            )
            return self.__send_one_op(
                operation=operation,
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def delegate_vesting_shares(
            self,
            delegator: AccountNameApiType,
            delegatee: AccountNameApiType,
            vesting_shares: Asset.VestsT,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Delegates vesting shares to another account.

            :param delegator: The name of the account delegating the vesting shares.
            :param delegatee: The name of the account receiving the vesting shares.
            :param vesting_shares: The amount of vesting shares to delegate.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            accounts = self.get_accounts([delegator, delegatee])
            if len(accounts) != 2:
                raise exceptions.DelegatorOrDelegateeNotExistError
            if delegator != accounts[0].name:
                raise exceptions.DelegatorIsNotRightError
            if delegatee != accounts[1].name:
                raise exceptions.DelegateeIsNotRightError
            return self.__send_one_op(
                DelegateVestingSharesOperation(delegator=delegator, delegatee=delegatee, vesting_shares=vesting_shares),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def delegate_vesting_shares_and_transfer(
            self,
            delegator: AccountNameApiType,
            delegatee: AccountNameApiType,
            vesting_shares: Asset.VestsT,
            transfer_amount: Asset.AssetHiveT | Asset.AssetHbdT,
            transfer_memo: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Delegates vesting shares and transfers an amount to another account.

            :param delegator: The name of the account delegating the vesting shares.
            :param delegatee: The name of the account receiving the vesting shares and transfer amount.
            :param vesting_shares: The amount of vesting shares to delegate.
            :param transfer_amount: The amount of HIVE or HBD to transfer.
            :param transfer_memo: The memo for the transfer.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            with self.__wallet.in_single_transaction(broadcast=broadcast) as transaction:
                self.delegate_vesting_shares(delegator=delegator, delegatee=delegatee, vesting_shares=vesting_shares)
                self.transfer(from_=delegator, to=delegatee, amount=transfer_amount, memo=transfer_memo)
            return transaction.get_response()

        @warn_if_only_result_set()
        def delegate_vesting_shares_and_transfer_nonblocking(
            self,
            delegator: AccountNameApiType,
            delegatee: AccountNameApiType,
            vesting_shares: Asset.VestsT,
            transfer_amount: Asset.AssetHiveT | Asset.AssetHbdT,
            transfer_memo: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponseBase:
            """
            Delegates vesting shares and transfers an amount to another account and non-blocking broadcast.

            :param delegator: The name of the account delegating the vesting shares.
            :param delegatee: The name of the account receiving the vesting shares and transfer amount.
            :param vesting_shares: The amount of vesting shares to delegate.
            :param transfer_amount: The amount of HIVE or HBD to transfer.
            :param transfer_memo: The memo for the transfer.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            with self.__wallet.in_single_transaction(blocking=False, broadcast=broadcast) as transaction:
                self.delegate_vesting_shares(delegator=delegator, delegatee=delegatee, vesting_shares=vesting_shares)
                self.transfer(from_=delegator, to=delegatee, amount=transfer_amount, memo=transfer_memo)
            return transaction.get_response()

        @warn_if_only_result_set()
        def delegate_vesting_shares_nonblocking(
            self,
            delegator: AccountNameApiType,
            delegatee: AccountNameApiType,
            vesting_shares: Asset.VestsT,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponseBase:
            """
            Delegates vesting shares and non-blocking broadcast.

            :param delegator: The name of the account delegating the vesting shares.
            :param delegatee: The name of the account receiving the vesting shares.
            :param vesting_shares: The amount of vesting shares to delegate.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            return self.__send_one_op(
                DelegateVestingSharesOperation(delegator=delegator, delegatee=delegatee, vesting_shares=vesting_shares),
                broadcast=broadcast,
                blocking=False,
            )

        @warn_if_only_result_set()
        def escrow_approve(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            agent: AccountNameApiType,
            who: AccountNameApiType,
            escrow_id: int,
            approve: bool,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Approves or disapproves an escrow transaction.

            :param from_: The account sending the escrow.
            :param to: The account receiving the escrow.
            :param agent: The escrow agent.
            :param who: The account approving or disapproving the escrow.
            :param escrow_id: The ID of the escrow.
            :param approve: If True, the escrow is approved. If False, the escrow is disapproved.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                EscrowApproveOperation(from_=from_, to=to, agent=agent, who=who, escrow_id=escrow_id, approve=approve),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def escrow_dispute(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            agent: AccountNameApiType,
            who: AccountNameApiType,
            escrow_id: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Disputes an escrow transaction.

            :param from_: The account sending the escrow.
            :param to: The account receiving the escrow.
            :param agent: The escrow agent.
            :param who: The account disputing the escrow.
            :param escrow_id: The ID of the escrow.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                EscrowDisputeOperation(from_=from_, to=to, agent=agent, who=who, escrow_id=escrow_id),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def escrow_release(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            agent: AccountNameApiType,
            who: AccountNameApiType,
            receiver: AccountNameApiType,
            escrow_id: int,
            hbd_amount: AssetHbdHF26,
            hive_amount: AssetHiveHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Releases funds from an escrow transaction.

            :param from_: The account sending the escrow.
            :param to: The account receiving the escrow.
            :param agent: The escrow agent.
            :param who: The account releasing the escrow.
            :param receiver: The account receiving the funds.
            :param escrow_id: The ID of the escrow.
            :param hbd_amount: The amount of HBD to release.
            :param hive_amount: The amount of HIVE to release.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                EscrowReleaseOperation(
                    from_=from_,
                    to=to,
                    agent=agent,
                    who=who,
                    receiver=receiver,
                    escrow_id=escrow_id,
                    hbd_amount=hbd_amount,
                    hive_amount=hive_amount,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def escrow_transfer(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            agent: AccountNameApiType,
            escrow_id: int,
            hbd_amount: AssetHbdHF26,
            hive_amount: AssetHiveHF26,
            fee: AssetHiveHF26 | AssetHbdHF26,
            ratification_deadline: HiveDateTimeApiType,
            escrow_expiration: HiveDateTimeApiType,
            json_meta: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Transfers funds into escrow.

            :param from_: The account sending the escrow.
            :param to: The account receiving the escrow.
            :param agent: The escrow agent.
            :param escrow_id: The ID of the escrow.
            :param hbd_amount: The amount of HBD to transfer.
            :param hive_amount: The amount of HIVE to transfer.
            :param fee: The fee for the escrow.
            :param ratification_deadline: The deadline for the ratification of the escrow.
            :param escrow_expiration: The expiration time of the escrow.
            :param json_meta: The JSON metadata associated with the escrow.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                EscrowTransferOperation(
                    from_=from_,
                    to=to,
                    agent=agent,
                    escrow_id=escrow_id,
                    hbd_amount=hbd_amount.as_nai(),
                    hive_amount=hive_amount.as_nai(),
                    fee=fee.as_nai(),
                    ratification_deadline=ratification_deadline,
                    escrow_expiration=escrow_expiration,
                    json_meta=json_meta,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def estimate_hive_collateral(self, hbd_amount_to_get, only_result: bool | None = None):
            """
            Estimates the amount of HIVE collateral required for a given amount of HBD.

            :param hbd_amount_to_get: The amount of HBD to estimate the collateral for.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The estimated HIVE collateral.
            """
            assert not self.is_locked()
            return self._send("estimate_hive_collateral", hbd_amount_to_get=hbd_amount_to_get, only_result=only_result)

        @warn_if_only_result_set()
        def exit(self, only_result: bool | None = None) -> None:
            """
            Exits the wallet.

            :param only_result: This argument is no longer active and should not be provided.
            :return: None.
            """
            return self.__wallet.close()

        @warn_if_only_result_set()
        def find_proposals(
            self, proposal_ids: list[int], as_list: bool = False, only_result: bool | None = None
        ) -> FindProposals | HiveList[Proposal[AssetHbdHF26]]:
            """
            Finds proposals by their IDs.

            :param proposal_ids: The list of proposal IDs to find.
            :param as_list: If True, returns the proposals as a list. If False, returns a FindProposals object.
            :param only_result: This argument is no longer active and should not be provided.
            :return: A list of proposals or a FindProposals object.
            """
            proposals = self.__wallet.connected_node.api.wallet_bridge.find_proposals(proposal_ids)
            if as_list:
                return proposals.proposals
            return proposals

        @warn_if_only_result_set()
        def find_rc_accounts(
            self, accounts: list[AccountNameApiType], only_result: bool | None = None
        ) -> FindRcAccounts:
            """
            Finds RC (Resource Credit) accounts.

            :param accounts: The list of account names to find.
            :param only_result: This argument is no longer active and should not be provided.
            :return: A FindRcAccounts object containing information about the RC accounts.
            """
            return self.__wallet.connected_node.api.wallet_bridge.find_rc_accounts(accounts)

        @warn_if_only_result_set()
        def find_recurrent_transfers(
            self, from_: AccountNameApiType, only_result: bool | None = None
        ) -> FindRecurrentTransfers:
            """
            Finds recurrent transfers for a given account.

            :param from_: The account to find recurrent transfers for.
            :param only_result: This argument is no longer active and should not be provided.
            :return: A FindRecurrentTransfers object containing information about the recurrent transfers.
            """
            return self.__wallet.connected_node.api.wallet_bridge.find_recurrent_transfers(from_)

        @warn_if_only_result_set()
        def follow(
            self,
            follower: AccountNameApiType,
            following: AccountNameApiType,
            what: list[str],
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ):
            """
            Follows an account.

            :param follower: The account that will follow.
            :param following: The account to be followed.
            :param what: A list of follow keywords.
            :param broadcast: If True, the transaction is broadcasted to the blockchain. If False, the transaction is only built without sending.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Response object containing information about the transaction.
            """
            assert not self.is_locked()
            follow_operation = FollowOperation(follower=follower, following=following, what=what)
            operation = CustomJsonOperation(
                required_auths=[],
                required_posting_auths=[follower],
                id_="follow",
                json_=HF26Representation(type=follow_operation.get_name_with_suffix(), value=follow_operation).json(),
            )
            operation.json_ = json.dumps(operation.json_)
            return self.__send_one_op(
                operation=operation,
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def get_account(
            self, account_name: AccountNameApiType | AccountNameApiType, only_result: bool | None = None
        ) -> GetAccount:
            """
            Retrieves account information for a given account name.

            :param account_name: The name of the account.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The account information.
            """
            account_name = (
                account_name if isinstance(account_name, AccountNameApiType) else AccountNameApiType(account_name)
            )
            trx = self.__wallet.connected_node.api.wallet_bridge.get_account(account_name)
            if trx is None:
                raise exceptions.AccountNotExistError
            return trx

        @warn_if_only_result_set()
        def get_account_history(
            self, account: AccountNameApiType, from_: int, limit: int, only_result: bool | None = None
        ) -> GetAccountHistory:
            """
            Retrieves the account history for a given account.

            :param account: The name of the account.
            :param from_: The starting point of the history.
            :param limit: The maximum number of history entries to retrieve.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The account history.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_account_history(account, from_, limit)

        @warn_if_only_result_set()
        def get_accounts(self, account_names: list[AccountNameApiType], only_result: bool | None = None) -> GetAccounts:
            """
            Retrieves information for a list of accounts.

            :param account_names: The list of account names.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Information about the accounts.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_accounts(account_names)

        @warn_if_only_result_set()
        def get_active_witnesses(
            self, include_future: bool, only_witnesses: bool = False, only_result: bool | None = None
        ) -> list | GetActiveWitnesses:
            """
            Retrieves the list of active witnesses.

            :param include_future: If True, includes future witnesses.
            :param only_witnesses: If True, returns only the witness names.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of active witnesses or GetActiveWitnesses object.
            """
            active_witnesses = self.__wallet.connected_node.api.wallet_bridge.get_active_witnesses(include_future)
            if only_witnesses:
                return active_witnesses.witnesses
            return active_witnesses

        @warn_if_only_result_set()
        def get_block(
            self, num: int, only_block: bool = False, only_result: bool | None = None
        ) -> GetBlock | Hf26Block:
            """
            Retrieves information about a specific block.

            :param num: The block number.
            :param only_block: If True, returns only the block information.
            :param only_result: This argument is no longer active and should not be provided.
            :return: Information about the block or GetBlock object.
            """
            block = self.__wallet.connected_node.api.wallet_bridge.get_block(num)
            if only_block:
                return block.block
            return block

        @warn_if_only_result_set()
        def get_collateralized_conversion_requests(
            self, owner: AccountNameApiType, only_result: bool | None = None
        ) -> GetCollateralizedConversionRequests:
            """
            Retrieves the list of collateralized conversion requests for a given account.

            :param owner: The name of the account.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of collateralized conversion requests.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_collateralized_conversion_requests(owner)

        @warn_if_only_result_set()
        def get_conversion_requests(
            self, owner: AccountNameApiType, only_result: bool | None = None
        ) -> GetConversionRequests:
            """
            Retrieves the list of conversion requests for a given account.

            :param owner: The name of the account.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of conversion requests.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_conversion_requests(owner)

        @warn_if_only_result_set()
        def get_encrypted_memo(
            self, from_: AccountNameApiType, to: AccountNameApiType, memo: str, only_result: bool | None = None
        ) -> str:
            """
            Encrypts a memo for secure messaging between accounts.

            :param from_: The account sending the memo.
            :param to: The account receiving the memo.
            :param memo: The memo content to encrypt.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The encrypted memo.
            """
            from_account = self.get_account(from_)
            to_account = self.get_account(to)

            return wax_helpy.encrypt_memo(
                main_encryption_key=from_account.memo_key,
                other_encryption_key=to_account.memo_key,
                content=memo,
                second_step_callback=self.__wallet.beekeeper_wallet.encrypt_data,
            )

        @warn_if_only_result_set()
        def get_feed_history(self, only_result: bool | None = None) -> GetFeedHistory:
            """
            Retrieves the feed history.

            :param only_result: This argument is no longer active and should not be provided.
            :return: The feed history.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_feed_history()

        @warn_if_only_result_set()
        def get_open_orders(self, accountname: AccountNameApiType, only_result: bool | None = None) -> GetOpenOrders:
            """
            Retrieves the open orders for a given account.

            :param accountname: The name of the account.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of open orders.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_open_orders(accountname)

        @warn_if_only_result_set()
        def get_ops_in_block(
            self, block_num: int, only_virtual: bool, only_result: bool | None = None
        ) -> GetOpsInBlock:
            """
            Retrieves the operations in a specific block.

            :param block_num: The block number.
            :param only_virtual: If True, returns only virtual operations.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The operations in the block.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_ops_in_block(block_num, only_virtual)

        @warn_if_only_result_set()
        def get_order_book(self, limit: int, only_result: bool | None = None) -> GetOrderBook:
            """
            Retrieves the order book with a specified limit.

            :param limit: The maximum number of orders to retrieve.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The order book.
            """
            assert limit <= 1000
            return self.__wallet.connected_node.api.wallet_bridge.get_order_book(limit)

        @warn_if_only_result_set()
        def get_owner_history(
            self, account: AccountNameApiType, as_list: bool = False, only_result: bool | None = None
        ) -> list | GetOwnerHistory:
            """
            Retrieves the owner history for a given account.

            :param account: The name of the account.
            :param as_list: If True, returns the owner history as a list. If False, returns a GetOwnerHistory object.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The owner history.
            """
            owner_history = self.__wallet.connected_node.api.wallet_bridge.get_owner_history(account)
            if as_list:
                return owner_history.owner_auths
            return owner_history

        @warn_if_only_result_set()
        def get_private_key_from_password(
            self, account: AccountNameApiType, role: str, password: str, only_result: bool | None = None
        ) -> list:
            """
            Generates a private key from a given password.

            :param account: The name of the account.
            :param role: The role associated with the key.
            :param password: The password to generate the key from.
            :param only_result: This argument is no longer active and should not be provided.
            :return: A list containing the associated public key and the private key in WIF format.
            """
            assert not self.is_locked()
            private_key = wax.generate_password_based_private_key(
                account=account.encode(), role=role.encode(), password=password.encode()
            )
            return [private_key.associated_public_key.decode(), private_key.wif_private_key.decode()]

        @warn_if_only_result_set()
        def get_prototype_operation(self, operation_type: str, only_result: bool | None = None) -> dict:
            """
            Retrieves a prototype operation.

            :param operation_type: The type of the operation.
            :param only_result: This argument is no longer active and should not be provided.
            :return: A dictionary representing the prototype operation.
            """
            operations = getattr(AnyOperation, "__args__", None)
            for operation in operations:
                if operation.get_name_with_suffix() == operation_type:
                    return {"type": operation.get_name(), "value": operation.__fields__}

        @warn_if_only_result_set()
        def get_transaction(self, trx_id: str, only_result: bool | None = None) -> GetTransaction:
            """
            Retrieves a transaction by its ID.

            :param trx_id: The ID of the transaction.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The transaction.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_transaction(trx_id)

        @warn_if_only_result_set()
        def get_withdraw_routes(
            self,
            account: AccountNameApiType,
            type_: WalletBridgeApi.WITHDRAW_ROUTE_TYPES,
            only_result: bool | None = None,
        ) -> GetWithdrawRoutes:
            """
            Retrieves the withdraw routes for a given account.

            :param account: The name of the account.
            :param type_: The type of withdraw routes.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The withdraw routes.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_withdraw_routes(account, type_)

        @warn_if_only_result_set()
        def get_witness(self, owner_account: AccountNameApiType, only_result: bool | None = None) -> GetWitness:
            """
            Retrieves information about a witness.

            :param owner_account: The account of the witness.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The witness information.
            """
            return self.__wallet.connected_node.api.wallet_bridge.get_witness(owner_account)

        @warn_if_only_result_set()
        def gethelp(self, method, only_result: bool | None = None):
            """
            Raises an exception indicating that the method is deprecated.

            :param method: The deprecated method.
            :param only_result: This argument is no longer active and should not be provided.
            :raises MethodDeprecatedInBeekeeperWalletError: Always raised to indicate deprecation.
            """
            raise exceptions.MethodDeprecatedInBeekeeperWalletError()

        @warn_if_only_result_set()
        def help(self, only_result: bool | None = None):
            """
            Raises an exception to indicate that the method is deprecated.

            :param only_result: This argument is no longer active and should not be provided.
            :raises MethodDeprecatedInBeekeeperWalletError: Always raised to indicate deprecation.
            """
            raise exceptions.MethodDeprecatedInBeekeeperWalletError()

        @warn_if_only_result_set()
        def import_key(self, wif_key: str, only_result: bool | None = None) -> PublicKeyApiType:
            """
            Imports a private key into the wallet.

            :param wif_key: The WIF-formatted private key to import.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The corresponding public key.
            """
            assert not self.is_locked()
            return self.__wallet.beekeeper_wallet.import_key(private_key=wif_key)

        @warn_if_only_result_set()
        def import_keys(self, wif_keys: list[str], only_result: bool | None = None) -> list[PublicKeyApiType]:
            """
            Imports multiple private keys into the wallet.

            :param wif_keys: A list of WIF-formatted private keys to import.
            :param only_result: This argument is no longer active and should not be provided.
            """
            assert not self.is_locked()
            return self.__wallet.beekeeper_wallet.import_keys(private_keys=wif_keys)

        @warn_if_only_result_set()
        def info(self, only_result: bool | None = None):
            """
            Raises an exception to indicate that the method is deprecated.

            :param only_result: This argument is no longer active and should not be provided.
            :raises MethodDeprecatedInBeekeeperWalletError: Always raised to indicate deprecation.
            """
            raise exceptions.MethodDeprecatedInBeekeeperWalletError()

        @warn_if_only_result_set()
        def is_locked(self, only_result: bool | None = None) -> bool:
            """
            Checks if the wallet is locked.

            :param only_result: This argument is no longer active and should not be provided.
            :return: True if the wallet is locked, False otherwise.
            """
            unlocked_wallet = self.__wallet.beekeeper_wallet.unlocked
            return True if unlocked_wallet is None else False

        @warn_if_only_result_set()
        def is_new(self, only_result: bool | None = None) -> bool:
            """
            Checks if the wallet is new (contains no public keys).

            :param only_result: This argument is no longer active and should not be provided.
            :return: True if the wallet is new, False otherwise.
            """
            return len(self.__wallet.beekeeper_wallet.public_keys) == 0

        @warn_if_only_result_set()
        def list_accounts(self, lowerbound: str, limit: int, only_result: bool | None = None) -> ListAccounts:
            """
            Lists accounts based on a lower bound and a limit.

            :param lowerbound: The lower bound for listing accounts.
            :param limit: The maximum number of accounts to list.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of accounts.
            """
            return self.__wallet.connected_node.api.wallet_bridge.list_accounts(lowerbound, limit)

        @warn_if_only_result_set()
        def list_keys(self, only_result: bool | None = None) -> list[PublicKeyApiType]:
            """
            Lists the public keys in the wallet.

            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of public keys.
            """
            assert not self.is_locked()
            return self.__wallet.beekeeper_wallet.public_keys

        @warn_if_only_result_set()
        def list_my_accounts(self, only_result: bool | None = None) -> ListMyAccounts:
            """
            Lists the accounts associated with the public keys in the wallet.

            :param only_result: This argument is no longer active and should not be provided.
            :return:  The list of accounts created with this wallet.
            """
            assert not self.is_locked(), "Wallet must be unlocked to list accounts"
            keys = self.__wallet.beekeeper_wallet.public_keys

            return self.__wallet.connected_node.api.wallet_bridge.list_my_accounts(keys)

        @warn_if_only_result_set()
        def list_proposal_votes(
            self,
            start: datetime,
            limit: int,
            order_by: WalletBridgeApi.SORT_TYPES,
            order_type: WalletBridgeApi.SORT_DIRECTION,
            status: WalletBridgeApi.PROPOSAL_STATUS,
            only_result: bool | None = None,
        ) -> ListProposalVotes:
            """
            Lists proposal votes based on specified criteria.

            :param start: The start date for listing votes.
            :param limit: The maximum number of votes to list.
            :param order_by: The field to order votes by.
            :param order_type: The direction of the ordering.
            :param status: The status of the proposals.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of proposal votes.
            """
            return self.__wallet.connected_node.api.wallet_bridge.list_proposal_votes(
                start, limit, order_by, order_type, status
            )

        @warn_if_only_result_set()
        def list_proposals(
            self,
            start: datetime,
            limit: int,
            order_by: WalletBridgeApi.SORT_TYPES,
            order_type: WalletBridgeApi.SORT_DIRECTION,
            status: WalletBridgeApi.PROPOSAL_STATUS,
            only_result: bool | None = None,
        ) -> ListProposals:
            """
            Lists proposals based on specified criteria.

            :param start: The start date for listing proposals.
            :param limit: The maximum number of proposals to list.
            :param order_by: The field to order proposals by.
            :param order_type: The direction of the ordering.
            :param status: The status of the proposals.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of proposals.
            """
            return self.__wallet.connected_node.api.wallet_bridge.list_proposals(
                start, limit, order_by, order_type, status
            )

        @warn_if_only_result_set()
        def list_rc_accounts(
            self, account: AccountNameApiType, limit: int, only_result: bool | None = None
        ) -> ListRcAccounts:
            """
            Lists RC accounts based on specified criteria.

            :param account: The name of the account.
            :param limit: The maximum number of accounts to list.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of RC accounts.
            """
            return self.__wallet.connected_node.api.wallet_bridge.list_rc_accounts(account, limit)

        @warn_if_only_result_set()
        def list_rc_direct_delegations(
            self, start: list[AccountNameApiType, AccountNameApiType], limit: int, only_result: bool | None = None
        ) -> ListRcDirectDelegations:
            """
            Lists direct delegations of resource credits (RC).

            :param start: The start of the listing.
            :param limit: The maximum number of delegations to list.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of direct RC delegations.
            """
            return self.__wallet.connected_node.api.wallet_bridge.list_rc_direct_delegations(start, limit)

        @warn_if_only_result_set()
        def list_witnesses(
            self, lowerbound: str, limit: int, only_names: bool = False, only_result: bool | None = None
        ) -> list | ListWitnesses:
            """
            Lists witnesses based on specified criteria.

            :param lowerbound: The lower bound for listing witnesses.
            :param limit: The maximum number of witnesses to list.
            :param only_names: If True, only returns the names of witnesses.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The list of witnesses or ListWitnesses object.
            """
            witnesses = self.__wallet.connected_node.api.wallet_bridge.list_witnesses(lowerbound, limit)
            if only_names:
                only_names = []
                for witness in witnesses.witnesses:
                    only_names.append(witness.owner)
                return only_names
            return witnesses

        @warn_if_only_result_set()
        def load_wallet_file(self, wallet_filename, only_result: bool | None = None):
            """
            Raises an exception to indicate that the method is deprecated.

            :param wallet_filename: The filename of the wallet.
            :param only_result: This argument is no longer active and should not be provided.
            :raises MethodDeprecatedInBeekeeperWalletError: Always raised to indicate deprecation.
            """
            raise exceptions.MethodDeprecatedInBeekeeperWalletError()

        @warn_if_only_result_set()
        def lock(self, only_result: bool | None = None) -> None:
            """
            Locks the wallet.

            :param only_result: This argument is no longer active and should not be provided.
            """
            assert not self.is_locked()
            self.__wallet.beekeeper_wallet.lock()

        @warn_if_only_result_set()
        def normalize_brain_key(self, s: str, only_result: bool | None = None) -> str:
            """
            Normalizes a brain key string by converting it to uppercase and stripping any leading or trailing whitespace.

            :param s: The brain key string to normalize.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The normalized brain key string.
            """
            return s.upper().strip()

        @warn_if_only_result_set()
        def post_comment(
            self,
            author: AccountNameApiType,
            permlink: str,
            parent_author: AccountNameApiType | EmptyStringApiType,
            parent_permlink: str,
            title: str,
            body: str,
            json: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Posts a comment on the Hive blockchain.

            :param author: The author of the comment.
            :param permlink: The permlink of the comment.
            :param parent_author: The author of the parent comment or post.
            :param parent_permlink: The permlink of the parent comment or post.
            :param title: The title of the comment.
            :param body: The body of the comment.
            :param json: The JSON metadata associated with the comment.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                CommentOperation(
                    author=author,
                    permlink=permlink,
                    parent_author=parent_author,
                    parent_permlink=parent_permlink,
                    title=title,
                    body=body,
                    json_metadata=json,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def publish_feed(
            self,
            witness: AccountNameApiType,
            exchange_rate: HbdExchangeRateApiType[AssetHiveHF26, AssetHbdHF26],
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Publishes a price feed for a witness.

            :param witness: The witness publishing the feed.
            :param exchange_rate: The exchange rate for HBD to HIVE.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                FeedPublishOperation(
                    publisher=witness,
                    exchange_rate=HbdExchangeRate(
                        base=exchange_rate["base"],
                        quote=exchange_rate["quote"],
                    ),
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def recover_account(
            self,
            account_to_recover: AccountNameApiType,
            recent_authority: Authority,
            new_authority: Authority,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Recovers a compromised account using a new authority.

            :param account_to_recover: The account to recover.
            :param recent_authority: The recent authority of the account.
            :param new_authority: The new authority for the account.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                RecoverAccountOperation(
                    account_to_recover=account_to_recover,
                    recent_owner_authority=recent_authority,
                    new_owner_authority=new_authority,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def recurrent_transfer(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            amount: AssetHiveHF26 | AssetHbdHF26,
            memo: str,
            recurrence: int,
            executions: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Initiates a recurrent transfer of funds.

            :param from_: The account from which to transfer the funds.
            :param to: The account to which to transfer the funds.
            :param amount: The amount of funds to transfer.
            :param memo: The memo associated with the transfer.
            :param recurrence: The recurrence interval in seconds.
            :param executions: The number of times the transfer should be executed.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            self.__check_memo(memo)
            assert not self.is_locked()
            return self.__send_one_op(
                RecurrentTransferOperation(
                    from_=from_, to=to, amount=amount, memo=memo, recurrence=recurrence, executions=executions
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def recurrent_transfer_with_id(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            amount: AssetHiveHF26 | AssetHbdHF26,
            memo: str,
            recurrence: int,
            executions: int,
            pair_id: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Initiates a recurrent transfer of funds with a specified pair ID.

            :param from_: The account from which to transfer the funds.
            :param to: The account to which to transfer the funds.
            :param amount: The amount of funds to transfer.
            :param memo: The memo associated with the transfer.
            :param recurrence: The recurrence interval in seconds.
            :param executions: The number of times the transfer should be executed.
            :param pair_id: The ID of the transfer pair.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            self.__check_memo(memo)
            assert not self.is_locked()
            return self.__send_one_op(
                RecurrentTransferOperation(
                    from_=from_,
                    to=to,
                    amount=amount,
                    memo=memo,
                    recurrence=recurrence,
                    executions=executions,
                    extensions=[{"type": "recurrent_transfer_pair_id", "value": {"pair_id": pair_id}}],
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def remove_proposal(
            self,
            deleter: AccountNameApiType,
            ids: list[int],
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Removes a proposal from the blockchain.

            :param deleter: The account removing the proposal.
            :param ids: The IDs of the proposals to remove.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                RemoveProposalOperation(proposal_owner=deleter, proposal_ids=ids),
                broadcast=broadcast,
            )

        def request_account_recovery(
            self,
            recovery_account: AccountNameApiType,
            account_to_recover: AccountNameApiType,
            new_authority: Authority,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Requests account recovery using a new authority.

            :param recovery_account: The account initiating the recovery.
            :param account_to_recover: The account to be recovered.
            :param new_authority: The new authority for the recovered account.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                RequestAccountRecoveryOperation(
                    recovery_account=recovery_account,
                    account_to_recover=account_to_recover,
                    new_owner_authority=new_authority,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def save_wallet_file(self, wallet_filename, only_result: bool | None = None):
            """
            Raises an exception to indicate that the method is deprecated.

            :param wallet_filename: The filename of the wallet.
            :param only_result: This argument is no longer active and should not be provided.
            :raises MethodDeprecatedInBeekeeperWalletError: Always raised to indicate deprecation.
            """
            raise exceptions.MethodDeprecatedInBeekeeperWalletError()

        @warn_if_only_result_set()
        def serialize_transaction(self, tx: Transaction, only_result: bool | None = None) -> Hex:
            """
            Serializes a transaction.

            :param tx: The transaction to serialize.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The serialized transaction.
            """
            hex = self.__wallet.connected_node.api.database.get_transaction_hex(trx=tx)
            return hex.hex_

        @warn_if_only_result_set()
        def set_password(self, password, only_result: bool | None = None):
            """
            Raises an exception to indicate that the method is deprecated.

            :param password: The password to set
            :param only_result: This argument is no longer active and should not be provided.
            :raises MethodDeprecatedInBeekeeperWalletError: Always raised to indicate deprecation.
            """
            raise exceptions.MethodDeprecatedInBeekeeperWalletError()

        @warn_if_only_result_set()
        def set_transaction_expiration(self, seconds: int, only_result: bool | None = None) -> None:
            """
            Sets the expiration time for transactions.

            :param seconds: The number of seconds until expiration.
            :param only_result: This argument is no longer active and should not be provided.
            """
            assert seconds < HIVE_MAX_TIME_UNTIL_EXPIRATION
            self.__wallet._transaction_expiration_offset = timedelta(seconds=seconds)

        @warn_if_only_result_set()
        def set_voting_proxy(
            self,
            account_to_modify: AccountNameApiType,
            proxy: AccountNameApiType | EmptyStringApiType,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Sets a voting proxy for an account.

            :param account_to_modify: The account for which to set the proxy.
            :param proxy: The proxy account or an empty string to remove the proxy.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            return self.__send_one_op(
                AccountWitnessProxyOperation(account=account_to_modify, proxy=proxy),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def set_withdraw_vesting_route(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            percent: int,
            auto_vest: bool,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Sets up a vesting withdrawal route for an account.

            :param from_: The account from which to withdraw vesting.
            :param to: The account to receive the withdrawn vesting.
            :param percent: The percentage of the withdrawn vesting to route to the 'to' account.
            :param auto_vest: Whether to automatically conversion HIVE to HP in the withdrawn.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                SetWithdrawVestingRouteOperation(
                    from_account=from_, to_account=to, percent=percent, auto_vest=auto_vest
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def sign_transaction(
            self, tx: SimpleTransaction, broadcast: bool = True, only_result: bool | None = None
        ) -> WalletResponse:
            """
            Signs a transaction and optionally broadcasts it to the network.

            :param tx: The transaction to sign.
            :param broadcast: Whether to broadcast the signed transaction to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            tx = self.__wallet.sign_transaction(self.__wallet.connected_node, tx)
            if broadcast:
                broadcast_response = self.__wallet.connected_node.api.wallet_bridge.broadcast_transaction_synchronous(
                    tx
                )

                return WalletResponse(
                    transaction_id=wax_helpy.calculate_transaction_id(transaction=tx),
                    block_num=broadcast_response.block_num,
                    transaction_num=broadcast_response.trx_num,
                    rc_cost=broadcast_response.rc_cost,
                    ref_block_num=tx.ref_block_num,
                    ref_block_prefix=tx.ref_block_prefix,
                    expiration=tx.expiration,
                    extensions=tx.extensions,
                    signatures=tx.signatures,
                    operations=tx.operations,
                )

            return WalletResponseBase(
                transaction_id=wax_helpy.calculate_transaction_id(transaction=tx),
                ref_block_num=tx.ref_block_num,
                ref_block_prefix=tx.ref_block_prefix,
                expiration=tx.expiration,
                extensions=tx.extensions,
                signatures=tx.signatures,
                operations=tx.operations,
            )

        @warn_if_only_result_set()
        def suggest_brain_key(self, only_result: bool | None = None) -> dict:
            """
            Generates a suggested brain key.

            :param only_result: This argument is no longer active and should not be provided.
            :return: A dictionary containing the suggested brain key, associated WIF private key, and public key.
            """
            brain_key = wax.suggest_brain_key()
            return {
                "brain_priv_key": brain_key.brain_key.decode(),
                "wif_priv_key": brain_key.wif_private_key.decode(),
                "pub_key": brain_key.associated_public_key,
            }

        @warn_if_only_result_set()
        def transfer(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            amount: Asset.AssetHiveT | Asset.AssetHbdT,
            memo: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Transfers assets from one account to another.

            :param from_: The account from which to transfer the assets.
            :param to: The account to which to transfer the assets.
            :param amount: The amount of assets to transfer.
            :param memo: The memo associated with the transfer.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            self.__check_memo(memo)
            assert not self.is_locked()
            return self.__send_one_op(
                TransferOperation(from_=from_, to=to, amount=amount, memo=memo),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def transfer_from_savings(
            self,
            from_: AccountNameApiType,
            request_id: int,
            to: AccountNameApiType,
            amount: AssetHiveHF26 | AssetHbdHF26,
            memo: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Transfers assets from savings to another account.

            :param from_: The account from which to transfer the assets.
            :param request_id: The ID of the savings withdrawal request.
            :param to: The account to which to transfer the assets.
            :param amount: The amount of assets to transfer.
            :param memo: The memo associated with the transfer.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            self.__check_memo(memo)
            assert not self.is_locked()
            return self.__send_one_op(
                TransferFromSavingsOperation(from_=from_, request_id=request_id, to=to, amount=amount, memo=memo),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def transfer_nonblocking(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            amount: Asset.AssetHiveT | Asset.AssetHbdT,
            memo: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponseBase:
            """
            Transfers assets from one account to another and non-blocking broadcast.

            :param from_: The account from which to transfer the assets.
            :param to: The account to which to transfer the assets.
            :param amount: The amount of assets to transfer.
            :param memo: The memo associated with the transfer.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            self.__check_memo(memo)
            assert not self.is_locked()
            return self.__send_one_op(
                TransferOperation(from_=from_, to=to, amount=amount, memo=memo),
                broadcast=broadcast,
                blocking=False,
            )

        @warn_if_only_result_set()
        def transfer_to_savings(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType,
            amount: AssetHiveHF26 | AssetHbdHF26,
            memo: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Transfers assets from one account to other into savings.

            :param from_: The account from which to transfer the assets.
            :param to: The account to which to transfer the assets.
            :param amount: The amount of assets to transfer.
            :param memo: The memo associated with the transfer.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            self.__check_memo(memo)
            assert not self.is_locked()
            return self.__send_one_op(
                TransferToSavingsOperation(from_=from_, to=to, amount=amount, memo=memo),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def transfer_to_vesting(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType | EmptyStringApiType,
            amount: AssetHiveHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Transfers assets to vesting.

            :param from_: The account from which to transfer the assets.
            :param to: The account to which to transfer the assets.
            :param amount: The amount of HIVE to transfer to vesting.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                TransferToVestingOperation(from_=from_, to=to, amount=amount),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def transfer_to_vesting_nonblocking(
            self,
            from_: AccountNameApiType,
            to: AccountNameApiType | EmptyStringApiType,
            amount: AssetHiveHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponseBase:
            """
            Transfers assets to vesting and non-blocking broadcast.

            :param from_: The account from which to transfer the assets.
            :param to: The account to which to transfer the assets.
            :param amount: The amount of HIVE to transfer to vesting.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                TransferToVestingOperation(from_=from_, to=to, amount=amount),
                broadcast=broadcast,
                blocking=False,
            )

        @warn_if_only_result_set()
        def unlock(self, password: str, only_result: bool | None = None) -> UnlockedWallet:
            """
            Unlocks the wallet using the provided password.

            :param password: The password to unlock the wallet.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The unlocked wallet object.
            """
            assert self.is_locked()
            return self.__wallet.beekeeper_wallet.unlock(password)

        @warn_if_only_result_set()
        def update_account(
            self,
            accountname: AccountNameApiType,
            json_meta: str,
            owner: PublicKeyApiType,
            active: PublicKeyApiType,
            posting: PublicKeyApiType,
            memo: PublicKeyApiType,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates the account with new authority and metadata.

            :param accountname: The name of the account to update.
            :param json_meta: The JSON metadata to update.
            :param owner: The new owner key.
            :param active: The new active key.
            :param posting: The new posting key.
            :param memo: The new memo key.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                AccountUpdateOperation(
                    account=accountname,
                    json_metadata=json_meta,
                    owner=self.get_authority(owner),
                    active=self.get_authority(active),
                    posting=self.get_authority(posting),
                    memo_key=memo,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_account_auth_account(
            self,
            account_name: AccountNameApiType,
            type_: str,
            auth_account: AccountNameApiType,
            weight: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates the account with a new authority account.

            :param account_name: The name of the account to update.
            :param type_: The type of authority (e.g., owner, active, posting).
            :param auth_account: The new authority account.
            :param weight: The weight of the authority.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            account = self.get_account(account_name=account_name)
            kwargs: dict[str, Authority] = {type_: account[type_]}
            kwargs[type_].account_auths.append([auth_account, weight])

            return self.__send_one_op(
                AccountUpdateOperation(
                    account=account_name, json_metadata=account.json_metadata, memo_key=account.memo_key, **kwargs
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_account_auth_key(
            self,
            account_name: AccountNameApiType,
            type_: str,
            key: str,
            weight: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates the account with a new authority key.

            :param account_name: The name of the account to update.
            :param type_: The type of authority (e.g., owner, active, posting).
            :param key: The new authority key.
            :param weight: The weight of the authority.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            account = self.get_account(account_name=account_name)
            kwargs: dict[str, Authority] = {type_: account[type_]}
            kwargs[type_].key_auths.append([key, weight])

            return self.__send_one_op(
                AccountUpdateOperation(
                    account=account_name, json_metadata=account.json_metadata, memo_key=account.memo_key, **kwargs
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_account_auth_threshold(
            self,
            account_name: AccountNameApiType,
            type_: str,
            threshold: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Update the authority threshold for an account.

            :param account_name: The name of the account to update.
            :param type_: The type of authority to update ('owner', 'active', or 'posting').
            :param threshold: The new threshold value for the authority.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            account = self.get_account(account_name=account_name)
            if threshold == 0:
                raise exceptions.TresholdOutOfRangeError

            kwargs: dict[str, Authority] = {type_: account[type_]}
            kwargs[type_].weight_threshold = threshold

            return self.__send_one_op(
                AccountUpdateOperation(
                    account=account_name, json_metadata=account.json_metadata, memo_key=account.memo_key, **kwargs
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_account_memo_key(
            self,
            account_name: AccountNameApiType,
            key: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates the account with a new memo key.

            :param account_name: The name of the account to update.
            :param key: The new memo key.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            account = self.get_account(account_name=account_name)
            return self.__send_one_op(
                AccountUpdateOperation(account=account_name, memo_key=key, json_metadata=account.json_metadata),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_account_meta(
            self,
            account_name: AccountNameApiType,
            json_meta: str,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates the account metadata.

            :param account_name: The name of the account to update.
            :param json_meta: The JSON metadata to update.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            account = self.get_account(account_name=account_name)

            return self.__send_one_op(
                AccountUpdateOperation(account=account_name, json_metadata=json_meta, memo_key=account.memo_key),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_proposal(
            self,
            proposal_id: int,
            creator: AccountNameApiType,
            daily_pay: AssetHbdHF26,
            subject: str,
            permlink: str,
            end_date: datetime | str | None,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates a proposal.

            :param proposal_id: The ID of the proposal to update.
            :param creator: The account that created the proposal.
            :param daily_pay: The daily pay of the proposal.
            :param subject: The subject of the proposal.
            :param permlink: The permlink of the proposal.
            :param end_date: The end date of the proposal.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            if end_date:
                return self.__send_one_op(
                    UpdateProposalOperation(
                        proposal_id=proposal_id,
                        creator=creator,
                        daily_pay=daily_pay,
                        subject=subject,
                        permlink=permlink,
                        extensions=[{"type": "update_proposal_end_date", "value": {"end_date": end_date}}],
                    ),
                    broadcast=broadcast,
                )
            return self.__send_one_op(
                UpdateProposalOperation(
                    proposal_id=proposal_id,
                    creator=creator,
                    daily_pay=daily_pay,
                    subject=subject,
                    permlink=permlink,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_proposal_votes(
            self,
            voter: AccountNameApiType,
            proposals: list[int],
            approve: bool,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates proposal votes.

            :param voter: The account voting on the proposals.
            :param proposals: The list of proposal IDs.
            :param approve: Whether to approve or unapprove the proposals.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                UpdateProposalVotesOperation(
                    voter=voter,
                    proposal_ids=proposals,
                    approve=approve,
                ),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def update_witness(
            self,
            witness_name: AccountNameApiType,
            url: WitnessUrlApiType,
            block_signing_key: PublicKeyApiType,
            props: dict,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Updates a witness.

            :param witness_name: The name of the witness to update.
            :param url: The URL of the witness.
            :param block_signing_key: The block signing key of the witness.
            :param props: The properties of the witness.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                WitnessUpdateOperation(owner=witness_name, url=url, block_signing_key=block_signing_key, props=props),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def use_authority(
            self, type_: AuthorityType, account_name: AccountNameApiType, only_result: bool | None = None
        ) -> None:
            """
            Set the authority type for the specified account.

            :param type_: The authority type.
            :param account_name: The name of the account.
            :param only_result: This argument is no longer active and should not be provided.
            """
            self.__wallet._use_authority[account_name] = type_

        @warn_if_only_result_set()
        def use_automatic_authority(self, only_result: bool | None = None) -> None:
            """
            Clear the automatic authority usage.
            """
            self.__wallet._use_authority.clear()

        @warn_if_only_result_set()
        def vote(
            self,
            voter: AccountNameApiType,
            author: AccountNameApiType,
            permlink: str,
            weight: int,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Vote on a post.

            :param voter: The account voting.
            :param author: The author of the post to vote on.
            :param permlink: The permlink of the post to vote on.
            :param weight: The weight of the vote.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            if abs(weight) > 100:
                raise exceptions.WeightOutOfRangeError
            return self.__send_one_op(
                VoteOperation(voter=voter, author=author, permlink=permlink, weight=weight * 100),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def vote_for_witness(
            self,
            account_to_vote_with: AccountNameApiType,
            witness_to_vote_for: AccountNameApiType,
            approve: bool,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Vote for a witness.

            :param account_to_vote_with: The account voting for the witness.
            :param witness_to_vote_for: The witness to vote for.
            :param approve: Whether to approve (True) or unapprove (False) the witness.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                AccountWitnessVoteOperation(account=account_to_vote_with, witness=witness_to_vote_for, approve=approve),
                broadcast=broadcast,
            )

        @warn_if_only_result_set()
        def withdraw_vesting(
            self,
            from_: AccountNameApiType,
            vesting_shares: AssetVestsHF26,
            broadcast: bool | None = None,
            only_result: bool | None = None,
        ) -> WalletResponse:
            """
            Withdraw vesting shares.

            :param from_: The account from which to withdraw vesting shares.
            :param vesting_shares: The amount of vesting shares to withdraw.
            :param broadcast: Whether to broadcast the operation to the network.
            :param only_result: This argument is no longer active and should not be provided.
            :return: The response from the blockchain.
            """
            assert not self.is_locked()
            return self.__send_one_op(
                WithdrawVestingOperation(account=from_, vesting_shares=vesting_shares),
                broadcast=broadcast,
            )

    def __init__(self, *, attach_to: None | Node | RemoteNode, handle: WalletHandle | None = None):
        super().__init__(handle=handle)

        self.api = Wallet.Api(self)
        self.connected_node: None | AnyNode | RemoteNode = attach_to
        self._use_authority: dict[str, AuthorityType] = {}
        self.__beekeeper: Beekeeper | None = None
        self.__beekeeper_session: Session | None = None
        self._beekeeper_wallet: UnlockedWallet | None = None
        self._transaction_expiration_offset = timedelta(seconds=30)
        self.logger = logger.bind(target="cli_wallet")
        self.__prepare_directory()

        self.run()

    def __prepare_directory(self):
        if isinstance(self.connected_node, Node):
            self.name = context.names.register_numbered_name(f"{self.connected_node}.Wallet")
            self.directory = self.connected_node.directory.parent / self.name
            self.connected_node.register_wallet(self)
        elif isinstance(self.connected_node, RemoteNode):
            self.name = context.names.register_numbered_name(f"{self.connected_node}.Wallet")
            self.directory = context.get_current_directory() / self.name
        else:
            self.name = context.names.register_numbered_name("Wallet")
            self.directory = context.get_current_directory() / self.name

        if self.directory.exists():
            shutil.rmtree(self.directory)

    @property
    def beekeeper_wallet(self) -> UnlockedWallet:
        return self._beekeeper_wallet

    def send(
        self, operations: list[AnyOperation], broadcast: bool, blocking: bool
    ) -> None | WalletResponseBase | WalletResponse:
        return self.api._send(operations, broadcast, blocking)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def get_stdout_file_path(self) -> Path:
        return self.directory / "stdout.txt"

    def get_stderr_file_path(self) -> Path:
        return self.directory / "stderr.txt"

    def is_running(self) -> bool:
        return self._beekeeper_wallet is not None

    def run(
        self,
    ) -> None:
        if self.is_running():
            raise RuntimeError("Wallet is already running")

        if self.connected_node is not None:
            if not self.connected_node.is_running():
                raise exceptions.NodeIsNotRunningError("Before attaching wallet you have to run node")
        self.__beekeeper = beekeeper_factory(
            settings=Settings(working_directory=self.directory, communicator=RequestCommunicator)
        )
        self.__beekeeper_session = self.__beekeeper.create_session()

        try:
            self._beekeeper_wallet = self.__beekeeper_session.create_wallet(
                name=self.name, password=self.DEFAULT_PASSWORD
            )
            self._beekeeper_wallet.import_key(private_key=Account("initminer").private_key)
        except helpy.exceptions.RequestError as exception:
            if f"Wallet with name: '{self.name}' already exists" in exception.error:
                self._beekeeper_wallet = self.__beekeeper_session.open_wallet(name=self.name)
                self._beekeeper_wallet = self._beekeeper_wallet.unlock(self.DEFAULT_PASSWORD)
            else:
                raise exception

    def at_exit_from_scope(self):
        self.close()

    def restart(self) -> None:
        self.close()
        self.run()

    def close(self) -> None:
        if self.is_running():
            self.__beekeeper_session.close_session()
            self.__beekeeper.delete()
        self.__beekeeper = None
        self._beekeeper_wallet = None
        self.__beekeeper_session = None

    def create_account(
        self,
        name: str,
        *,
        creator: str = "initminer",
        hives: Asset.TestT | float | int | None = None,
        vests: Asset.TestT | float | int | None = None,
        hbds: Asset.TbdT | float | int | None = None,
    ) -> dict:
        """
        The `transfer_to_vesting` operation can be only done by sending the Asset.Test type, that's why method in place
        of `vests` accepts the Asset.Test and numeric types instead of Asset.Vest.
        """
        if isinstance(hives, float | int):
            hives = Asset.Test(hives)
        if isinstance(vests, float | int):
            vests = Asset.Test(vests)
        if isinstance(hbds, float | int):
            hbds = Asset.Tbd(hbds)

        account = Account(name)
        with self.in_single_transaction() as transaction:
            self.api.create_account_with_keys(
                creator,
                account.name,
                "{}",
                account.public_key,
                account.public_key,
                account.public_key,
                account.public_key,
            )

            if hives is not None:
                self.api.transfer(creator, name, hives, "memo")

            if vests is not None:
                self.api.transfer_to_vesting(creator, name, vests)

            if hbds is not None:
                self.api.transfer(creator, name, hbds, "memo")

        self.api.import_key(account.private_key)
        return transaction.get_response()

    def create_accounts(
        self, number_of_accounts: int, name_base: str = "account", *, secret: str = "secret", import_keys: bool = True
    ) -> list[Account]:
        previous_transaction_expiration_offset = self._transaction_expiration_offset
        self._transaction_expiration_offset = timedelta(seconds=1800)
        accounts_per_transaction: Final[int] = 500
        private_keys_per_transaction: Final[int] = 500

        def send_transaction(accounts_: list[Account]):
            operations = []
            accounts_range_message = f"{accounts_[0].name}..{accounts_[-1].name}"
            for account in accounts_:
                operation = AccountCreateOperation(
                    creator="initminer",
                    new_account_name=account.name,
                    json_metadata="{}",
                    fee=Asset.Test(0).as_nai(),
                    owner=self.api.get_authority(account.public_key),
                    active=self.api.get_authority(account.public_key),
                    posting=self.api.get_authority(account.public_key),
                    memo_key=account.public_key,
                )  # type: ignore

                operations.append(operation)

            def retry_until_success(predicate: Callable[[], Any], *, fail_message: str, max_retries: int = 20) -> bool:
                retries = 0
                while retries <= max_retries:
                    try:
                        predicate()
                        return True
                    except:
                        self.logger.error(fail_message)
                        retries += 1
                return False

            def ensure_accounts_exists() -> None:
                listed_accounts = self.api.list_accounts(accounts_[0].name, 1)
                if accounts_[0].name in listed_accounts:
                    self.logger.debug(f"Accounts created: {accounts_range_message}")

            # Send transaction
            while True:
                if not retry_until_success(
                    lambda: self._prepare_and_send_transaction(operations, True, True),
                    fail_message=f"Failed to send transaction: {accounts_range_message}",
                ):
                    continue

                if retry_until_success(
                    ensure_accounts_exists,
                    fail_message=f"Node ignored create accounts request of accounts {accounts_range_message}, requesting again...",
                    max_retries=5,
                ):
                    return

        def run_in_thread_pool_executor(
            predicate: Callable[[Any], Any], iterable_args: list[Any], *, max_threads=(os.cpu_count() or 24)
        ) -> None:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures: list[concurrent.futures.Future] = []
                for args in iterable_args:
                    futures.append(executor.submit(predicate, args))

                start = time.perf_counter()
                while (
                    len((tasks := concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED))[0])
                    > 0
                ):
                    futures.pop(futures.index(tasks[0].pop()))
                    self.logger.debug(f"Joined next item after {(time.perf_counter() - start) :.4f} seconds...")
                    start = time.perf_counter()

        def split(
            collection: list[Any], items_per_chunk: int, *, predicate: Callable[[Any], Any] = lambda x: x
        ) -> list[Any]:
            return [
                [predicate(item) for item in collection[i : i + items_per_chunk]]
                for i in range(0, len(collection), items_per_chunk)
            ]

        accounts = Account.create_multiple(number_of_accounts, name_base, secret=secret)
        run_in_thread_pool_executor(send_transaction, split(accounts, accounts_per_transaction))
        if import_keys:
            self.logger.info("starting importing keys")

            def importing_keys(keys):
                self.logger.info(f"{threading.get_native_id()}) part of importing keys started")
                self.api.import_keys(keys)
                self.logger.info(f"{threading.get_native_id()}) part of importing keys finished")

            run_in_thread_pool_executor(
                importing_keys, split(accounts, private_keys_per_transaction, predicate=lambda x: x.private_key), max_threads=4
            )
            self.logger.info("finished importing keys")

        self._transaction_expiration_offset = previous_transaction_expiration_offset
        return accounts

    def list_accounts(self) -> list[str]:
        next_account = ""
        all_accounts = []
        while True:
            result = self.api.list_accounts(next_account, 1000)

            if len(result) == 1:
                all_accounts.extend(result)
                break

            all_accounts.extend(result[:-1])
            next_account = result[-1]

        return all_accounts

    def __get_tapos_data(self, block_id: str) -> wax.python_ref_block_data:
        return wax.get_tapos_data(block_id.encode())  # type: ignore[no-any-return]

    def __generate_transaction_template(
        self,
        node: AnyNode,
    ) -> SimpleTransaction:
        gdpo = node.api.database.get_dynamic_global_properties()
        if isinstance(gdpo, dict | list):
            logger.error(gdpo)
            raise Exception(gdpo)

        block_id = gdpo.head_block_id

        # set header
        tapos_data = self.__get_tapos_data(block_id)
        ref_block_num = tapos_data.ref_block_num
        ref_block_prefix = tapos_data.ref_block_prefix

        assert ref_block_num >= 0, f"ref_block_num value `{ref_block_num}` is invalid`"
        assert ref_block_prefix > 0, f"ref_block_prefix value `{ref_block_prefix}` is invalid`"

        return SimpleTransaction(
            ref_block_num=HiveInt(ref_block_num),
            ref_block_prefix=HiveInt(ref_block_prefix),
            expiration=gdpo.time + self._transaction_expiration_offset,
            extensions=[],
            signatures=[],
            operations=[],
        )

    def _prepare_and_send_transaction(
        self, operations: list[AnyOperation], blocking: bool, broadcast: bool
    ) -> WalletResponseBase | WalletResponse:
        transaction = self.__generate_transaction_template(self.connected_node)
        for operation in operations:
            transaction.add_operation(operation)

        transaction = self.sign_transaction(self.connected_node, transaction)

        if broadcast:
            if blocking:
                broadcast_response = self.connected_node.api.wallet_bridge.broadcast_transaction_synchronous(
                    transaction
                )
                return WalletResponse(
                    transaction_id=wax_helpy.calculate_transaction_id(transaction=transaction),
                    block_num=broadcast_response.block_num,
                    transaction_num=broadcast_response.trx_num,
                    rc_cost=broadcast_response.rc_cost,
                    ref_block_num=transaction.ref_block_num,
                    ref_block_prefix=transaction.ref_block_prefix,
                    expiration=transaction.expiration,
                    extensions=transaction.extensions,
                    signatures=transaction.signatures,
                    operations=transaction.operations,
                )
            else:
                self.connected_node.api.wallet_bridge.broadcast_transaction(transaction)

        return WalletResponseBase(
            transaction_id=wax_helpy.calculate_transaction_id(transaction=transaction),
            ref_block_num=transaction.ref_block_num,
            ref_block_prefix=transaction.ref_block_prefix,
            expiration=transaction.expiration,
            extensions=transaction.extensions,
            signatures=transaction.signatures,
            operations=transaction.operations,
        )

    def sign_transaction(self, node: AnyNode, transaction: SimpleTransaction) -> SimpleTransaction:
        transaction_bytes = transaction.json(exclude_none=True, by_alias=True, ensure_ascii=False).encode()
        wax_helpy.calculate_transaction_id(transaction=transaction)
        node_config = node.api.database.get_config()
        if isinstance(node_config, dict | list):
            logger.error(node_config)
            raise Exception(node_config)

        sig_digest = wax_helpy.calculate_sig_digest(transaction, node_config.HIVE_CHAIN_ID)
        assert self._beekeeper_wallet is not None
        keys_to_sign_with = self.import_required_keys(transaction_bytes)
        for key in keys_to_sign_with:
            signature = self._beekeeper_wallet.sign_digest(sig_digest=sig_digest, key=key)
            transaction.signatures.append(signature)
        transaction.signatures = list(set(transaction.signatures))

        wax_helpy.validate_transaction(transaction)
        return transaction

    def import_required_keys(self, transaction: bytes):
        authorities_accounts = self.__get_authority_accounts(transaction=transaction)

        def remove_from_collection(account: str, collection: set[str]) -> None:
            if account in collection:
                collection.remove(account)

        for account_name, authority_type in self._use_authority.items():
            match authority_type:
                case "active":
                    remove_from_collection(account_name, authorities_accounts.owner)
                    remove_from_collection(account_name, authorities_accounts.posting)
                case "posting":
                    remove_from_collection(account_name, authorities_accounts.owner)
                    remove_from_collection(account_name, authorities_accounts.active)
                case "owner":
                    remove_from_collection(account_name, authorities_accounts.active)
                    remove_from_collection(account_name, authorities_accounts.posting)

        assert self.connected_node is not None
        keys_for_signing = set()
        pubkey_account_association: dict[PublicKey, str] = {}

        finded_accounts = self.connected_node.api.database.find_accounts(accounts=list(authorities_accounts.all()))
        if isinstance(finded_accounts, dict | list):
            logger.error(finded_accounts)
            raise Exception(finded_accounts)

        for account in self.connected_node.api.database.find_accounts(
            accounts=list(authorities_accounts.all())
        ).accounts:
            key_to_add: PublicKey
            if account.name in authorities_accounts.posting:
                key_to_add = account.posting.key_auths[0][0]
            elif account.name in authorities_accounts.active:
                key_to_add = account.active.key_auths[0][0]
            elif account.name in authorities_accounts.owner:
                key_to_add = account.owner.key_auths[0][0]
            else:
                raise KeyError(
                    f"Not matching keys for {account.name} found. Rule: only `{self._use_authority.get(account.name)}`"
                )

            key_to_add = key_to_add
            keys_for_signing.add(key_to_add)
            pubkey_account_association[key_to_add] = account.name

        imported_keys_in_beekeeper = set([key for key in self.beekeeper_wallet.public_keys])
        unknown_keys = keys_for_signing.difference(imported_keys_in_beekeeper)
        if len(unknown_keys) == 0:
            return keys_for_signing

        for ukey in unknown_keys:
            account = Account(pubkey_account_association[ukey])
            received_pub_key = self.beekeeper_wallet.import_key(private_key=account.private_key)
            assert ukey == received_pub_key
        return keys_for_signing

    def __get_authority_accounts(self, transaction: bytes) -> AuthorityRequirementsHolder:
        auths = wax.get_transaction_required_authorities(transaction=transaction)
        result = AuthorityRequirementsHolder()
        result.active = set([account.decode("ascii") for account in auths.active_accounts])
        result.owner = set([account.decode("ascii") for account in auths.owner_accounts])
        result.posting = set([account.decode("ascii") for account in auths.posting_accounts])
        return result

    def in_single_transaction(self, *, broadcast: bool = True, blocking: bool = True) -> SingleTransactionContext:
        if broadcast == None:
            broadcast = True
        return SingleTransactionContext(self, broadcast=broadcast, blocking=blocking)


class SingleTransactionContext(ContextSync["SingleTransactionContext"]):
    def __init__(self, wallet_: Wallet, *, broadcast, blocking):
        self.__wallet = wallet_
        self.__broadcast = broadcast
        self.__blocking = blocking
        self.__response = None
        self.__was_run_as_context_manager = False

    def get_response(self) -> None | WalletResponseBase | WalletResponse:
        return self.__response

    def as_dict(self) -> dict:
        if isinstance(self.__response, WalletResponseBase | WalletResponse):
            return self.__response.__dict__

    def __del__(self) -> None:
        if not self.__was_run_as_context_manager:
            raise RuntimeError(
                f'You used {Wallet.__name__}.{Wallet.in_single_transaction.__name__}() not in "with" statement'
            )

    def _enter(self) -> SingleTransactionContext:
        self.__wallet.api._start_gathering_operations_for_single_transaction()
        self.__was_run_as_context_manager = True
        return self

    def _finally(self) -> None:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_value is not None:
            raise exc_value
        self.__response = self.__wallet.api._send_gathered_operations_as_single_transaction(
            broadcast=self.__broadcast, blocking=self.__blocking
        )
