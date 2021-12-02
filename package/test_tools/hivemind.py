import signal
import subprocess
import time
import psycopg2
import shutil

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

    # database = "postgresql://dev:devdevdev@localhost:5432/hivemind_pyt"

    def environment_setup(self):
        self.remove_directory('hivemind_sync')
        self.remove_directory('hivemind_server')

        connect_postgres = psycopg2.connect(
            host=self.host,
            database='postgres',
            user=self.user,
            password=self.password,
            port=self.port)

        connect_postgres.autocommit = True
        cursor = connect_postgres.cursor()
        db_drop = F'DROP DATABASE IF EXISTS {self.database_name};'
        cursor.execute(db_drop)
        db_create = F'CREATE database {self.database_name};'
        cursor.execute(db_create)
        connect_postgres.close()

        connect_hivemind = psycopg2.connect(
            host=self.host,
            database=self.database_name,
            user=self.user,
            password=self.password,
            port=self.port)

        connect_hivemind.autocommit = True
        cursor = connect_hivemind.cursor()
        db_extension = 'CREATE EXTENSION intarray;'
        cursor.execute(db_extension)
        connect_hivemind.close()

    def run_sync(self, node):
        self.create_directory('hivemind_sync')

        while node.get_last_block_number() < 25:
            logger.info(node.get_last_block_number())
            time.sleep(1)

        http_endpoint = self.node.get_http_endpoint()
        self.process_sync = subprocess.Popen(
            [
                'hive',
                'sync',
                "--database-url=" + self.database_adress,
                "--steemd-url={" + '"default" : "' + http_endpoint + '"}'
            ],
            cwd=self.directory,
            stdout=open(self.directory / 'stdout.txt', 'w'),
            stderr=open(self.directory / 'stderr.txt', 'w')
        )
        # logger.info(f'{self.process.pid=}')
        logger.info('Sync RUN')

    def run_server(self):
        self.create_directory('hivemind_server')
        # time.sleep(23)
        while self.is_in_stderr_hive_sync(trigger_string='[LIVE SYNC] <===== Processed block 21') == False :
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
        hivemind_sync_directory = context.get_current_directory() / 'hivemind_sync'
        with open(hivemind_sync_directory / 'stderr.txt') as file:
            stderr = file.read()
        trigger_string = trigger_string
        return trigger_string in stderr

# [LIVE SYNC] <===== Processed block 22