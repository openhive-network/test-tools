# fmt: off
# ruff: noqa
from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._executable.abc.arguments import Arguments
from msgspec import field

from test_tools.__private.process.node_common import NodeCommon
from test_tools.__private.process.node_defaults import NodeDefaults

if TYPE_CHECKING:
    from pathlib import Path


# All config items are automatically generated
class NodeArguments(NodeCommon, Arguments):
    """Parameters used in command line."""

    @classmethod
    def just_list_plugins(cls) -> NodeArguments:
        return cls(list_plugins=True)

    account_history_rocksdb_dump_balance_history: str | None = NodeDefaults.DEFAULT_ACCOUNT_HISTORY_ROCKSDB_DUMP_BALANCE_HISTORY
    """
    Dumps balances for all tracked accounts to a CSV file every time they change
    """

    account_history_rocksdb_stop_import_at_block: int = NodeDefaults.DEFAULT_ACCOUNT_HISTORY_ROCKSDB_STOP_IMPORT_AT_BLOCK
    """
    Allows to specify block number, the data import process should stop at.
    """

    advanced_benchmark: bool = NodeDefaults.DEFAULT_ADVANCED_BENCHMARK
    """
    Make profiling for every plugin.
    """

    chain_id: str = NodeDefaults.DEFAULT_CHAIN_ID
    """
    chain ID to connect to
    """

    check_locks: bool = NodeDefaults.DEFAULT_CHECK_LOCKS
    """
    Check correctness of chainbase locking
    """

    comments_rocksdb_path: Path = NodeDefaults.DEFAULT_COMMENTS_ROCKSDB_PATH
    """
    the location of the comments data files
    """

    config: Path = NodeDefaults.DEFAULT_CONFIG
    """
    Configuration file name relative to data-dir
    """

    data_dir: Path | None = NodeDefaults.DEFAULT_DATA_DIR
    """
    Directory containing configuration file config.ini. Default location: $HOME/.hived or CWD/. hived
    """

    disable_get_block: bool = NodeDefaults.DEFAULT_DISABLE_GET_BLOCK
    """
    Disable get_block API call
    """

    dump_config: bool = NodeDefaults.DEFAULT_DUMP_CONFIG
    """
    Dump configuration and exit
    """

    dump_memory_details: bool = NodeDefaults.DEFAULT_DUMP_MEMORY_DETAILS
    """
    Dump database objects memory usage info. Use set-benchmark-interval to set dump interval.
    """

    dump_options: bool = NodeDefaults.DEFAULT_DUMP_OPTIONS
    """
    Dump information about all supported command line and config options in JSON format and exit
    """

    dump_snapshot: str | None = NodeDefaults.DEFAULT_DUMP_SNAPSHOT
    """
    Allows to force immediate snapshot dump at plugin startup. All data in the snaphsot storage are overwritten
    """

    exit_at_block: int | None = NodeDefaults.DEFAULT_EXIT_AT_BLOCK
    """
    Same as --stop-at-block, but also exit the application
    """

    exit_before_sync: bool = NodeDefaults.DEFAULT_EXIT_BEFORE_SYNC
    """
    Exits before starting sync, handy for dumping snapshot without starting replay
    """

    force_replay: bool = NodeDefaults.DEFAULT_FORCE_REPLAY
    """
    Before replaying clean all old files. If specifed, `--replay-blockchain` flag is implied
    """

    generate_completions: bool = NodeDefaults.DEFAULT_GENERATE_COMPLETIONS
    """
    Generate bash auto-complete script (try: eval "$(hived --generate-completions)")
    """

    help_: bool = field(name="help", default=NodeDefaults.DEFAULT_HELP_)
    """
    Print this help message and exit.
    """

    list_plugins: bool = NodeDefaults.DEFAULT_LIST_PLUGINS
    """
    Print names of all available plugins and exit
    """

    load_snapshot: str | None = NodeDefaults.DEFAULT_LOAD_SNAPSHOT
    """
    Allows to force immediate snapshot import at plugin startup. All data in state storage are overwritten
    """

    p2p_force_validate: bool = NodeDefaults.DEFAULT_P2P_FORCE_VALIDATE
    """
    Force validation of all transactions.
    """

    process_snapshot_threads_num: int | None = NodeDefaults.DEFAULT_PROCESS_SNAPSHOT_THREADS_NUM
    """
    Number of threads intended for snapshot processing. By default set to detected available threads count.
    """

    replay_blockchain: bool = NodeDefaults.DEFAULT_REPLAY_BLOCKCHAIN
    """
    clear chain database and replay all blocks
    """

    resync_blockchain: bool = NodeDefaults.DEFAULT_RESYNC_BLOCKCHAIN
    """
    clear chain database and block log
    """

    set_benchmark_interval: int | None = NodeDefaults.DEFAULT_SET_BENCHMARK_INTERVAL
    """
    Print time and memory usage every given number of blocks
    """

    skeleton_key: str = NodeDefaults.DEFAULT_SKELETON_KEY
    """
    WIF PRIVATE key to be used as skeleton key for all accounts
    """

    statsd_record_on_replay: bool = NodeDefaults.DEFAULT_STATSD_RECORD_ON_REPLAY
    """
    Records statsd events during replay
    """

    stop_at_block: int | None = NodeDefaults.DEFAULT_STOP_AT_BLOCK
    """
    Stop after reaching given block number
    """

    validate_database_invariants: bool = NodeDefaults.DEFAULT_VALIDATE_DATABASE_INVARIANTS
    """
    Validate all supply invariants check out
    """

    validate_during_replay: bool = NodeDefaults.DEFAULT_VALIDATE_DURING_REPLAY
    """
    Runs all validations that are normally turned off during replay
    """

    version_: bool = field(name="version", default=NodeDefaults.DEFAULT_VERSION_)
    """
    Print version information.
    """
