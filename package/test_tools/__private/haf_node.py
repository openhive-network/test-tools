from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import sqlalchemy
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import create_database, database_exists, drop_database

from test_tools.__private.logger.logger_internal_interface import logger
from test_tools.__private.preconfigured_node import PreconfiguredNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class HafNode(PreconfiguredNode):
    def __init__(
        self, *, name: str = "HafNode", network: Network | None = None, handle: NodeHandle | None = None
    ) -> None:
        super().__init__(name=name, network=network, handle=handle)
        self.__session: Session | None = None

        self.config.plugin.append("sql_serializer")

    @property
    def session(self) -> Session:
        assert self.__session, "Session is not available since node was not run yet! Call the 'run()' method first."
        return self.__session

    def _actions_before_run(self) -> None:
        self.__make_database()

    def __make_database(self) -> None:
        url = "postgresql:///haf_block_log"
        url = url + "_" + uuid4().hex
        self.config.psql_url = url
        logger.info(f"Preparing database {url}")
        if database_exists(url):
            drop_database(url)
        create_database(url)

        engine = sqlalchemy.create_engine(url, echo=False, poolclass=NullPool)
        with engine.connect() as connection:
            connection.execute("CREATE EXTENSION hive_fork_manager CASCADE;")

        session = sessionmaker(bind=engine)
        self.__session = session()

    def close(self) -> None:
        super().close()
        self.__close_session()

    def __close_session(self) -> None:
        if self.__session is not None:
            self.__session.close()
