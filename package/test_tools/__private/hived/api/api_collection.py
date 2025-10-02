from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy.handle.remote import AppStatusProbeSyncApiCollection

from test_tools.__private.hived.api.account_by_key_api import SyncAccountByKeyApi
from test_tools.__private.hived.api.account_history_api import SyncAccountHistoryApi
from test_tools.__private.hived.api.block_api import SyncBlockApi
from test_tools.__private.hived.api.condenser_api import SyncCondenserApi
from test_tools.__private.hived.api.database_api import SyncDatabaseApi
from test_tools.__private.hived.api.debug_node_api import SyncDebugNodeApi
from test_tools.__private.hived.api.jsonrpc import SyncJsonrpc
from test_tools.__private.hived.api.market_history_api import SyncMarketHistoryApi
from test_tools.__private.hived.api.network_broadcast_api import SyncNetworkBroadcastApi
from test_tools.__private.hived.api.network_node_api import SyncNetworkNodeApi
from test_tools.__private.hived.api.rc_api import SyncRcApi
from test_tools.__private.hived.api.reputation_api import SyncReputationApi
from test_tools.__private.hived.api.transaction_status_api import SyncTransactionStatusApi
from test_tools.__private.hived.api.wallet_bridge_api import SyncWalletBridgeApi

if TYPE_CHECKING:
    from beekeepy.handle.remote import SyncSendable


class HivedSyncApiCollection(AppStatusProbeSyncApiCollection):
    def __init__(self, owner: SyncSendable) -> None:
        super().__init__(owner)
        self.account_by_key = SyncAccountByKeyApi(owner=self._owner)
        self.account_history = SyncAccountHistoryApi(owner=self._owner)
        self.block = SyncBlockApi(owner=self._owner)
        self.condenser = SyncCondenserApi(owner=self._owner)
        self.database = SyncDatabaseApi(owner=self._owner)
        self.debug_node = SyncDebugNodeApi(owner=self._owner)
        self.jsonrpc = SyncJsonrpc(owner=self._owner)
        self.market_history = SyncMarketHistoryApi(owner=self._owner)
        self.network_broadcast = SyncNetworkBroadcastApi(owner=self._owner)
        self.network_node = SyncNetworkNodeApi(owner=self._owner)
        self.rc = SyncRcApi(owner=self._owner)
        self.reputation = SyncReputationApi(owner=self._owner)
        self.transaction_status = SyncTransactionStatusApi(owner=self._owner)
        self.wallet_bridge = SyncWalletBridgeApi(owner=self._owner)

        self.account_by_key_api = self.account_by_key
        self.account_history_api = self.account_history
        self.block_api = self.block
        self.condenser_api = self.condenser
        self.database_api = self.database
        self.debug_node_api = self.debug_node
        self.jsonrpc_api = self.jsonrpc
        self.market_history_api = self.market_history
        self.network_broadcast_api = self.network_broadcast
        self.network_node_api = self.network_node
        self.rc_api = self.rc
        self.reputation_api = self.reputation
        self.transaction_status_api = self.transaction_status
        self.wallet_bridge_api = self.wallet_bridge
