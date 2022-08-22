from typing import TYPE_CHECKING as __TYPE_CHECKING

from test_tools.__private import cleanup_policy
from test_tools.__private import constants
from test_tools.__private import exceptions
from test_tools.__private import paths_to_executables
from test_tools.__private.account import Account
from test_tools.__private.asset import Asset
from test_tools.__private.block_log import BlockLog
from test_tools.__private.keys import PrivateKey, PublicKey
from test_tools.__private.logger.logger_user_interface import logger

# User handles
from test_tools.__private.user_handles import ApiNodeHandle as ApiNode
from test_tools.__private.user_handles import context
from test_tools.__private.user_handles import InitNodeHandle as InitNode
from test_tools.__private.user_handles import NetworkHandle as Network
from test_tools.__private.user_handles import RawNodeHandle as RawNode
from test_tools.__private.user_handles import RemoteNodeHandle as RemoteNode
from test_tools.__private.user_handles import WalletHandle as Wallet
from test_tools.__private.user_handles import WitnessNodeHandle as WitnessNode

# Type annotations
if __TYPE_CHECKING:
    # If you encountered error like:
    # E   AttributeError: module 'test_tools' has no attribute 'TypeAnnotationDefinedBelow'
    # You need to add following import at the top of client module:
    # from __future__ import annotations
    #
    # Note for TestTools developers:
    #   Above information is needed only in Python older than 3.10 and should be removed,
    #   when we will remove support for these versions.
    from test_tools.__private.type_annotations import AnyAsset
    from test_tools.__private.type_annotations import AnyLocalNodeHandle as AnyLocalNode
    from test_tools.__private.type_annotations import AnyNodeHandle as AnyNode
