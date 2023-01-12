"""Begin of machine generated code"""

# pylint: disable=line-too-long too-many-instance-attributes too-many-statements too-few-public-methods

from test_tools.__private.node_config_entry_types import Boolean, Integer, List, PrivateKey, String, StringQuoted


class NodeConfigAttributes:
    """Stores all attributes."""

    def __init__(self):
        self.__enter_initialization_stage()
        self.__initialize()
        self.__exit_initialization_stage()

    def __enter_initialization_stage(self):
        super().__setattr__("_initialization_stage", None)

    def __exit_initialization_stage(self):
        super().__delattr__("_initialization_stage")

    def __initialize(self):

        super().__setattr__(f"_{self.__class__.__name__}__entries", {})

        self.log_appender = List(
            String
        )  # Appender definition json: {"appender", "stream", "file"} Can only specify a file OR a stream
        self.log_console_appender = List(String)
        self.log_file_appender = List(String)
        self.log_logger = List(String)  # Logger definition json: {"name", "level", "appender"}
        self.notifications_endpoint = List(
            String, single_line=False
        )  # list of addresses, that will receive notification about in-chain events
        self.backtrace = String()  # Whether to print backtrace on SIGSEGV
        self.plugin = List(String)  # Plugin(s) to enable, may be specified multiple times
        self.account_history_rocksdb_path = (
            StringQuoted()
        )  # The location of the rocksdb database for account history. By default it is $DATA_DIR/blockchain/account-history-rocksdb-storage
        self.account_history_rocksdb_track_account_range = List(
            String, single_line=False
        )  # Defines a range of accounts to track as a json pair ["from","to"] [from,to] Can be specified multiple times.
        self.account_history_rocksdb_whitelist_ops = List(
            String
        )  # Defines a list of operations which will be explicitly logged.
        self.account_history_rocksdb_blacklist_ops = List(
            String
        )  # Defines a list of operations which will be explicitly ignored.
        self.block_data_export_file = String()  # Where to export data (NONE to discard)
        self.block_data_skip_empty = Boolean()  # Skip producing when no factory is registered
        self.block_log_info_print_interval_seconds = Integer()  # How often to print out block_log_info (default 1 day)
        self.block_log_info_print_irreversible = Boolean()  # Whether to defer printing until block is irreversible
        self.block_log_info_print_file = String()  # Where to print (filename or special sink ILOG, STDOUT, STDERR)
        self.shared_file_dir = (
            StringQuoted()
        )  # the location of the chain shared memory files (absolute path or relative to application data dir)
        self.shared_file_size = (
            String()
        )  # Size of the shared memory file. Default: 24G. If running with many plugins, increase this value to 28G.
        self.shared_file_full_threshold = (
            Integer()
        )  # A 2 precision percentage (0-10000) that defines the threshold for when to autoscale the shared memory file. Setting this to 0 disables autoscaling. Recommended value for consensus node is 9500 (95%).
        self.shared_file_scale_rate = (
            Integer()
        )  # A 2 precision percentage (0-10000) that defines how quickly to scale the shared memory file. When autoscaling occurs the file's size will be increased by this percent. Setting this to 0 disables autoscaling. Recommended value is between 1000-2000 (10-20%)
        self.checkpoint = List(String)  # Pairs of [BLOCK_NUM,BLOCK_ID] that should be enforced as checkpoints.
        self.flush_state_interval = Integer()  # flush shared memory changes to disk every N blocks
        self.enable_block_log_compression = Boolean()  # Compress blocks using zstd as they're added to the block log
        self.block_log_compression_level = (
            Integer()
        )  # Block log zstd compression level 0 (fast, low compression) - 22 (slow, high compression)
        self.blockchain_thread_pool_size = (
            Integer()
        )  # Number of worker threads used to pre-validate transactions and blocks
        self.block_stats_report_type = (
            String()
        )  # Level of detail of block stat reports: NONE, MINIMAL, REGULAR, FULL. Default FULL (recommended for API nodes).
        self.block_stats_report_output = String()  # Where to put block stat reports: DLOG, ILOG, NOTIFY. Default ILOG.
        self.cashout_logging_starting_block = Integer()  # Starting block for comment cashout log
        self.cashout_logging_ending_block = Integer()  # Ending block for comment cashout log
        self.cashout_logging_log_path_dir = StringQuoted()  # Path to log file
        self.debug_node_edit_script = List(String)  # Database edits to apply on startup (may specify multiple times)
        self.edit_script = List(
            String
        )  # Database edits to apply on startup (may specify multiple times). Deprecated in favor of debug-node-edit-script.
        self.follow_max_feed_size = Integer()  # Set the maximum size of cached feed for an account
        self.follow_start_feeds = Integer()  # Block time (in epoch seconds) when to start calculating feeds
        self.log_json_rpc = String()  # json-rpc log directory name.
        self.market_history_bucket_size = (
            String()
        )  # Track market history by grouping orders into buckets of equal size measured in seconds specified as a JSON array of numbers
        self.market_history_buckets_per_size = (
            Integer()
        )  # How far back in time to track history for each bucket size, measured in the number of buckets (default: 5760)
        self.p2p_endpoint = String()  # The local IP address and port to listen for incoming connections.
        self.p2p_max_connections = Integer()  # Maxmimum number of incoming connections on P2P endpoint.
        self.seed_node = List(
            String
        )  # The IP address and port of a remote peer to sync with. Deprecated in favor of p2p-seed-node.
        self.p2p_seed_node = List(String)  # The IP address and port of a remote peer to sync with.
        self.p2p_parameters = (
            String()
        )  # P2P network parameters. (Default: {"listen_endpoint":"0.0.0.0:0","accept_incoming_connections":true,"wait_if_endpoint_is_busy":true,"private_key":"0000000000000000000000000000000000000000000000000000000000000000","desired_number_of_connections":20,"maximum_number_of_connections":200,"peer_connection_retry_timeout":30,"peer_inactivity_timeout":5,"peer_advertising_disabled":false,"maximum_number_of_blocks_to_handle_at_one_time":200,"maximum_number_of_sync_blocks_to_prefetch":20000,"maximum_blocks_per_peer_during_syncing":200,"active_ignored_request_timeout_microseconds":6000000} )
        self.rc_skip_reject_not_enough_rc = (
            Boolean()
        )  # Skip rejecting transactions when account has insufficient RCs. This is not recommended.
        self.rc_stats_report_type = (
            String()
        )  # Level of detail of daily RC stat reports: NONE, MINIMAL, REGULAR, FULL. Default REGULAR.
        self.rc_stats_report_output = String()  # Where to put daily RC stat reports: DLOG, ILOG, NOTIFY. Default ILOG.
        self.snapshot_root_dir = (
            StringQuoted()
        )  # The location (root-dir) of the snapshot storage, to save/read portable state dumps
        self.statsd_endpoint = String()  # Endpoint to send statsd messages to.
        self.statsd_batchsize = Integer()  # Size to batch statsd messages.
        self.statsd_whitelist = List(String)  # Whitelist of statistics to capture.
        self.statsd_blacklist = List(String)  # Blacklist of statistics to capture.
        self.tags_start_promoted = (
            Integer()
        )  # Block time (in epoch seconds) when to start calculating promoted content. Should be 1 week prior to current time.
        self.tags_skip_startup_update = (
            Boolean()
        )  # Skip updating tags on startup. Can safely be skipped when starting a previously running node. Should not be skipped when reindexing.
        self.transaction_status_block_depth = (
            Integer()
        )  # Defines the number of blocks from the head block that transaction statuses will be tracked.
        self.transaction_status_track_after_block = (
            Integer()
        )  # Defines the block number the transaction status plugin will begin tracking.
        self.webserver_http_endpoint = String()  # Local http endpoint for webserver requests.
        self.webserver_unix_endpoint = String()  # Local unix http endpoint for webserver requests.
        self.webserver_ws_endpoint = String()  # Local websocket endpoint for webserver requests.
        self.webserver_ws_deflate = (
            Boolean()
        )  # Enable the RFC-7692 permessage-deflate extension for the WebSocket server (only used if the client requests it).  This may save bandwidth at the expense of CPU
        self.rpc_endpoint = (
            String()
        )  # Local http and websocket endpoint for webserver requests. Deprecated in favor of webserver-http-endpoint and webserver-ws-endpoint
        self.webserver_thread_pool_size = Integer()  # Number of threads used to handle queries. Default: 32.
        self.enable_stale_production = Boolean()  # Enable block production, even if the chain is stale.
        self.required_participation = (
            Integer()
        )  # Percent of witnesses (0-99) that must be participating in order to produce blocks
        self.witness = List(
            StringQuoted, single_line=False
        )  # name of witness controlled by this node (e.g. initwitness )
        self.private_key = List(
            PrivateKey, single_line=False
        )  # WIF PRIVATE KEY to be used by one or more witnesses or miners
        self.witness_skip_enforce_bandwidth = (
            Boolean()
        )  # Skip enforcing bandwidth restrictions. Default is true in favor of rc_plugin.


# End of machine generated code
