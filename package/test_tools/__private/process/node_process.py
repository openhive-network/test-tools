from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.fields.version import HiveVersionFromExecutable  # noqa: TC001
from test_tools.__private.executable_info import ExecutableInfo
from test_tools.__private.process.node_arguments import NodeArguments
from test_tools.__private.process.node_config import NodeConfig
from test_tools.__private.process.process import Process

if TYPE_CHECKING:
    from beekeepy.handle.runnable import AutoCloser
    from loguru import Logger

    from schemas.fields.basic import NodeType


class HivedVersionOutput(PreconfiguredBaseModel):
    version: HiveVersionFromExecutable


class NodeProcess(Process[NodeConfig, NodeArguments]):
    def __init__(self, directory: Path | str, logger: Logger) -> None:
        super().__init__(directory, ExecutableInfo("hived"), logger)

    @property
    def build_version(self) -> NodeType:
        return self.version().version.node_type

    def get_build_commit_hash(self) -> str:
        return self.version().version.hive_revision

    def version(self) -> HivedVersionOutput:  # type: ignore[override]
        assert self.executable_info.executable_name == "hived", "version can only be checked for hived binary!"
        return HivedVersionOutput.parse_raw(super().version())

    def get_supported_plugins(self) -> list[str]:
        return self.run_and_get_output(arguments=self.arguments.just_list_plugins()).split("\n")

    def run(
        self,
        *,
        blocking: bool,
        save_config: bool = True,
        propagate_sigint: bool = False,
        with_arguments: NodeArguments | None = None,
        with_environment_variables: dict[str, str] | None = None,
        with_time_control: str | None = None,
    ) -> AutoCloser:
        with self.restore_arguments(new_arguments=with_arguments):
            if save_config:
                self.config.save(self.working_directory)
            return super().run(
                blocking=blocking,
                propagate_sigint=propagate_sigint,
                with_arguments=with_arguments,
                with_environment_variables=with_environment_variables,
                with_time_control=with_time_control,
            )

    def _construct_arguments(self) -> NodeArguments:
        return NodeArguments(data_dir=Path())

    def _construct_config(self) -> NodeConfig:
        return NodeConfig.default()
