from fedora_cpu_limit.profiles import ProfileConfig


def test_profile_defaults():
    config = ProfileConfig()
    assert config.ac_percent == 100
    assert config.battery_percent == 70
    assert config.automatic is False
