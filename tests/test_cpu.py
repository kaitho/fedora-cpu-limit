from fedora_cpu_limit.cpu import target_frequency


def test_target_frequency_percentages() -> None:
    maximum = 4_151_538
    assert target_frequency(100, maximum) == 4_151_538
    assert target_frequency(80, maximum) == 3_321_230
    assert target_frequency(50, maximum) == 2_075_769


def test_target_frequency_rejects_invalid_values() -> None:
    maximum = 4_151_538
    for value in (0, -1, 101):
        try:
            target_frequency(value, maximum)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid percentage was accepted")
