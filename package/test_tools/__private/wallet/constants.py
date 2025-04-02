from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Final, Literal

from schemas.fields.basic import AccountName, EmptyString, PrivateKey, PublicKey, WitnessUrl
from schemas.fields.compound import HbdExchangeRate
from schemas.fields.hive_datetime import HiveDateTime
from schemas.operations import convert_to_representation
from schemas.transaction import Transaction

if TYPE_CHECKING:
    from schemas.operation import Operation
    from test_tools.__private.node import Node
    from test_tools.__private.remote_node import RemoteNode

    AnyNode = Node | RemoteNode

DEFAULT_PASSWORD: Final[str] = "password"
HIVE_MAX_TIME_UNTIL_EXPIRATION: Final[int] = 60 * 60
HIVE_MAX_TIME_UNTIL_SIGNATURE_EXPIRATION: Final[int] = 86400
ACCOUNT_PER_TRANSACTION: Final[int] = 500
MULTIPLE_IMPORT_KEYS_BATCH_SIZE: Final[int] = 10000

AccountNameApiType = AccountName | str
EmptyStringApiType = EmptyString | str
HiveDateTimeApiType = HiveDateTime | datetime | str
PublicKeyApiType = PublicKey | str
WitnessUrlApiType = WitnessUrl | str
HbdExchangeRateApiType = HbdExchangeRate | dict

AuthorityType = Literal["active", "owner", "posting"]
TransactionSerializationTypes = Literal["hf26", "legacy"]


@dataclass
class AuthorityRequirementsHolder:
    active: set[str] = field(default_factory=set)
    owner: set[str] = field(default_factory=set)
    posting: set[str] = field(default_factory=set)

    def all_(self) -> set[str]:
        return {*self.active, *self.owner, *self.posting}


@dataclass
class AuthorityHolder:
    active: dict[PublicKey, PrivateKey] = field(default_factory=dict)
    owner: dict[PublicKey, PrivateKey] = field(default_factory=dict)
    posting: dict[PublicKey, PrivateKey] = field(default_factory=dict)

    def all_(self) -> dict[PublicKey, PrivateKey]:
        result = self.active.copy()
        result.update(self.owner)
        result.update(self.posting)
        return result


class SimpleTransaction(Transaction):
    def add_operation(self, operation: Operation) -> None:
        representation = convert_to_representation(operation)
        self.operations.append(representation)

    def add_operation(self, operation: Operation) -> None:
        representation = convert_to_representation(operation)
        self.operations.append(representation)


class WalletResponseBase(SimpleTransaction):
    transaction_id: str


class WalletResponse(WalletResponseBase):
    block_num: int
    transaction_num: int
    rc_cost: None | int
