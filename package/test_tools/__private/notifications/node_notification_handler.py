from __future__ import annotations

from threading import Event
from typing import TYPE_CHECKING, Any

from helpy import HivedNotificationHandler, HttpUrl
from helpy._interfaces.url import P2PUrl, WsUrl
from test_tools.__private import exceptions
from test_tools.__private.raise_exception_helper import RaiseExceptionHelper

if TYPE_CHECKING:
    from loguru import Logger

    from schemas.notifications import (
        Error,
        KnownNotificationT,
        Notification,
        P2PListening,
        Status,
        SwitchingForks,
        WebserverListening,
    )


class NodeNotificationHandler(HivedNotificationHandler):
    def __init__(self, node_name: str, logger: Logger, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.node_name = node_name
        self.__logger = logger

        self.http_listening_event = Event()
        self.http_endpoint: HttpUrl | None = None

        self.ws_listening_event = Event()
        self.ws_endpoint: WsUrl | None = None

        self.p2p_plugin_started_event = Event()
        self.p2p_endpoint: P2PUrl | None = None

        self.synchronization_started_event = Event()
        self.live_mode_entered_event = Event()

        self.chain_api_ready_event = Event()
        self.replay_finished_event = Event()

        self.snapshot_dumped_event = Event()
        self.api_mode_entered_event = Event()

        self.switch_fork_event = Event()
        self.number_of_forks = 0

    async def on_status_changed(self, notification: Notification[Status]) -> None:
        match notification.value.current_status:
            case "finished replaying":
                self.replay_finished_event.set()
            case "finished dumping snapshot":
                self.snapshot_dumped_event.set()
            case "syncing":
                self.synchronization_started_event.set()
            case "entering live mode":
                self.live_mode_entered_event.set()
            case "chain API ready":
                self.chain_api_ready_event.set()
            case "entering API mode":
                self.api_mode_entered_event.set()

    async def on_http_webserver_bind(self, notification: Notification[WebserverListening]) -> None:
        self.http_endpoint = HttpUrl(self.__combine_url_string_from_notification(notification), protocol="http")
        self.http_listening_event.set()

    async def on_ws_webserver_bind(self, notification: Notification[WebserverListening]) -> None:
        self.ws_endpoint = WsUrl(self.__combine_url_string_from_notification(notification), protocol="ws")
        self.ws_listening_event.set()

    async def on_p2p_server_bind(self, notification: Notification[P2PListening]) -> None:
        self.p2p_endpoint = P2PUrl(self.__combine_url_string_from_notification(notification))
        self.p2p_plugin_started_event.set()

    async def on_switching_forks(self, _: Notification[SwitchingForks]) -> None:
        self.number_of_forks += 1
        self.switch_fork_event.set()
        self.switch_fork_event.clear()

    async def on_error(self, notification: Notification[Error]) -> None:
        RaiseExceptionHelper.raise_exception_in_main_thread(
            exceptions.InternalNodeError(f"{self.node_name}: '{notification.value.message}'")
        )

    async def handle_notification(self, notification: Notification[KnownNotificationT]) -> None:
        self.__logger.info(f"Received message: {notification.json(by_alias=True)}")
        return await super().handle_notification(notification)

    def __combine_url_string_from_notification(
        self, notification: Notification[WebserverListening] | Notification[P2PListening]
    ) -> str:
        return f"{notification.value.address}:{notification.value.port}"
