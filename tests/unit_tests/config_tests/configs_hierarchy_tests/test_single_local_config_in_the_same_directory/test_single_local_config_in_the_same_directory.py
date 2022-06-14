from pathlib import Path

from test_tools.__private.configuration.experimental_config import Config


def test_loading_local_parameter():
    config = Config(Path(__file__).parent)
    assert config.example_parameter is True
