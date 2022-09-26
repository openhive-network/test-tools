from typing import Optional, TYPE_CHECKING

from test_tools.__private.scope.scope_singleton import context

if TYPE_CHECKING:
    from test_tools.__private.logger.logger_wrapper import LoggerWrapper


class LoggerInterfaceBase:
    def __init__(self, instance: Optional["LoggerWrapper"] = None, *, message_prefix: str = ""):
        self.__message_prefix = message_prefix
        self.__instance: Optional["LoggerWrapper"] = instance

    @property
    def _logger(self) -> "LoggerWrapper":
        return self.__instance if self.__instance is not None else context.get_logger()

    def debug(self, message: str, stacklevel: int = 1):
        self._logger.debug(f"{self.__message_prefix}{message}", stacklevel=stacklevel + 1)

    def info(self, message: str, stacklevel: int = 1):
        self._logger.info(f"{self.__message_prefix}{message}", stacklevel=stacklevel + 1)

    def warning(self, message: str, stacklevel: int = 1):
        self._logger.warning(f"{self.__message_prefix}{message}", stacklevel=stacklevel + 1)

    def error(self, message: str, stacklevel: int = 1):
        self._logger.error(f"{self.__message_prefix}{message}", stacklevel=stacklevel + 1)

    def critical(self, message: str, stacklevel: int = 1):
        self._logger.critical(f"{self.__message_prefix}{message}", stacklevel=stacklevel + 1)
