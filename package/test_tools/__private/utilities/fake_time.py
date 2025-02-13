from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from loguru import Logger


def configure_fake_time(logger: Logger, env: dict[str, str], time_control: str) -> None:
    logger.info(f"Using time_control {time_control}")

    env["LD_PRELOAD"] = get_fake_time_path(logger).as_posix()
    env["FAKETIME"] = time_control
    env["FAKETIME_DONT_RESET"] = "1"
    env["FAKETIME_DONT_FAKE_MONOTONIC"] = "1"
    env["TZ"] = "UTC"

    logger.debug(
        "Following environments are set after fake time configuration:\n"
        + str(dict(filter(lambda kv: kv[0].startswith("CI_"), env.items())))
    )


def get_fake_time_path(logger: Logger) -> Path:
    installation_manual: Final[str] = (
        "To install libfaketime perform following operations:\n"
        "\n"
        "    git clone https://github.com/wolfcw/libfaketime.git\n"
        "    cd libfaketime/src/\n"
        "    sudo make install"
    )

    default_installation_path = Path("/usr/local/lib/faketime/libfaketimeMT.so.1")
    ubuntu_package_installation_path = Path("/usr/lib/x86_64-linux-gnu/faketime/libfaketimeMT.so.1")

    if "LIBFAKETIME_PATH" in os.environ:
        libfake_path_from_envs = os.getenv("LIBFAKETIME_PATH")
        assert libfake_path_from_envs is not None  # mypy check
        fake_time_path = Path(libfake_path_from_envs)
        assert fake_time_path.exists(), f'File defined in LIBFAKETIME_PATH ("{fake_time_path}") does not exist.'
    elif default_installation_path.exists():
        fake_time_path = default_installation_path
    elif ubuntu_package_installation_path.exists():
        logger.warning(
            f"You are using libfaketime from Ubuntu package repository, which is not supported.\n"
            f"Recommended way is to build them from sources.\n\n"
            f"{installation_manual}"
        )
        fake_time_path = ubuntu_package_installation_path
    else:
        raise RuntimeError(
                f"Missing path to libfaketime.\n\n"
                f"{installation_manual}"
            )  # fmt: skip

    assert fake_time_path.is_file(), f'LIBFAKETIME_PATH (with value "{fake_time_path}") is not path of file.'
    return fake_time_path
