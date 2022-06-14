def test_loading_default_parameter(config):
    assert config.location == 'default'
    assert config.data == ['a']
