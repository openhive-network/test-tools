from test_tools.network import Network
from test_tools.private.nodes_creator import NodesCreator


class World(NodesCreator):
    def __init__(self):
        super().__init__()

        self.__networks = []
        self.__name = 'World'
        self.__is_monitoring_resources = False

    def __str__(self):
        return self.__name

    def __enter__(self):
        if self.__is_monitoring_resources:
            raise RuntimeError('You already have activated context manager (`with World(): ...`)')

        self.__is_monitoring_resources = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__is_monitoring_resources:
            self.close()

    def close(self):
        self.handle_final_cleanup()

    def handle_final_cleanup(self):
        if not self.__is_monitoring_resources:
            raise RuntimeError('World was already closed. Can be closed only once.')

        self._handle_final_cleanup()

        for network in self.__networks:
            network.handle_final_cleanup()

    def create_network(self, name=None):
        if name is not None:
            self._children_names.register_name(name)
        else:
            name = self._children_names.create_name('Network')

        network = Network(name)
        self.__networks.append(network)
        return network

    def network(self, name: str) -> Network:
        for network in self.__networks:
            if str(network) == name:
                return network

        raise RuntimeError(
            f'There is no network with name "{name}". Available networks are:\n'
            f'{[str(network) for network in self.__networks]}'
        )

    def networks(self):
        return self.__networks

    def nodes(self):
        """Returns list of all nodes in the world (including nodes in networks)"""

        nodes = self._nodes.copy()
        for network in self.__networks:
            nodes += network.nodes()
        return nodes
