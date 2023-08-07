from __future__ import annotations

from typing import cast, Optional, TYPE_CHECKING

from test_tools.__private.init_node import InitNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.runnable_node_handle import RunnableNodeHandle
from test_tools.__private.vest_price import Asset

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class InitNodeHandle(RunnableNodeHandle):
    def __init__(self, network: Optional[Network] = None):
        super().__init__(
            implementation=InitNode(
                network=get_implementation(network),
                handle=self,
            )
        )

    @property
    def __implementation(self) -> InitNode:
        return cast(InitNode, get_implementation(self))

    def set_vest_price(
        self, quote: Asset.Vest, base: Asset.Test = Asset.Test(1), invest: Asset.Test = Asset.Test(10_000_000)
    ) -> object:
        """
        Used to set a new price for vests in relation to hive on a blockchain node. It calculates the new price,
        logs it, and then updates the vest price on the node using the API call.
        :param invest: The hive amount to be invested in the network to mitigate inflation during the price change.
        :param base: The base asset for the price calculation (hive).
        :param quote: The quote asset for the price calculation (vests).
        :raises RuntimeError: When the node is not running.
        """
        return self.__implementation.set_vest_price(base, quote, invest)
