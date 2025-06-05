from __future__ import annotations

import concurrent
import concurrent.futures
import os
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from loguru import logger

from schemas.fields.assets import AssetHive
from schemas.fields.assets._base import AssetNaiAmount
from schemas.fields.compound import Authority
from schemas.fields.hive_int import HiveInt
from schemas.operations.account_create_operation import AccountCreateOperation
from test_tools.__private.account import Account
from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.wallet.constants import (
    ACCOUNT_PER_TRANSACTION,
    MULTIPLE_IMPORT_KEYS_BATCH_SIZE,
    SimpleTransaction,
    WalletResponseBase,
)
from test_tools.__private.wax_wrapper import (
    calculate_sig_digest,
    calculate_transaction_id,
    get_tapos_data,
    validate_transaction,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from beekeepy import Beekeeper, PackedSyncBeekeeper
    from beekeepy._interface.abc.synchronous.wallet import UnlockedWallet
    from beekeepy.interfaces import HttpUrl

    from schemas.fields.basic import PublicKey
    from schemas.operations import Hf26Operations
    from test_tools.__private.node import Node

    AnyNode = Node | RemoteNode


def get_authority(key: PublicKey | str) -> Authority:
    return Authority(weight_threshold=1, account_auths=[], key_auths=[(key, 1)])


def generate_transaction_template(node: RemoteNode) -> SimpleTransaction:
    gdpo = node.api.database.get_dynamic_global_properties()
    block_id = gdpo.head_block_id

    # set header
    tapos_data = get_tapos_data(block_id)
    ref_block_num = tapos_data.ref_block_num
    ref_block_prefix = tapos_data.ref_block_prefix

    assert ref_block_num >= 0, f"ref_block_num value `{ref_block_num}` is invalid`"
    assert ref_block_prefix > 0, f"ref_block_prefix value `{ref_block_prefix}` is invalid`"

    return SimpleTransaction(
        ref_block_num=HiveInt(ref_block_num),
        ref_block_prefix=HiveInt(ref_block_prefix),
        expiration=gdpo.time + timedelta(seconds=1800),
        extensions=[],
        signatures=[],
        operations=[],
    )


def sign_transaction(
    node: RemoteNode, transaction: SimpleTransaction, beekeeper_wallet: UnlockedWallet
) -> SimpleTransaction:
    calculate_transaction_id(transaction)
    node_config = node.api.database.get_config()

    sig_digest = calculate_sig_digest(transaction, node_config.HIVE_CHAIN_ID)
    key_to_sign_with = beekeeper_wallet.import_key(private_key=Account("initminer").private_key)

    time_before = datetime.now()
    signature = beekeeper_wallet.sign_digest(sig_digest=sig_digest, key=key_to_sign_with)
    logger.info(f"Sign digest time: {datetime.now() - time_before}")

    transaction.signatures.append(signature)

    transaction.signatures = list(set(transaction.signatures))
    validate_transaction(transaction)

    return transaction


def prepare_transaction(
    operations: list[Hf26Operations], node: RemoteNode, beekeeper_wallet: UnlockedWallet
) -> WalletResponseBase:
    transaction = generate_transaction_template(node)

    account_creation_fee = node.api.wallet_bridge.get_chain_properties().account_creation_fee

    for operation in operations:
        if isinstance(operation, AccountCreateOperation):
            operation.fee = account_creation_fee
        transaction.add_operation(operation)
    transaction = sign_transaction(node, transaction, beekeeper_wallet)

    return WalletResponseBase(
        transaction_id=calculate_transaction_id(transaction),
        ref_block_num=transaction.ref_block_num,
        ref_block_prefix=transaction.ref_block_prefix,
        expiration=transaction.expiration,
        extensions=transaction.extensions,
        signatures=transaction.signatures,
        operations=transaction.operations,
    )


def send_transaction(  # noqa: C901
    accounts_: list[Account],
    packed_beekeeper: PackedSyncBeekeeper,
    node_address: HttpUrl,
    beekeeper_wallet_name: str,
    beekeeper_wallet_password: str,
) -> None:
    def retry_until_success(predicate: Callable[[], Any], *, fail_message: str, max_retries: int = 20) -> bool:
        retries = 0
        while retries <= max_retries:
            try:
                predicate()
            except Exception as e:  # noqa: BLE001
                logger.error(f"{fail_message} ; {e}")
                retries += 1
            else:
                return True
        return False

    def ensure_accounts_exists() -> None:
        listed_accounts = node.api.wallet_bridge.list_accounts(accounts_[0].name, 1)
        logger.info(listed_accounts)
        if accounts_[0].name in listed_accounts:
            logger.debug(f"Accounts created: {accounts_range_message}")

    def broadcast_transaction(
        operations: list[Hf26Operations], node: RemoteNode, beekeeper_wallet: UnlockedWallet
    ) -> bool:
        def prepare_and_broadcast() -> None:
            trx = prepare_transaction(operations, node, beekeeper_wallet)
            with node.restore_settings():
                node.settings.timeout = timedelta(hours=1)
                node.api.wallet_bridge.broadcast_transaction_synchronous(trx)

        return retry_until_success(
            prepare_and_broadcast,
            fail_message=f"Failed to send transaction: {accounts_range_message}",
        )

    operations: list[Hf26Operations] = []
    beekeeper = packed_beekeeper.unpack()
    node = RemoteNode(http_endpoint=node_address)

    accounts_range_message = f"{accounts_[0].name}..{accounts_[-1].name}"
    for account in accounts_:
        operation = AccountCreateOperation(
            creator="initminer",
            new_account_name=account.name,
            json_metadata="{}",
            fee=AssetHive(AssetNaiAmount(1)),
            owner=get_authority(account.public_key),
            active=get_authority(account.public_key),
            posting=get_authority(account.public_key),
            memo_key=account.public_key,
        )

        operations.append(operation)

    # Send transaction
    with beekeeper.create_session() as session:
        beekeeper_wallet = session.open_wallet(name=beekeeper_wallet_name)
        beekeeper_wallet = beekeeper_wallet.unlock(beekeeper_wallet_password)

        while True:
            if not broadcast_transaction(operations, node, beekeeper_wallet):
                continue

            if retry_until_success(
                ensure_accounts_exists,
                fail_message=f"Node ignored create accounts request of accounts {accounts_range_message}, requesting again...",
                max_retries=5,
            ):
                return


def create_accounts(
    beekeeper: Beekeeper,
    node: AnyNode,
    beekeeper_wallet_name: str,
    beekeeper_wallet_password: str,
    number_of_accounts: int,
    import_keys: bool,
    name_base: str = "account",
    *,
    secret: str = "secret",
) -> list[Account]:
    def run_in_thread_pool_executor(
        predicate: Callable[..., Any],
        iterable_args: list[Any],
        packed_beekeeper: PackedSyncBeekeeper,
        node_address: HttpUrl,
        beekeeper_wallet_name: str,
        beekeeper_wallet_password: str,
        *,
        max_threads: int = (os.cpu_count() or 24),
    ) -> None:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_threads) as executor:
            futures: list[concurrent.futures.Future[Any]] = []
            for args in iterable_args:
                futures.append(
                    executor.submit(
                        predicate,
                        args,
                        packed_beekeeper,
                        node_address,
                        beekeeper_wallet_name,
                        beekeeper_wallet_password,
                    )
                )

            start = time.perf_counter()
            while (
                len((tasks := concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED))[0]) > 0
            ):
                task = tasks[0].pop()
                futures.pop(futures.index(task))
                logger.debug(f"Joined next item after {(time.perf_counter() - start) :.4f} seconds...")
                start = time.perf_counter()

                if (exc := task.exception()) is not None:
                    logger.error(f"got {exc=}")
                    raise exc

    def split(
        collection: list[Any], items_per_chunk: int, *, predicate: Callable[[Any], Any] = lambda x: x
    ) -> list[Any]:
        return [
            [predicate(item) for item in collection[i : i + items_per_chunk]]
            for i in range(0, len(collection), items_per_chunk)
        ]

    packed_beekeeper = beekeeper.pack()

    accounts = Account.create_multiple(number_of_accounts, name_base, secret=secret)
    run_in_thread_pool_executor(
        send_transaction,
        split(accounts, ACCOUNT_PER_TRANSACTION, predicate=lambda x: x.safe()),
        packed_beekeeper,
        node.http_endpoint,
        beekeeper_wallet_name,
        beekeeper_wallet_password,
    )

    with beekeeper.create_session() as session:
        beekeeper_wallet = session.open_wallet(name=beekeeper_wallet_name)
        beekeeper_wallet = beekeeper_wallet.unlock(beekeeper_wallet_password)
        if import_keys:
            keys: list[str] = []
            for account in accounts:
                keys.append(str(account.private_key))

            num_keys = len(keys)

            for i in range(0, num_keys, MULTIPLE_IMPORT_KEYS_BATCH_SIZE):
                batch_keys = keys[i : i + MULTIPLE_IMPORT_KEYS_BATCH_SIZE]
                time1 = datetime.now()
                beekeeper_wallet.import_keys(private_keys=batch_keys)
                time2 = datetime.now()
                logger.info(f"Import time: {time2-time1}")

    return accounts
