from datetime import datetime, timedelta
import os
import time
from typing import Any, Callable, Final

from loguru import logger
from beekeepy import PackedBeekeeper
from beekeepy._interface.synchronous.beekeeper import Beekeeper
from beekeepy._interface.synchronous.wallet import UnlockedWallet
import helpy
from helpy._interfaces.asset.asset import Asset
from schemas.fields.basic import PublicKey
from schemas.fields.hive_int import HiveInt
from schemas.operations import AnyOperation
from schemas.operations.account_create_operation import AccountCreateOperation
from schemas.operations.representations.hf26_representation import HF26Representation
from schemas.transaction import Transaction
from test_tools.__private.account import Account
from test_tools.__private.remote_node import RemoteNode
import concurrent

from test_tools.__private.type_annotations.any_node import AnyNode
from helpy import wax as wax_helpy
import wax


class SimpleTransaction(Transaction):  # OUT
    def add_operation(self, operation: AnyOperation) -> None:
        self.operations.append(HF26Representation(type=operation.get_name_with_suffix(), value=operation))


class WalletResponseBase(SimpleTransaction):  # OUT
    transaction_id: str


def get_authority(key: str) -> dict:
    return {"weight_threshold": 1, "account_auths": [], "key_auths": [[key, 1]]}


def generate_transaction_template(node: AnyNode) -> SimpleTransaction:
    gdpo = node.api.database.get_dynamic_global_properties()
    if isinstance(gdpo, dict | list):
        logger.error(gdpo)
        raise Exception(gdpo)

    block_id = gdpo.head_block_id

    # set header
    tapos_data = wax.get_tapos_data(block_id.encode())  # type: ignore[no-any-return]
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
    node: AnyNode, transaction: SimpleTransaction, beekeeper_wallet: UnlockedWallet
) -> SimpleTransaction:
    wax_helpy.calculate_transaction_id(transaction=transaction)
    node_config = node.api.database.get_config()
    if isinstance(node_config, dict | list):
        logger.error(node_config)
        raise Exception(node_config)

    sig_digest = wax_helpy.calculate_sig_digest(transaction, node_config.HIVE_CHAIN_ID)
    key_to_sign_with = beekeeper_wallet.import_key(private_key=Account("initminer").private_key)

    time_before = datetime.now()
    signature = beekeeper_wallet.sign_digest(sig_digest=sig_digest, key=key_to_sign_with)
    logger.info(f"Czas podpisu: {datetime.now() - time_before}")

    transaction.signatures.append(signature)

    transaction.signatures = list(set(transaction.signatures))

    wax_helpy.validate_transaction(transaction)

    return transaction


def prepare_transaction(
    operations: list[AnyOperation], node: AnyNode, beekeeper_wallet: UnlockedWallet
) -> WalletResponseBase:
    transaction = generate_transaction_template(node)
    for operation in operations:
        transaction.add_operation(operation)
    transaction = sign_transaction(node, transaction, beekeeper_wallet)

    return WalletResponseBase(
        transaction_id=wax_helpy.calculate_transaction_id(transaction=transaction),
        ref_block_num=transaction.ref_block_num,
        ref_block_prefix=transaction.ref_block_prefix,
        expiration=transaction.expiration,
        extensions=transaction.extensions,
        signatures=transaction.signatures,
        operations=transaction.operations,
    )


def send_transaction(
    accounts_: list[Account],
    packed_beekeeper: PackedBeekeeper,
    node_address: helpy.HttpUrl,
    beekeeper_wallet_name: str,
    beekeeper_wallet_password: str,
    import_keys: bool,
):
    def retry_until_success(predicate: Callable[[], Any], *, fail_message: str, max_retries: int = 20) -> bool:
        retries = 0
        while retries <= max_retries:
            try:
                predicate()
                return True
            except:
                logger.error(fail_message)
                retries += 1
        return False

    def ensure_accounts_exists() -> None:
        listed_accounts = node.api.wallet_bridge.list_accounts(accounts_[0].name, 1)
        logger.info(listed_accounts)
        if accounts_[0].name in listed_accounts:
            logger.debug(f"Accounts created: {accounts_range_message}")

    def broadcast_transaction(operations: list, node: AnyNode, beekeeper_wallet: UnlockedWallet) -> bool:
        trx = prepare_transaction(operations, node, beekeeper_wallet)
        return retry_until_success(
            lambda: node.api.network_broadcast.broadcast_transaction(trx=trx),
            fail_message=f"Failed to send transaction: {accounts_range_message}",
        )

    operations = []
    beekeeper = packed_beekeeper.unpack()
    node = RemoteNode(http_endpoint=node_address)

    accounts_range_message = f"{accounts_[0].name}..{accounts_[-1].name}"
    for account in accounts_:
        operation = AccountCreateOperation(
            creator="initminer",
            new_account_name=account.name,
            json_metadata="{}",
            fee=Asset.Test(0).as_nai(),
            owner=get_authority(account.public_key),
            active=get_authority(account.public_key),
            posting=get_authority(account.public_key),
            memo_key=account.public_key,
        )  # type: ignore

        operations.append(operation)

    # Send transaction
    with beekeeper.create_session() as session:
        beekeeper_wallet = session.open_wallet(name=beekeeper_wallet_name)
        beekeeper_wallet = beekeeper_wallet.unlock(beekeeper_wallet_password)
        if import_keys:
            keys = []
            for account in accounts_:
                keys.append(account.private_key)
            beekeeper_wallet.import_keys(private_keys=keys)

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
        predicate: Callable[[Any], Any],
        iterable_args: list[Any],
        packed_beekeeper: PackedBeekeeper,
        node_address: helpy.HttpUrl,
        beekeeper_wallet_name: str,
        beekeeper_wallet_password: str,
        import_keys: bool,
        *,
        max_threads=(os.cpu_count() or 24),
    ) -> None:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_threads) as executor:
            futures: list[concurrent.futures.Future] = []
            for args in iterable_args:
                futures.append(
                    executor.submit(
                        predicate,
                        args,
                        packed_beekeeper,
                        node_address,
                        beekeeper_wallet_name,
                        beekeeper_wallet_password,
                        import_keys,
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

    accounts_per_transaction: Final[int] = 500
    packed_beekeeper = beekeeper.pack()

    accounts = Account.create_multiple(number_of_accounts, name_base, secret=secret)
    run_in_thread_pool_executor(
        send_transaction,
        split(accounts, accounts_per_transaction),
        packed_beekeeper,
        node.http_endpoint,
        beekeeper_wallet_name,
        beekeeper_wallet_password,
        import_keys,
    )

    return accounts
