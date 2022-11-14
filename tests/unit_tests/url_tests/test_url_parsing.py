import pytest

from local_tools.constants import DEFAULT_ADDRESS, DEFAULT_PORT
from test_tools.__private.url import Url


@pytest.mark.parametrize(
    "input_url, expected_protocol",
    [
        (f"http://{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "http"),
        (f"ws://{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "ws"),
    ],
)
def test_url_parsing_without_expected_protocol(input_url, expected_protocol):
    url = Url(input_url)

    assert url.protocol == expected_protocol
    assert url.address == DEFAULT_ADDRESS
    assert url.port == DEFAULT_PORT


@pytest.mark.parametrize(
    "input_url, expected_protocol",
    [
        (f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "http"),
        (f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "ws"),
    ],
)
def test_url_parsing_with_expected_protocol(input_url, expected_protocol):
    url = Url(input_url, protocol=expected_protocol)

    assert url.protocol == expected_protocol
    assert url.address == DEFAULT_ADDRESS
    assert url.port == DEFAULT_PORT


@pytest.mark.parametrize(
    "input_url, expected_protocol",
    [
        (DEFAULT_ADDRESS, "http"),
        (DEFAULT_ADDRESS, "ws"),
    ],
)
def test_url_parsing_without_port_given(input_url: str, expected_protocol: int):
    url = Url(input_url, protocol=expected_protocol)

    assert url.protocol == expected_protocol
    assert url.address == DEFAULT_ADDRESS
    assert url.port is None


def test_url_parsing_without_address_given():
    with pytest.raises(ValueError) as exception:
        Url(f":{DEFAULT_PORT}")

    assert str(exception.value) == "Address was not specified."
