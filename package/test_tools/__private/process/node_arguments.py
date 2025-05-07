from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from beekeepy.handle.runnable import Arguments

from test_tools.__private.process.node_commons import ConfigurationCommonHived

if TYPE_CHECKING:
    from typing_extensions import Self

BacktraceAllowedValues = Literal["yes", "no"]
SinkAllowedValues = Literal["STDERR", "STDOUT", "WLOG", "ELOG", "DLOG", "ILOG"]
ReportTypes = Literal["NONE", "MINIMAL", "REGULAR", "FULL"]


class NodeArguments(Arguments, ConfigurationCommonHived):
    account_history_rocksdb_dump_balance_history: str | None = None
    account_history_rocksdb_stop_import_at_block: str | None = None
    advanced_benchmark: bool | None = None
    alternate_chain_spec: Path | None = None
    chain_id: str | None = None
    check_locks: bool | None = None
    config: Path | None = None
    data_dir: Path | None = None
    disable_get_block: bool | None = None
    dump_memory_details: bool | None = None
    dump_snapshot: str | None = None
    exit_at_block: int | None = None
    exit_before_sync: bool | None = None
    flush_state_interval: int | None = None
    force_replay: bool | None = None
    generate_completions: bool | None = None
    list_plugins: bool | None = None
    load_snapshot: str | None = None
    p2p_force_validate: bool | None = None
    process_snapshot_threads_num: str | None = None
    replay_blockchain: bool | None = None
    resync_blockchain: bool | None = None
    set_benchmark_interval: str | None = None
    skeleton_key: str | None = None
    statsd_record_on_replay: bool | None = None
    stop_at_block: int | None = None
    validate_database_invariants: bool | None = None
    validate_during_replay: bool | None = None

    class Config(Arguments.Config, ConfigurationCommonHived.Config):
        pass

    @classmethod
    def just_list_plugins(cls) -> Self:
        return cls(list_plugins=True)

    @classmethod
    def just_dump_config(cls) -> Self:
        return cls(dump_config=True, data_dir=Path())

    def _convert_member_value_to_string_default(self, member_value: Any) -> str | Any:
        raise NotImplementedError
