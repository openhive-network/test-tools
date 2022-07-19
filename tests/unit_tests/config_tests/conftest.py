import pytest

from test_tools.__private.configuration.experimental_config import Config


@pytest.fixture
def config(request):
    return Config(request.module.__package__)
