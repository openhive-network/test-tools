from __future__ import annotations

import logging
from pathlib import Path
import sys
from typing import Optional

from test_tools.__private.logger.levels import Level


class LoggerWrapper:
    __FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)")

    def __init__(self, name, *, parent: Optional["LoggerWrapper"], level=Level.TRACE, propagate=True):
        self.parent = parent

        self.internal_logger: logging.Logger
        if self.parent is None:
            self.internal_logger = logging.getLogger("root")
        else:
            self.internal_logger = self.parent.internal_logger.getChild(name)
            self.internal_logger.propagate = propagate

        self.internal_logger.setLevel(level)
        self.__file_handler: Optional[logging.FileHandler] = None
        self.__stream_handler: Optional[logging.StreamHandler] = None

    def __repr__(self):
        return f"<LoggerWrapper: {self.internal_logger.name}>"

    def create_child_logger(self, name: str, child_type: LoggerWrapper = None):
        if child_type is None:
            child_type = LoggerWrapper

        return child_type(name, parent=self)

    def set_file_handler(self, path):
        self.__file_handler = logging.FileHandler(path, mode="w")
        self.__file_handler.setFormatter(self.__FORMATTER)
        self.__file_handler.setLevel(logging.DEBUG)
        self.internal_logger.addHandler(self.__file_handler)

    def log_to_file(self, file_path: Optional[Path] = None) -> None:
        if file_path is not None:
            self.set_file_handler(file_path)
            return

        # Break import-cycle
        from test_tools.__private.scope import context  # pylint: disable=import-outside-toplevel, cyclic-import

        self.set_file_handler(context.get_current_directory().joinpath("last_run.log"))

    def log_to_stdout(self):
        pass
        self.__stream_handler = logging.StreamHandler(sys.stdout)
        # self.__stream_handler.setFormatter(self.__FORMATTER)
        # self.__stream_handler.setLevel(logging.INFO)
        # logging.root.addHandler(self.__stream_handler)

    def set_stream_handler_level(self, level: Level) -> None:
        self.__stream_handler.setLevel(level)

    def set_file_handler_level(self, level: Level) -> None:
        self.__file_handler.setLevel(level)

    def trace(self, message, stacklevel=1):
        self.internal_logger.log(Level.TRACE, message, stacklevel=stacklevel + 1)

    def debug(self, message, stacklevel=1):
        self.internal_logger.debug(message, stacklevel=stacklevel + 1)

    def info(self, message, stacklevel=1):
        self.internal_logger.info(message, stacklevel=stacklevel + 1)

    def warning(self, message, stacklevel=1):
        self.internal_logger.warning(message, stacklevel=stacklevel + 1)

    def error(self, message, stacklevel=1):
        self.internal_logger.error(message, stacklevel=stacklevel + 1)

    def critical(self, message, stacklevel=1):
        self.internal_logger.critical(message, stacklevel=stacklevel + 1)
