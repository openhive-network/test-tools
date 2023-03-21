from __future__ import annotations
from uuid import uuid4

from typing import Optional, TYPE_CHECKING

from test_tools.__private.preconfigured_node import PreconfiguredNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle

import pytest
import sqlalchemy
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, close_all_sessions
from sqlalchemy.pool import NullPool

from test_tools.__private.logger.logger_internal_interface import logger


class HafNode(PreconfiguredNode):
    def __init__(
            self, *, name: str = "HafNode", network: Optional[Network] = None, handle: Optional[NodeHandle] = None
    ):
        super().__init__(name=name, network=network, handle=handle)

        self.config.plugin.remove("witness")  # remove after new changes from Mateusz Kudela
        self.config.plugin.append('sql_serializer')

    def make_database(self):
        url = 'postgresql:///haf_block_log'
        url = url + '_' + uuid4().hex
        self.config.psql_url = url
        logger.info(f'Preparing database {url}')
        if database_exists(url):
            drop_database(url)
        create_database(url)

        engine = sqlalchemy.create_engine(url, echo=False, poolclass=NullPool)
        with engine.connect() as connection:
            connection.execute('CREATE EXTENSION hive_fork_manager CASCADE;')

        with engine.connect() as connection:
            connection.execute('SET ROLE hived_group')

        Session = sessionmaker(bind=engine)
        session = Session()

        return session
