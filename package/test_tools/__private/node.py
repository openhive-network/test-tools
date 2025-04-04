from __future__ import annotations

import contextlib
import math
import os
import shutil
import time
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

from beekeepy.interfaces import HttpUrl

from test_tools.__private import cleanup_policy, exceptions, paths_to_executables
from test_tools.__private.base_node import BaseNode
from test_tools.__private.block_log import BlockLog
from test_tools.__private.constants import CleanupPolicy
from test_tools.__private.executable import Executable
from test_tools.__private.network import Network
from test_tools.__private.notifications.node_notification_server import NodeNotificationServer
from test_tools.__private.process import Process
from test_tools.__private.scope import ScopedObject, context
from test_tools.__private.snapshot import Snapshot
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.wait_for import wait_for_event
from test_tools.node_configs.default import create_default_config
from wax.helpy._interfaces.time import StartTimeControl, TimeControl

if TYPE_CHECKING:
    from collections.abc import Sequence

    from beekeepy.interfaces import P2PUrl, WsUrl
    from loguru import Record

    from schemas.apis.network_node_api.response_schemas import SetAllowedPeers
    from test_tools.__private.alternate_chain_specs import AlternateChainSpecs
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle
    from test_tools.__private.wallet.wallet import Wallet


class Node(BaseNode, ScopedObject):
    # This pylint warning is right, but this refactor has low priority. Will be done later...

    DEFAULT_WAIT_FOR_LIVE_TIMEOUT = int(os.environ.get("TEST_TOOLS_NODE_DEFAULT_WAIT_FOR_LIVE_TIMEOUT", default=30))

    def __init__(self, *, name: str, network: NetworkHandle | None = None, handle: NodeHandle | None = None) -> None:
        super().__init__(name=name, handle=handle)
        self.directory = context.get_current_directory().joinpath(self.get_name()).absolute()
        self.__node_sink_id: int | None = None
        self.__notification_sink_id: int | None = None
        self.__produced_files = False

        self.__network: Network | None = get_implementation(network, Network) if network is not None else None
        if self.__network is not None:
            self.__network.add(self)

        self.__executable = Executable("hived")
        self.__process = Process(self.directory, self.__executable, self.logger)
        self.__notifications = self.__create_notifications_server()
        self.__cleanup_policy: CleanupPolicy | None = None
        self.__alternate_chain_specs: AlternateChainSpecs | None = None

        self.config = create_default_config()

        self.__wallets: list[Wallet] = []

    @property
    def config_file_path(self) -> Path:
        return self.directory / "config.ini"

    def __create_notifications_server(self) -> NodeNotificationServer:
        return NodeNotificationServer(
            node_name=self.get_name(),
            logger=self.logger.bind(notifications=True),
            notification_endpoint=self.settings.notification_endpoint,
        )

    def is_running(self) -> bool:
        return self.__process.is_running()

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

    @property
    def http_endpoint(self) -> HttpUrl:
        endpoint = self.__notifications.handler.http_endpoint
        assert endpoint is not None
        return endpoint

    @http_endpoint.setter
    def http_endpoint(self, value: object | str | HttpUrl | None) -> None:
        if value is None:
            value = HttpUrl("0.0.0.0:0", protocol="http")

        assert isinstance(value, str | HttpUrl)
        value = HttpUrl(value, protocol="http")
        self.config.webserver_http_endpoint = value.as_string(with_protocol=False)
        super().http_endpoint = value  #  type: ignore[misc]

    def get_supported_plugins(self) -> list[str]:
        return self.__executable.get_supported_plugins()

    def __wait_for_p2p_plugin_start(self, timeout: float = 10) -> None:
        if not self.__notifications.handler.p2p_plugin_started_event.wait(timeout=timeout):
            raise TimeoutError(f"Waiting too long for start of {self} p2p plugin")

    def __wait_for_http_listening(self, timeout: float = 10) -> None:
        if not self.__notifications.handler.http_listening_event.wait(timeout):
            raise TimeoutError(f"Waiting too long for {self} to start listening on http port")

    def __wait_for_ws_listening(self, timeout: float = 10) -> None:
        if not self.__notifications.handler.ws_listening_event.wait(timeout):
            raise TimeoutError(f"Waiting too long for {self} to start listening on ws port")

    def get_id(self) -> str:
        response = self.api.network_node.get_info()
        return response.node_id

    def set_allowed_nodes(self, nodes: list[Node]) -> SetAllowedPeers:
        return self.api.network_node.set_allowed_peers(allowed_peers=[node.get_id() for node in nodes])

    def get_version(self) -> dict[str, Any]:
        return self.__executable.get_version()

    def dump_config(self) -> None:
        assert not self.is_running()

        self.logger.info("Config dumping started...")

        config_was_modified = self.config != create_default_config()
        self.__run_process(blocking=True, with_arguments=["--dump-config"], write_config_before_run=config_was_modified)

        try:
            self.config.load_from_file(self.config_file_path)
        except KeyError as exception:
            raise exceptions.ConfigError(
                f"{self.get_name()} config dump failed because of entry not known to TestTools."
            ) from exception

        self.logger.info("Config dumped")

    def dump_snapshot(self, *, name: str = "snapshot", close: bool = False) -> Snapshot:
        self.logger.info("Snapshot dumping started...")
        self.__ensure_that_plugin_required_for_snapshot_is_included()

        if not close:
            self.__close_wallets()

        self.close()

        self.__run_process(
            blocking=True,
            with_arguments=[
                f"--dump-snapshot={name}",
                "--exit-before-sync",
            ],
        )

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
        with_arguments: Sequence[str] = (),
        with_environment_variables: dict[str, str] | None = None,
        with_time_control: str | None = None,
    ) -> None:
        self.__notifications = self.__create_notifications_server()
        port = self.__notifications.run()
        self.config.notifications_endpoint = f"127.0.0.1:{port}"
        self.directory.mkdir(exist_ok=True)

        if write_config_before_run:
            self.config.write_to_file(self.config_file_path)

        self.__process.run(
            blocking=blocking,
            with_arguments=with_arguments,
            with_time_control=with_time_control,
            with_environment_variables=with_environment_variables,
        )

        if blocking:
            self.__notifications.close()

    def __enable_logging(self) -> None:
        self.__disable_logging()

        def filter_function(record: Record) -> bool:
            return (
                record["extra"].get("notifications", False) is True
                and record["extra"].get("name", False) == self.get_name()
            )

        self.__node_sink_id: int | None = self.logger.add(self.directory / "latest.log")  # type: ignore[no-redef]
        self.__notification_sink_id: int | None = self.logger.add(  # type: ignore[no-redef]
            sink=self.directory / "notifications.log", level="DEBUG", enqueue=True, filter=filter_function
        )

    def __disable_logging(self) -> None:
        if self.__node_sink_id is not None:
            self.logger.remove(self.__node_sink_id)
            self.__node_sink_id = None
        if self.__notification_sink_id is not None:
            self.logger.remove(self.__notification_sink_id)
            self.__notification_sink_id = None

    def run(  # noqa: C901, PLR0912, PLR0915
        self,
        *,
        load_snapshot_from: str | Path | Snapshot | None = None,
        replay_from: BlockLog | Path | str | None = None,
        stop_at_block: int | None = None,
        exit_at_block: int | None = None,
        exit_before_synchronization: bool = False,
        wait_for_live: bool | None = None,
        arguments: list[str] | tuple[str, ...] = (),
        environment_variables: dict[str, str] | None = None,
        timeout: float = DEFAULT_WAIT_FOR_LIVE_TIMEOUT,
        time_control: TimeControl | str | None = None,
        alternate_chain_specs: AlternateChainSpecs | None = None,
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

        assert timeout >= 0
        deadline = time.time() + timeout

        self.__check_if_executable_is_built_in_supported_versions()

        if not self.__produced_files and self.directory.exists():
            shutil.rmtree(self.directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.__enable_logging()

        self.__set_unset_endpoints()

        log_message = f"Running {self}"

        additional_arguments = [*arguments]
        if load_snapshot_from is not None:
            self.__handle_loading_snapshot(load_snapshot_from, additional_arguments)
            log_message += ", loading snapshot"

        if exit_at_block is not None and stop_at_block is not None:
            raise RuntimeError("exit_at_block and stop_at_block can't be used together")
        if stop_at_block is not None:
            additional_arguments.append(f"--stop-at-block={stop_at_block}")
        if exit_at_block is not None:
            additional_arguments.append(f"--exit-at-block={exit_at_block}")
        if alternate_chain_specs is not None or self.alternate_chain_specs is not None:
            if alternate_chain_specs is not None:  # write or override
                self.__alternate_chain_specs = alternate_chain_specs
            if self.__alternate_chain_specs is not None:
                destination = self.__alternate_chain_specs.export_to_file(self.directory).absolute().as_posix()
                additional_arguments.append(f"--alternate-chain-spec={destination}")
        if replay_from is not None:
            self.__handle_replay(replay_from, additional_arguments)
            log_message += ", replaying"

        if isinstance(time_control, TimeControl):
            if isinstance(time_control, StartTimeControl) and time_control.is_start_time_equal_to("head_block_time"):
                assert (
                    self.block_log.path.exists()
                ), "Block log directory does not exist. Block_log is necessary to use 'head_block_time' as time_control"
                assert (
                    self.block_log.block_files
                ), "Could not find block log file(s). Block_log is necessary to use 'head_block_time' as time_control"
                time_control.apply_head_block_time(self.block_log.get_head_block_time())

            time_control = time_control.as_string()

        if exit_at_block is not None or exit_before_synchronization or "--exit-before-sync" in additional_arguments:
            if wait_for_live is not None:
                raise RuntimeError("wait_for_live can't be used with exit_before_synchronization")

            wait_for_live = False

            if exit_before_synchronization:
                additional_arguments.append("--exit-before-sync")

            self.logger.info(f"{log_message} and waiting for close...")
        elif wait_for_live is None or wait_for_live is True:
            wait_for_live = True
            self.logger.info(f"{log_message} and waiting for live...")
        else:
            self.logger.info(f"{log_message} and NOT waiting for live...")

        exit_before_synchronization = exit_before_synchronization or "--exit-before-sync" in additional_arguments

        self._actions_before_run()

        self.__run_process(
            blocking=exit_before_synchronization or bool(exit_at_block),
            with_arguments=additional_arguments,
            with_time_control=time_control,
            with_environment_variables=environment_variables,
        )

        if replay_from is not None and not exit_before_synchronization:
            self.__notifications.handler.replay_finished_event.wait()

        self.__produced_files = True

        if not exit_before_synchronization and exit_at_block is None:
            self.__wait_for_synchronization(deadline, timeout, wait_for_live, stop_at_block)

        self.__log_run_summary()

    def __wait_for_synchronization(
        self, deadline: float, timeout: float, wait_for_live: bool, stop_at_block: int | None
    ) -> None:
        wait_for_event(
            self.__notifications.handler.synchronization_started_event,
            deadline=deadline,
            exception_message="Synchronization not started on time.",
        )

        wait_for_event(
            self.__notifications.handler.http_listening_event,
            deadline=deadline,
            exception_message="HTTP server didn't start listening on time.",
        )

        wait_for_event(
            self.__notifications.handler.ws_listening_event,
            deadline=deadline,
            exception_message="WS server didn't start listening on time.",
        )

        if stop_at_block is not None or "queen" in self.config.plugin:
            self.wait_for_api_mode(timeout=timeout)
        elif wait_for_live:
            self.wait_for_live_mode(timeout=timeout)

        wait_for_event(
            self.__notifications.handler.chain_api_ready_event,
            deadline=deadline,
            exception_message="Node is not ready at time",
        )

    def _actions_before_run(self) -> None:
        """Override this method to hook just before starting node process."""

    def __handle_loading_snapshot(
        self, snapshot_source: str | Path | Snapshot, additional_arguments: list[str]
    ) -> None:
        if not isinstance(snapshot_source, Snapshot):
            snapshot_source = Path(snapshot_source)
            snapshot_source = Snapshot(
                snapshot_source,
                BlockLog(snapshot_source.joinpath("../../blockchain"), "auto"),
            )

        self.__ensure_that_plugin_required_for_snapshot_is_included()
        additional_arguments.append(f"--load-snapshot={snapshot_source.name}")
        with contextlib.suppress(
            shutil.SameFileError
        ):  # It's ok, just skip copying because user want to load node's own snapshot.
            snapshot_source.copy_to(self.directory)

    def __handle_replay(self, replay_source: BlockLog | Path | str, additional_arguments: list[str]) -> None:
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

        additional_arguments.append("--replay-blockchain")

        block_log_directory = self.directory.joinpath("blockchain")
        if block_log_directory.exists() and "--force-replay" in additional_arguments:
            shutil.rmtree(block_log_directory)
        block_log_directory.mkdir(exist_ok=True)
        replay_source.copy_to(block_log_directory, artifacts="optional")

    def __log_run_summary(self) -> None:
        if self.is_running():
            message = f"Run with pid {self.__process.get_id()}, "

            endpoints = self.__get_opened_endpoints()
            if endpoints:
                message += f'with servers: {", ".join([f"{endpoint[1]}://{endpoint[0]}" for endpoint in endpoints])}'
            else:
                message += "without any server"
        else:
            message = "Run completed"

        message += f", {self.__executable.build_version} build"
        message += f" commit={self.__executable.get_build_commit_hash()[:8]}"
        self.logger.info(message)

    def __get_opened_endpoints(self) -> list[tuple[str, str]]:
        endpoints = [
            (self.config.webserver_http_endpoint, "http"),
            (self.config.webserver_ws_endpoint, "ws"),
            (self.config.webserver_unix_endpoint, "unix"),
        ]

        return [endpoint for endpoint in endpoints if endpoint[0] is not None]  # type: ignore[misc]

    def __set_unset_endpoints(self) -> None:
        if self.config.p2p_endpoint is None:
            self.config.p2p_endpoint = "0.0.0.0:0"

        if self.config.webserver_http_endpoint is None:
            self.config.webserver_http_endpoint = "0.0.0.0:0"

        if self.config.webserver_ws_endpoint is None:
            self.config.webserver_ws_endpoint = "0.0.0.0:0"

    def __check_if_executable_is_built_in_supported_versions(self) -> None:
        supported_builds = ["testnet", "mirrornet"]
        if self.__executable.build_version not in supported_builds:
            raise NotImplementedError(
                f"You have configured a path to an unsupported version of the hived build.\n"
                f"At this moment only {supported_builds} builds are supported.\n"
                f'Your current hived path is: {paths_to_executables.get_path_of("hived")}\n'
                f"\n"
                f"Please check the following page if you need help with paths configuration:\n"
                f"https://gitlab.syncad.com/hive/test-tools/-/blob/master/documentation/paths_to_executables.md"
            )

    def get_p2p_endpoint(self) -> P2PUrl:
        self.__wait_for_p2p_plugin_start()
        assert self.__notifications.handler.p2p_endpoint is not None  # mypy check
        return self.__notifications.handler.p2p_endpoint

    def get_http_endpoint(self) -> HttpUrl:
        self.__wait_for_http_listening()
        assert self.__notifications.handler.http_endpoint is not None  # mypy check
        return self.__notifications.handler.http_endpoint

    def get_ws_endpoint(self) -> WsUrl:
        self.__wait_for_ws_listening()
        assert self.__notifications.handler.ws_endpoint is not None  # mypy check
        return self.__notifications.handler.ws_endpoint

    def close(self) -> None:
        self.__process.close()
        self.__notifications.close()
        self.teardown()
        self.__disable_logging()

    def at_exit_from_scope(self) -> None:
        self.handle_final_cleanup()
        self._actions_after_final_cleanup()

    def handle_final_cleanup(self) -> None:
        self.close()
        self.__process.close_opened_files()
        self.__remove_files()

    def _actions_after_final_cleanup(self) -> None:
        """Override this method to hook just after handling the final cleanup."""

    def restart(
        self,
        wait_for_live: bool = True,
        timeout: float = DEFAULT_WAIT_FOR_LIVE_TIMEOUT,
        time_control: TimeControl | str | None = None,
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
        assert timeout >= 0
        deadline = time.time() + timeout
        wait_for_event(
            self.__notifications.handler.switch_fork_event,
            deadline=deadline,
            exception_message="Fork did not happen on time.",
        )

    def wait_for_live_mode(self, timeout: float = math.inf) -> None:
        assert timeout >= 0
        deadline = time.time() + timeout
        wait_for_event(
            self.__notifications.handler.live_mode_entered_event,
            deadline=deadline,
            exception_message=f"{self.get_name()}: Live mode not activated on time.",
        )

    def wait_for_api_mode(self, timeout: float = math.inf) -> None:
        assert timeout >= 0
        deadline = time.time() + timeout
        wait_for_event(
            self.__notifications.handler.api_mode_entered_event,
            deadline=deadline,
            exception_message=f"{self.get_name()}: API mode not activated on time.",
        )

    def get_number_of_forks(self) -> int:
        return self.__notifications.handler.number_of_forks

    def register_wallet(self, wallet: Wallet) -> None:
        if wallet not in self.__wallets:
            self.__wallets.append(wallet)

    def unregister_wallet(self, wallet: Wallet) -> None:
        if wallet in self.__wallets:
            self.__wallets.remove(wallet)
