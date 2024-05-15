from __future__ import annotations

from helpy import HttpUrl
from helpy import Settings as HelpySettings


class Settings(HelpySettings):
    """Note: This class will be moved to beekeepy project in near future."""

    http_endpoint: HttpUrl | None = None  # type: ignore[assignment]
    notification_endpoint: HttpUrl | None = None
