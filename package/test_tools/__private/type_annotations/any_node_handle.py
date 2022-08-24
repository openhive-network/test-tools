from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from test_tools.__private.type_annotations.any_local_node_handle import AnyLocalNodeHandle
    from test_tools.__private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle

    AnyNodeHandle = Union[AnyLocalNodeHandle, RemoteNodeHandle]
