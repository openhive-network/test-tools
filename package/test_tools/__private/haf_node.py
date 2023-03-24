from __future__ import annotations

from typing import TYPE_CHECKING, Final
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
    DEFAULT_DATABASE_URL: Final[str] = "postgresql:///haf_block_log"

    def __init__(
        self,
        *,
        name: str = "HafNode",
        network: Network | None = None,
        database_url: str = DEFAULT_DATABASE_URL,
        handle: NodeHandle | None = None,
    ) -> None:
        super().__init__(name=name, network=network, handle=handle)
        self.__database_url: str = self.__create_unique_url(database_url)
        self.__session: Session | None = None
        self.config.plugin.append("sql_serializer")

    @property
    def session(self) -> Session:
        assert self.__session, "Session is not available since node was not run yet! Call the 'run()' method first."
        return self.__session

    @property
    def database_url(self) -> str:
        return self.__database_url

    def _actions_before_run(self) -> None:
        self.__make_database()

    @staticmethod
    def __create_unique_url(database_url):
        return database_url + "_" + uuid4().hex

    def __make_database(self) -> None:
        self.config.psql_url = self.__database_url
        logger.info(f"Preparing database {self.__database_url}")
        if database_exists(self.__database_url):
            drop_database(self.__database_url)
        create_database(self.__database_url)

        engine = sqlalchemy.create_engine(self.__database_url, echo=False, poolclass=NullPool)
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
