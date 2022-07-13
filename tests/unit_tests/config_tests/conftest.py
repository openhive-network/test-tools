from pathlib import Path

import pytest

from test_tools.__private.configuration.experimental_config import Config


@pytest.fixture(autouse=True)
def config(request):
    return Config(Path(request.path).parent)
