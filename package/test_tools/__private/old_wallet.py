# mypy: ignore-errors
# ruff: noqa
# file for deletion after cli_wallet deprecation
from __future__ import annotations

import concurrent.futures
import copy
import math
import os
import re
import shutil
import signal
import subprocess
import warnings
from argparse import ArgumentParser
from typing import TYPE_CHECKING, Final, Literal, Any
from typing_extensions import Self
from loguru import logger

from test_tools.__private import communication, paths_to_executables
from test_tools.__private.account import Account
from wax.helpy import Hf26Asset as Asset
from test_tools.__private.exceptions import NodeIsNotRunningError
from beekeepy.exceptions import CommunicationError
from test_tools.__private.node import Node
from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.scope import ScopedObject, context
from wax.helpy import Time
from beekeepy.interfaces import SelfContextSync
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation
from test_tools.__private.utilities.fake_time import configure_fake_time

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from test_tools.__private.user_handles.handles.old_wallet_handle import OldWalletHandle


# This pylint warning is right, but refactor has low priority. Will be done later...
# It can be solved by moving the generated code to a separate file and disabling the warning in that file only.


class OldWallet(UserHandleImplementation, ScopedObject):
    # This pylint warning is right, but this refactor has low priority. Will be done later...

    DEFAULT_RUN_TIMEOUT = 15
    DEFAULT_PASSWORD = "password"
    DEFAULT_TRANSACTION_SERIALIZATION: Literal["legacy", "hf26"] = "legacy"

    class Api:
        # OldWallet api is out of TestTools control

        class TransactionBuilder:
            """Helper class for sending multiple operations in single transaction."""

            def __init__(self):
                self.__transaction = None

            def append_operation(self, response):
                if self.__transaction is None:
                    self.__transaction = response["result"]
                else:
                    operation = response["result"]["operations"][0]
                    self.__transaction["operations"].append(operation)

            def get_transaction(self):
                return self.__transaction

        def __init__(self, wallet: OldWallet):
            self.__wallet = wallet
            self.__transaction_builder = None

        @property
        def _transaction_builder(self) -> TransactionBuilder:
            assert self.__transaction_builder is not None
            return self.__transaction_builder

        def _start_gathering_operations_for_single_transaction(self):
            if self.__transaction_builder is not None:
                raise RuntimeError("You cannot create transaction inside another transaction")

            self.__transaction_builder = self.TransactionBuilder()

        def _send_gathered_operations_as_single_transaction(self, *, broadcast):
            transaction = self._transaction_builder.get_transaction()
            self.__transaction_builder = None

            return self.sign_transaction(transaction, broadcast=broadcast) if transaction is not None else None

        def __send(self, method_, jsonrpc="2.0", id_=0, *, only_result: bool, **params):
            if "broadcast" in params:
                self.__handle_broadcast_parameter(params)

            response = self.__wallet.send(method_, *list(params.values()), jsonrpc=jsonrpc, id_=id_)

            if self.__is_transaction_build_in_progress():
                self._transaction_builder.append_operation(response)

            return response["result"] if only_result else response

        def __handle_broadcast_parameter(self, params):
            if params["broadcast"] is None:
                params["broadcast"] = self.__get_default_broadcast_value()
            elif self.__is_transaction_build_in_progress():
                if params["broadcast"] is True:
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
            elif params["broadcast"] is True and not self.__is_transaction_build_in_progress():
                warnings.warn(
                    'Avoid explicit setting "broadcast" parameter to True in this context, it is default value.\n'
                    "It is considered bad practice, because obscures code and decreases its readability.",
                    stacklevel=1,
                )

        def __get_default_broadcast_value(self):
            return not self.__is_transaction_build_in_progress()

        def __is_transaction_build_in_progress(self):
            return self.__transaction_builder is not None

        # Below code is machine generated. Don't update it manually.
        #
        # If you updated wallet API in C++ sources and you want to synchronize TestTools with it,
        # run following script: test_tools/package/test_tools/private/scripts/update_wallet_api.py
        #
        # If you want to introduce some other changes, you need to modify mentioned script and rerun it.
        #
        # Begin of machine generated code
        def about(self, only_result: bool = True):
            return self.__send("about", only_result=only_result)

        def cancel_order(self, owner, orderid, broadcast=None, only_result: bool = True):
            return self.__send(
                "cancel_order", owner=owner, orderid=orderid, broadcast=broadcast, only_result=only_result
            )

        def cancel_transfer_from_savings(self, from_, request_id, broadcast=None, only_result: bool = True):
            return self.__send(
                "cancel_transfer_from_savings",
                from_=from_,
                request_id=request_id,
                broadcast=broadcast,
                only_result=only_result,
            )

        def change_recovery_account(self, owner, new_recovery_account, broadcast=None, only_result: bool = True):
            return self.__send(
                "change_recovery_account",
                owner=owner,
                new_recovery_account=new_recovery_account,
                broadcast=broadcast,
                only_result=only_result,
            )

        def claim_account_creation(self, creator, fee, broadcast=None, only_result: bool = True):
            return self.__send(
                "claim_account_creation", creator=creator, fee=fee, broadcast=broadcast, only_result=only_result
            )

        def claim_account_creation_nonblocking(self, creator, fee, broadcast=None, only_result: bool = True):
            return self.__send(
                "claim_account_creation_nonblocking",
                creator=creator,
                fee=fee,
                broadcast=broadcast,
                only_result=only_result,
            )

        def claim_reward_balance(
            self, account, reward_hive, reward_hbd, reward_vests, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "claim_reward_balance",
                account=account,
                reward_hive=reward_hive,
                reward_hbd=reward_hbd,
                reward_vests=reward_vests,
                broadcast=broadcast,
                only_result=only_result,
            )

        def convert_hbd(self, from_, amount, broadcast=None, only_result: bool = True):
            return self.__send("convert_hbd", from_=from_, amount=amount, broadcast=broadcast, only_result=only_result)

        def convert_hive_with_collateral(self, from_, collateral_amount, broadcast=None, only_result: bool = True):
            return self.__send(
                "convert_hive_with_collateral",
                from_=from_,
                collateral_amount=collateral_amount,
                broadcast=broadcast,
                only_result=only_result,
            )

        def create_account(self, creator, new_account_name, json_meta, broadcast=None, only_result: bool = True):
            return self.__send(
                "create_account",
                creator=creator,
                new_account_name=new_account_name,
                json_meta=json_meta,
                broadcast=broadcast,
                only_result=only_result,
            )

        def create_account_delegated(
            self,
            creator,
            hive_fee,
            delegated_vests,
            new_account_name,
            json_meta,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "create_account_delegated",
                creator=creator,
                hive_fee=hive_fee,
                delegated_vests=delegated_vests,
                new_account_name=new_account_name,
                json_meta=json_meta,
                broadcast=broadcast,
                only_result=only_result,
            )

        def create_account_with_keys(
            self, creator, newname, json_meta, owner, active, posting, memo, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "create_account_with_keys",
                creator=creator,
                newname=newname,
                json_meta=json_meta,
                owner=owner,
                active=active,
                posting=posting,
                memo=memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def create_account_with_keys_delegated(
            self,
            creator,
            hive_fee,
            delegated_vests,
            newname,
            json_meta,
            owner,
            active,
            posting,
            memo,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "create_account_with_keys_delegated",
                creator=creator,
                hive_fee=hive_fee,
                delegated_vests=delegated_vests,
                newname=newname,
                json_meta=json_meta,
                owner=owner,
                active=active,
                posting=posting,
                memo=memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def create_funded_account_with_keys(
            self,
            creator,
            new_account_name,
            initial_amount,
            memo,
            json_meta,
            owner_key,
            active_key,
            posting_key,
            memo_key,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "create_funded_account_with_keys",
                creator=creator,
                new_account_name=new_account_name,
                initial_amount=initial_amount,
                memo=memo,
                json_meta=json_meta,
                owner_key=owner_key,
                active_key=active_key,
                posting_key=posting_key,
                memo_key=memo_key,
                broadcast=broadcast,
                only_result=only_result,
            )

        def create_order(
            self,
            owner,
            order_id,
            amount_to_sell,
            min_to_receive,
            fill_or_kill,
            expiration,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "create_order",
                owner=owner,
                order_id=order_id,
                amount_to_sell=amount_to_sell,
                min_to_receive=min_to_receive,
                fill_or_kill=fill_or_kill,
                expiration=expiration,
                broadcast=broadcast,
                only_result=only_result,
            )

        def create_proposal(
            self,
            creator,
            receiver,
            start_date,
            end_date,
            daily_pay,
            subject,
            permlink,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "create_proposal",
                creator=creator,
                receiver=receiver,
                start_date=start_date,
                end_date=end_date,
                daily_pay=daily_pay,
                subject=subject,
                permlink=permlink,
                broadcast=broadcast,
                only_result=only_result,
            )

        def decline_voting_rights(self, account, decline, broadcast=None, only_result: bool = True):
            return self.__send(
                "decline_voting_rights", account=account, decline=decline, broadcast=broadcast, only_result=only_result
            )

        def decrypt_memo(self, memo, only_result: bool = True):
            return self.__send("decrypt_memo", memo=memo, only_result=only_result)

        def delegate_rc(self, from_, delegatees, max_rc, broadcast=None, only_result: bool = True):
            return self.__send(
                "delegate_rc",
                from_=from_,
                delegatees=delegatees,
                max_rc=max_rc,
                broadcast=broadcast,
                only_result=only_result,
            )

        def delegate_vesting_shares(
            self, delegator, delegatee, vesting_shares, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "delegate_vesting_shares",
                delegator=delegator,
                delegatee=delegatee,
                vesting_shares=vesting_shares,
                broadcast=broadcast,
                only_result=only_result,
            )

        def delegate_vesting_shares_and_transfer(
            self,
            delegator,
            delegatee,
            vesting_shares,
            transfer_amount,
            transfer_memo,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "delegate_vesting_shares_and_transfer",
                delegator=delegator,
                delegatee=delegatee,
                vesting_shares=vesting_shares,
                transfer_amount=transfer_amount,
                transfer_memo=transfer_memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def delegate_vesting_shares_and_transfer_nonblocking(
            self,
            delegator,
            delegatee,
            vesting_shares,
            transfer_amount,
            transfer_memo,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "delegate_vesting_shares_and_transfer_nonblocking",
                delegator=delegator,
                delegatee=delegatee,
                vesting_shares=vesting_shares,
                transfer_amount=transfer_amount,
                transfer_memo=transfer_memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def delegate_vesting_shares_nonblocking(
            self, delegator, delegatee, vesting_shares, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "delegate_vesting_shares_nonblocking",
                delegator=delegator,
                delegatee=delegatee,
                vesting_shares=vesting_shares,
                broadcast=broadcast,
                only_result=only_result,
            )

        def escrow_approve(self, from_, to, agent, who, escrow_id, approve, broadcast=None, only_result: bool = True):
            return self.__send(
                "escrow_approve",
                from_=from_,
                to=to,
                agent=agent,
                who=who,
                escrow_id=escrow_id,
                approve=approve,
                broadcast=broadcast,
                only_result=only_result,
            )

        def escrow_dispute(self, from_, to, agent, who, escrow_id, broadcast=None, only_result: bool = True):
            return self.__send(
                "escrow_dispute",
                from_=from_,
                to=to,
                agent=agent,
                who=who,
                escrow_id=escrow_id,
                broadcast=broadcast,
                only_result=only_result,
            )

        def escrow_release(
            self,
            from_,
            to,
            agent,
            who,
            receiver,
            escrow_id,
            hbd_amount,
            hive_amount,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "escrow_release",
                from_=from_,
                to=to,
                agent=agent,
                who=who,
                receiver=receiver,
                escrow_id=escrow_id,
                hbd_amount=hbd_amount,
                hive_amount=hive_amount,
                broadcast=broadcast,
                only_result=only_result,
            )

        def escrow_transfer(
            self,
            from_,
            to,
            agent,
            escrow_id,
            hbd_amount,
            hive_amount,
            fee,
            ratification_deadline,
            escrow_expiration,
            json_meta,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "escrow_transfer",
                from_=from_,
                to=to,
                agent=agent,
                escrow_id=escrow_id,
                hbd_amount=hbd_amount,
                hive_amount=hive_amount,
                fee=fee,
                ratification_deadline=ratification_deadline,
                escrow_expiration=escrow_expiration,
                json_meta=json_meta,
                broadcast=broadcast,
                only_result=only_result,
            )

        def estimate_hive_collateral(self, hbd_amount_to_get, only_result: bool = True):
            return self.__send("estimate_hive_collateral", hbd_amount_to_get=hbd_amount_to_get, only_result=only_result)

        def exit(self, only_result: bool = True):
            return self.__send("exit", only_result=only_result)

        def find_proposals(self, proposal_ids, only_result: bool = True):
            return self.__send("find_proposals", proposal_ids=proposal_ids, only_result=only_result)

        def find_rc_accounts(self, accounts, only_result: bool = True):
            return self.__send("find_rc_accounts", accounts=accounts, only_result=only_result)

        def find_recurrent_transfers(self, from_, only_result: bool = True):
            return self.__send("find_recurrent_transfers", from_=from_, only_result=only_result)

        def follow(self, follower, following, what, broadcast=None, only_result: bool = True):
            return self.__send(
                "follow",
                follower=follower,
                following=following,
                what=what,
                broadcast=broadcast,
                only_result=only_result,
            )

        def get_account(self, account_name, only_result: bool = True):
            return self.__send("get_account", account_name=account_name, only_result=only_result)

        def get_account_history(self, account, from_, limit, only_result: bool = True):
            return self.__send(
                "get_account_history", account=account, from_=from_, limit=limit, only_result=only_result
            )

        def get_accounts(self, account_names, only_result: bool = True):
            return self.__send("get_accounts", account_names=account_names, only_result=only_result)

        def get_active_witnesses(self, include_future, only_result: bool = True):
            return self.__send("get_active_witnesses", include_future=include_future, only_result=only_result)

        def get_block(self, num, only_result: bool = True):
            return self.__send("get_block", num=num, only_result=only_result)

        def get_collateralized_conversion_requests(self, owner, only_result: bool = True):
            return self.__send("get_collateralized_conversion_requests", owner=owner, only_result=only_result)

        def get_conversion_requests(self, owner, only_result: bool = True):
            return self.__send("get_conversion_requests", owner=owner, only_result=only_result)

        def get_encrypted_memo(self, from_, to, memo, only_result: bool = True):
            return self.__send("get_encrypted_memo", from_=from_, to=to, memo=memo, only_result=only_result)

        def get_feed_history(self, only_result: bool = True):
            return self.__send("get_feed_history", only_result=only_result)

        def get_open_orders(self, accountname, only_result: bool = True):
            return self.__send("get_open_orders", accountname=accountname, only_result=only_result)

        def get_ops_in_block(self, block_num, only_virtual, only_result: bool = True):
            return self.__send(
                "get_ops_in_block", block_num=block_num, only_virtual=only_virtual, only_result=only_result
            )

        def get_order_book(self, limit, only_result: bool = True):
            return self.__send("get_order_book", limit=limit, only_result=only_result)

        def get_owner_history(self, account, only_result: bool = True):
            return self.__send("get_owner_history", account=account, only_result=only_result)

        def get_private_key(self, pubkey, only_result: bool = True):
            return self.__send("get_private_key", pubkey=pubkey, only_result=only_result)

        def get_private_key_from_password(self, account, role, password, only_result: bool = True):
            return self.__send(
                "get_private_key_from_password", account=account, role=role, password=password, only_result=only_result
            )

        def get_prototype_operation(self, operation_type, only_result: bool = True):
            return self.__send("get_prototype_operation", operation_type=operation_type, only_result=only_result)

        def get_transaction(self, trx_id, only_result: bool = True):
            return self.__send("get_transaction", trx_id=trx_id, only_result=only_result)

        def get_withdraw_routes(self, account, type_, only_result: bool = True):
            return self.__send("get_withdraw_routes", account=account, type_=type_, only_result=only_result)

        def get_witness(self, owner_account, only_result: bool = True):
            return self.__send("get_witness", owner_account=owner_account, only_result=only_result)

        def gethelp(self, method, only_result: bool = True):
            return self.__send("gethelp", method=method, only_result=only_result)

        def help(self, only_result: bool = True):
            return self.__send("help", only_result=only_result)

        def import_key(self, wif_key, only_result: bool = True):
            return self.__send("import_key", wif_key=wif_key, only_result=only_result)

        def import_keys(self, wif_keys, only_result: bool = True):
            return self.__send("import_keys", wif_keys=wif_keys, only_result=only_result)

        def info(self, only_result: bool = True):
            return self.__send("info", only_result=only_result)

        def is_locked(self, only_result: bool = True):
            return self.__send("is_locked", only_result=only_result)

        def is_new(self, only_result: bool = True):
            return self.__send("is_new", only_result=only_result)

        def list_accounts(self, lowerbound, limit, only_result: bool = True):
            return self.__send("list_accounts", lowerbound=lowerbound, limit=limit, only_result=only_result)

        def list_keys(self, only_result: bool = True):
            return self.__send("list_keys", only_result=only_result)

        def list_my_accounts(self, only_result: bool = True):
            return self.__send("list_my_accounts", only_result=only_result)

        def list_proposal_votes(self, start, limit, order_by, order_type, status, only_result: bool = True):
            return self.__send(
                "list_proposal_votes",
                start=start,
                limit=limit,
                order_by=order_by,
                order_type=order_type,
                status=status,
                only_result=only_result,
            )

        def list_proposals(self, start, limit, order_by, order_type, status, only_result: bool = True):
            return self.__send(
                "list_proposals",
                start=start,
                limit=limit,
                order_by=order_by,
                order_type=order_type,
                status=status,
                only_result=only_result,
            )

        def list_rc_accounts(self, account, limit, only_result: bool = True):
            return self.__send("list_rc_accounts", account=account, limit=limit, only_result=only_result)

        def list_rc_direct_delegations(self, start, limit, only_result: bool = True):
            return self.__send("list_rc_direct_delegations", start=start, limit=limit, only_result=only_result)

        def list_witnesses(self, lowerbound, limit, only_result: bool = True):
            return self.__send("list_witnesses", lowerbound=lowerbound, limit=limit, only_result=only_result)

        def load_wallet_file(self, wallet_filename, only_result: bool = True):
            return self.__send("load_wallet_file", wallet_filename=wallet_filename, only_result=only_result)

        def lock(self, only_result: bool = True):
            return self.__send("lock", only_result=only_result)

        def normalize_brain_key(self, s, only_result: bool = True):
            return self.__send("normalize_brain_key", s=s, only_result=only_result)

        def post_comment(
            self,
            author,
            permlink,
            parent_author,
            parent_permlink,
            title,
            body,
            json,
            broadcast=None,
            only_result: bool = True,
        ):
            return self.__send(
                "post_comment",
                author=author,
                permlink=permlink,
                parent_author=parent_author,
                parent_permlink=parent_permlink,
                title=title,
                body=body,
                json=json,
                broadcast=broadcast,
                only_result=only_result,
            )

        def publish_feed(self, witness, exchange_rate, broadcast=None, only_result: bool = True):
            return self.__send(
                "publish_feed",
                witness=witness,
                exchange_rate=exchange_rate,
                broadcast=broadcast,
                only_result=only_result,
            )

        def recover_account(
            self, account_to_recover, recent_authority, new_authority, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "recover_account",
                account_to_recover=account_to_recover,
                recent_authority=recent_authority,
                new_authority=new_authority,
                broadcast=broadcast,
                only_result=only_result,
            )

        def recurrent_transfer(
            self, from_, to, amount, memo, recurrence, executions, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "recurrent_transfer",
                from_=from_,
                to=to,
                amount=amount,
                memo=memo,
                recurrence=recurrence,
                executions=executions,
                broadcast=broadcast,
                only_result=only_result,
            )

        def recurrent_transfer_with_id(
            self, from_, to, amount, memo, recurrence, executions, pair_id, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "recurrent_transfer_with_id",
                from_=from_,
                to=to,
                amount=amount,
                memo=memo,
                recurrence=recurrence,
                executions=executions,
                pair_id=pair_id,
                broadcast=broadcast,
                only_result=only_result,
            )

        def remove_proposal(self, deleter, ids, broadcast=None, only_result: bool = True):
            return self.__send(
                "remove_proposal", deleter=deleter, ids=ids, broadcast=broadcast, only_result=only_result
            )

        def request_account_recovery(
            self, recovery_account, account_to_recover, new_authority, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "request_account_recovery",
                recovery_account=recovery_account,
                account_to_recover=account_to_recover,
                new_authority=new_authority,
                broadcast=broadcast,
                only_result=only_result,
            )

        def save_wallet_file(self, wallet_filename, only_result: bool = True):
            return self.__send("save_wallet_file", wallet_filename=wallet_filename, only_result=only_result)

        def serialize_transaction(self, tx, only_result: bool = True):
            return self.__send("serialize_transaction", tx=tx, only_result=only_result)

        def set_password(self, password, only_result: bool = True):
            return self.__send("set_password", password=password, only_result=only_result)

        def set_transaction_expiration(self, seconds, only_result: bool = True):
            return self.__send("set_transaction_expiration", seconds=seconds, only_result=only_result)

        def set_voting_proxy(self, account_to_modify, proxy, broadcast=None, only_result: bool = True):
            return self.__send(
                "set_voting_proxy",
                account_to_modify=account_to_modify,
                proxy=proxy,
                broadcast=broadcast,
                only_result=only_result,
            )

        def set_withdraw_vesting_route(self, from_, to, percent, auto_vest, broadcast=None, only_result: bool = True):
            return self.__send(
                "set_withdraw_vesting_route",
                from_=from_,
                to=to,
                percent=percent,
                auto_vest=auto_vest,
                broadcast=broadcast,
                only_result=only_result,
            )

        def sign_transaction(self, tx, broadcast=None, only_result: bool = True):
            return self.__send("sign_transaction", tx=tx, broadcast=broadcast, only_result=only_result)

        def suggest_brain_key(self, only_result: bool = True):
            return self.__send("suggest_brain_key", only_result=only_result)

        def transfer(self, from_, to, amount, memo, broadcast=None, only_result: bool = True):
            return self.__send(
                "transfer", from_=from_, to=to, amount=amount, memo=memo, broadcast=broadcast, only_result=only_result
            )

        def transfer_from_savings(self, from_, request_id, to, amount, memo, broadcast=None, only_result: bool = True):
            return self.__send(
                "transfer_from_savings",
                from_=from_,
                request_id=request_id,
                to=to,
                amount=amount,
                memo=memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def transfer_nonblocking(self, from_, to, amount, memo, broadcast=None, only_result: bool = True):
            return self.__send(
                "transfer_nonblocking",
                from_=from_,
                to=to,
                amount=amount,
                memo=memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def transfer_to_savings(self, from_, to, amount, memo, broadcast=None, only_result: bool = True):
            return self.__send(
                "transfer_to_savings",
                from_=from_,
                to=to,
                amount=amount,
                memo=memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def transfer_to_vesting(self, from_, to, amount, broadcast=None, only_result: bool = True):
            return self.__send(
                "transfer_to_vesting", from_=from_, to=to, amount=amount, broadcast=broadcast, only_result=only_result
            )

        def transfer_to_vesting_nonblocking(self, from_, to, amount, broadcast=None, only_result: bool = True):
            return self.__send(
                "transfer_to_vesting_nonblocking",
                from_=from_,
                to=to,
                amount=amount,
                broadcast=broadcast,
                only_result=only_result,
            )

        def unlock(self, password, only_result: bool = True):
            return self.__send("unlock", password=password, only_result=only_result)

        def update_account(
            self, accountname, json_meta, owner, active, posting, memo, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "update_account",
                accountname=accountname,
                json_meta=json_meta,
                owner=owner,
                active=active,
                posting=posting,
                memo=memo,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_account_auth_account(
            self, account_name, type_, auth_account, weight, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "update_account_auth_account",
                account_name=account_name,
                type_=type_,
                auth_account=auth_account,
                weight=weight,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_account_auth_key(self, account_name, type_, key, weight, broadcast=None, only_result: bool = True):
            return self.__send(
                "update_account_auth_key",
                account_name=account_name,
                type_=type_,
                key=key,
                weight=weight,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_account_auth_threshold(
            self, account_name, type_, threshold, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "update_account_auth_threshold",
                account_name=account_name,
                type_=type_,
                threshold=threshold,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_account_memo_key(self, account_name, key, broadcast=None, only_result: bool = True):
            return self.__send(
                "update_account_memo_key",
                account_name=account_name,
                key=key,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_account_meta(self, account_name, json_meta, broadcast=None, only_result: bool = True):
            return self.__send(
                "update_account_meta",
                account_name=account_name,
                json_meta=json_meta,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_proposal(
            self, proposal_id, creator, daily_pay, subject, permlink, end_date, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "update_proposal",
                proposal_id=proposal_id,
                creator=creator,
                daily_pay=daily_pay,
                subject=subject,
                permlink=permlink,
                end_date=end_date,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_proposal_votes(self, voter, proposals, approve, broadcast=None, only_result: bool = True):
            return self.__send(
                "update_proposal_votes",
                voter=voter,
                proposals=proposals,
                approve=approve,
                broadcast=broadcast,
                only_result=only_result,
            )

        def update_witness(self, witness_name, url, block_signing_key, props, broadcast=None, only_result: bool = True):
            return self.__send(
                "update_witness",
                witness_name=witness_name,
                url=url,
                block_signing_key=block_signing_key,
                props=props,
                broadcast=broadcast,
                only_result=only_result,
            )

        def use_authority(self, type_, account_name, only_result: bool = True):
            return self.__send("use_authority", type_=type_, account_name=account_name, only_result=only_result)

        def use_automatic_authority(self, only_result: bool = True):
            return self.__send("use_automatic_authority", only_result=only_result)

        def vote(self, voter, author, permlink, weight, broadcast=None, only_result: bool = True):
            return self.__send(
                "vote",
                voter=voter,
                author=author,
                permlink=permlink,
                weight=weight,
                broadcast=broadcast,
                only_result=only_result,
            )

        def vote_for_witness(
            self, account_to_vote_with, witness_to_vote_for, approve, broadcast=None, only_result: bool = True
        ):
            return self.__send(
                "vote_for_witness",
                account_to_vote_with=account_to_vote_with,
                witness_to_vote_for=witness_to_vote_for,
                approve=approve,
                broadcast=broadcast,
                only_result=only_result,
            )

        def withdraw_vesting(self, from_, vesting_shares, broadcast=None, only_result: bool = True):
            return self.__send(
                "withdraw_vesting",
                from_=from_,
                vesting_shares=vesting_shares,
                broadcast=broadcast,
                only_result=only_result,
            )

        # End of machine generated code

    def __init__(
        self,
        *,
        attach_to: None | Node | RemoteNode,
        additional_arguments: Iterable = (),
        preconfigure: bool = True,
        handle: OldWalletHandle | None = None,
        time_control: str | None = None,
    ):
        super().__init__(handle=handle)

        self.api = OldWallet.Api(self)
        self.http_server_port = None
        self.connected_node: None | Node | RemoteNode = attach_to
        self.password = None

        if isinstance(self.connected_node, Node):
            self.name = context.names.register_numbered_name(f"{self.connected_node}.OldWallet")
            self.directory = self.connected_node.directory.parent / self.name
            self.connected_node.register_wallet(self)
        elif isinstance(self.connected_node, RemoteNode):
            self.name = context.names.register_numbered_name(f"{self.connected_node}.OldWallet")
            self.directory = context.get_current_directory() / self.name
        else:
            self.name = context.names.register_numbered_name("OldWallet")
            self.directory = context.get_current_directory() / self.name

        self.executable_file_path = None
        self.stdout_file = None
        self.stderr_file = None
        self.process = None
        self.additional_arguments = list(additional_arguments)
        self.__produced_files = False
        self.logger = logger.bind(target="cli_wallet")

        self.run(preconfigure=preconfigure, time_control=time_control)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def get_stdout_file_path(self) -> Path:
        return self.directory / "stdout.log"

    def get_stderr_file_path(self) -> Path:
        return self.directory / "stderr.log"

    def is_running(self):
        if not self.process:
            return False

        return self.process.poll() is None

    def __is_ready(self):
        with open(self.get_stderr_file_path(), encoding="utf-8") as file:
            for line in file:
                if "Entering Daemon Mode, ^C to exit" in line:
                    return True

        return False

    def run(
        self,
        timeout: float = DEFAULT_RUN_TIMEOUT,
        *,
        preconfigure: bool = True,
        clean: bool | None = None,
        time_control: str | None = None,
    ):
        """
        Starts wallet. Blocks until wallet will be ready for use.

        :param timeout: TimeoutError will be raised, if wallet won't start before specified timeout.
        :param preconfigure: If set to True, wallet will be unlocked with password OldWallet.DEFAULT_PASSWORD and initminer
                             key imported.
        :param clean: If set to True, wallet directory with all its files will be removed before run.
        :param time_control: Allows to change system date and time a node sees (without changing real OS time).
            Can be specified either absolutely, relatively and speed up or slow down clock. Value passed in
            `time_control` is written to `FAKETIME` environment variable. For details and examples see libfaketime
            official documentation: https://github.com/wolfcw/libfaketime.
        """
        run_parameters = [
            "--daemon",
            "--rpc-http-allowip=127.0.0.1",
        ]

        if self.is_running():
            raise RuntimeError("OldWallet is already running")

        if not self.executable_file_path:
            self.executable_file_path = paths_to_executables.get_path_of("cli_wallet")

        if self.__is_online():
            if not self.connected_node.is_running():
                raise NodeIsNotRunningError("Before attaching wallet you have to run node")
        else:
            run_parameters.append("--offline")

        if not self.http_server_port:
            self.http_server_port = 0

        run_parameters.extend([f"--rpc-http-endpoint=0.0.0.0:{self.http_server_port}"])

        if clean is None:
            # If wallet is run the first time, by default should remove files,
            # because they were generated in previous test run and are outdated.
            clean = not self.__produced_files

        if clean:
            shutil.rmtree(self.directory, ignore_errors=True)

        self.directory.mkdir(parents=True, exist_ok=True)

        # Files opened here have to exist longer than current scope
        self.stdout_file = open(self.get_stdout_file_path(), "w", encoding="utf-8")
        self.stderr_file = open(self.get_stderr_file_path(), "w", encoding="utf-8")

        retry_server_connection_delay = 1

        if self.__is_online():
            run_parameters.extend(
                [
                    f"--server-rpc-endpoint={self.connected_node.get_ws_endpoint().as_string(with_protocol=True)}",
                    "--retry-server-connection",
                    f"--retry-server-connection-delay={retry_server_connection_delay}",
                ]
            )

        run_parameters.extend(self.additional_arguments)

        command = [str(self.executable_file_path), *run_parameters]
        self.logger.debug(" ".join(item for item in command))

        environment_variables = dict(os.environ)

        if time_control is not None:
            environment_variables.update(configure_fake_time(self.logger, time_control))

        # Process created here have to exist longer than current scope
        self.process = subprocess.Popen(
            command, cwd=self.directory, stdout=self.stdout_file, stderr=self.stderr_file, env=environment_variables
        )

        self.__produced_files = True

        # Assuming that:
        #   timeout = DEFAULT_RUN_TIMEOUT       = 15s
        #   retry-server-connection is ENABLED
        #   retry_server_connection_delay       = 1s
        #   internal timeout of c++ websocket   = 5s (take a look at `timeout_pong` in {websocketpp library}/websocketpp/config/core.hpp)
        # we have 3 attempts of establishing connection wallet<->node, because:
        #   try-connect(5s) + retry_server_connection_delay(1s) + try-connect(5s) + retry_server_connection_delay(1s) + try-connect(here only 3s) == DEFAULT_RUN_TIMEOUT

        timeout -= Time.wait_for(
            self.__is_ready, timeout=timeout, timeout_error_message=f"{self} was not ready on time.", poll_time=0.1
        )

        endpoint = self.__get_http_server_endpoint()
        self.http_server_port = endpoint.split(":")[1]

        if self.__is_online():
            timeout -= Time.wait_for(
                self.__is_communication_established,
                timeout=timeout,
                timeout_error_message=(
                    f"Problem with starting wallet. See {self.get_stderr_file_path()} for more details."
                ),
            )

        if preconfigure:
            password = self.DEFAULT_PASSWORD

            if not self.__is_password_set():
                self.api.set_password(password)

            self.api.unlock(password)
            self.api.import_key(Account("initminer").private_key)

        self.logger.info(f'Started{"" if self.__is_online() else " in offline mode"}, listening on {endpoint}')

    def __is_online(self) -> bool:
        return self.connected_node is not None

    @property
    def transaction_serialization(self) -> Literal["legacy", "hf26"]:
        parser = ArgumentParser()
        parser.add_argument(
            "--transaction-serialization",
            choices=["legacy", "hf26"],
            required=False,
            default=self.DEFAULT_TRANSACTION_SERIALIZATION,
        )
        arguments, _ = parser.parse_known_args(self.additional_arguments)
        return arguments.transaction_serialization

    def __is_communication_established(self):
        try:
            self.api.info()
        except CommunicationError:
            return False
        return True

    def __get_http_server_endpoint(self):
        with self.get_stderr_file_path().open(encoding="utf-8") as output:
            for line in output:
                if "Listening for incoming HTTP RPC requests on" in line:
                    endpoint = re.match(r"^.*Listening for incoming HTTP RPC requests on ([\d\.]+\:\d+)\s*$", line)[1]
                    endpoint = endpoint.replace("0.0.0.0", "127.0.0.1")
                    self.logger.info(f"from stderr: wallet listening endpoint is: {endpoint}")
                    return endpoint
        return None

    def __is_password_set(self) -> bool:
        return not self.api.is_new()

    def connect_to(self, node):
        self.connected_node.unregister_wallet(self)
        self.connected_node = node
        self.connected_node.register_wallet(self)

    def at_exit_from_scope(self):
        self.close()

    def restart(self, *, preconfigure=True, time_control: str | None = None):
        self.close()
        self.run(preconfigure=preconfigure, clean=False, time_control=time_control)

    def close(self) -> None:
        self.__close_process()
        self.__close_opened_files()
        self.http_server_port = None

    def __close_process(self):
        if self.process is None:
            return

        self.process.send_signal(signal.SIGINT)
        try:
            return_code = self.process.wait(timeout=3)
            self.logger.debug(f"Closed with {return_code} return code")
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
            self.logger.warning("Process was force-closed with SIGKILL, because didn't close before timeout")
        finally:
            self.process = None

    def __close_opened_files(self):
        for file_handle, file_path in [
            (self.stdout_file, self.get_stdout_file_path()),
            (self.stderr_file, self.get_stderr_file_path()),
        ]:
            if file_handle is not None:
                file_handle.close()
                if not file_path.exists():
                    logger.warning(f"closed file does not exists: {file_path.as_posix()}")
                amount_of_history_files = len(list(file_path.parent.glob(pattern=file_path.name + ".*")))
                file_path.rename(file_path.with_stem(file_path.name + f"_{amount_of_history_files}"))

        self.stdout_file = None
        self.stderr_file = None

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
        def send_transaction(accounts_):
            # Prepare transaction
            transaction = copy.deepcopy(transaction_pattern)

            for account in accounts_:
                operation = copy.deepcopy(operation_pattern)

                operation[1]["new_account_name"] = account.name
                operation[1]["memo_key"] = account.public_key
                for key_type in ("owner", "active", "posting"):
                    operation[1][key_type]["key_auths"] = [[account.public_key, 1]]

                transaction["operations"].append(operation)

            # Send transaction
            while True:
                response = self.api.sign_transaction(transaction)

                # Ensure that accounts exists
                if accounts_[0].name in self.api.list_accounts(accounts_[0].name, 1):
                    self.logger.debug(f"Accounts created: {accounts_[0].name}..{accounts_[-1].name}")
                    return response

                self.logger.debug(
                    f"Node ignored create accounts request of accounts "
                    f"{accounts_[0].name}..{accounts_[-1].name}, requesting again..."
                )

        accounts = Account.create_multiple(number_of_accounts, name_base, secret=secret)

        transaction_pattern = self.api.create_account_with_keys(
            "initminer", accounts[0].name, "{}", *(4 * [accounts[0].public_key]), broadcast=False
        )

        operation_pattern: Final = transaction_pattern["operations"][0]
        transaction_pattern["operations"].clear()

        accounts_per_transaction: Final = 500
        max_threads: Final = 24
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(math.ceil(number_of_accounts / accounts_per_transaction), max_threads)
        ) as executor:
            futures = []
            for i in range(0, len(accounts), accounts_per_transaction):
                futures.append(executor.submit(send_transaction, accounts[i : i + accounts_per_transaction]))

        for future in futures:
            future.result()

        if import_keys:
            private_keys_per_transaction: Final = 10_000
            for i in range(0, len(accounts), private_keys_per_transaction):
                self.api.import_keys(
                    [account.private_key for account in accounts[i : i + private_keys_per_transaction]]
                )

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

    def set_executable_file_path(self, executable_file_path):
        self.executable_file_path = executable_file_path

    def set_http_server_port(self, port):
        self.http_server_port = port

    def send(self, method, *params, jsonrpc="2.0", id_=0):
        endpoint = f"http://127.0.0.1:{self.http_server_port}"
        message = {
            "jsonrpc": jsonrpc,
            "id": id_,
            "method": method,
            "params": list(params),
        }
        return communication.request(endpoint, message, self.__use_nai_assets)

    @property
    def __use_nai_assets(self) -> bool:
        return "--transaction-serialization=hf26" in self.additional_arguments

    def in_single_transaction(self, *, broadcast=None) -> SingleTransactionContext:
        return SingleTransactionContext(self, broadcast=broadcast)


class SingleTransactionContext(SelfContextSync):
    def __init__(self, wallet_: OldWallet, *, broadcast):
        self.__wallet = wallet_
        self.__broadcast = broadcast
        self.__response = None
        self.__was_run_as_context_manager = False

    def get_response(self):
        return self.__response

    def __del__(self):
        if not self.__was_run_as_context_manager:
            raise RuntimeError(
                f'You used {OldWallet.__name__}.{OldWallet.in_single_transaction.__name__}() not in "with" statement'
            )

    def _enter(self) -> Self:
        self.__wallet.api._start_gathering_operations_for_single_transaction()
        self.__was_run_as_context_manager = True
        return self

    def _finally(self) -> None:
        self.__response = self.__wallet.api._send_gathered_operations_as_single_transaction(broadcast=self.__broadcast)
