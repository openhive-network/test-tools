def test_loading_default_parameter(config):
    assert config.location == 'same_folder'
    assert config.data == ['a', 'b']
