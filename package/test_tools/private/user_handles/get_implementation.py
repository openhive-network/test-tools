from typing import Any, Optional

from test_tools.private.user_handles.implementation import Implementation


def get_implementation(handle: Optional[Any]) -> Optional[Implementation]:
    # pylint: disable=import-outside-toplevel
    # Break import-cycle
    from test_tools.private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle
    from test_tools.private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase
    from test_tools.private.user_handles.handles.network_handle import NetworkHandle  # pylint: disable=cyclic-import

    if handle is None:
        return None

    if isinstance(handle, RemoteNodeHandle):
        return handle._RemoteNodeHandle__implementation  # pylint: disable=protected-access

    if isinstance(handle, NodeHandleBase):
        return handle._NodeHandleBase__implementation  # pylint: disable=protected-access

    if isinstance(handle, NetworkHandle):
        return handle._NetworkHandle__implementation  # pylint: disable=protected-access

    raise RuntimeError(f'Unable to get implementation for {handle}')


def get_handle(implementation: Optional[Implementation]) -> Optional[Any]:
    if implementation is None:
        return None

    return implementation._Implementation__handle  # pylint: disable=protected-access
