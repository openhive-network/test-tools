import os
import signal
import subprocess
import time
import shutil

import psycopg2

from test_tools import logger
from test_tools.private.scope import context, ScopedObject


class Hivemind(ScopedObject):
    def __init__(self, host, port, database_name, user, password, node):
        super().__init__()

        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password
        self.node = node
        self.database_adress = F'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}'

        self.hivemind_sync_directory = None
        self.directory = None
        self.process_server = None
        self.process_sync = None
        self.parameters = {'log_level': 'INFO',
                           'http_server_port': '8080',
                           'max_batch': '35',
                           'max_workers': '6',
                           'max_retries': '-1',
                           'trial_blocks': '2',
                           'hived_database_url': ''}

    def detabase_prepare(self):
        os.system(
            "PGPASSWORD=devdevdev psql -h 127.0.0.1 -U dev -d postgres -a -c 'DROP DATABASE IF EXISTS hivemind_pyt'")
        os.system(
            "PGPASSWORD=devdevdev psql -h 127.0.0.1 -U dev -d postgres -a -c 'CREATE DATABASE hivemind_pyt'")
        os.system(
            "PGPASSWORD=devdevdev psql -h 127.0.0.1 -U dev -d hivemind_pyt -a -c 'CREATE EXTENSION intarray'")

    def set_run_parameters(self,
                           log_level='INFO',
                           http_server_port='8080',
                           max_batch='35',
                           max_workers='6',
                           max_retries='-1',
                           trial_blocks='2',
                           hived_database_url=''
                           ):

        self.parameters = {'log_level': log_level,
                           'http_server_port': http_server_port,
                           'max_batch': max_batch,
                           'max_workers': max_workers,
                           'max_retries': max_retries,
                           'trial_blocks': trial_blocks,
                           'hived_database_url': hived_database_url}

    def run_sync(self, node):
        self.remove_directory('hivemind_sync')
        self.create_directory('hivemind_sync')

        while node.get_last_block_number() < 24:
            logger.info(node.get_last_block_number())
            time.sleep(1)

        http_endpoint = self.node.get_http_endpoint()
        self.process_sync = subprocess.Popen(
            [
                'hive',
                'sync',
                "--database-url=" + self.database_adress,
                "--steemd-url={" + '"default" : "' + http_endpoint + '"}',
                F'--log-level={self.parameters["log_level"]}',
                F'--http-server-port={self.parameters["http_server_port"]}',
                F'--max-batch={self.parameters["max_batch"]}',
                F'--max-workers={self.parameters["max_workers"]}',
                F'--max-retries={self.parameters["max_retries"]}',
                F'--trail-blocks={self.parameters["trial_blocks"]}',
                F'--hived-database-url={self.parameters["hived_database_url"]}'
            ],
            cwd=self.directory,
            stdout=open(self.directory / 'stdout.txt', 'w'),
            stderr=open(self.directory / 'stderr.txt', 'w')
        )
        # logger.info(f'{self.process.pid=}')
        logger.info('Sync RUN')

    def run_server(self):
        self.remove_directory('hivemind_server')
        self.create_directory('hivemind_server')
        # time.sleep(23)
        while not self.is_in_stderr_hive_sync(trigger_string='[LIVE SYNC] <===== Processed block 21'):
            time.sleep(1)

        self.process_server = subprocess.Popen(
            [
                'hive',
                'server',
                "--database-url=" + self.database_adress,
            ],
            cwd=self.directory,
            stdout=open(self.directory / 'stdout.txt', 'w'),
            stderr=open(self.directory / 'stderr.txt', 'w')
        )
        logger.info('Server RUN')

    def at_exit_from_scope(self):
        self.process_sync.send_signal(signal.SIGINT)
        self.process_server.send_signal(signal.SIGINT)

    def create_directory(self, directory_name):
        self.directory = context.get_current_directory() / directory_name
        self.directory.mkdir(parents=True, exist_ok=True)

    def remove_directory(self, directory_name):
        self.directory = context.get_current_directory() / directory_name
        shutil.rmtree(self.directory, ignore_errors=True)

    def is_in_stderr_hive_sync(self, trigger_string):
        self.hivemind_sync_directory = context.get_current_directory() / 'hivemind_sync'
        with open(self.hivemind_sync_directory / 'stderr.txt') as file:
            stderr = file.read()
        return trigger_string in stderr
