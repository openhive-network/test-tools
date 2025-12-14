from __future__ import annotations

import contextlib
import math
import os
import shutil
import time
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, cast, overload

from beekeepy.exceptions import CommunicationError, FailedToStartExecutableError
from beekeepy.handle.runnable import RunnableHandle
from beekeepy.interfaces import AnyUrl, HttpUrl, P2PUrl, Stopwatch, WsUrl
from beekeepy.settings import RunnableHandleSettings as Settings

from test_tools.__private import cleanup_policy, paths_to_executables
from test_tools.__private.base_node import BaseNode
from test_tools.__private.block_log import BlockLog
from test_tools.__private.constants import CleanupPolicy
from test_tools.__private.network import Network
from test_tools.__private.process.node_arguments import NodeArguments
from test_tools.__private.process.node_config import NodeConfig
from test_tools.__private.process.node_process import HivedVersionOutput, NodeProcess
from test_tools.__private.scope import ScopedObject, context
from test_tools.__private.snapshot import Snapshot
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.utilities.fake_time import configure_fake_time
from wax.helpy import StartTimeControl, TimeControl

if TYPE_CHECKING:
    from collections.abc import Callable

    from beekeepy.handle.runnable import PortMatchingResult

    from schemas.apis.app_status_api.fundaments_of_responses import WebserverItem
    from schemas.apis.app_status_api.response_schemas import GetAppStatus
    from schemas.apis.network_node_api.response_schemas import SetAllowedPeers
    from test_tools.__private.alternate_chain_specs import AlternateChainSpecs
    from test_tools.__private.executable_info import ExecutableInfo
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle
    from test_tools.__private.wallet.wallet import Wallet


