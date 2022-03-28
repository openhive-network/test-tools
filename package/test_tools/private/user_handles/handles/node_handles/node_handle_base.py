from __future__ import annotations

import math
from typing import TYPE_CHECKING

from test_tools.private.node import Node

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Dict, List, Optional, Tuple, Union
    from test_tools.cleanup_policy import CleanupPolicy
    from test_tools.node_api.node_apis import Apis
    from test_tools.node_config import NodeConfig
    from test_tools.private.block_log import BlockLog
    from test_tools.private.snapshot import Snapshot


class NodeHandleBase:
    __DEFAULT_WAIT_FOR_LIVE_TIMEOUT = Node.DEFAULT_WAIT_FOR_LIVE_TIMEOUT

    def __init__(self, *, implementation: Node):
        self.__implementation: Node = implementation

    @property
    def api(self) -> Apis:
        """
        Returns grouped all node's APIs.

        Should be used in following way:
          node.api.<API>.<METHOD>()
        e.g.:
          node.api.database.get_version()
        """
        return self.__implementation.api

    def close(self) -> None:
        return self.__implementation.close()

    @property
    def config(self) -> NodeConfig:
        """Provides way to edit node's configuration file."""
        return self.__implementation.config

    @property
    def directory(self) -> Path:
        return self.__implementation.directory

    def dump_config(self) -> None:
        return self.__implementation.dump_config()

    def dump_snapshot(self, *, close: bool = False) -> Snapshot:
        return self.__implementation.dump_snapshot(close=close)

    def get_block_log(self, *, include_index: bool = True) -> BlockLog:
        return self.__implementation.get_block_log(include_index)

    def get_last_block_number(self) -> int:
        return self.__implementation.get_last_block_number()

    @property
    def http_endpoint(self) -> str:
        return self.__implementation.get_http_endpoint()

    def is_running(self) -> bool:
        """Returns True if node's process is running, False if process is closed."""
        return self.__implementation.is_running()

    def run(self, *, load_snapshot_from=None, replay_from=None, stop_at_block=None,
            exit_before_synchronization: bool = False, wait_for_live=None,
            arguments: Union[List[str], Tuple[str, ...]] = (), environment_variables: Optional[Dict] = None,
            timeout=__DEFAULT_WAIT_FOR_LIVE_TIMEOUT, time_offset: Optional[str] = None) -> None:
        """
        :param wait_for_live: Stops execution until node will generate or receive blocks.
        :param timeout: If wait_for_live is set to True, this parameter sets how long waiting can take. When
                        timeout is reached, TimeoutError exception is thrown.
        :param arguments: Additional arguments passed to node during running. Should be separated in the same way as in
                          `subprocess.run` function.
        :param environment_variables: Additional environment variables passed to node run environment. If variable name
                                      is already defined, its value will be overwritten with one provided by this
                                      parameter.
        """
        return self.__implementation.run(
            load_snapshot_from=load_snapshot_from,
            replay_from=replay_from,
            stop_at_block=stop_at_block,
            exit_before_synchronization=exit_before_synchronization,
            wait_for_live=wait_for_live,
            arguments=arguments,
            environment_variables=environment_variables,
            timeout=timeout,
            time_offset=time_offset,
        )

    def restart(self, wait_for_live: bool = True, timeout: float = __DEFAULT_WAIT_FOR_LIVE_TIMEOUT) -> None:
        return self.__implementation.restart(wait_for_live=wait_for_live, timeout=timeout)

    def set_cleanup_policy(self, policy: CleanupPolicy) -> None:
        return self.__implementation.set_cleanup_policy(policy)

    def wait_number_of_blocks(self, blocks_to_wait: int, *, timeout: float = math.inf) -> None:
        return self.__implementation.wait_number_of_blocks(blocks_to_wait, timeout=timeout)

    def wait_for_block_with_number(self, number: int, *, timeout: float = math.inf) -> None:
        return self.__implementation.wait_for_block_with_number(number, timeout=timeout)

    @property
    def ws_endpoint(self) -> str:
        return self.__implementation.get_ws_endpoint()
