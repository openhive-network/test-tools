import signal
import subprocess
import time
import psycopg2

from test_tools import logger
from test_tools.private.scope import context, ScopedObject


class Sync(ScopedObject):
    def __init__(self, database_adress, node):
        super().__init__()

        self.database_adress = database_adress
        self.node = node

    def environment_setup(self):
        connect_postgres = psycopg2.connect(
            host='localhost',
            database='postgres',
            user='dev',
            password='devdevdev',
            port='5432')
        connect_postgres.autocommit = True
        cursor = connect_postgres.cursor()
        db_drop = 'DROP DATABASE IF EXISTS hivemind_pyt;'
        cursor.execute(db_drop)
        db_create = 'CREATE database hivemind_pyt;'
        cursor.execute(db_create)
        connect_postgres.close()

        connect_hivemind = psycopg2.connect(
            host='localhost',
            database='hivemind_pyt',
            user='dev',
            password='devdevdev',
            port='5432')
        connect_hivemind.autocommit = True
        cursor = connect_hivemind.cursor()
        db_extension = 'CREATE EXTENSION intarray;'
        cursor.execute(db_extension)
        connect_hivemind.close()

        self.remove_directory()

    def run(self, node):
        self.create_directory()

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

    def create_directory(self):
        self.directory = context.get_current_directory() / 'hivemind'
        self.directory.mkdir(parents=True, exist_ok=True)

    def remove_directory(self):
        self.directory = context.get_current_directory() / 'hivemind'
        self.directory.rmdir()