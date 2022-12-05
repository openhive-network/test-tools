from __future__ import annotations

import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
from threading import Event
import time
from typing import Dict, List, Literal, NoReturn, Optional, Tuple, TYPE_CHECKING, Union
import warnings

from test_tools.__private import cleanup_policy, communication, exceptions, paths_to_executables
from test_tools.__private.block_log import BlockLog
from test_tools.__private.constants import CleanupPolicy
from test_tools.__private.logger.logger_internal_interface import logger
from test_tools.__private.node_http_server import NodeHttpServer
from test_tools.__private.node_message import NodeMessage
from test_tools.__private.node_option import NodeOption
from test_tools.__private.raise_exception_helper import RaiseExceptionHelper
from test_tools.__private.scope import context, ScopedObject
from test_tools.__private.snapshot import Snapshot
from test_tools.__private.time.time import Time
from test_tools.__private.url import Url
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation
from test_tools.__private.utilities.fake_time import configure_fake_time
from test_tools.__private.wait_for import wait_for_event
from test_tools.node_api.node_apis import Apis
from test_tools.node_configs.default import create_default_config

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle
    from test_tools.__private.wallet import Wallet


class Node(UserHandleImplementation, ScopedObject):
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    # This pylint warning is right, but this refactor has low priority. Will be done later...

    DEFAULT_WAIT_FOR_LIVE_TIMEOUT = int(os.environ.get("TEST_TOOLS_NODE_DEFAULT_WAIT_FOR_LIVE_TIMEOUT", default=20))

    class __Executable:
        def __init__(self):
            self.__path = None

        def get_path(self):
            return paths_to_executables.get_path_of("hived") if self.__path is None else self.__path

        def set_path(self, path):
            self.__path = path

        @property
        def build_version(self) -> Literal["testnet", "mirrornet", "mainnet"]:
            return self.get_version()["version"]["node_type"]

        def get_build_commit_hash(self):
            return self.get_version()["version"]["hive_revision"]

        def get_version(self):
            return json.loads(self.__run_and_get_output("--version"))

        def __run_and_get_output(self, *arguments):
            result = subprocess.check_output(
                [str(self.get_path()), *arguments],
                stderr=subprocess.STDOUT,
            )

            return result.decode("utf-8").strip()

        def get_supported_plugins(self) -> List[str]:
            output = self.__run_and_get_output("--list-plugins")
            return output.split("\n")

        @property
        def config_options(self) -> List[NodeOption]:
            output = self.__run_and_get_output("--dump-options")
            return list(map(NodeOption.from_dict, json.loads(output)["config_file"]))

        @property
        def cli_options(self) -> List[NodeOption]:
            output = self.__run_and_get_output("--dump-options")
            return list(map(NodeOption.from_dict, json.loads(output)["command_line"]))

    class __Process:
        def __init__(self, directory, executable, logger):
            self.__process = None
            self.__directory = Path(directory).absolute()
            self.__executable = executable
            self.__logger = logger
            self.__files = {
                "stdout": None,
                "stderr": None,
            }

        def run(self, *, blocking, with_arguments=(), with_environment_variables=None, with_time_offset=None):
            self.__directory.mkdir(exist_ok=True)
            self.__prepare_files_for_streams()

            command = [str(self.__executable.get_path()), "-d", ".", *with_arguments]
            self.__logger.debug(" ".join(item for item in command))

            environment_variables = dict(os.environ)

            if with_environment_variables is not None:
                environment_variables.update(with_environment_variables)

            if with_time_offset is not None:
                configure_fake_time(self.__logger, environment_variables, with_time_offset)

            if blocking:
                subprocess.run(
                    command,
                    cwd=self.__directory,
                    **self.__files,
                    env=environment_variables,
                    check=True,
                )
            else:
                # pylint: disable=consider-using-with
                # Process created here have to exist longer than current scope
                self.__process = subprocess.Popen(
                    command,
                    cwd=self.__directory,
                    env=environment_variables,
                    **self.__files,
                )

        def get_id(self):
            return self.__process.pid

        def __prepare_files_for_streams(self):
            for name, file in self.__files.items():
                if file is None:
                    # pylint: disable=consider-using-with
                    # Files opened here have to exist longer than current scope
                    self.__files[name] = open(self.__directory.joinpath(f"{name}.txt"), "w", encoding="utf-8")

        def close(self):
            if self.__process is None:
                return

            self.__process.send_signal(signal.SIGINT)
            try:
                return_code = self.__process.wait(timeout=10)
                self.__logger.debug(f"Closed with {return_code} return code")
            except subprocess.TimeoutExpired:
                self.__process.kill()
                self.__process.wait()
                warnings.warn("Process was force-closed with SIGKILL, because didn't close before timeout")

            self.__process = None

        def close_opened_files(self):
            for name, file in self.__files.items():
                if file is not None:
                    file.close()
                    self.__files[name] = None

        def is_running(self):
            if not self.__process:
                return False

            return self.__process.poll() is None

        def get_stderr_file_path(self):
            stderr_file = self.__files["stderr"]
            return Path(stderr_file.name) if stderr_file is not None else None

    class __NotificationsServer:
        def __init__(self, node: "Node", logger):
            self.node: "Node" = node
            self.server = NodeHttpServer(self, name=f"{self.node}.NotificationsServer")
            self.__logger = logger

            self.http_listening_event = Event()
            self.http_endpoint: Optional[str] = None

            self.ws_listening_event = Event()
            self.ws_endpoint: Optional[str] = None

            self.p2p_plugin_started_event = Event()
            self.p2p_endpoint: Optional[str] = None

            self.synchronization_started_event = Event()
            self.live_mode_entered_event = Event()

            self.replay_finished_event = Event()

            self.snapshot_dumped_event = Event()

            self.switch_fork_event = Event()
            self.number_of_forks = 0

        def listen(self):
            self.node.config.notifications_endpoint = f"127.0.0.1:{self.server.port}"
            self.server.run()

            self.__logger.debug(f"Notifications server is listening on {self.node.config.notifications_endpoint}...")

        def notify(self, message):
            if message["name"] == "webserver listening":
                details = message["value"]
                if details["type"] == "HTTP":
                    endpoint = f'{details["address"].replace("0.0.0.0", "127.0.0.1")}:{details["port"]}'
                    self.http_endpoint = Url(endpoint, protocol="http").as_string(with_protocol=False)
                    self.http_listening_event.set()
                elif details["type"] == "WS":
                    endpoint = f'{details["address"].replace("0.0.0.0", "127.0.0.1")}:{details["port"]}'
                    self.ws_endpoint = Url(endpoint, protocol="ws").as_string(with_protocol=False)
                    self.ws_listening_event.set()
            elif message["name"] == "hived_status":
                details = message["value"]
                if details["current_status"] == "finished replaying":
                    self.replay_finished_event.set()
                elif details["current_status"] == "finished dumping snapshot":
                    self.snapshot_dumped_event.set()
                elif details["current_status"] == "syncing":
                    self.synchronization_started_event.set()
                elif details["current_status"] == "entering live mode":
                    self.live_mode_entered_event.set()
            elif message["name"] == "P2P listening":
                details = message["value"]
                endpoint = f'{details["address"].replace("0.0.0.0", "127.0.0.1")}:{details["port"]}'
                self.p2p_endpoint = Url(endpoint).as_string(with_protocol=False)
                self.p2p_plugin_started_event.set()
            elif message["name"] == "switching forks":
                self.number_of_forks += 1
                self.switch_fork_event.set()
                self.switch_fork_event.clear()
            elif message["name"] == "error":
                RaiseExceptionHelper.raise_exception_in_main_thread(
                    exceptions.InternalNodeError(f'{self.node}: {message["value"]["message"]}')
                )

            self.__logger.info(f"Received message: {message}")

        def close(self):
            self.server.close()

            self.http_listening_event.clear()
            self.ws_listening_event.clear()
            self.p2p_plugin_started_event.clear()
            self.synchronization_started_event.clear()
            self.live_mode_entered_event.clear()
            self.replay_finished_event.clear()
            self.snapshot_dumped_event.clear()
            self.switch_fork_event.clear()

            self.__logger.debug("Notifications server closed")

    def __init__(self, *, name, network: Optional[Network] = None, handle: Optional[NodeHandle] = None):
        super().__init__(handle=handle)

        self.api = Apis(self)

        self.__name = context.names.register_numbered_name(name)
        self.directory = context.get_current_directory().joinpath(self.__name).absolute()
        self.__produced_files = False
        self.__logger = logger.create_child_logger(self.__name)

        self.__network: Optional[Network] = network
        if self.__network is not None:
            self.__network.add(self)

        self.__executable = self.__Executable()
        self.__process = self.__Process(self.directory, self.__executable, self.__logger)
        self.__notifications = self.__NotificationsServer(self, self.__logger)
        self.__cleanup_policy = None

        self.config = create_default_config()

        self.__wallets: List[Wallet] = []

    def __str__(self):
        return self.__name

    def __repr__(self) -> str:
        return str(self)

    @property
    def config_file_path(self):
        return self.directory / "config.ini"

    def is_running(self):
        return self.__process.is_running()

    def is_able_to_produce_blocks(self):
        conditions = [
            self.config.enable_stale_production,
            self.config.required_participation == 0,
            bool(self.config.witness),
            bool(self.config.private_key),
        ]

        return all(conditions)

    def get_name(self):
        return self.__name

    @property
    def block_log(self) -> BlockLog:
        return BlockLog(self.directory.joinpath("blockchain/block_log"))

    def get_supported_plugins(self) -> List[str]:
        return self.__executable.get_supported_plugins()

    @property
    def config_options(self) -> List[NodeOption]:
        return self.__executable.config_options

    @property
    def cli_options(self) -> List[NodeOption]:
        return self.__executable.cli_options

    def wait_number_of_blocks(self, blocks_to_wait, *, timeout=math.inf):
        assert blocks_to_wait > 0
        self.wait_for_block_with_number(self.get_last_block_number() + blocks_to_wait, timeout=timeout)

    def wait_for_block_with_number(self, number, *, timeout=math.inf):
        Time.wait_for(
            lambda: self.__is_block_with_number_reached(number),
            timeout=timeout,
            timeout_error_message=f"Waiting too long for block {number}",
            poll_time=2.0,
        )

    def __is_block_with_number_reached(self, number):
        last = self.get_last_block_number()
        return last >= number

    def wait_for_irreversible_block(
        self, number: Optional[int] = None, *, max_blocks_to_wait: Optional[int] = None, timeout=math.inf
    ) -> None:
        def __is_number_param_given() -> bool:
            return number is not None

        def __is_max_blocks_to_wait_param_given() -> bool:
            return max_blocks_to_wait is not None

        last_block_number = self.get_last_block_number()
        target_block_number = number if __is_number_param_given() else last_block_number
        max_wait_block_number = (
            last_block_number + max_blocks_to_wait if __is_max_blocks_to_wait_param_given() else None
        )

        log_message = f"Waiting for block with number `{target_block_number}` to become irreversible..."

        if __is_max_blocks_to_wait_param_given():
            log_message += f" (max wait block number: `{max_wait_block_number}`)"

        self.__logger.info(log_message)

        Time.wait_for(
            lambda: self.__is_block_with_number_irreversible(target_block_number, max_wait_block_number),
            timeout=timeout,
            timeout_error_message=f"Waiting too long for irreversible block {target_block_number}",
            poll_time=2.0,
        )

    def __is_block_with_number_irreversible(self, number: int, max_wait_block_number: Optional[int]) -> bool:
        if max_wait_block_number is not None:
            self.__assert_block_with_number_reached_irreversibility_before_limit(number, max_wait_block_number)

        last_irreversible_block_number = self.get_last_irreversible_block_number()
        return last_irreversible_block_number >= number

    def __assert_block_with_number_reached_irreversibility_before_limit(
        self, number: int, max_wait_block_number: int
    ) -> Optional[NoReturn]:
        def __expected_block_was_reached_but_is_still_not_irreversible() -> bool:
            return last_block_number >= max_wait_block_number and last_irreversible_block_number < number

        response = self.api.database.get_dynamic_global_properties()  # to avoid 2 calls to the node
        last_block_number = response["head_block_number"]
        last_irreversible_block_number = response["last_irreversible_block_num"]

        if __expected_block_was_reached_but_is_still_not_irreversible():
            raise exceptions.BlockWaitTimeoutError(
                f"Block with number `{last_block_number}` was just reached but expected `{number}` is still not"
                f" irreversible.\n"
                f"Last irreversible block number is `{last_irreversible_block_number}`."
            )

    def get_last_block_number(self):
        response = self.api.database.get_dynamic_global_properties()
        return response["head_block_number"]

    def get_last_irreversible_block_number(self) -> int:
        response = self.api.database.get_dynamic_global_properties()
        return response["last_irreversible_block_num"]

    def get_current_witness(self) -> str:
        response = self.api.database.get_dynamic_global_properties()
        return response["current_witness"]

    def __wait_for_p2p_plugin_start(self, timeout=10):
        if not self.__notifications.p2p_plugin_started_event.wait(timeout=timeout):
            raise TimeoutError(f"Waiting too long for start of {self} p2p plugin")

    def send(self, method, params=None, jsonrpc="2.0", id_=1, *, only_result: bool = True):
        if self.config.webserver_http_endpoint is None:
            raise Exception("Webserver http endpoint is unknown")

        endpoint = f"http://{self.get_http_endpoint()}"

        self.__wait_for_http_listening()

        message = NodeMessage(method, params, jsonrpc, id_).as_json()
        response = communication.request(endpoint, message)

        return response["result"] if only_result else response

    def __wait_for_http_listening(self, timeout=10):
        if not self.__notifications.http_listening_event.wait(timeout):
            raise TimeoutError(f"Waiting too long for {self} to start listening on http port")

    def __wait_for_ws_listening(self, timeout=10):
        if not self.__notifications.ws_listening_event.wait(timeout):
            raise TimeoutError(f"Waiting too long for {self} to start listening on ws port")

    def get_id(self):
        response = self.api.network_node.get_info()
        return response["node_id"]

    def set_allowed_nodes(self, nodes):
        return self.api.network_node.set_allowed_peers(allowed_peers=[node.get_id() for node in nodes])

    def get_version(self):
        return self.__executable.get_version()

    def dump_config(self):
        assert not self.is_running()

        self.__logger.info("Config dumping started...")

        config_was_modified = self.config != create_default_config()
        self.__run_process(blocking=True, with_arguments=["--dump-config"], write_config_before_run=config_was_modified)

        try:
            self.config.load_from_file(self.config_file_path)
        except KeyError as exception:
            raise exceptions.ConfigError(
                f"{self.get_name()} config dump failed because of entry not known to TestTools."
            ) from exception

        self.__logger.info("Config dumped")

    def dump_snapshot(self, *, close=False):
        self.__logger.info("Snapshot dumping started...")
        self.__ensure_that_plugin_required_for_snapshot_is_included()

        if not close:
            self.__close_wallets()

        self.close()

        snapshot_path = Path(".")
        self.__run_process(
            blocking=close,
            with_arguments=[
                f"--dump-snapshot={snapshot_path}",
                *(["--exit-before-sync"] if close else []),
            ],
        )

        if not close:
            self.__notifications.snapshot_dumped_event.wait()
            self.__run_wallets()

            # Each time the node is restarted, the first operation may not be possible to create because of expiration
            # time being checked. This is due to the loss of reversible blocks when the node is closed and the HEAD
            # block after restart is set to last irreversible.
            # The new operation fails because expiration time is compared to the last irreversible and may be exceeded.
            self.wait_number_of_blocks(1)

        self.__logger.info("Snapshot dumped")

        return Snapshot(
            self.directory / "snapshot" / snapshot_path,
            self.directory / "blockchain/block_log",
            self.directory / "blockchain/block_log.artifacts",
            self,
        )

    def __ensure_that_plugin_required_for_snapshot_is_included(self):
        plugin_required_for_snapshots = "state_snapshot"
        if plugin_required_for_snapshots not in self.config.plugin:
            self.config.plugin.append(plugin_required_for_snapshots)

    def __close_wallets(self):
        for wallet in self.__wallets:
            wallet.close()

    def __run_wallets(self):
        for wallet in self.__wallets:
            wallet.run()

    def __run_process(
        self,
        *,
        blocking,
        write_config_before_run=True,
        with_arguments=(),
        with_environment_variables=None,
        with_time_offset=None,
    ):
        self.__notifications.listen()

        if write_config_before_run:
            self.config.write_to_file(self.config_file_path)

        self.__process.run(
            blocking=blocking,
            with_arguments=with_arguments,
            with_time_offset=with_time_offset,
            with_environment_variables=with_environment_variables,
        )

        if blocking:
            self.__notifications.close()

    def run(
        self,
        *,
        load_snapshot_from=None,
        replay_from=None,
        stop_at_block=None,
        exit_before_synchronization: bool = False,
        wait_for_live=None,
        arguments: Union[List[str], Tuple[str, ...]] = (),
        environment_variables: Optional[Dict] = None,
        timeout=DEFAULT_WAIT_FOR_LIVE_TIMEOUT,
        time_offset=None,
    ):
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
        # pylint: disable=too-many-branches
        # This pylint warning is right, but this refactor has low priority. Will be done later...

        assert timeout >= 0
        deadline = time.time() + timeout

        self.__check_if_executable_is_built_in_supported_versions()

        if not self.__produced_files and self.directory.exists():
            shutil.rmtree(self.directory)
        self.directory.mkdir(parents=True, exist_ok=True)

        self.__set_unset_endpoints()

        log_message = f"Running {self}"

        additional_arguments = [*arguments]
        if load_snapshot_from is not None:
            self.__handle_loading_snapshot(load_snapshot_from, additional_arguments)
            log_message += ", loading snapshot"

        if replay_from is not None:
            self.__handle_replay(replay_from, stop_at_block, additional_arguments)
            log_message += ", replaying"

        if exit_before_synchronization or "--exit-after-replay" in additional_arguments:
            if wait_for_live is not None:
                raise RuntimeError("wait_for_live can't be used with exit_before_synchronization")

            wait_for_live = False

            if exit_before_synchronization:
                additional_arguments.append("--exit-before-sync")

            self.__logger.info(f"{log_message} and waiting for close...")
        elif wait_for_live is None:
            wait_for_live = True
            self.__logger.info(f"{log_message} and waiting for live...")
        else:
            self.__logger.info(f"{log_message} and NOT waiting for live...")

        exit_before_synchronization = exit_before_synchronization or "--exit-after-replay" in additional_arguments
        self.__run_process(
            blocking=exit_before_synchronization,
            with_arguments=additional_arguments,
            with_time_offset=time_offset,
            with_environment_variables=environment_variables,
        )

        if replay_from is not None and not exit_before_synchronization:
            self.__notifications.replay_finished_event.wait()

        self.__produced_files = True

        if not exit_before_synchronization:
            wait_for_event(
                self.__notifications.synchronization_started_event,
                deadline=deadline,
                exception_message="Synchronization not started on time.",
            )

            wait_for_event(
                self.__notifications.http_listening_event,
                deadline=deadline,
                exception_message="HTTP server didn't start listening on time.",
            )

            wait_for_event(
                self.__notifications.ws_listening_event,
                deadline=deadline,
                exception_message="WS server didn't start listening on time.",
            )

            if wait_for_live:
                self.wait_for_live_mode(timeout=timeout)

        self.__log_run_summary()

    def __handle_loading_snapshot(self, snapshot_source: Union[str, Path, Snapshot], additional_arguments: list):
        if not isinstance(snapshot_source, Snapshot):
            snapshot_source = Snapshot(
                snapshot_source,
                Path(snapshot_source).joinpath("../blockchain/block_log"),
                Path(snapshot_source).joinpath("../blockchain/block_log.artifacts"),
            )

        self.__ensure_that_plugin_required_for_snapshot_is_included()
        additional_arguments.append("--load-snapshot=.")
        snapshot_source.copy_to(self.directory)

    def __handle_replay(self, replay_source: BlockLog, stop_at_block: int, additional_arguments: list):
        if not isinstance(replay_source, BlockLog):
            replay_source = BlockLog(replay_source)

        additional_arguments.append("--force-replay")
        if stop_at_block is not None:
            additional_arguments.append(f"--stop-replay-at-block={stop_at_block}")

        block_log_directory = self.directory.joinpath("blockchain")
        block_log_directory.mkdir()
        replay_source.copy_to(block_log_directory / "block_log", artifacts="optional")

    def __log_run_summary(self):
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
        self.__logger.info(message)

    def __get_opened_endpoints(self):
        endpoints = [
            (self.config.webserver_http_endpoint, "http"),
            (self.config.webserver_ws_endpoint, "ws"),
            (self.config.webserver_unix_endpoint, "unix"),
        ]

        return [endpoint for endpoint in endpoints if endpoint[0] is not None]

    def __set_unset_endpoints(self):
        if self.config.p2p_endpoint is None:
            self.config.p2p_endpoint = "0.0.0.0:0"

        if self.config.webserver_http_endpoint is None:
            self.config.webserver_http_endpoint = "0.0.0.0:0"

        if self.config.webserver_ws_endpoint is None:
            self.config.webserver_ws_endpoint = "0.0.0.0:0"

    def __check_if_executable_is_built_in_supported_versions(self) -> Optional[NoReturn]:
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

    def get_p2p_endpoint(self):
        self.__wait_for_p2p_plugin_start()
        return self.__notifications.p2p_endpoint

    def get_http_endpoint(self):
        self.__wait_for_http_listening()
        return self.__notifications.http_endpoint

    def get_ws_endpoint(self):
        self.__wait_for_ws_listening()
        return self.__notifications.ws_endpoint

    def close(self):
        self.__process.close()
        self.__notifications.close()

    def at_exit_from_scope(self):
        self.handle_final_cleanup()

    def handle_final_cleanup(self):
        self.close()
        self.__process.close_opened_files()
        self.__remove_files()

    def restart(self, wait_for_live=True, timeout=DEFAULT_WAIT_FOR_LIVE_TIMEOUT, time_offset: Optional[str] = None):
        self.__close_wallets()
        self.close()
        self.run(wait_for_live=wait_for_live, timeout=timeout, time_offset=time_offset)
        self.__run_wallets()

    def __remove_files(self):
        policy = cleanup_policy.get_default() if self.__cleanup_policy is None else self.__cleanup_policy

        if policy == CleanupPolicy.DO_NOT_REMOVE_FILES:
            pass
        elif policy == CleanupPolicy.REMOVE_ONLY_UNNEEDED_FILES:
            self.__remove_unneeded_files()
        elif policy == CleanupPolicy.REMOVE_EVERYTHING:
            self.__remove_all_files()

    @staticmethod
    def __remove(path: Path):
        try:
            shutil.rmtree(path) if path.is_dir() else path.unlink()
        except FileNotFoundError:
            pass  # It is ok that file to remove was removed earlier or never existed

    def __remove_unneeded_files(self):
        unneeded_files_or_directories = [
            "blockchain/shared_memory.bin",
            "blockchain/block_log.artifacts",
            "snapshot/",
        ]

        self.__register_rocksdb_data_to_remove(unneeded_files_or_directories)

        for unneeded in unneeded_files_or_directories:
            self.__remove(self.directory.joinpath(unneeded))

    def __register_rocksdb_data_to_remove(self, unneeded_files_or_directories):
        rocksdb_directory = self.directory.joinpath("blockchain/account-history-rocksdb-storage")
        if not rocksdb_directory:
            return

        # All files below will be removed
        unneeded_files_or_directories.extend(
            [
                *rocksdb_directory.glob("*.sst"),
            ]
        )

    def __remove_all_files(self):
        self.__remove(self.directory)

    def set_executable_file_path(self, executable_file_path):
        self.__executable.set_path(executable_file_path)

    def set_cleanup_policy(self, policy: CleanupPolicy):
        self.__cleanup_policy = policy

    def wait_for_next_fork(self, timeout=math.inf):
        assert timeout >= 0
        deadline = time.time() + timeout
        wait_for_event(
            self.__notifications.switch_fork_event, deadline=deadline, exception_message="Fork did not happen on time."
        )

    def wait_for_live_mode(self, timeout=math.inf):
        assert timeout >= 0
        deadline = time.time() + timeout
        wait_for_event(
            self.__notifications.live_mode_entered_event,
            deadline=deadline,
            exception_message="Live mode not activated on time.",
        )

    def get_number_of_forks(self):
        return self.__notifications.number_of_forks

    def register_wallet(self, wallet: Wallet) -> None:
        if wallet not in self.__wallets:
            self.__wallets.append(wallet)

    def unregister_wallet(self, wallet: Wallet) -> None:
        if wallet in self.__wallets:
            self.__wallets.remove(wallet)
