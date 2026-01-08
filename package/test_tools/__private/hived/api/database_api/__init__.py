from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from database_api.database_api_client_sync import DatabaseApi as SyncDatabaseApi
except ImportError:
    if TYPE_CHECKING:
        from typing import Any

        SyncDatabaseApi: Any
    else:

        class SyncDatabaseApi:  # type: ignore[no-redef]
            """Placeholder when sync client is not available in the package."""

            def __init__(self, *args: object, **kwargs: object) -> None:
                raise ImportError(
                    "database_api.database_api_client_sync is not available. "
                    "Please install a newer version of hiveio-database-api package."
                )

__all__ = ["SyncDatabaseApi"]
