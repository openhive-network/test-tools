from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._communication.universal_notification_server import UniversalNotificationServer

from test_tools.__private.notifications.node_notification_handler import NodeNotificationHandler

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl
    from loguru import Logger


class NodeNotificationServer(UniversalNotificationServer):
    def __init__(self, node_name: str, logger: Logger, notification_endpoint: HttpUrl | None) -> None:
        self.__logger = logger
        self.__node_name = node_name
        self.__handler = NodeNotificationHandler(node_name=self.__node_name, logger=logger)
        super().__init__(
            self.__handler,
            notification_endpoint,
            thread_name=f"{self.__node_name}.NotificationServerThread",
        )

    def run(self) -> int:
        self.__logger.info(f"Starting notification server for {self.__node_name}")
        port = super().run()
        self.__logger.info(f"Started notification server for {self.__node_name} on 0.0.0.0:{port}")
        return port

    def close(self) -> None:
        self.__logger.info(f"Closing notification server for {self.__node_name}")
        return super().close()

    @property
    def handler(self) -> NodeNotificationHandler:
        return self.__handler
