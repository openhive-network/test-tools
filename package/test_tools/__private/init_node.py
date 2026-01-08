from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.exceptions import NodeIsNotRunningError
from test_tools.__private.vest_price import VestPrice
from test_tools.__private.witness_node import WitnessNode
from wax.helpy import Hf26Asset as Asset

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class InitNode(WitnessNode):
    """Node which is ready to produce blocks."""

    def __init__(self, *, name: str = "InitNode", network: Network | None, handle: NodeHandle | None = None) -> None:
        super().__init__(name=name, network=network, witnesses=["initminer"], handle=handle)
        self.config.enable_stale_production = True
        self.config.required_participation = 0

    def set_vest_price(
        self, base: Asset.TestT, quote: Asset.VestsT, invest: Asset.TestT = Asset.Test(10_000_000)  # noqa: B008
    ) -> None:
        if not self.is_running():
            raise NodeIsNotRunningError(
                "Cannot set a price on a disabled node. Please start node before setting the price."
            )

        price = VestPrice(base=base, quote=quote)
        self.wait_for_block_with_number(2)
        self.__set_new_price(price)
        if invest > Asset.Test(0):
            self.__stabilize_the_price(invest=invest)
        self.__log_vest_price_from_network()

    def __set_new_price(self, new_price: VestPrice) -> None:
        # FIXME: https://gitlab.syncad.com/hive/hive/-/issues/254#note_131758
        self.logger.info(f"new vests price (wrapped) {new_price}.")
        self.api.debug_node.debug_set_vest_price(vest_price=new_price.as_schema())

    def __stabilize_the_price(self, invest: Asset.TestT) -> None:
        from test_tools.__private.wallet.wallet import Wallet

        wallet = Wallet(attach_to=self)

        # this is required to minimize inflation impact on vest price
        wallet.api.transfer_to_vesting("initminer", "initminer", invest)
        self.logger.info(f"Price stabilization completed. Invested: {invest} in network.")
        wallet.close()

    def __log_vest_price_from_network(self) -> None:
        dgpo = self.api.wallet_bridge.get_dynamic_global_properties()
        self.logger.info(f"new vests price (real): {VestPrice.from_dgpo(dgpo)}")  # type: ignore[arg-type]
