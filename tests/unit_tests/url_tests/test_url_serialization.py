import pytest

from local_tools.constants import DEFAULT_ADDRESS, DEFAULT_PORT
from test_tools.__private.url import Url


@pytest.mark.parametrize(
    "url, with_protocol, expected",
    [
        (Url(f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", protocol="http"), True, f"http://{DEFAULT_ADDRESS}:{DEFAULT_PORT}"),
        (Url(f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", protocol="http"), False, f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}"),
        (Url(f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}"), False, f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}"),
    ],
)
def test_serialization(url: Url, with_protocol: bool, expected: str):
    assert url.as_string(with_protocol=with_protocol) == expected
