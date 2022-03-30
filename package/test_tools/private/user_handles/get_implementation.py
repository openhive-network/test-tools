from test_tools.private.user_handles.implementation import Implementation
from test_tools.private.user_handles.handles.remote_node_handle import RemoteNodeHandle


def get_implementation(handle):
    if isinstance(handle, RemoteNodeHandle):
        return handle._RemoteNodeHandle__implementation  # pylint: disable=protected-access

    raise RuntimeError(f'Unable to get implementation for {handle}')


def get_handle(implementation: Implementation):
    return implementation._Implementation__handle  # pylint: disable=protected-access
