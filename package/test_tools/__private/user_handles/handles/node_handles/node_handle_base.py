from __future__ import annotations

import math
import typing
from typing import TYPE_CHECKING

from test_tools.__private.node import Node
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Dict, List, Optional, Tuple, Union
    from test_tools.node_api.node_apis import Apis
    from test_tools.__private.block_log import BlockLog
    from test_tools.__private.cleanup_policy import CleanupPolicy
    from test_tools.__private.node_config import NodeConfig
    from test_tools.__private.snapshot import Snapshot


class NodeHandleBase(Handle):
    __DEFAULT_WAIT_FOR_LIVE_TIMEOUT = Node.DEFAULT_WAIT_FOR_LIVE_TIMEOUT

    @property
    def __implementation(self) -> Node:
        return typing.cast(Node, get_implementation(self))

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
        """
        Stops node's process with SIGINT (same as Ctrl+C in terminal). If node doesn't stop within 10 seconds, is
        stopped with SIGKILL and warning about problems with closing is emitted.
        """
        return self.__implementation.close()

    @property
    def config(self) -> NodeConfig:
        """Provides way to edit node's configuration file."""
        return self.__implementation.config

    @property
    def directory(self) -> Path:
        """Returns path to directory, where node runs and generates its files."""
        return self.__implementation.directory

    def dump_config(self) -> None:
        """Saves node's config to file. Requires that node is not running."""
        return self.__implementation.dump_config()

    def dump_snapshot(self, *, close: bool = False) -> Snapshot:
        """
        Closes node and saves snapshot data to node's directory. By default, node after snapshot dumping is restarted,
        but can be left closed, with `close` flag set to True.

        :param close: If set to True, closes node after snapshot dumping. Otherwise, restarts node after dumping.
        :return: Snapshot object, which can be used by another node to load it at startup.
        """
        return self.__implementation.dump_snapshot(close=close)

    def get_block_log(self, *, include_index: bool = True) -> BlockLog:
        """
        Returns block log object, containing paths to block log and optionally block log index. Presence of index can be
        configured with `include_index` flag. It is safe to get block log object when node is running, but copying or
        using for replay might lead to problems, because files referenced by block log object might be modified.

        :param include_index: When set to True, block log object will contain block log index path.
        :return: Block log object, which can be used by another node to perform replay.
        """
        return self.__implementation.get_block_log(include_index)

    def get_last_block_number(self) -> int:
        """Returns number of the newest block known to node."""
        return self.__implementation.get_last_block_number()

    @property
    def http_endpoint(self) -> str:
        """
        Returns opened HTTP endpoint. Blocks program execution if HTTP endpoint is not ready. When endpoint is
        configured with special values like 0.0.0.0 address or 0 port, special values are replaced with actually
        selected by node.
        """
        return self.__implementation.get_http_endpoint()

    def is_running(self) -> bool:
        """Returns True if node's process is running, False if process is closed."""
        return self.__implementation.is_running()

    def run(self, *, load_snapshot_from: Union[Snapshot, Path, str, None] = None,
            replay_from: Union[BlockLog, Path, str, None] = None, stop_at_block: Optional[int] = None,
            exit_before_synchronization: bool = False, wait_for_live: Optional[bool] = None,
            arguments: Union[List[str], Tuple[str, ...]] = (), environment_variables: Optional[Dict] = None,
            timeout: float = __DEFAULT_WAIT_FOR_LIVE_TIMEOUT, time_offset: Optional[str] = None) -> None:
        """
        Starts node synchronously. By default, program execution is blocked until node enters live mode (see
        `wait_for_live` parameter for details).

        Node starts from optional snapshot loading. Executes only if `load_snapshot_from` parameter is passed. Then can
        be performed optional replay, if `replay_from` parameter is passed. By default, full replay will be performed.
        It can be limited with `stop_at_block` parameter. Now node will try to synchronize with network. Synchronization
        can be optionally stopped at this moment with `exit_before_synchronization` parameter. During node
        synchronization program execution is blocked dependent on `wait_for_live` flag state. If node starting process
        takes too long and `timeout` exceeds, TimeoutError is raised and node is stopped.

        :param load_snapshot_from: Path to snapshot data directory. When provided, snapshot data are copied into node's
            directory and then node loads snapshot. Note that snapshot requires also block log and optionally block log
            index. These files should be in blockchain directory, at the same level as directory with snapshot files.
            For details see tutorial at:
            https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/tutorials/snapshot.md.
        :param replay_from: Path to block log (and optionally block log index), which will be replayed. When provided,
            given block log is copied into node's directory and then is used for replay. For details see tutorial at:
            https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/tutorials/replay.md.
        :param stop_at_block: Number of last block which should be replayed. After this block, replay is interrupted and
            synchronization starts.
        :param exit_before_synchronization: Stops node startup and closes node before synchronization.
        :param wait_for_live: Blocks program execution until node starts to generate or receive blocks.
        :param arguments: Additional arguments passed to node during running. Should be separated in the same way as in
            `subprocess.run` function.
        :param environment_variables: Additional environment variables passed to node run environment. If variable name
            is already defined, its value will be overwritten with one provided by this parameter.
        :param timeout: If `wait_for_live` is set to True, this parameter sets how long waiting can take. When timeout
            is reached, `TimeoutError` exception is thrown. Expressed in seconds.
        :param time_offset:
            Allows to change system date and time a node sees (without changing real OS time). Can be specified either
            absolutely, relatively and speed up or slow down clock. Value passed in `time_offset` is written to
            `FAKETIME` environment variable. For details and examples see libfaketime official documentation:
            https://github.com/wolfcw/libfaketime.
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
        """
        Stops node and immediately starts it again. Whole restart is performed synchronously. By default, program
        execution is blocked until node will enter live mode. This behavior can be modified with `wait_for_live`
        parameter. If node starting process takes too long and `timeout` exceeds, TimeoutError is raised and node is
        stopped.

        :param wait_for_live: Blocks program execution until node starts to generate or receive blocks.
        :param timeout: If `wait_for_live` is set to True, this parameter sets how long waiting can take. When timeout
            is reached, `TimeoutError` exception is thrown. Expressed in seconds.
        """
        return self.__implementation.restart(wait_for_live=wait_for_live, timeout=timeout)

    def set_cleanup_policy(self, policy: CleanupPolicy) -> None:
        """
        Specifies which files will be automatically removed at node's cleanup. For details see:
        https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/clean_up_policies.md

        :param policy: Cleanup is performed according to given policy.
        """
        return self.__implementation.set_cleanup_policy(policy)

    def wait_number_of_blocks(self, blocks_to_wait: int, *, timeout: float = math.inf) -> None:
        """
        Blocks program execution until number of new blocks specified by `blocks_to_wait` will be produced. For example
        if node's newest block is 10th and `blocks_to_wait` is set to 3, program execution will be resumed when node's
        newest block will be 13th. Maximum wait time can be limited with `timeout` parameter.

        :param blocks_to_wait: Number of blocks produced, after which execution will be resumed.
        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.

        See also similar methods: `wait_for_block_with_number` and `wait_until_block_will_be_irreversible`.
        """
        return self.__implementation.wait_number_of_blocks(blocks_to_wait, timeout=timeout)

    def wait_for_block_with_number(self, number: int, *, timeout: float = math.inf) -> None:
        """
        Blocks program execution until block with specified `number` is produced. If specified block number is already
        produced, program execution is immediately resumed. Maximum wait time can be limited with `timeout` parameter.

        :param number: Block's number produced, after which execution will be resumed.
        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.

        See also similar method: `wait_number_of_blocks`.
        """
        return self.__implementation.wait_for_block_with_number(number, timeout=timeout)

    def wait_until_block_will_be_irreversible(self, number_of_block: int, *, timeout: float = math.inf) -> None:
        """
        Blocks program execution until block with specified number by `number_of_block` will be irreversible. Maximum
        wait time can be limited with `timeout` parameter.

        :param number_of_block: When block with this number will be irreversible, execution will be resumed.
        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.
        """
        return self.__implementation.wait_until_block_will_be_irreversible(number_of_block, timeout=timeout)

    @property
    def ws_endpoint(self) -> str:
        """
        Returns opened WS endpoint. Blocks program execution if WS endpoint is not ready. When endpoint is configured
        with special values like 0.0.0.0 address or 0 port, special values are replaced with actually selected by node.
        """
        return self.__implementation.get_ws_endpoint()
