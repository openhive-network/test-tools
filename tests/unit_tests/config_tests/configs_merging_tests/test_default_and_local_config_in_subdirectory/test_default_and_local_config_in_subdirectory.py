def test_loading_local_parameter(config):
    assert config.location == 'same_folder_local'
    assert config.data == ['b', 'c']
