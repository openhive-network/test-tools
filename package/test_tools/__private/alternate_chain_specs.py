from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Protocol

from test_tools.__private.user_handles import context


class InitialVesting(BaseModel):
    vests_per_hive: int
    hive_amount: int


class HardforkSchedule(BaseModel):
    hardfork: int
    block_num: int


class AlternateChainSpecs(BaseModel):
    FILENAME: ClassVar[str] = "alternate-chain-spec.json"

    genesis_time: int
    hardfork_schedule: list[HardforkSchedule]
    init_supply: int | None = None
    hbd_init_supply: int | None = None
    initial_vesting: InitialVesting | None = None
    init_witnesses: list[str] | None = None
    hive_owner_update_limit: int | None = None
    generate_missed_block_operations: bool | None = None
    min_root_comment_interval: int | None = None
    min_reply_interval: int | None = None

    def export_to_file(self, output_dir: Path | None = None) -> Path:
        if output_dir is None:
            output_dir = context.get_current_directory()
        output_dir.mkdir(parents=True, exist_ok=True)
        destination = output_dir / AlternateChainSpecs.FILENAME
        with destination.open("w") as json_file:
            json_file.write(self.json(exclude_none=True))
        return destination

    @classmethod
    def parse_file(
        cls: type[AlternateChainSpecs],
        path: str | Path,
        *,
        content_type: str | None = None,
        encoding: str = "utf8",
        proto: Protocol | None = None,
        allow_pickle: bool = False,
    ) -> AlternateChainSpecs:
        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            path = path / AlternateChainSpecs.FILENAME

        assert path.is_file(), f"Given path: `{path.as_posix()}` is not pointing to file!"
        return super().parse_file(
            path, content_type=content_type, encoding=encoding, proto=proto, allow_pickle=allow_pickle  # type: ignore
        )
