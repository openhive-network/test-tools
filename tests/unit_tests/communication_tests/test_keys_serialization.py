import json

import pytest

import test_tools as tt
from test_tools.__private.communication import CustomJsonEncoder


@pytest.mark.requires_hived_executables
def test_keys_serialization():
    def as_json(key) -> str:
        return json.dumps(key, cls=CustomJsonEncoder)

    assert as_json(tt.PrivateKey('alice')) == '"5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik"'
    assert as_json(tt.PublicKey('alice')) == '"TST5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW"'
