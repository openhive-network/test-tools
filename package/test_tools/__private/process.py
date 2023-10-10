from __future__ import annotations

import os
import signal
import subprocess
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from test_tools.__private.utilities.fake_time import configure_fake_time

if TYPE_CHECKING:
    from collections.abc import Sequence

    from loguru import Logger

    from test_tools.__private.executable import Executable


class Process:
    def __init__(self, directory: Path | str, executable: Executable, logger: Logger) -> None:
        self.__process: subprocess.Popen[str] | None = None
        self.__directory = Path(directory).absolute()
        self.__executable = executable
        self.__logger = logger
        self.__files: dict[str, TextIO | None] = {
            "stdout": None,
            "stderr": None,
        }

    def run(
        self,
        *,
        blocking: bool,
        with_arguments: Sequence[str] | None = None,
        with_environment_variables: dict[str, str] | None = None,
        with_time_offset: str | None = None,
    ) -> None:
        if with_arguments is None:
            with_arguments = []
        self.__directory.mkdir(exist_ok=True)
        self.__prepare_files_for_streams()

        command = [str(self.__executable.get_path()), *with_arguments]
        if self.__executable.executable_name == "hived":
            command += ["-d", "."]
        self.__logger.debug(" ".join(item for item in command))

        environment_variables = dict(os.environ)

        if with_environment_variables is not None:
            environment_variables.update(with_environment_variables)

        if with_time_offset is not None:
            configure_fake_time(self.__logger, environment_variables, with_time_offset)

        if blocking:
            subprocess.run(  # type: ignore[call-overload]
                command,
                cwd=self.__directory,
                **self.__files,
                env=environment_variables,
                check=True,
            )
        else:
            # Process created here have to exist longer than current scope
            self.__process = subprocess.Popen(  # type: ignore[call-overload]
                command,
                cwd=self.__directory,
                env=environment_variables,
                **self.__files,
            )

    def get_id(self) -> int:
        assert self.__process is not None
        return self.__process.pid

    def __prepare_files_for_streams(self) -> None:
        for name, file in self.__files.items():
            if file is None:
                # Files opened here have to exist longer than current scope
                self.__files[name] = (self.__directory / f"{name}.txt").open("w", encoding="utf-8")

    def close(self) -> None:
        if self.__process is None:
            return

        self.__process.send_signal(signal.SIGINT)
        try:
            return_code = self.__process.wait(timeout=10)
            self.__logger.debug(f"Closed with {return_code} return code")
        except subprocess.TimeoutExpired:
            self.__process.kill()
            self.__process.wait()
            warnings.warn("Process was force-closed with SIGKILL, because didn't close before timeout", stacklevel=1)

        self.__process = None

    def close_opened_files(self) -> None:
        for name, file in self.__files.items():
            if file is not None:
                file.close()
                self.__files[name] = None

    def is_running(self) -> bool:
        if not self.__process:
            return False

        return self.__process.poll() is None

    def get_stderr_file_path(self) -> Path | None:
        stderr_file = self.__files["stderr"]
        return Path(stderr_file.name) if stderr_file is not None else None
