from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from test_tools.__private.remote_node import RemoteNode
    from test_tools.__private.type_annotations.any_local_node import AnyLocalNode

    AnyNode = Union[AnyLocalNode, RemoteNode]
