from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from test_tools.__private.type_annotations.any_local_node import AnyLocalNode
    from test_tools.__private.remote_node import RemoteNode

    AnyNode = Union[AnyLocalNode, RemoteNode]
