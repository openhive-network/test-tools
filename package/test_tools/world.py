from pathlib import Path

from test_tools import constants
from test_tools.network import Network
from test_tools.private.nodes_creator import NodesCreator
from test_tools.private.block_log import BlockLog


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
def get_time_offset_from_file(name):
    timestamp = ''
    with open(name, 'r') as f:
        timestamp = f.read()
    timestamp = timestamp.strip()
    current_time = datetime.now(timezone.utc)
    new_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    difference = round(new_time.timestamp()-current_time.timestamp()) - 10 # circa 10 seconds is needed for nodes to startup
    time_offset = str(difference) + 's'
    return time_offset


def run_networks(world, blocklog_directory):
    time_offset = get_time_offset_from_file(blocklog_directory/'timestamp')

    block_log = BlockLog(None, blocklog_directory/'block_log', include_index=False)

    nodes = world.nodes()
    nodes[0].run(wait_for_live=False, replay_from=block_log, time_offset=time_offset)
    endpoint = nodes[0].get_p2p_endpoint()
    for node in nodes[1:]:
        node.config.p2p_seed_node.append(endpoint)
        node.run(wait_for_live=False, replay_from=block_log, time_offset=time_offset)

    for network in world.networks():
        network.is_running = True
    for node in nodes:
        node.wait_for_live()
