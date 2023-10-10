from __future__ import annotations

from test_tools.__private.user_handles.handles.node_handles.api_node_handle import ApiNodeHandle
from test_tools.__private.user_handles.handles.node_handles.full_api_node_handle import FullApiNodeHandle
from test_tools.__private.user_handles.handles.node_handles.init_node_handle import InitNodeHandle
from test_tools.__private.user_handles.handles.node_handles.raw_node_handle import RawNodeHandle
from test_tools.__private.user_handles.handles.node_handles.witness_node_handle import WitnessNodeHandle

AnyLocalNodeHandle = ApiNodeHandle | FullApiNodeHandle | InitNodeHandle | RawNodeHandle | WitnessNodeHandle