class Node(RunnableHandle[NodeProcess, NodeConfig, NodeArguments, Settings], BaseNode, ScopedObject):
    # This pylint warning is right, but this refactor has low priority. Will be done later...

    DEFAULT_WAIT_FOR_LIVE_TIMEOUT = int(os.environ.get("TEST_TOOLS_NODE_DEFAULT_WAIT_FOR_LIVE_TIMEOUT", default=30))

    def __init__(self, *, name: str, network: NetworkHandle | None = None, handle: NodeHandle | None = None) -> None:
        self._set_name(name)
        self.__directory = context.get_current_directory().joinpath(self.get_name()).absolute()
        super().__init__(name=name, handle=handle)
        with self.update_settings() as settings:
            settings.working_directory = self.__directory
        del self.__directory
        self.__node_sink_id: int | None = None
        self.__produced_files = False

        self.__network: Network | None = get_implementation(network, Network) if network is not None else None
        if self.__network is not None:
            self.__network.add(self)

        self.__cleanup_policy: CleanupPolicy | None = None
        self.__alternate_chain_specs: AlternateChainSpecs | None = None

        self.__wallets: list[Wallet] = []

        self.__is_testnet: bool | None = None

    @property
    def config(self) -> NodeConfig:
        return self.__process.config

    @property
    def arguments(self) -> NodeArguments:
        return self.__process.arguments

    @property
    def __process(self) -> NodeProcess:
        return self._exec

    @property
    def __executable(self) -> ExecutableInfo:
        return self.__process.executable_info

    @property
    def config_file_path(self) -> Path:
        return self.directory / "config.ini"

    @property
    def directory(self) -> Path:
        return self.settings.ensured_working_directory

    def _get_settings(self) -> Settings:
        return self.settings

    def _construct_executable(self) -> NodeProcess:
        return NodeProcess(self.__directory, self.logger)

    def _unify_cli_arguments(self, working_directory: Path, http_endpoint: HttpUrl) -> None:
        """Empty to avoid writing obtained values to config."""

    def _unify_config(self, working_directory: Path, http_endpoint: HttpUrl) -> None:
        """Empty to avoid writing obtained values to config."""

    def _get_http_endpoint_from_cli_arguments(self) -> HttpUrl | None:
        return self.arguments.webserver_http_endpoint

    def _get_http_endpoint_from_config(self) -> HttpUrl | None:
        return self.config.webserver_http_endpoint

    def _get_working_directory_from_cli_arguments(self) -> Path | None:
        return self.arguments.data_dir

    def _setup_ports(self, ports: PortMatchingResult) -> None:
        assert ports.http is not None, "Http endpoint must be set"
        self.http_endpoint = ports.http

    def is_able_to_produce_blocks(self) -> bool:
        conditions = [
            self.config.enable_stale_production,
            self.config.required_participation == 0,
            bool(self.config.witness),
            bool(self.config.private_key),
        ]

        return all(conditions)

    @property
    def alternate_chain_specs(self) -> AlternateChainSpecs | None:
        return self.__alternate_chain_specs

    @property
    def block_log(self) -> BlockLog:
        """
        TODO: When setting of initial values of node config is restored, change the code below as follows.

        assert self.config.block_log_split is not None, "Should have been set on init!"
        return BlockLog(
            self.directory / "blockchain",
            "monolithic" if self.config.block_log_split == -1 else "split",
        )
        """
        return BlockLog(
            self.directory / "blockchain",
            "split"
            if self.config.block_log_split is None
            else "monolithic"
            if self.config.block_log_split == -1
            else "split",
        )

    def get_supported_plugins(self) -> list[str]:
        return self.__process.get_supported_plugins()

    def get_id(self) -> str:
        response = self.api.network_node.get_info()
        return response.node_id

    def set_allowed_nodes(self, nodes: list[Node]) -> SetAllowedPeers:
        return self.api.network_node.set_allowed_peers(allowed_peers=[node.get_id() for node in nodes])

    def get_version(self) -> HivedVersionOutput:  # type: ignore[override]
        return self.__process.version()

    def dump_config(self) -> NodeConfig:
        assert not self.is_running()
        return self.generate_default_config_from_executable()

    def dump_snapshot(self, *, name: str = "snapshot", close: bool = False, max_retries: int = 3) -> Snapshot:
        self.logger.info("Snapshot dumping started...")
        self.__ensure_that_plugin_required_for_snapshot_is_included()

        if not close:
            self.__close_wallets()

        self.close()

        # Retry logic to handle transient failures during snapshot dump (e.g., under CI load)
        for attempt in range(max_retries):
            try:
                self.__run_process(blocking=True, with_arguments=NodeArguments(dump_snapshot=name, exit_before_sync=True))
                break
            except FailedToStartExecutableError as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Snapshot dump failed (attempt {attempt + 1}/{max_retries}): {e}, retrying...")
                    time.sleep(1)
                else:
                    raise

        if not close:
            self.run()
            self.__run_wallets()

            # Each time the node is restarted, the first operation may not be possible to create because of expiration
            # time being checked. This is due to the loss of reversible blocks when the node is closed and the HEAD
            # block after restart is set to last irreversible.
            # The new operation fails because expiration time is compared to the last irreversible and may be exceeded.
            self.wait_number_of_blocks(1)

        self.logger.info("Snapshot dumped")

        return Snapshot(
            self.directory / "snapshot" / name,
            self.block_log,
            self,
        )

    def __ensure_that_plugin_required_for_snapshot_is_included(self) -> None:
        plugin_required_for_snapshots = "state_snapshot"
        if plugin_required_for_snapshots not in self.config.plugin:
            self.config.plugin.append(plugin_required_for_snapshots)

    def __close_wallets(self) -> None:
        for wallet in self.__wallets:
            wallet.close()

    def __run_wallets(self) -> None:
        for wallet in self.__wallets:
            wallet.run()

    def __run_process(
        self,
        *,
        blocking: bool,
        write_config_before_run: bool = True,
        with_arguments: NodeArguments | None = None,
        with_environment_variables: dict[str, str] | None = None,
        process_startup_timeout: float | None = None,
    ) -> None:
        process_startup_timeout = process_startup_timeout or self.settings.initialization_timeout.total_seconds()
        args = with_arguments or NodeArguments()
        args.data_dir = self.directory
        with self.__process.restore_arguments(with_arguments):
            self._run(
                blocking=blocking,
                environment_variables=with_environment_variables,
                save_config=write_config_before_run,
                perform_unification=False,
                timeout=process_startup_timeout,
            )

    def __enable_logging(self) -> None:
        self.__disable_logging()
        self.__node_sink_id: int | None = self.logger.add(self.directory / "latest.log")  # type: ignore[no-redef]

    def __disable_logging(self) -> None:
        if self.__node_sink_id is not None:
            self.logger.remove(self.__node_sink_id)
            self.__node_sink_id = None

    def run(  # noqa: C901, PLR0912, PLR0915
        self,
        *,
        load_snapshot_from: str | Path | Snapshot | None = None,
        replay_from: BlockLog | Path | str | None = None,
        stop_at_block: int | None = None,
        exit_at_block: int | None = None,
        exit_before_synchronization: bool = False,
        wait_for_live: bool | None = None,
        arguments: NodeArguments | list[str] | None = None,
        environment_variables: dict[str, str] | None = None,
        timeout: float = DEFAULT_WAIT_FOR_LIVE_TIMEOUT,
        time_control: TimeControl | None = None,
        alternate_chain_specs: AlternateChainSpecs | None = None,
        explicit_blocking: bool = False,
    ) -> None:
        """
        Runs node.

        :param wait_for_live: Stops execution until node will generate or receive blocks.
        :param timeout: If wait_for_live is set to True, this parameter sets how long waiting can take. When
                        timeout is reached, TimeoutError exception is thrown.
        :param arguments: Additional arguments passed to node during running. Should be separated in the same way as in
                          `subprocess.run` function.
        :param environment_variables: Additional environment variables passed to node run environment. If variable name
                                      is already defined, its value will be overwritten with one provided by this
                                      parameter.
        """
        # This pylint warning is right, but this refactor has low priority. Will be done later...

        self.__validate_timeout(timeout)
        process_startup_timeout: float | None = None
        assert time_control is None or isinstance(
            time_control, TimeControl
        ), "time_control can only be subclass of TimeControl class"
        deadline = time.time() + timeout

        self.__check_if_executable_is_built_in_supported_versions()

        if not self.__produced_files and self.directory.exists():
            shutil.rmtree(self.directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.__enable_logging()

        self.__set_unset_endpoints()
        self.__assure_that_app_status_api_is_enabled()
        arguments = self.__convert_to_node_arguments(arguments)
        log_message = f"Running {self}"

        additional_arguments = arguments or self.arguments.copy()
        if load_snapshot_from is not None:
            self.__handle_loading_snapshot(load_snapshot_from, additional_arguments)
            log_message += ", loading snapshot"

        if exit_at_block is not None and stop_at_block is not None:
            raise RuntimeError("exit_at_block and stop_at_block can't be used together")
        if stop_at_block is not None:
            additional_arguments.stop_at_block = stop_at_block
        if exit_at_block is not None:
            additional_arguments.exit_at_block = exit_at_block
        if alternate_chain_specs is not None or self.alternate_chain_specs is not None:
            if alternate_chain_specs is not None:  # write or override
                self.__alternate_chain_specs = alternate_chain_specs
            if self.__alternate_chain_specs is not None:
                destination = self.__alternate_chain_specs.export_to_file(self.directory).absolute()
                additional_arguments.alternate_chain_spec = destination
        if replay_from is not None:
            self.__handle_replay(replay_from, additional_arguments)
            log_message += ", replaying"

        environment_variables = environment_variables or dict(os.environ)

        if isinstance(time_control, TimeControl):
            if isinstance(time_control, StartTimeControl) and time_control.is_start_time_equal_to("head_block_time"):
                assert (
                    self.block_log.path.exists()
                ), "Block log directory does not exist. Block_log is necessary to use 'head_block_time' as time_control"
                assert (
                    self.block_log.block_files
                ), "Could not find block log file(s). Block_log is necessary to use 'head_block_time' as time_control"
                time_control.apply_head_block_time(self.block_log.get_head_block_time())

            time_control_str = time_control.as_string()
            self.logger.info(f"Setting FAKE_TIME for {self.get_name()} as: `{time_control_str}`")
            environment_variables.update(configure_fake_time(self._logger, time_control_str))

        if exit_at_block is not None or exit_before_synchronization or additional_arguments.exit_before_sync:
            if wait_for_live is not None:
                raise RuntimeError("wait_for_live can't be used with exit_before_synchronization")

            wait_for_live = False

            if exit_before_synchronization:
                additional_arguments.exit_before_sync = True

            self.logger.info(f"{log_message} and waiting for close...")
        elif wait_for_live is None or wait_for_live is True:
            wait_for_live = True
            self.logger.info(f"{log_message} and waiting for live...")
        else:
            self.logger.info(f"{log_message} and NOT waiting for live...")

        exit_before_synchronization = bool(exit_before_synchronization) or bool(additional_arguments.exit_before_sync)

        self._actions_before_run()
        blocking = explicit_blocking or exit_before_synchronization or bool(exit_at_block)
        if blocking:
            process_startup_timeout = math.inf
        with Stopwatch() as sw:
            self.__run_process(
                blocking=blocking,
                with_arguments=additional_arguments,
                with_environment_variables=environment_variables,
                process_startup_timeout=process_startup_timeout,
            )
        self.logger.info(f"Waiting for process start of {self.get_name()} took {sw.seconds_delta :.2f} seconds")

        if replay_from is not None and not blocking:
            self.__wait_for_replay_finish()

        self.__produced_files = True

        if not blocking:
            self.logger.info("Waiting for synchronization...")
            with Stopwatch() as sw:
                self.__wait_for_synchronization(
                    deadline=deadline,
                    wait_for_live=wait_for_live,
                    stop_at_block=stop_at_block,
                    is_queen_active=("queen" in self.config.plugin),
                )
            self.logger.info(f"Waiting for synchronization for {self.get_name()} took {sw.seconds_delta :.2f} seconds")

        self.__log_run_summary()

    def __wait_for_replay_finish(self) -> None:
        self.logger.info("Waiting for replay to finish...")
        with Stopwatch() as sw:
            self.__wait_for_status(
                deadline=math.inf,
                predicate=lambda _, s: "finished replaying" in s.statuses,
                message="replay was not finished",
            )
        self.logger.info(f"Replay for {self.get_name()} finished; took {sw.seconds_delta :.6f} seconds")

    def __calculate_timeout(self, deadline: float) -> float:
        return deadline - time.time()

    def __wait_for_synchronization(
        self, *, deadline: float, wait_for_live: bool, stop_at_block: int | None, is_queen_active: bool
    ) -> None:
        timeout = self.__calculate_timeout(deadline)
        if (stop_at_block is not None) or (is_queen_active) or wait_for_live:
            self.wait_for_api_or_live_mode(timeout=timeout)  # entering API mode

        timeout = self.__calculate_timeout(deadline)
        self.wait_for_chain_api_ready(timeout=timeout)  # chain API ready

    def _actions_before_run(self) -> None:
        """Override this method to hook just before starting node process."""

    def __handle_loading_snapshot(
        self, snapshot_source: str | Path | Snapshot, additional_arguments: NodeArguments
    ) -> None:
        if not isinstance(snapshot_source, Snapshot):
            snapshot_source = Path(snapshot_source)
            snapshot_source = Snapshot(
                snapshot_source,
                BlockLog(snapshot_source.joinpath("../../blockchain"), "auto"),
            )

        self.__ensure_that_plugin_required_for_snapshot_is_included()
        additional_arguments.load_snapshot = snapshot_source.name
        snapshot_source.copy_to(self.directory)

    def __convert_to_node_arguments(self, arguments: NodeArguments | list[str] | None) -> NodeArguments:
        if arguments is None:
            return NodeArguments()

        if isinstance(arguments, NodeArguments):
            return arguments

        return NodeArguments.parse_cli_input(arguments)

    def __handle_replay(self, replay_source: BlockLog | Path | str, additional_arguments: NodeArguments) -> None:
        if not isinstance(replay_source, BlockLog):
            """
            TODO: When setting of initial values of node config is restored, change the code below as follows.

            assert self.config.block_log_split is not None, "Should have been set on init!"
            replay_source = BlockLog(
                replay_source,
                "monolithic" if self.config.block_log_split == -1 else "split",
            )
            """
            replay_source = BlockLog(
                replay_source,
                "split"
                if self.config.block_log_split is None
                else "monolithic"
                if self.config.block_log_split == -1
                else "split",
            )

        additional_arguments.replay_blockchain = True

        block_log_directory = self.directory.joinpath("blockchain")
        if block_log_directory.exists() and additional_arguments.force_replay is True:
            shutil.rmtree(block_log_directory)
        block_log_directory.mkdir(exist_ok=True)
        replay_source.copy_to(block_log_directory, artifacts="optional")

    def __log_run_summary(self) -> None:
        if self.is_running():
            message = f"Run with pid {self.__process.pid}, "

            endpoints = self.__get_opened_endpoints()
            if endpoints:
                message += f'with servers: {", ".join([str(endpoint[0]) for endpoint in endpoints])}'
            else:
                message += "without any server"
        else:
            message = "Run completed"

        message += f", {self.__process.build_version} build"
        message += f" commit={self.__process.get_build_commit_hash()[:8]}"
        self.logger.info(message)

    def __get_opened_endpoints(self) -> list[tuple[str, str]]:
        endpoints = [
            (self.get_http_endpoint(), "http"),
            (self.get_ws_endpoint(), "ws"),
            (self.config.webserver_unix_endpoint, "unix"),
        ]

        return [endpoint for endpoint in endpoints if endpoint[0] is not None]  # type: ignore[misc]

    def __set_unset_endpoints(self) -> None:
        if self.config.p2p_endpoint is None:
            self.config.p2p_endpoint = P2PUrl("0.0.0.0:0")

        if self.config.webserver_http_endpoint is None:
            self.config.webserver_http_endpoint = HttpUrl("0.0.0.0:0")

        if self.config.webserver_ws_endpoint is None:
            self.config.webserver_ws_endpoint = WsUrl("0.0.0.0:0")

    def __assure_that_app_status_api_is_enabled(self) -> None:
        if "app_status_api" not in self.config.plugin:
            self.__process.config.plugin.append("app_status_api")

    def __check_if_executable_is_built_in_supported_versions(self) -> None:
        supported_builds = ["testnet", "mirrornet"]
        if self.__process.build_version not in supported_builds:
            raise NotImplementedError(
                f"You have configured a path to an unsupported version of the hived build.\n"
                f"At this moment only {supported_builds} builds are supported.\n"
                f'Your current hived path is: {paths_to_executables.get_path_of("hived")}\n'
                f"\n"
                f"Please check the following page if you need help with paths configuration:\n"
                f"https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/paths_to_executables.md"
            )

    def get_p2p_endpoint(self) -> P2PUrl:
        return cast(P2PUrl, self.__wait_for_endpoint(endpoint_t=P2PUrl, get_endpoint=lambda s: s.webservers.P2P))

    def get_http_endpoint(self) -> HttpUrl:
        return self.http_endpoint

    def get_ws_endpoint(self) -> WsUrl:
        return cast(WsUrl, self.__wait_for_endpoint(endpoint_t=WsUrl, get_endpoint=lambda s: s.webservers.WS))

    def __wait_for_endpoint(
        self, get_endpoint: Callable[[GetAppStatus], WebserverItem | None], endpoint_t: type[AnyUrl]
    ) -> AnyUrl:
        def retrieve(_: GetAppStatus, status: GetAppStatus) -> bool:
            return get_endpoint(status) is not None

        self.__wait_for_status(
            timeout=10.0,
            predicate=retrieve,
            message=f"{endpoint_t.__class__.__qualname__} webserver address not received in time",
        )
        endpoint = get_endpoint(self.api.app_status.get_app_status())
        assert endpoint is not None  # mypy check
        return endpoint_t.factory(port=endpoint.port, address=endpoint.address)

    def close(self) -> None:
        self.logger.info(f"Closing {self.get_name()}...")
        with Stopwatch() as sw:
            self.__process.close(self.settings.close_timeout.total_seconds())
            self.teardown()
        self.logger.info(f"Closed {self.get_name()} in {sw.seconds_delta :.2f} seconds")
        self.__disable_logging()

    def at_exit_from_scope(self) -> None:
        self.handle_final_cleanup()
        self._actions_after_final_cleanup()

    def handle_final_cleanup(self) -> None:
        self.close()
        self.__remove_files()

    def _actions_after_final_cleanup(self) -> None:
        """Override this method to hook just after handling the final cleanup."""

    def restart(
        self,
        wait_for_live: bool = True,
        timeout: float = DEFAULT_WAIT_FOR_LIVE_TIMEOUT,
        time_control: TimeControl | None = None,
        alternate_chain_specs: AlternateChainSpecs | None = None,
    ) -> None:
        self.close()
        self.run(
            wait_for_live=wait_for_live,
            timeout=timeout,
            time_control=time_control,
            alternate_chain_specs=alternate_chain_specs,
        )

    def __remove_files(self) -> None:
        policy = cleanup_policy.get_default() if self.__cleanup_policy is None else self.__cleanup_policy

        if policy == CleanupPolicy.DO_NOT_REMOVE_FILES:
            """For now this is not handled, but it's explicitly handled"""
        elif policy == CleanupPolicy.REMOVE_ONLY_UNNEEDED_FILES:
            self.__remove_unneeded_files()
        elif policy == CleanupPolicy.REMOVE_EVERYTHING:
            self.__remove_all_files()

    @staticmethod
    def __remove(path: Path) -> None:
        with suppress(FileNotFoundError):  # It is ok that file to remove was removed earlier or never existed
            shutil.rmtree(path) if path.is_dir() else path.unlink()

    def __remove_unneeded_files(self) -> None:
        unneeded_files_or_directories = [
            "blockchain/shared_memory.bin",
            "snapshot/",
        ]

        self.__register_rocksdb_data_to_remove(unneeded_files_or_directories)

        for unneeded in unneeded_files_or_directories:
            self.__remove(self.directory.joinpath(unneeded))

        artifact_files = BlockLog.get_existing_artifact_files(False, self.directory.joinpath("blockchain"))
        artifact_files.extend(BlockLog.get_existing_artifact_files(True, self.directory.joinpath("blockchain")))
        for unneeded_file in artifact_files:
            self.__remove(unneeded_file)

    def __register_rocksdb_data_to_remove(self, unneeded_files_or_directories: list[str]) -> None:
        rocksdb_directory = self.directory.joinpath("blockchain/account-history-rocksdb-storage")
        if not rocksdb_directory:
            return

        # All files below will be removed
        unneeded_files_or_directories.extend([path.as_posix() for path in rocksdb_directory.glob("*.sst")])

    def __remove_all_files(self) -> None:
        self.__remove(self.directory)

    def set_executable_file_path(self, executable_file_path: Path) -> None:
        self.__executable.set_path(executable_file_path)

    def set_cleanup_policy(self, policy: CleanupPolicy) -> None:
        self.__cleanup_policy = policy

    def wait_for_next_fork(self, timeout: float = math.inf) -> None:
        self.__validate_timeout(timeout)

        self.__wait_for_status(
            timeout=timeout,
            message="Fork did not happen on time.",
            predicate=lambda prev, curr: len(curr.forks) > len(prev.forks),
            previous_required=True,
        )

    def wait_for_live_mode(self, timeout: float = math.inf) -> None:
        self.__validate_timeout(timeout)
        self.__wait_for_status(
            timeout=timeout,
            predicate=lambda _, s: "entering live mode" in s.statuses,
            message=f"{self.get_name()}: Live mode not activated on time.",
        )

    def wait_for_api_or_live_mode(self, timeout: float = math.inf) -> None:
        self.__validate_timeout(timeout)
        self.__wait_for_status(
            timeout=timeout,
            predicate=lambda _, s: (("entering live mode" in s.statuses) or ("entering API mode" in s.statuses)),
            message=f"{self.get_name()}: API or live mode not activated on time.",
        )

    def wait_for_chain_api_ready(self, timeout: float = math.inf) -> None:
        self.__validate_timeout(timeout)
        self.__wait_for_status(
            timeout=timeout,
            predicate=lambda _, s: "chain API ready" in s.statuses,
            message=f"{self.get_name()}: Chain API not activated on time.",
        )

    def wait_for_api_mode(self, timeout: float = math.inf) -> None:
        self.__validate_timeout(timeout)
        self.__wait_for_status(
            timeout=timeout,
            predicate=lambda _, s: "entering API mode" in s.statuses,
            message=f"{self.get_name()}: API mode not activated on time.",
        )

    def get_number_of_forks(self) -> int:
        return len(self.api.app_status.get_app_status().forks)

    def register_wallet(self, wallet: Wallet) -> None:
        if wallet not in self.__wallets:
            self.__wallets.append(wallet)

    def unregister_wallet(self, wallet: Wallet) -> None:
        if wallet in self.__wallets:
            self.__wallets.remove(wallet)

    @overload
    def __wait_for_status(
        self,
        *,
        predicate: Callable[[GetAppStatus, GetAppStatus], bool],
        message: str,
        timeout: float,
        previous_required: bool = False,
    ) -> None:
        ...

    @overload
    def __wait_for_status(
        self,
        *,
        predicate: Callable[[GetAppStatus, GetAppStatus], bool],
        message: str,
        deadline: float,
        previous_required: bool = False,
    ) -> None:
        ...

    def __wait_for_status(
        self,
        *,
        predicate: Callable[[GetAppStatus, GetAppStatus], bool],
        message: str,
        timeout: float | None = None,
        deadline: float | None = None,
        previous_required: bool = False,
    ) -> None:
        """
        Waits for predicate to return true until deadline.

        Args:
        ----
            deadline: time till predicate will be checked
            timeout: time till predicate will be checked
            predicate: gets previous and current return from app_status_api.get_app_status and returns true if condition is fulfilled, false otherwise
            previous_required: if set to True there will be initial delay to acquire difference in app state
            message: message to be printed in case of timeout

        """
        assert (
            "app_status_api" in self.config.plugin
        ), "app_status_api is not enabled, enable it to allow test-tools properly handle hived binary"
        assert (timeout is not None and deadline is None) or (
            deadline is not None and timeout is None
        ), "only one of: timeout or deadline can and have to be set"
        start = time.time()

        def continue_waiting() -> bool:
            if timeout is not None:
                return (start + timeout) >= time.time()
            if deadline is not None:
                return deadline >= time.time()
            raise AssertionError("unknown decision path for timeout calculation")

        def get_status() -> GetAppStatus:
            while continue_waiting():
                with contextlib.suppress(CommunicationError):
                    return self.api.app_status.get_app_status()
            raise TimeoutError(f"cannot obtain app_status_api.get_app_status; {message}")

        if previous_required:
            previous_response = get_status()
            time.sleep(0.1)
        response = get_status()
        if not previous_required:
            previous_response = response

        while continue_waiting() and not predicate(previous_response, response):
            previous_response = response
            response = get_status()

        if not continue_waiting():
            raise TimeoutError(message)

    def __validate_timeout(self, timeout: float) -> None:
        if timeout < 0:
            raise TimeoutError(f"Timeout must be greater than or equal to 0, but is: {timeout :.4f}")

    def is_testnet(self) -> bool:
        if self.__is_testnet is None:
            self.__is_testnet = (self.get_version()["version"]["node_type"]) == "testnet"
        return self.__is_testnet
