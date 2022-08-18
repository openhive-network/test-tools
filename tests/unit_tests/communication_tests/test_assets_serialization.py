import json

import test_tools as tt
from test_tools.__private.communication import JsonEncoderWithLegacyAssets, JsonEncoderWithNaiAssets


def test_legacy_serialization():
    serialized = json.dumps(tt.Asset.Hive(10), cls=JsonEncoderWithLegacyAssets)
    assert serialized == '"10.000 HIVE"'


def test_nai_serialization():
    serialized = json.dumps(tt.Asset.Hive(10), cls=JsonEncoderWithNaiAssets)
    assert serialized == '{"amount": "10000", "precision": 3, "nai": "@@000000021"}'
