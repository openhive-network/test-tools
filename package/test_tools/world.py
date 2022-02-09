from pathlib import Path

from test_tools import constants
from test_tools.network import Network
from test_tools.private.nodes_creator import NodesCreator
from test_tools.private.prepared_block_log.block_log_utils import get_prepared_block_log, get_prepared_time_offset


class World(NodesCreator):
    def __init__(self, directory=None):
        super().__init__()

        self.__networks = []
        self.__name = 'World'
        self.__is_monitoring_resources = False
        self.__clean_up_policy = constants.WorldCleanUpPolicy.DO_NOT_REMOVE_FILES

        if directory is None:
            self._directory = Path() / f'GeneratedIn{self}'
        else:
            self._directory = directory

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

        nodes_creator_policy = self.__get_corresponding_nodes_creator_policy(self.__clean_up_policy)
        self._handle_final_cleanup(default_policy=nodes_creator_policy)

        for network in self.__networks:
            network.handle_final_cleanup(default_policy=self.__get_corresponding_network_policy(self.__clean_up_policy))

    @staticmethod
    def __get_corresponding_nodes_creator_policy(policy: constants.WorldCleanUpPolicy) -> NodesCreator.CleanUpPolicy:
        WorldPolicy = constants.WorldCleanUpPolicy
        NodesCreatorPolicy = NodesCreator.CleanUpPolicy

        return {
            WorldPolicy.REMOVE_EVERYTHING:          NodesCreatorPolicy.REMOVE_EVERYTHING,
            WorldPolicy.REMOVE_ONLY_UNNEEDED_FILES: NodesCreatorPolicy.REMOVE_ONLY_UNNEEDED_FILES,
            WorldPolicy.DO_NOT_REMOVE_FILES:        NodesCreatorPolicy.DO_NOT_REMOVE_FILES,
        }[policy]

    @staticmethod
    def __get_corresponding_network_policy(policy: constants.WorldCleanUpPolicy) -> constants.NetworkCleanUpPolicy:
        WorldPolicy = constants.WorldCleanUpPolicy
        NetworkPolicy = constants.NetworkCleanUpPolicy

        return {
            WorldPolicy.REMOVE_EVERYTHING:          NetworkPolicy.REMOVE_EVERYTHING,
            WorldPolicy.REMOVE_ONLY_UNNEEDED_FILES: NetworkPolicy.REMOVE_ONLY_UNNEEDED_FILES,
            WorldPolicy.DO_NOT_REMOVE_FILES:        NetworkPolicy.DO_NOT_REMOVE_FILES,
        }[policy]

    def create_network(self, name=None):
        if name is not None:
            self._children_names.register_name(name)
        else:
            name = self._children_names.create_name('Network')

        network = Network(name, self._directory)
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

    def set_directory(self, directory):
        self._directory = Path(directory)

    def set_clean_up_policy(self, policy: constants.WorldCleanUpPolicy):
        self.__clean_up_policy = policy

    def run_all_nodes(self, prepared_block_log=False, replay_all_nodes=True, wait_for_live=True):
        block_log = None
        time_offset = None
        if prepared_block_log:
            block_log = get_prepared_block_log()
            time_offset = get_prepared_time_offset()

        nodes_to_run = self.nodes()
        seed_node = nodes_to_run[0]
        seed_node.run(wait_for_live=False, replay_from=block_log, time_offset=time_offset)
        endpoint = seed_node.get_p2p_endpoint()
        for node in nodes_to_run[1:]:
            node.config.p2p_seed_node.append(endpoint)
            if replay_all_nodes:
                node.run(wait_for_live=False, replay_from=block_log, time_offset=time_offset)
            else:
                node.run(wait_for_live=False, time_offset=time_offset)

        for network in self.networks():
            network.is_running = True

        if wait_for_live:
            for node in nodes_to_run:
                node.wait_for_live()
