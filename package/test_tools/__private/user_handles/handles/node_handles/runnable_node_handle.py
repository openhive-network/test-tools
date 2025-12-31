from __future__ import annotations

import math
from typing import TYPE_CHECKING

from test_tools.__private.node import Node
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase

if TYPE_CHECKING:
    from pathlib import Path

    from beekeepy.interfaces import HttpUrl, P2PUrl, WsUrl

    from test_tools.__private.alternate_chain_specs import AlternateChainSpecs
    from test_tools.__private.block_log import BlockLog
    from test_tools.__private.constants import CleanupPolicy
    from test_tools.__private.process.node_arguments import NodeArguments
    from test_tools.__private.process.node_config import NodeConfig
    from test_tools.__private.process.node_process import HivedVersionOutput
    from test_tools.__private.snapshot import Snapshot
    from wax.helpy._interfaces.time import TimeControl


class RunnableNodeHandle(NodeHandleBase):
    DEFAULT_WAIT_FOR_LIVE_TIMEOUT = Node.DEFAULT_WAIT_FOR_LIVE_TIMEOUT

    @property
    def __implementation(self) -> Node:  # type: ignore[override]
        return get_implementation(self, Node)

    def close(self) -> None:
        """
        Stops node's process with SIGINT (same as Ctrl+C in terminal).

        If node doesn't stop within 10 seconds, is stopped with SIGKILL and warning about problems with closing is emitted.
        """
        return self.__implementation.close()

    @property
    def config(self) -> NodeConfig:
        """Provides way to edit node's configuration file."""
        return self.__implementation.config

    @property
    def config_file_path(self) -> Path:
        """Returns path to node's configuration file."""
        return self.__implementation.config_file_path

    @property
    def directory(self) -> Path:
        """Returns path to directory, where node runs and generates its files."""
        return self.__implementation.directory

    def dump_config(self) -> NodeConfig:
        """Saves node's config to file and returns it as object. Requires that node is not running."""
        return self.__implementation.dump_config()

    def dump_snapshot(self, *, name: str = "snapshot", close: bool = False) -> Snapshot:
        """
        Closes node and saves snapshot data to node's directory.

        By default, node after snapshot dumping is restarted, but can be left closed, with `close` flag set to True.

        :param close: If set to True, closes node after snapshot dumping. Otherwise, restarts node after dumping.
        :return: Snapshot object, which can be used by another node to load it at startup.
        """
        return self.__implementation.dump_snapshot(name=name, close=close)

    @property
    def block_log(self) -> BlockLog:
        """
        Returns block log object, containing paths to block log and block log artifacts.

        It is safe to get block log object when node is running, but copying or using
        for replay might lead to problems, because files referenced by block log object might be modified.

        :return: Block log object, which can be used by another node to perform replay.
        """
        return self.__implementation.block_log

    def run(
        self,
        *,
        load_snapshot_from: Snapshot | Path | str | None = None,
        replay_from: BlockLog | Path | str | None = None,
        stop_at_block: int | None = None,
        exit_at_block: int | None = None,
        exit_before_synchronization: bool = False,
        wait_for_live: bool | None = None,
        arguments: NodeArguments | None = None,
        environment_variables: dict[str, str] | None = None,
        timeout: float = DEFAULT_WAIT_FOR_LIVE_TIMEOUT,
        time_control: TimeControl | None = None,
        alternate_chain_specs: AlternateChainSpecs | None = None,
        explicit_blocking: bool = False,
        max_retries: int = 1,
    ) -> None:
        """
        Starts node synchronously. By default, program execution is blocked until node enters live mode (see `wait_for_live` parameter for details).

        Node starts from optional snapshot loading. Executes only if `load_snapshot_from` parameter is passed. Then can
        be performed optional replay, if `replay_from` parameter is passed. By default, full replay will be performed.
        After that, the node will try to synchronize with network.
        Both replay and synchronization can be limited to a given block number with `stop_at_block` parameter.
        Synchronization can also be stopped with `exit_before_synchronization` parameter. During node
        synchronization program execution is blocked if `wait_for_live` flag if set. If node starting process
        takes too long and `timeout` exceeds, TimeoutError is raised and node is stopped.

        :param load_snapshot_from: Path to snapshot data directory. When provided, snapshot data are copied into node's
            directory and then node loads snapshot. Note that snapshot requires also block log and optionally block log
            artifacts. These files should be in blockchain directory, at the same level as directory with snapshot
            files. For details see tutorial at:
            https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/tutorials/snapshot.md.
        :param replay_from: Path to block log (and optionally block log artifacts), which will be replayed. When
            provided, given block log is copied into node's directory and then is used for replay. For details see
            tutorial at: https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/tutorials/replay.md.
        :param stop_at_block: Number of last block which should be replayed/synchronized. After this block,
            replay/sync is interrupted and web server starts.
        :param exit_before_synchronization: Stops node startup and closes node before synchronization.
        :param wait_for_live: Blocks program execution until node starts to generate or receive blocks.
        :param arguments: Additional arguments passed to node during running. Should be separated in the same way as in
            `subprocess.run` function.
        :param environment_variables: Additional environment variables passed to node run environment. If variable name
            is already defined, its value will be overwritten with one provided by this parameter.
        :param timeout: If `wait_for_live` is set to True, this parameter sets how long waiting can take. When timeout
            is reached, `TimeoutError` exception is thrown. Expressed in seconds.
        :param time_control:
            Allows to change system date and time a node sees (without changing real OS time). Can be specified either
            absolutely, relatively and speed up or slow down clock. TimeControl object is resolved to proper
            `FAKETIME` environment variable. For details and examples see libfaketime official documentation:
            https://github.com/wolfcw/libfaketime.
        :param alternate_chain_specs:
            Allows to change few properties of blockchain so it acts for example faster in certain ways to reduce duration
            of tests. If it is used once it is cached and will be used after restart and future runs for this
            instance of hived, even if it's not passed directly.
        :param max_retries:
            Number of times to retry node startup in case of transient errors.
        """
        return self.__implementation.run(
            load_snapshot_from=load_snapshot_from,
            replay_from=replay_from,
            stop_at_block=stop_at_block,
            exit_at_block=exit_at_block,
            exit_before_synchronization=exit_before_synchronization,
            wait_for_live=wait_for_live,
            arguments=arguments,
            environment_variables=environment_variables,
            timeout=timeout,
            time_control=time_control,
            alternate_chain_specs=alternate_chain_specs,
            explicit_blocking=explicit_blocking,
            max_retries=max_retries,
        )

    def restart(
        self,
        wait_for_live: bool = True,
        timeout: float | None = None,
        time_control: TimeControl | None = None,
        alternate_chain_specs: AlternateChainSpecs | None = None,
        max_retries: int | None = None,
    ) -> None:
        """
        Stops node and immediately starts it again. Whole restart is performed synchronously.

        By default, program execution is blocked until node will enter live mode. This behavior can be modified with
        `wait_for_live` parameter. If node starting process takes too long and `timeout` exceeds,
        TimeoutError is raised and node is stopped.

        :param wait_for_live: Blocks program execution until node starts to generate or receive blocks.
        :param timeout: If `wait_for_live` is set to True, this parameter sets how long waiting can take. When timeout
            is reached, `TimeoutError` exception is thrown. Expressed in seconds. If None, inherits from last run().
        :param time_control:
            See parameter ``time_control`` in :func:`run`.
        :param alternate_chain_specs:
            See parameter ``alternate_chain_specs`` in :func:`run`.
        :param max_retries:
            See parameter ``max_retries`` in :func:`run`. If None, inherits from last run().
        """
        return self.__implementation.restart(
            wait_for_live=wait_for_live,
            timeout=timeout,
            time_control=time_control,
            alternate_chain_specs=alternate_chain_specs,
            max_retries=max_retries,
        )

    def set_cleanup_policy(self, policy: CleanupPolicy) -> None:
        """
        Specifies which files will be automatically removed at node's cleanup.

        For details see: https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/clean_up_policies.md.

        :param policy: Cleanup is performed according to given policy.
        """
        return self.__implementation.set_cleanup_policy(policy)

    def wait_for_live_mode(self, timeout: float = math.inf) -> None:
        """
        Blocks program execution until node is in live mode. It's detected by waiting for `hive_status` notification.

        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.
        """
        self.__implementation.wait_for_live_mode(timeout=timeout)

    def get_version(self) -> HivedVersionOutput:
        """Returns output from hived for --version flag."""
        return self.__implementation.get_version()

    @property
    def http_endpoint(self) -> HttpUrl:
        """
        Returns opened HTTP endpoint.

        Blocks program execution if HTTP endpoint is not ready. When endpoint is configured with special
        values like 0.0.0.0 address or 0 port, special values are replaced with actually selected by node.
        """
        return self.__implementation.get_http_endpoint()

    @property
    def ws_endpoint(self) -> WsUrl:
        """
        Returns opened WS endpoint.

        Blocks program execution if WS endpoint is not ready. When endpoint is configured with special values
        like 0.0.0.0 address or 0 port, special values are replaced with actually selected by node.
        """
        return self.__implementation.get_ws_endpoint()

    @property
    def p2p_endpoint(self) -> P2PUrl:
        """
        Returns opened P2P endpoint.

        Blocks program execution if WS endpoint is not ready. When endpoint is configured with special
        values like 0.0.0.0 address or 0 port, special values are replaced with actually selected by node.
        """
        return self.__implementation.get_p2p_endpoint()

    @property
    def alternate_chain_specs(self) -> AlternateChainSpecs | None:
        """Returns chain spec that is currently used by this node. If none is used, None will be returned."""
        return self.__implementation.alternate_chain_specs
