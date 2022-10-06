from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from test_tools.__private.network import Network
    from test_tools.__private.node import Node
    from test_tools.__private.remote_node import RemoteNode
    from test_tools.__private.wallet import Wallet

    UserHandleImplementation = Union[Network, Node, RemoteNode, Wallet]
