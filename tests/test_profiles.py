from fedora_cpu_limit.profiles import ProfileConfig, _valid_percent


def test_profile_defaults():
    config = ProfileConfig()
    assert config.ac_percent == 100
    assert config.battery_percent == 70
    assert config.automatic is False


def test_invalid_profile_percent_falls_back():
    assert _valid_percent(75, 70) == 70
    assert _valid_percent("invalid", 100) == 100


def test_valid_profile_percent_is_kept():
    assert _valid_percent(80, 100) == 80
