from __future__ import annotations

import shutil
import warnings
from datetime import timedelta
from typing import TYPE_CHECKING, Any, get_args

from beekeepy import Beekeeper, Settings

import helpy
import wax
from helpy import Hf26Asset as Asset
from helpy import wax as wax_helpy
from schemas.fields.basic import PublicKey
from schemas.fields.hex import Hex
from schemas.fields.hive_int import HiveInt
from test_tools.__private import exceptions
from test_tools.__private.account import Account
from test_tools.__private.node import Node
from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.scope import ScopedObject, context
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation
from test_tools.__private.wallet.constants import (
    DEFAULT_PASSWORD,
    AuthorityType,
    SimpleTransaction,
    TransactionSerializationTypes,
    WalletResponse,
    WalletResponseBase,
)
from test_tools.__private.wallet.create_accounts import (
    create_accounts,
)
from test_tools.__private.wallet.single_transaction_context import SingleTransactionContext
from test_tools.__private.wallet.wallet_api import Api

if TYPE_CHECKING:
    from pathlib import Path

    from beekeepy._interface.abc.synchronous.session import Session
    from beekeepy._interface.abc.synchronous.wallet import UnlockedWallet

    from schemas.apis.wallet_bridge_api.fundaments_of_responses import Account as AccountSchema
    from schemas.fields.assets.hbd import AssetHbdHF26
    from schemas.fields.assets.hive import AssetHiveHF26
    from schemas.fields.assets.vests import AssetVestsHF26
    from schemas.fields.compound import Authority
    from schemas.operations import AnyOperation
    from test_tools.__private.user_handles.handles.wallet_handle import WalletHandle

    AnyNode = Node | RemoteNode


