from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from schemas._preconfigured_base_model import PreconfiguredBaseModel
from test_tools.__private.user_handles import context

if TYPE_CHECKING:
    from schemas.decoders import DecoderFactory


class Protocol(str, Enum):
    json = "json"
    pickle = "pickle"


class InitialVesting(PreconfiguredBaseModel):
    vests_per_hive: int
    hive_amount: int


class HardforkSchedule(PreconfiguredBaseModel):
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
    witness_custom_op_block_limit: int | None = None

    def export_to_file(self, output_dir: Path | None = None) -> Path:
        if output_dir is None:
            output_dir = context.get_current_directory()
        output_dir.mkdir(parents=True, exist_ok=True)
        destination = output_dir / AlternateChainSpecs.FILENAME
        with destination.open("w") as json_file:
            json_file.write(self.json(exclude_none=True))
        return destination

    @classmethod
    def parse_file(cls, path: Path, custom_decoder_factory: DecoderFactory | None = None) -> AlternateChainSpecs:
        # Default decoder is hf26_decoder
        if custom_decoder_factory is None:
            from schemas.decoders import get_hf26_decoder

            custom_decoder_factory = get_hf26_decoder

        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            path = path / AlternateChainSpecs.FILENAME

        assert path.is_file(), f"Given path: `{path.as_posix()}` is not pointing to file!"
        return super().parse_file(path, custom_decoder_factory)
