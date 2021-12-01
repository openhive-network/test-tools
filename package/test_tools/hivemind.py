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
        http_endpoint_clean = http_endpoint.replace("'", "")
        self.process = subprocess.Popen(
            [
                'hive',
                'sync',
                "--database-url=" + self.database_adress,
                "--steemd-url={" + '"default" : "' + http_endpoint_clean + '"}'
            ],
            cwd=self.directory,
            stdout=open(self.directory / 'stdout.txt', 'w'),
            stderr=open(self.directory / 'stderr.txt', 'w')
        )
        logger.info(f'{self.process.pid=}')

    def at_exit_from_scope(self):
        self.process.send_signal(signal.SIGINT)

    def create_directory(self, directory_name):
        self.directory = context.get_current_directory() / directory_name
        self.directory.mkdir(parents=True, exist_ok=True)

    def remove_directory(self, directory_name):
        self.directory = context.get_current_directory() / directory_name
        shutil.rmtree(self.directory, ignore_errors=True)
