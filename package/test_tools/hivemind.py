import os
from pathlib import Path
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
                 database_host: str = 'localhost',
                 database_port: str = '5432',
                 maintance_database_name: str = 'postgres'
                 ):
        """
        Database params are specyfic to usage of program. If you want sync or sync and server, database with parameters
        will be create or reset. If you want to use only server, parameters should be involve with existing database,
        consist correct hivemind data.

        :param database_name:
        :param database_user:
        :param database_password:
        :param database_host:
        :param database_port:
        :param maintance_database_name:
        """

        super().__init__()

        self.with_time_offset = None
        self.node = None
        self.host = database_host
        self.port = database_port
        self.database_name = database_name
        self.user = database_user
        self.password = database_password
        self.maintance_database_name = maintance_database_name
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

    def database_prepare(self):
        # Terminate all of connection to repair problem with droping database
        subprocess.run(
            [
                F'PGPASSWORD={self.password} psql -h {self.host} -U {self.user} -d {self.maintance_database_name} -a '
                F'-c "SELECT pid, pg_terminate_backend(pid) '
                F'FROM pg_stat_activity '
                F'WHERE datname = \'hivemind_pyt\' AND pid <> pg_backend_pid();"'
            ],
            shell=True)

        subprocess.run(
            [
                F"PGPASSWORD={self.password} psql -h {self.host} -U {self.user} -d {self.maintance_database_name} -a "
                F"-c 'DROP DATABASE IF EXISTS {self.database_name}' "
            ],
            shell=True)

        subprocess.run(
            [
                F"PGPASSWORD={self.password} psql -h {self.host} -U {self.user} -d {self.maintance_database_name} -a -c 'CREATE DATABASE {self.database_name}'"
            ],
            shell=True)

        subprocess.run(
            [
                F"PGPASSWORD={self.password} psql -h {self.host} -U {self.user} -d {self.database_name} -a -c 'CREATE EXTENSION intarray'"
            ],
            shell=True)

    def set_run_parameters(self,
                           log_level: str = 'INFO',
                           http_server_port: str = '8080',
                           max_batch: str = '35',
                           max_workers: str = '6',
                           max_retries: str = '-1',
                           trial_blocks: str = '2',
                           ):

        self.parameters = {'log_level': log_level,
                           'http_server_port': http_server_port,
                           'max_batch': max_batch,
                           'max_workers': max_workers,
                           'max_retries': max_retries,
                           'trial_blocks': trial_blocks}

    def run(self,
            sync_with,
            run_sync: bool = True,
            run_server: bool = True,
            with_time_offset: str = None,
            database_prepare: bool = True
            ):
        self.node = sync_with
        self.with_time_offset = with_time_offset
        self.remove_directory('hivemind_sync')
        self.remove_directory('hivemind_server')

        if database_prepare:
            self.database_prepare()
        if run_sync:
            self.run_sync()
        if run_server:
            self.run_server()

    def run_sync(self):
        self.create_directory('hivemind_sync')
        self.stdout_file_sync = open(self.directory / 'stdout.txt', 'w')
        self.stderr_file_sync = open(self.directory / 'stderr.txt', 'w')

        env = dict(os.environ)
        if self.with_time_offset is not None:
            self.__configure_fake_time(env, self.with_time_offset)

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
            stderr=self.stderr_file_sync,
            env=env,
        )
        # logger.info(f'{self.process.pid=}')
        logger.info('Sync RUN')

    def run_server(self):
        self.create_directory('hivemind_server')
        self.stdout_file_server = open(self.directory / 'stdout.txt', 'w')
        self.stderr_file_server = open(self.directory / 'stderr.txt', 'w')

        env = dict(os.environ)
        if self.with_time_offset is not None:
            self.__configure_fake_time(env, self.with_time_offset)

#TODO Improve trigger to start server
        if self.process_sync is not None:
            if self.with_time_offset is None:
                while not self.is_in_stderr_hive_sync(trigger_string='[LIVE SYNC] <===== Processed block 21'):
                    time.sleep(1)
            else:
                __last_block = self.node.get_last_block_number()
                while __last_block < 30:
                    __last_block = self.node.get_last_block_number()
                    time.sleep(1)
        time.sleep(10)
        self.process_server = subprocess.Popen(
            [
                'hive',
                'server',
                "--database-url=" + self.database_adress,
                F'--http-server-port={self.parameters["http_server_port"]}'
            ],
            cwd=self.directory,
            stdout=self.stdout_file_server,
            stderr=self.stdout_file_server,
            env=env,
        )
        logger.info('Server is running...')
        time.sleep(5)
        logger.info('Server RUN')

    def __configure_fake_time(self, env, time_offset):
        libfaketime_path = os.getenv('LIBFAKETIME_PATH') or '/usr/lib/x86_64-linux-gnu/faketime/libfaketime.so.1'
        if not Path(libfaketime_path).is_file():
            raise RuntimeError(f'libfaketime was not found at {libfaketime_path}')
        self.logger.info(f"using time_offset {time_offset}")
        env['LD_PRELOAD'] = libfaketime_path
        env['FAKETIME'] = time_offset
        env['FAKETIME_DONT_RESET'] = '1'
        env['TZ'] = 'UTC'

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

    def stop(self):
        if self.process_sync is not None:
            self.stdout_file_sync.close()
            self.stderr_file_sync.close()
            self.__close_process(self.process_sync)
        if self.process_server is not None:
            self.stdout_file_server.close()
            self.stderr_file_server.close()
            self.__close_process(self.process_server)
        self.logger.debug("Stop HIVEMIND process")

    def at_exit_from_scope(self):
        if self.process_sync is not None:
            self.stdout_file_sync.close()
            self.stderr_file_sync.close()
            self.__close_process(self.process_sync)

        if self.process_server is not None:
            self.stdout_file_server.close()
            self.stderr_file_server.close()
            self.__close_process(self.process_server)
