import os
import signal
import subprocess
import time
from typing import TYPE_CHECKING
import shutil

from test_tools import logger
from test_tools.private.logger.logger_internal_interface import logger
from test_tools.private.scope import context, ScopedObject

# if TYPE_CHECKING:
#     from test_tools.types import Node


class Hivemind(ScopedObject):
    def __init__(self,
                 database_name: str,
                 database_user: str,
                 database_password: str,
                 sync_with,
                 database_host: str = 'localhost',
                 database_port: str = '5432',
                 ):
        """
        :param sync_with: Node to sync with.

        """

        super().__init__()

        self.host = database_host
        self.port = database_port
        self.database_name = database_name
        self.user = database_user
        self.password = database_password
        self.node = sync_with
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
                           'trial_blocks': '2'}

        self.logger = logger.create_child_logger('Logger')

    def detabase_prepare(self):
        subprocess.run(
            [
                "PGPASSWORD=devdevdev psql -h 127.0.0.1 -U dev -d postgres -a -c 'DROP DATABASE IF EXISTS hivemind_pyt'"
            ],
            shell=True)
        subprocess.run(
            [
                "PGPASSWORD=devdevdev psql -h 127.0.0.1 -U dev -d postgres -a -c 'CREATE DATABASE hivemind_pyt'"
            ],
            shell=True)

        subprocess.run(
            [
                "PGPASSWORD=devdevdev psql -h 127.0.0.1 -U dev -d hivemind_pyt -a -c 'CREATE EXTENSION intarray'"
            ],
            shell=True)

    def set_run_parameters(self,
                           log_level='INFO',
                           http_server_port='8080',
                           max_batch='35',
                           max_workers='6',
                           max_retries='-1',
                           trial_blocks='2',
                           ):

        self.parameters = {'log_level': log_level,
                           'http_server_port': http_server_port,
                           'max_batch': max_batch,
                           'max_workers': max_workers,
                           'max_retries': max_retries,
                           'trial_blocks': trial_blocks}

    def run(self):
        self.run_sync()
        self.run_server()

    def run_sync(self):
        self.remove_directory('hivemind_sync')
        self.create_directory('hivemind_sync')
        self.stdout_file_sync = open(self.directory / 'stdout.txt', 'w')
        self.stderr_file_sync = open(self.directory / 'stderr.txt', 'w')

        while self.node.get_last_block_number() < 24:
            logger.info(self.node.get_last_block_number())
            time.sleep(1)

        http_endpoint = self.node.get_http_endpoint()
        self.process_sync = subprocess.Popen(
            [
                'hive',
                'sync',
                "--database-url=" + self.database_adress,
                "--steemd-url={" + '"default" : "' + http_endpoint + '"}',
                F'--log-level={self.parameters["log_level"]}',

                F'--max-batch={self.parameters["max_batch"]}',
                F'--max-workers={self.parameters["max_workers"]}',
                F'--max-retries={self.parameters["max_retries"]}',
                F'--trail-blocks={self.parameters["trial_blocks"]}',
            ],
            cwd=self.directory,
            stdout=self.stdout_file_sync,
            stderr=self.stderr_file_sync
            )
        # logger.info(f'{self.process.pid=}')
        logger.info('Sync RUN')

    def run_server(self):
        self.remove_directory('hivemind_server')
        self.create_directory('hivemind_server')
        self.stdout_file_server = open(self.directory / 'stdout.txt', 'w')
        self.stderr_file_server = open(self.directory / 'stderr.txt', 'w')
        while not self.is_in_stderr_hive_sync(trigger_string='[LIVE SYNC] <===== Processed block 21'):
            time.sleep(1)

        self.process_server = subprocess.Popen(
            [
                'hive',
                'server',
                "--database-url=" + self.database_adress,
                F'--http-server-port={self.parameters["http_server_port"]}'
            ],
            cwd=self.directory,
            stdout=self.stdout_file_server,
            stderr=self.stdout_file_server
            )
        logger.info('Server RUN')

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

    def __close_process(self, process):
        if process is None:
            return

        process.send_signal(signal.SIGINT)
        try:
            return_code = process.wait(timeout=3)
            self.logger.debug(f'Closed with {return_code} return code')
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            self.logger.warning('Process was force-closed with SIGKILL, because didn\'t close before timeout')

    def at_exit_from_scope(self):
        self.stdout_file_server.close()
        self.stderr_file_server.close()
        self.stdout_file_sync.close()
        self.stderr_file_sync.close()
        self.__close_process(self.process_sync)
        self.__close_process(self.process_server)