class Wallet(UserHandleImplementation, ScopedObject):
    def __init__(
        self,
        *,
        attach_to: None | AnyNode,
        preconfigure: bool = True,
        chain_id: str = "default",
        transaction_serialization: TransactionSerializationTypes = "hf26",
        handle: WalletHandle | None = None,
    ):
        super().__init__(handle=handle)

        self.api = Api(self)
        self.connected_node: None | AnyNode = attach_to
        self.__chain_id: str = chain_id
        self._transaction_serialization: str = transaction_serialization
        assert self._transaction_serialization in get_args(
            TransactionSerializationTypes
        ), "Invalid transaction_serialization parameter value"
        self._use_authority: dict[str, AuthorityType] = {}
        self.__beekeeper: Beekeeper | None = None
        self.__beekeeper_session: Session | None = None
        self._beekeeper_wallet: UnlockedWallet | None = None
        self._transaction_expiration_offset = timedelta(seconds=30)
        self.__prepare_directory()
        self.run(preconfigure=preconfigure)
        if (
            self.connected_node is not None
            and self._transaction_serialization == "legacy"
            and self.connected_node.api.database.get_version().node_type == "testnet"
        ):
            warnings.warn("Wallet in legacy mode may not work correctly with the testnet hive instance.", stacklevel=1)

    @property
    def _force_connected_node(self) -> AnyNode:
        assert self.connected_node is not None, "Node not exist"
        return self.connected_node

    def __get_chain_id(self) -> Hex:
        node_config = self._force_connected_node.api.database.get_config()
        if self.__chain_id != "default":
            assert self.__chain_id.isdigit(), "Invalid chain_id value: it must be a digit string"
            chain_id = self.__chain_id[:64]
            return Hex(Hex.validate(chain_id.ljust(64, "0")))
        return node_config.HIVE_CHAIN_ID

    def __prepare_directory(self) -> None:
        self.name: str
        self.directory: Path
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
        assert self._beekeeper_wallet is not None, "Beekeeper wallet not exist"
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
        preconfigure: bool = True,
    ) -> None:
        if self.is_running():
            raise RuntimeError("Wallet is already running")

        if self.connected_node is not None and not self.connected_node.is_running():
            raise exceptions.NodeIsNotRunningError("Before attaching wallet you have to run node")

        self.__beekeeper = Beekeeper.factory(settings=Settings(working_directory=self.directory))
        self.__beekeeper_session = self.__beekeeper.create_session()

        try:
            self._beekeeper_wallet = self.__beekeeper_session.create_wallet(name=self.name, password=DEFAULT_PASSWORD)
            if preconfigure:
                self._beekeeper_wallet.import_key(private_key=Account("initminer").private_key)
        except helpy.exceptions.RequestError as exception:
            if f"Wallet with name: '{self.name}' already exists" in exception.error:
                locked_wallet = self.__beekeeper_session.open_wallet(name=self.name)
                self._beekeeper_wallet = locked_wallet.unlock(DEFAULT_PASSWORD)
            else:
                raise

    def at_exit_from_scope(self) -> None:
        self.close()

    def restart(self) -> None:
        self.close()
        self.run()

    def close(self) -> None:
        if self.is_running():
            if self.__beekeeper is not None:
                self.__beekeeper.teardown()
            self.__beekeeper = None
            self.__beekeeper_session = None
            self._beekeeper_wallet = None

    def create_account(
        self,
        name: str,
        *,
        creator: str = "initminer",
        hives: Asset.TestT | float | None = None,
        vests: Asset.TestT | float | None = None,
        hbds: Asset.TbdT | float | None = None,
    ) -> WalletResponseBase | WalletResponse | None:
        """
        The `transfer_to_vesting` operation can be only done by sending the Asset.Test type.

        That's why the method in place of `vests` accepts the Asset.Test and numeric types instead of Asset.Vest.
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
        assert self.__beekeeper is not None, "Beekeeper not exist"
        max_num_of_accounts_in_single_transaction = 500
        if number_of_accounts <= max_num_of_accounts_in_single_transaction:
            accounts = Account.create_multiple(number_of_accounts, name_base, secret=secret)
            with self.in_single_transaction():
                for account in accounts:
                    self.api.create_account("initminer", account.name, "{}")
            if import_keys:
                self.api.import_keys([account.private_key for account in accounts])
            return accounts

        return create_accounts(
            beekeeper=self.__beekeeper,
            node=self._force_connected_node,
            beekeeper_wallet_name=self.name,
            beekeeper_wallet_password=DEFAULT_PASSWORD,
            number_of_accounts=number_of_accounts,
            import_keys=import_keys,
            name_base=name_base,
            secret=secret,
        )

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

    def __generate_transaction_template(
        self,
        node: AnyNode,
    ) -> SimpleTransaction:
        gdpo = node.api.database.get_dynamic_global_properties()
        block_id = gdpo.head_block_id

        # set header
        tapos_data = wax_helpy.calculate_tapos_data(block_id)
        ref_block_num = tapos_data.ref_block_num
        ref_block_prefix = tapos_data.ref_block_prefix

        assert ref_block_num >= 0, f"ref_block_num value `{ref_block_num}` is invalid`"

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
        transaction = self.__generate_transaction_template(self._force_connected_node)
        for operation in operations:
            transaction.add_operation(operation)

        transaction = self.complex_transaction_sign(transaction)

        return self.broadcast_transaction(transaction, blocking, broadcast)

    def broadcast_transaction(
        self, transaction: SimpleTransaction, blocking: bool, broadcast: bool
    ) -> WalletResponseBase | WalletResponse:
        if broadcast:
            if blocking:
                with self._force_connected_node.restore_settings():
                    self._force_connected_node.settings.timeout = timedelta(hours=1)
                    broadcast_response = self._force_connected_node.api.wallet_bridge.broadcast_transaction_synchronous(
                        transaction
                    )

                return WalletResponse(
                    transaction_id=(
                        wax_helpy.calculate_transaction_id(transaction=transaction)
                        if self._transaction_serialization == "hf26"
                        else wax_helpy.calculate_legacy_transaction_id(transaction=transaction)
                    ),
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
            self._force_connected_node.api.wallet_bridge.broadcast_transaction(transaction)

        return WalletResponseBase(
            transaction_id=(
                wax_helpy.calculate_transaction_id(transaction=transaction)
                if self._transaction_serialization == "hf26"
                else wax_helpy.calculate_legacy_transaction_id(transaction=transaction)
            ),
            ref_block_num=transaction.ref_block_num,
            ref_block_prefix=transaction.ref_block_prefix,
            expiration=transaction.expiration,
            extensions=transaction.extensions,
            signatures=transaction.signatures,
            operations=transaction.operations,
        )

    def complex_transaction_sign(self, transaction: SimpleTransaction) -> SimpleTransaction:
        sig_digest = self.calculate_sig_digest(transaction)
        sign_keys, retrived_authorities = self.import_required_keys(transaction)
        signed_transaction = self.sign_transaction(transaction, sig_digest, sign_keys)
        if self._use_authority != {}:
            return signed_transaction
        reduced_sign_keys = self.reduce_signatures(signed_transaction, sign_keys, retrived_authorities)
        return self.sign_transaction(transaction, sig_digest, reduced_sign_keys)

    def calculate_sig_digest(self, transaction: SimpleTransaction) -> str:
        chain_id = self.__get_chain_id()
        return (
            wax_helpy.calculate_sig_digest(transaction, chain_id)
            if self._transaction_serialization == "hf26"
            else wax_helpy.calculate_legacy_sig_digest(transaction, chain_id)
        )

    def sign_transaction(
        self, transaction: SimpleTransaction, sig_digest: str, keys_to_sign_with: list[str] | list[Any]
    ) -> SimpleTransaction:
        assert self._beekeeper_wallet is not None
        for key in keys_to_sign_with:
            signature = self._beekeeper_wallet.sign_digest(sig_digest=sig_digest, key=key)
            transaction.signatures.append(signature)
        transaction.signatures = list(set(transaction.signatures))

        wax_helpy.validate_transaction(transaction)
        return transaction

    def reduce_signatures(
        self,
        transaction: SimpleTransaction,
        keys_to_sign_with: list[PublicKey],
        retrived_authorities: dict[bytes, wax.python_authorities],
    ) -> list[str] | list[Any]:
        def retrieve_witness_key(wittnes_name: bytes) -> bytes:
            get_witness = self._force_connected_node.api.wallet_bridge.get_witness(wittnes_name.decode())
            assert get_witness is not None
            return get_witness.signing_key.encode()

        return wax_helpy.minimize_required_signatures(
            transaction,
            chain_id=self.__get_chain_id(),
            available_keys=keys_to_sign_with,
            authorities_map=retrived_authorities,
            get_witness_key=retrieve_witness_key,
        )

    def import_required_keys(
        self, transaction: SimpleTransaction
    ) -> tuple[list[PublicKey], dict[bytes, wax.python_authorities]]:
        def list_to_dict(list_: list[Any]) -> dict[bytes, int]:
            result: dict[bytes, int] = {}
            for i in list_:
                result[i[0].encode()] = i[1]
            return result

        def to_python_authority(account_authority: Authority) -> wax.python_authority:
            return wax.python_authority(
                weight_threshold=account_authority.weight_threshold,
                account_auths=list_to_dict(account_authority.account_auths),
                key_auths=list_to_dict(account_authority.key_auths),
            )

        def to_python_authorities(
            account_authorities: AccountSchema[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
        ) -> wax.python_authorities:
            return wax.python_authorities(
                active=to_python_authority(account_authorities.active),
                owner=to_python_authority(account_authorities.owner),
                posting=to_python_authority(account_authorities.posting),
            )

        retrived_authorities: dict[bytes, wax.python_authorities] = {}

        def retrieve_authorities(account_names: list[bytes]) -> dict[bytes, wax.python_authorities]:
            accounts = self._force_connected_node.api.wallet_bridge.get_accounts(
                [account_name.decode() for account_name in account_names]
            )
            retrived_authoritity = {acc.name.encode(): to_python_authorities(acc) for acc in accounts}
            retrived_authorities.update(retrived_authoritity)
            return retrived_authoritity

        keys_for_signing = wax_helpy.collect_signing_keys(transaction, retrieve_authorities)

        if self._use_authority != {}:
            account_name = next(iter(self._use_authority.keys()))
            authority_account = self._force_connected_node.api.database.find_accounts(accounts=[account_name])
            return [
                getattr(authority_account.accounts[0], self._use_authority[account_name]).key_auths[0][0]
            ], retrived_authorities
        imported_keys_in_beekeeper = set(self.beekeeper_wallet.public_keys)
        sign_keys = list(set(keys_for_signing) & set(imported_keys_in_beekeeper))
        validated_sign_keys = [PublicKey(PublicKey.validate(key)) for key in sign_keys]
        return validated_sign_keys, retrived_authorities

    def in_single_transaction(
        self, *, broadcast: None | bool = True, blocking: bool = True
    ) -> SingleTransactionContext:
        if broadcast is None:
            broadcast = True
        return SingleTransactionContext(self, broadcast=broadcast, blocking=blocking)
