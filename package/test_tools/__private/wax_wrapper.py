from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from schemas.fields.assets.hive import AssetHiveHF26
from wax import create_wax_foundation
from wax._private.result_tools import (
    expose_result_as_python_string,
    to_cpp_string,
    to_python_string,
    validate_wax_result,
)
from wax.cpp_python_bridge import calculate_legacy_sig_digest as wax_calculate_legacy_sig_digest
from wax.cpp_python_bridge import calculate_legacy_transaction_id as wax_calculate_legacy_transaction_id
from wax.cpp_python_bridge import calculate_public_key as wax_calculate_public_key
from wax.cpp_python_bridge import calculate_sig_digest as wax_calculate_sig_digest
from wax.cpp_python_bridge import calculate_transaction_id as wax_calculate_transaction_id
from wax.cpp_python_bridge import collect_signing_keys as wax_collect_signing_keys
from wax.cpp_python_bridge import decode_encrypted_memo as wax_decode_encrypted_memo
from wax.cpp_python_bridge import encode_encrypted_memo as wax_encode_encrypted_memo
from wax.cpp_python_bridge import generate_password_based_private_key as wax_generate_password_based_private_key
from wax.cpp_python_bridge import get_hive_protocol_config as wax_get_hive_protocol_config
from wax.cpp_python_bridge import get_tapos_data as wax_get_tapos_data
from wax.cpp_python_bridge import minimize_required_signatures as wax_minimize_required_signatures
from wax.cpp_python_bridge import validate_transaction as wax_validate_transaction
from wax.wax_result import (
    python_authorities,
    python_authority,
    python_minimize_required_signatures_data,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from schemas.apis.wallet_bridge_api.fundaments_of_responses import Account as AccountSchema
    from schemas.fields.assets.hbd import AssetHbdHF26
    from schemas.fields.assets.vests import AssetVestsHF26
    from schemas.fields.basic import PublicKey
    from schemas.fields.compound import Authority, Price
    from schemas.transaction import Transaction
    from test_tools.__private.wallet.constants import AccountNameApiType
    from wax.models.key_data import IBrainKeyData
    from wax.wax_result import python_ref_block_data


wax_authorities = python_authorities
wax_authority = python_authority


@dataclass
class WaxPrivateKeyData:
    wif_private_key: str
    associated_public_key: str


@dataclass
class WaxEncryptedMemo:
    main_encryption_key: str
    other_encryption_key: str
    encrypted_content: str


def to_wax_authority(account_authority: Authority) -> wax_authority:
    """
    Convert the given account authority (api form) to python authority (wax form).

    Args:
    ----
    account_authority: The authority (not account!) object returned from the API.

    """

    def list_to_dict(list_: list[Any]) -> dict[bytes, int]:
        result: dict[bytes, int] = {}
        for i in list_:
            result[i[0].encode()] = i[1]
        return result

    return wax_authority(
        weight_threshold=account_authority.weight_threshold,
        account_auths=list_to_dict(account_authority.account_auths),
        key_auths=list_to_dict(account_authority.key_auths),
    )


def to_wax_authorities(
    account_authorities: AccountSchema[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
) -> wax_authorities:
    """
    Convert the given account authorities (api form) to python authorities (wax form).

    Args:
    ----
    account_authorities: The account object returned from the API.

    Returns:
    -------
    The converted python authorities.

    """
    return wax_authorities(
        active=to_wax_authority(account_authorities.active),
        owner=to_wax_authority(account_authorities.owner),
        posting=to_wax_authority(account_authorities.posting),
    )


def calculate_public_key(wif: str) -> str:
    result = wax_calculate_public_key(to_cpp_string(wif))
    validate_wax_result(result)
    return expose_result_as_python_string(result)


def get_tapos_data(head_block_id: str) -> python_ref_block_data:
    return wax_get_tapos_data(to_cpp_string(head_block_id))


def validate_transaction(transaction: Transaction) -> None:
    """
    Validate the given transaction.

    Args:
    ----
    transaction: The transaction to validate.

    Raises:
    ------
    WaxValidationError: If the transaction is invalid.

    """
    result = wax_validate_transaction(to_cpp_string(transaction.json()))
    validate_wax_result(result)


def calculate_transaction_id(transaction: Transaction) -> str:
    """
    Calculate the transaction id from the given transaction.

    Args:
    ----
    transaction: The transaction to calculate the id for.

    Returns:
    -------
    The calculated transaction id.

    Raises:
    ------
    WaxValidationError: If the transaction id could not be calculated.

    """
    result = wax_calculate_transaction_id(to_cpp_string(transaction.json()))
    validate_wax_result(result)
    return expose_result_as_python_string(result)


def calculate_legacy_transaction_id(transaction: Transaction) -> str:
    """
    Calculate the transaction id from the given transaction in the legacy format.

    Args:
    ----
    transaction: The transaction to calculate the id for.

    Returns:
    -------
    The calculated transaction id in the legacy format.

    Raises:
    ------
    WaxValidationError: If the transaction id could not be calculated.

    """
    result = wax_calculate_legacy_transaction_id(to_cpp_string(transaction.json()))
    validate_wax_result(result)
    return expose_result_as_python_string(result)


def calculate_sig_digest(transaction: Transaction, chain_id: str) -> str:
    """
    Calculate the sig digest from the given transaction and chain id.

    Args:
    ----
    transaction: The transaction to calculate the sig digest for.
    chain_id: The chain id to calculate the sig digest for.

    Returns:
    -------
    The calculated signature digest.

    Raises:
    ------
    WaxValidationError: If the signature digest could not be calculated.

    """
    result = wax_calculate_sig_digest(to_cpp_string(transaction.json()), to_cpp_string(chain_id))
    validate_wax_result(result)
    return expose_result_as_python_string(result)


def calculate_legacy_sig_digest(transaction: Transaction, chain_id: str) -> str:
    """
    Calculate the sig digest from the given transaction and chain id in the legacy format.

    Args:
    ----
    transaction: The transaction to calculate the sig digest for.
    chain_id: The chain id to calculate the sig digest for.

    Returns:
    -------
    The calculated signature digest in the legacy format.

    Raises:
    ------
    WaxValidationError: If the sig digest could not be calculated.

    """
    result = wax_calculate_legacy_sig_digest(to_cpp_string(transaction.json()), to_cpp_string(chain_id))
    validate_wax_result(result)
    return expose_result_as_python_string(result)


def get_hive_protocol_config(chain_id: str) -> dict[str, str]:
    return {
        to_python_string(key): to_python_string(value)
        for key, value in wax_get_hive_protocol_config(to_cpp_string(chain_id)).items()
    }


def minimize_required_signatures(
    transaction: Transaction,
    chain_id: str,
    available_keys: list[PublicKey],
    retrived_authorities: dict[bytes, wax_authorities],
    get_witness_key: Callable[[bytes], bytes],
) -> list[str]:
    """
    Minimize the required signatures for the given transaction.

    Args:
    ----
    transaction: The transaction to minimize the required signatures for.
    chain_id: chain id of the current chain type.
    available_keys: The available keys.
    retrived_authorities: The retrieved authorities.
    get_witness_key: The callable object to get the witness key.

    Returns:
    -------
    The minimized required signatures.

    """
    result = wax_minimize_required_signatures(
        to_cpp_string(transaction.json()),
        minimize_required_signatures_data=python_minimize_required_signatures_data(
            chain_id=to_cpp_string(chain_id),
            available_keys=[to_cpp_string(key) for key in available_keys],
            authorities_map=retrived_authorities,
            get_witness_key=get_witness_key,
        ),
    )
    return [to_python_string(signature) for signature in result]


def collect_signing_keys(
    transaction: Transaction, retrieve_authorities: Callable[[list[bytes]], dict[bytes, wax_authorities]]
) -> list[str]:
    """
    Collect the signing keys for the given transaction.

    Args:
    ----
    transaction: The transaction to collect the signing keys for.
    retrieve_authorities: The callable to retrieve the authorities.

    Returns:
    -------
    The collected signing keys.

    """
    return [
        to_python_string(key)
        for key in wax_collect_signing_keys(to_cpp_string(transaction.json()), retrieve_authorities)
    ]


def estimate_hive_collateral(
    hbd_amount_to_get: AssetHbdHF26,
    current_median_history: Price[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26],
    current_min_history: Price[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26],
) -> AssetHiveHF26:
    """
    Estimate the hive collateral for the given HBD amount to get.

    Args:
    ----
    _____
    hbd_amount_to_get: The HBD amount to get.
    current_median_history: The current median history (from the `get_feed_history`).
    current_min_history: The current min history (from the `get_feed_history`).

    Returns:
    -------
    The estimated hive collateral.

    """
    wax_base_api = create_wax_foundation()
    wax_asset = wax_base_api.estimate_hive_collateral(
        current_median_history.base.dict(),
        current_median_history.quote.dict(),
        current_min_history.base.dict(),
        current_min_history.quote.dict(),
        hbd_amount_to_get.dict(),
    )
    return AssetHiveHF26(amount=int(wax_asset.amount), nai=wax_asset.nai, precision=wax_asset.precision)


def generate_password_based_private_key(account: AccountNameApiType, role: str, password: str) -> WaxPrivateKeyData:
    """Generate a password based private key for the given account and role."""
    wax_result = wax_generate_password_based_private_key(account, role, password)
    return WaxPrivateKeyData(
        wif_private_key=to_python_string(wax_result.wif_private_key),
        associated_public_key=to_python_string(wax_result.associated_public_key),
    )


def suggest_brain_key() -> IBrainKeyData:
    """Suggest a brain key."""
    wax_base_api = create_wax_foundation()
    return wax_base_api.suggest_brain_key()


def decode_encrypted_memo(encoded_memo: str) -> WaxEncryptedMemo:
    wax_result = wax_decode_encrypted_memo(to_cpp_string(encoded_memo))
    return WaxEncryptedMemo(
        main_encryption_key=to_python_string(wax_result.main_encryption_key),
        other_encryption_key=to_python_string(wax_result.other_encryption_key),
        encrypted_content=to_python_string(wax_result.encrypted_content),
    )


def encode_encrypted_memo(encrypted_content: str, main_encryption_key: str, other_encryption_key: str = "") -> str:
    return to_python_string(
        wax_encode_encrypted_memo(
            to_cpp_string(encrypted_content), to_cpp_string(main_encryption_key), to_cpp_string(other_encryption_key)
        )
    )
