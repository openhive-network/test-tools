import pytest

import test_tools as tt


@pytest.mark.requires_hived_executables
def test_key_to_string_conversion_with_repr():
    assert repr(tt.PrivateKey('alice')) == "PrivateKey('5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik')"
    assert repr(tt.PublicKey('alice')) == "PublicKey('TST5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW')"


@pytest.mark.requires_hived_executables
def test_key_to_string_conversion_with_str():
    assert str(tt.PrivateKey('alice')) == '5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik'
    assert str(tt.PublicKey('alice')) == 'TST5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW'
