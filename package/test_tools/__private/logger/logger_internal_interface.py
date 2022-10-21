from typing import Optional

from test_tools.__private.logger.logger_interface_base import LoggerInterfaceBase
from test_tools.__private.logger.logger_wrapper import LoggerWrapper


class LoggerInternalInterface(LoggerInterfaceBase):
    def __init__(self, name: str = "", instance: Optional["LoggerWrapper"] = None):
        super().__init__(instance, message_prefix=f"{name}: " if name != "" else "")

    def create_child_logger(self, name: str) -> "LoggerInternalInterface":
        logger_wrapper = LoggerWrapper(name, parent=self._logger)
        return LoggerInternalInterface(name, logger_wrapper)

    def trace(self, message: str, stacklevel: int = 1):
        self._logger.trace(f"{self._message_prefix}{message}", stacklevel=stacklevel + 1)


logger = LoggerInternalInterface()
