from __future__ import annotations

from test_tools.__private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle
from test_tools.__private.user_handles.handles.node_handles.runnable_node_handle import RunnableNodeHandle

AnyNode = RunnableNodeHandle | RemoteNodeHandle
