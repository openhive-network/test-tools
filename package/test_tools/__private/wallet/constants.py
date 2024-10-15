from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from schemas.fields.basic import AccountName, EmptyString, PrivateKey, PublicKey, WitnessUrl
from schemas.fields.compound import HbdExchangeRate
from schemas.fields.hive_datetime import HiveDateTime
from schemas.operations.representations.hf26_representation import HF26Representation
from schemas.transaction import Transaction

if TYPE_CHECKING:
    from schemas.operations import AnyOperation
    from test_tools.__private.node import Node
    from test_tools.__private.remote_node import RemoteNode
    AnyNode = Node | RemoteNode


HIVE_MAX_TIME_UNTIL_EXPIRATION = 60 * 60

AccountNameApiType = AccountName | str
EmptyStringApiType = EmptyString | str
HiveDateTimeApiType = HiveDateTime | datetime | str
PublicKeyApiType = PublicKey | str
WitnessUrlApiType = WitnessUrl | str
HbdExchangeRateApiType = HbdExchangeRate | dict

AuthorityType = Literal["active", "owner", "posting"]

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
    def add_operation(self, operation: AnyOperation) -> None:
        self.operations.append(HF26Representation(type=operation.get_name_with_suffix(), value=operation))


class WalletResponseBase(SimpleTransaction):
    transaction_id: str


class WalletResponse(WalletResponseBase):
    block_num: int
    transaction_num: int
    rc_cost: None | int
