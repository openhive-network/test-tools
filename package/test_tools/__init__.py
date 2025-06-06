from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from test_tools.__private import (
    cleanup_policy,
    constants,
    exceptions,
    paths_to_executables,
    wax_wrapper,
)
from test_tools.__private.account import Account, PrivateKey, PublicKey
from test_tools.__private.alternate_chain_specs import AlternateChainSpecs, HardforkSchedule, InitialVesting
from test_tools.__private.block_log import BlockLog
from test_tools.__private.process.node_arguments import NodeArguments
from test_tools.__private.process.node_config import NodeConfig
from test_tools.__private.snapshot import Snapshot

# User handles
from test_tools.__private.user_handles import ApiNodeHandle as ApiNode
from test_tools.__private.user_handles import FullApiNodeHandle as FullApiNode
from test_tools.__private.user_handles import InitNodeHandle as InitNode
from test_tools.__private.user_handles import NetworkHandle as Network
from test_tools.__private.user_handles import OldWalletHandle as OldWallet
from test_tools.__private.user_handles import RawNodeHandle as RawNode
from test_tools.__private.user_handles import RemoteNodeHandle as RemoteNode
from test_tools.__private.user_handles import WalletHandle as Wallet
from test_tools.__private.user_handles import WitnessNodeHandle as WitnessNode
from test_tools.__private.user_handles import context
from wax.helpy import Hf26Asset as Asset
from wax.helpy import OffsetTimeControl, SpeedUpRateTimeControl, StartTimeControl, Time, TimeFormats

__all__ = [
    "Account",
    "AlternateChainSpecs",
    "ApiNode",
    "Asset",
    "BlockLog",
    "FullApiNode",
    "HardforkSchedule",
    "InitNode",
    "InitialVesting",
    "Network",
    "OffsetTimeControl",
    "OldWallet",
    "PrivateKey",
    "PublicKey",
    "RawNode",
    "RemoteNode",
    "SpeedUpRateTimeControl",
    "StartTimeControl",
    "wax_wrapper",
    "Time",
    "TimeFormats",
    "Wallet",
    "NodeArguments",
    "NodeConfig",
    "WitnessNode",
    "cleanup_policy",
    "constants",
    "context",
    "exceptions",
    "logger",
    "paths_to_executables",
]

if TYPE_CHECKING:
    from test_tools.__private.type_annotations.any_node import AnyNode  # noqa: TCH004

    __all__ = [*__all__, "AnyNode", "Snapshot"]  # noqa: PLE0604
