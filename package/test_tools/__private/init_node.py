from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.__private.asset import Asset
from test_tools.__private.exceptions import NodeIsNotRunning
from test_tools.__private.logger.logger_internal_interface import logger
from test_tools.__private.vest_price import VestPrice
from test_tools.__private.witness_node import WitnessNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class InitNode(WitnessNode):
    """Node which is ready to produce blocks"""

    def __init__(self, *, name: str = "InitNode", network: Optional[Network], handle: Optional[NodeHandle] = None):
        super().__init__(name=name, network=network, witnesses=["initminer"], handle=handle)
        self.config.enable_stale_production = True
        self.config.required_participation = 0

    def set_vest_price(self, base: Asset.Test, quote: Asset.Vest, invest: Asset.Test = Asset.Test(10_000_000)) -> None:
        if not self.is_running():
            raise NodeIsNotRunning("Cannot set a price on a disabled node. Please start node before setting the price.")

        price = VestPrice(base=base, quote=quote)
        self.wait_for_block_with_number(2)
        self.__set_new_price(price)
        if invest > Asset.Test(0):
            self.__stabilize_the_price(invest=invest)
        self.__log_vest_price_from_network()

    def __set_new_price(self, new_price) -> None:
        # FIXME: https://gitlab.syncad.com/hive/hive/-/issues/254#note_131758  # pylint: disable=fixme
        logger.info(f"new vests price (wrapped) {new_price}.")
        self.api.debug_node.debug_set_vest_price(vest_price=new_price.as_nai())

    def __stabilize_the_price(self, invest: Asset.Test) -> None:
        from test_tools.__private.wallet import Wallet  # pylint: disable=import-outside-toplevel, cyclic-import

        wallet = Wallet(attach_to=self)

        # this is required to minimize inflation impact on vest price
        wallet.api.transfer_to_vesting("initminer", "initminer", invest)
        logger.info(f"Price stabilization completed. Invested: {invest} in network.")
        wallet.close()

    def __log_vest_price_from_network(self) -> None:
        dgpo = self.api.wallet_bridge.get_dynamic_global_properties()
        logger.info(f"new vests price (real): {VestPrice.from_dgpo(dgpo)}")
