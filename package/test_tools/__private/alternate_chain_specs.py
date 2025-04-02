from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import msgspec

from schemas._preconfigured_base_model import PreconfiguredBaseModel
from test_tools.__private.user_handles import context

if TYPE_CHECKING:
    from collections.abc import Callable

    from schemas.decoders import T


class Protocol(str, Enum):
    json = "json"
    pickle = "pickle"


class InitialVesting(msgspec.Struct):
    vests_per_hive: int
    hive_amount: int


class HardforkSchedule(msgspec.Struct):
    hardfork: int
    block_num: int


class AlternateChainSpecs(PreconfiguredBaseModel):
    FILENAME: ClassVar[str] = "alternate-chain-spec.json"

    genesis_time: int
    hardfork_schedule: list[HardforkSchedule]
    init_supply: int | None = None
    hbd_init_supply: int | None = None
    initial_vesting: InitialVesting | None = None
    init_witnesses: list[str] | None = None
    hive_owner_update_limit: int | None = None
    generate_missed_block_operations: bool | None = None
    hf_21_stall_block: int | None = None
    min_root_comment_interval: int | None = None

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
        cls, path: str | Path, decoder_factory: Callable[[type[T]], msgspec.json.Decoder[T]]
    ) -> AlternateChainSpecs:
        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            path = path / cls.FILENAME

        assert path.is_file(), f"Given path: `{path.as_posix()}` is not pointing to file!"

        return super().parse_file(path, decoder_factory)
