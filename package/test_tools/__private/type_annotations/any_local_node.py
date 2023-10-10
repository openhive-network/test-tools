from __future__ import annotations

from test_tools.__private.api_node import ApiNode
from test_tools.__private.init_node import InitNode
from test_tools.__private.raw_node import RawNode
from test_tools.__private.witness_node import WitnessNode

AnyLocalNode = ApiNode | InitNode | RawNode | WitnessNode
