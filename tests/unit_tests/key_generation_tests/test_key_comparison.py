from __future__ import annotations

import pytest
import test_tools as tt

from schemas.fields.basic import PrivateKey, PublicKey


@pytest.mark.requires_hived_executables
def test_if_same_accounts_have_same_keys() -> None:
    assert tt.Account("alice") == tt.Account("alice")


@pytest.mark.requires_hived_executables
def test_if_different_accounts_have_different_keys() -> None:
    assert tt.Account("alice") != tt.Account("bob")


@pytest.mark.requires_hived_executables
def test_check_of_private_key_presence_in_set_of_keys() -> None:
    assert PrivateKey("5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n") in {
        PrivateKey(name)
        for name in [
            "4JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n",
            "5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n",
            "6JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n",
        ]
    }


@pytest.mark.requires_hived_executables
def test_check_of_public_key_presence_in_set_of_keys() -> None:
    assert PublicKey("STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4") in {
        PublicKey(name)
        for name in [
            "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg3",
            "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4",
            "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg5",
        ]
    }


@pytest.mark.requires_hived_executables
def test_check_of_private_key_presence_in_set_of_strings() -> None:
    assert PrivateKey("5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n") in {
        str(PrivateKey(name))
        for name in [
            "4JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n",
            "5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n",
            "6JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n",
        ]
    }


@pytest.mark.requires_hived_executables
def test_check_of_public_key_presence_in_set_of_strings() -> None:
    assert PublicKey("STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4") in {
        str(PublicKey(name))
        for name in [
            "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg3",
            "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4",
            "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg5",
        ]
    }
