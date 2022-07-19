from test_tools.node_api.api_base import ApiBase
from test_tools.node_api.api_base import NodeApiCallProxy


class WalletBridgeApiCallProxy(NodeApiCallProxy):
    @staticmethod
    def _prepare_params(*args, **kwargs):
        return [list(args)]


class WalletBridgeApi(ApiBase):
    _NodeApiCallProxyType = WalletBridgeApiCallProxy

    def __init__(self, node):
        super().__init__(node, 'wallet_bridge_api')
