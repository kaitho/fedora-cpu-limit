from fedora_cpu_limit.cpu import target_frequency


def test_target_frequency_80_percent():
    assert target_frequency(80, 4_151_538) == 3_321_230


def test_target_frequency_100_percent():
    assert target_frequency(100, 4_151_538) == 4_151_538


def test_target_frequency_rejects_invalid_values():
    for value in (0, 101, -1):
        try:
            target_frequency(value, 4_151_538)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid percentage was accepted")
