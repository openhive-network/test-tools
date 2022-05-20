import test_tools as tt


def test_string_conversions():
    for asset, expected in [
        (tt.Asset.Hbd(1000), '1000.000 HBD'),
        (tt.Asset.Hive(3.14), '3.140 HIVE'),
        (tt.Asset.Vest(1000), '1000.000000 VESTS'),
    ]:
        assert str(asset) == expected


def test_nai_conversions():
    def nai(amount, precision, symbol):
        # Example of nai format for '1.000 HIVE':
        # {
        #   "amount": "1000",
        #   "precision": 3,
        #   "nai": "@@000000021"
        # }
        return {'amount': str(amount), 'precision': precision, 'nai': symbol}

    assert tt.Asset.Hbd(1000).as_nai() == nai(1000_000, 3, '@@000000013')
    assert tt.Asset.Hive(3.14).as_nai() == nai(3_140, 3, '@@000000021')
    assert tt.Asset.Vest(1000).as_nai() == nai(1000_000000, 6, '@@000000037')
