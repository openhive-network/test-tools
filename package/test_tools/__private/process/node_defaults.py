# fmt: off
# ruff: noqa
from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from beekeepy._communication import HttpUrl, P2PUrl, WsUrl  # noqa: TCH002
from msgspec import field

from schemas._preconfigured_base_model import PreconfiguredBaseModel


class NodeDefaults(PreconfiguredBaseModel):
    DEFAULT_ACCOUNT_HISTORY_ROCKSDB_BLACKLIST_OPS: ClassVar[list[str]] = []
    DEFAULT_ACCOUNT_HISTORY_ROCKSDB_PATH: ClassVar[Path] = field(default_factory=lambda: Path("blockchain/account-history-rocksdb-storage"))
    DEFAULT_ACCOUNT_HISTORY_ROCKSDB_TRACK_ACCOUNT_RANGE: ClassVar[list[str]] = []
    DEFAULT_ACCOUNT_HISTORY_ROCKSDB_WHITELIST_OPS: ClassVar[list[str]] = []
    DEFAULT_ALTERNATE_CHAIN_SPEC: ClassVar[str | None] = None
    DEFAULT_BACKTRACE: ClassVar[str] = "yes"
    DEFAULT_BLOCK_DATA_EXPORT_FILE: ClassVar[str] = "NONE"
    DEFAULT_BLOCK_DATA_SKIP_EMPTY: ClassVar[bool] = False
    DEFAULT_BLOCK_LOG_COMPRESSION_LEVEL: ClassVar[str] = "15"
    DEFAULT_BLOCK_LOG_INFO_PRINT_FILE: ClassVar[str] = "ILOG"
    DEFAULT_BLOCK_LOG_INFO_PRINT_INTERVAL_SECONDS: ClassVar[str] = "86400"
    DEFAULT_BLOCK_LOG_INFO_PRINT_IRREVERSIBLE: ClassVar[bool] = True
    DEFAULT_BLOCK_LOG_SPLIT: ClassVar[str] = "9999"
    DEFAULT_BLOCK_STATS_REPORT_OUTPUT: ClassVar[str] = "ILOG"
    DEFAULT_BLOCK_STATS_REPORT_TYPE: ClassVar[str] = "FULL"
    DEFAULT_BLOCKCHAIN_THREAD_POOL_SIZE: ClassVar[int] = 8
    DEFAULT_CASHOUT_LOGGING_ENDING_BLOCK: ClassVar[int | None] = None
    DEFAULT_CASHOUT_LOGGING_LOG_PATH_DIR: ClassVar[Path | None] = None
    DEFAULT_CASHOUT_LOGGING_STARTING_BLOCK: ClassVar[int | None] = None
    DEFAULT_CHECKPOINT: ClassVar[list[str]] = []
    DEFAULT_COLONY_ARTICLE: ClassVar[str | None] = None
    DEFAULT_COLONY_CUSTOM: ClassVar[str | None] = None
    DEFAULT_COLONY_NO_BROADCAST: ClassVar[bool] = False
    DEFAULT_COLONY_REPLY: ClassVar[str | None] = None
    DEFAULT_COLONY_SIGN_WITH: ClassVar[list[str]] = []
    DEFAULT_COLONY_START_AT_BLOCK: ClassVar[int] = 0
    DEFAULT_COLONY_THREADS: ClassVar[int] = 4
    DEFAULT_COLONY_TRANSACTIONS_PER_BLOCK: ClassVar[int | None] = None
    DEFAULT_COLONY_TRANSFER: ClassVar[str | None] = None
    DEFAULT_COLONY_VOTE: ClassVar[str | None] = None
    DEFAULT_DEBUG_NODE_EDIT_SCRIPT: ClassVar[list[str]] = []
    DEFAULT_ENABLE_BLOCK_LOG_AUTO_FIXING: ClassVar[bool] = True
    DEFAULT_ENABLE_BLOCK_LOG_COMPRESSION: ClassVar[bool] = True
    DEFAULT_ENABLE_STALE_PRODUCTION: ClassVar[bool] = False
    DEFAULT_FLUSH_STATE_INTERVAL: ClassVar[int | None] = None
    DEFAULT_LOG_APPENDER: ClassVar[list[str]] = field(default_factory=lambda: [
        """{"appender":"stderr","stream":"std_error","time_format":"iso_8601_microseconds"}""",
        """{"appender":"p2p","file":"logs/p2p/p2p.log","time_format":"iso_8601_milliseconds"}"""
    ])
    DEFAULT_LOG_CONSOLE_APPENDER: ClassVar[list[str]] = []
    DEFAULT_LOG_FILE_APPENDER: ClassVar[list[str]] = []
    DEFAULT_LOG_JSON_RPC: ClassVar[Path | None] = None
    DEFAULT_LOG_LOGGER: ClassVar[list[str]] = field(default_factory=lambda: [
        """{"name":"default","level":"info","appenders":["stderr"]}""",
        """{"name":"user","level":"debug","appenders":["stderr"]}""",
        """{"name":"p2p","level":"warn","appenders":["p2p"]}"""
    ])
    DEFAULT_MARKET_HISTORY_BUCKET_SIZE: ClassVar[str] = "[15,60,300,3600,86400]"
    DEFAULT_MARKET_HISTORY_BUCKETS_PER_SIZE: ClassVar[int] = 5760
    DEFAULT_MAX_MEMPOOL_SIZE: ClassVar[str] = "100M"
    DEFAULT_NOTIFICATIONS_ENDPOINT: ClassVar[list[P2PUrl]] = []
    DEFAULT_P2P_ENDPOINT: ClassVar[P2PUrl | None] = None
    DEFAULT_P2P_MAX_CONNECTIONS: ClassVar[int | None] = None
    DEFAULT_P2P_PARAMETERS: ClassVar[str | None] = None
    DEFAULT_P2P_SEED_NODE: ClassVar[list[str]] = []
    DEFAULT_PACEMAKER_MAX_OFFSET: ClassVar[str] = "20000"
    DEFAULT_PACEMAKER_MIN_OFFSET: ClassVar[str] = "-300"
    DEFAULT_PACEMAKER_SOURCE: ClassVar[Path | None] = None
    DEFAULT_PLUGIN: ClassVar[list[str]] = field(default_factory=lambda: [
        "witness",
        "account_by_key",
        "account_by_key_api",
        "state_snapshot"
    ])
    DEFAULT_PRIVATE_KEY: ClassVar[list[str]] = []
    DEFAULT_QUEEN_BLOCK_SIZE: ClassVar[int] = 0
    DEFAULT_QUEEN_TX_COUNT: ClassVar[int] = 0
    DEFAULT_RC_FLOOD_LEVEL: ClassVar[str] = "20"
    DEFAULT_RC_FLOOD_SURCHARGE: ClassVar[str] = "10000"
    DEFAULT_RC_STATS_REPORT_OUTPUT: ClassVar[str] = "ILOG"
    DEFAULT_RC_STATS_REPORT_TYPE: ClassVar[str] = "REGULAR"
    DEFAULT_REQUIRED_PARTICIPATION: ClassVar[int] = 33
    DEFAULT_SHARED_FILE_DIR: ClassVar[Path] = field(default_factory=lambda: Path("blockchain"))
    DEFAULT_SHARED_FILE_FULL_THRESHOLD: ClassVar[str] = "0"
    DEFAULT_SHARED_FILE_SCALE_RATE: ClassVar[str] = "0"
    DEFAULT_SHARED_FILE_SIZE: ClassVar[str] = "24G"
    DEFAULT_SNAPSHOT_ROOT_DIR: ClassVar[Path] = field(default_factory=lambda: Path("snapshot"))
    DEFAULT_STATSD_BATCHSIZE: ClassVar[int] = 1
    DEFAULT_STATSD_BLACKLIST: ClassVar[list[str]] = []
    DEFAULT_STATSD_ENDPOINT: ClassVar[P2PUrl | None] = None
    DEFAULT_STATSD_WHITELIST: ClassVar[list[str]] = []
    DEFAULT_TRANSACTION_STATUS_BLOCK_DEPTH: ClassVar[int] = 64000
    DEFAULT_WEBSERVER_HTTP_ENDPOINT: ClassVar[HttpUrl | None] = None
    DEFAULT_WEBSERVER_HTTPS_CERTIFICATE_FILE_NAME: ClassVar[str | None] = None
    DEFAULT_WEBSERVER_HTTPS_ENDPOINT: ClassVar[HttpUrl | None] = None
    DEFAULT_WEBSERVER_HTTPS_KEY_FILE_NAME: ClassVar[str | None] = None
    DEFAULT_WEBSERVER_THREAD_POOL_SIZE: ClassVar[int] = 32
    DEFAULT_WEBSERVER_UNIX_ENDPOINT: ClassVar[P2PUrl | None] = None
    DEFAULT_WEBSERVER_WS_DEFLATE: ClassVar[bool] = False
    DEFAULT_WEBSERVER_WS_ENDPOINT: ClassVar[WsUrl | None] = None
    DEFAULT_WITNESS: ClassVar[list[str]] = []
    DEFAULT_ACCOUNT_HISTORY_ROCKSDB_DUMP_BALANCE_HISTORY: ClassVar[str | None] = None
    DEFAULT_ACCOUNT_HISTORY_ROCKSDB_STOP_IMPORT_AT_BLOCK: ClassVar[int] = 0
    DEFAULT_ADVANCED_BENCHMARK: ClassVar[bool] = False
    DEFAULT_CHAIN_ID: ClassVar[str] = "18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"
    DEFAULT_CHECK_LOCKS: ClassVar[bool] = False
    DEFAULT_COMMENTS_ROCKSDB_PATH: ClassVar[Path] = field(default_factory=lambda: Path("comments-rocksdb-storage"))
    DEFAULT_CONFIG: ClassVar[Path] = field(default_factory=lambda: Path("config.ini"))
    DEFAULT_DATA_DIR: ClassVar[Path | None] = None
    DEFAULT_DISABLE_GET_BLOCK: ClassVar[bool] = False
    DEFAULT_DUMP_CONFIG: ClassVar[bool] = False
    DEFAULT_DUMP_MEMORY_DETAILS: ClassVar[bool] = False
    DEFAULT_DUMP_OPTIONS: ClassVar[bool] = False
    DEFAULT_DUMP_SNAPSHOT: ClassVar[str | None] = None
    DEFAULT_EXIT_AT_BLOCK: ClassVar[int | None] = None
    DEFAULT_EXIT_BEFORE_SYNC: ClassVar[bool] = False
    DEFAULT_FORCE_REPLAY: ClassVar[bool] = False
    DEFAULT_GENERATE_COMPLETIONS: ClassVar[bool] = False
    DEFAULT_HELP_: ClassVar[bool] = False
    DEFAULT_LIST_PLUGINS: ClassVar[bool] = False
    DEFAULT_LOAD_SNAPSHOT: ClassVar[str | None] = None
    DEFAULT_P2P_FORCE_VALIDATE: ClassVar[bool] = False
    DEFAULT_PROCESS_SNAPSHOT_THREADS_NUM: ClassVar[int | None] = None
    DEFAULT_REPLAY_BLOCKCHAIN: ClassVar[bool] = False
    DEFAULT_RESYNC_BLOCKCHAIN: ClassVar[bool] = False
    DEFAULT_SET_BENCHMARK_INTERVAL: ClassVar[int | None] = None
    DEFAULT_SKELETON_KEY: ClassVar[str] = "5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n"
    DEFAULT_STATSD_RECORD_ON_REPLAY: ClassVar[bool] = False
    DEFAULT_STOP_AT_BLOCK: ClassVar[int | None] = None
    DEFAULT_VALIDATE_DATABASE_INVARIANTS: ClassVar[bool] = False
    DEFAULT_VALIDATE_DURING_REPLAY: ClassVar[bool] = False
    DEFAULT_VERSION_: ClassVar[bool] = False
