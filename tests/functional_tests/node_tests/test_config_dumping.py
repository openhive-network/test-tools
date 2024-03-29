from __future__ import annotations

import pytest
import test_tools as tt


def test_config_dumping_with_unknown_entry() -> None:
    # ARRANGE
    node = tt.RawNode()

    node.config_file_path.parent.mkdir(parents=True, exist_ok=True)
    with node.config_file_path.open("w", encoding="utf-8") as file:
        file.write("unknown_entry = 1")

    # ACT & ASSERT
    with pytest.raises(tt.exceptions.ConfigError) as exception:
        node.dump_config()

    assert str(exception.value) == "RawNode0 config dump failed because of entry not known to TestTools."
