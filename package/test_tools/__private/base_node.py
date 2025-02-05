from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, cast

from beekeepy import Settings

from helpy import Hived
from test_tools.__private.scope import context
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation

if TYPE_CHECKING:
    from helpy._interfaces.url import HttpUrl
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase


class BaseNode(UserHandleImplementation, Hived):
    def __init__(self, *, name: str, handle: NodeHandleBase | None = None) -> None:
        self.__name = context.names.register_numbered_name(name)
        super().__init__(
            handle=handle,
            settings=Settings(
                period_between_retries=timedelta(seconds=0.5),
                max_retries=8,
            ),
        )

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return str(self)

    def get_name(self) -> str:
        return self.__name

    def is_running(self) -> bool:
        return True

    def _logger_extras(self) -> dict[str, Any]:
        return {**super()._logger_extras(), "name": self.get_name()}

    def get_http_endpoint(self) -> HttpUrl:
        return self.http_endpoint

    @property
    def settings(self) -> Settings:
        return cast(Settings, super().settings)
