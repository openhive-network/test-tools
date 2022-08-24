from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from test_tools.__private.user_handles.handles.node_handles.api_node_handle import ApiNodeHandle
    from test_tools.__private.user_handles.handles.node_handles.init_node_handle import InitNodeHandle
    from test_tools.__private.user_handles.handles.node_handles.raw_node_handle import RawNodeHandle
    from test_tools.__private.user_handles.handles.node_handles.witness_node_handle import WitnessNodeHandle

    AnyLocalNodeHandle = Union[ApiNodeHandle, InitNodeHandle, RawNodeHandle, WitnessNodeHandle]
