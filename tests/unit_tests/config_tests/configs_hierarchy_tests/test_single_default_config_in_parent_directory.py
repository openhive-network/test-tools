def test_loading_default_parameter(config):

    assert config.location == 'parent'
    assert config.data == ['a']
