from pathlib import Path

import fedora_cpu_limit.cpu as cpu
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


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def test_intel_pstate_active_uses_native_percentage(tmp_path, monkeypatch) -> None:
    cpufreq = tmp_path / "cpufreq"
    intel = tmp_path / "intel_pstate"

    _write(cpufreq / "policy0" / "scaling_driver", "intel_pstate\n")
    _write(cpufreq / "policy0" / "scaling_max_freq", "4300000\n")
    _write(cpufreq / "policy0" / "cpuinfo_max_freq", "4300000\n")
    _write(intel / "status", "active\n")
    _write(intel / "max_perf_pct", "80\n")

    monkeypatch.setattr(cpu, "BASE", cpufreq)
    monkeypatch.setattr(cpu, "INTEL_PSTATE_BASE", intel)

    assert cpu.driver() == "intel_pstate"
    assert cpu.intel_pstate_active() is True
    assert cpu.control_mode() == "intel_percent"
    assert cpu.current_percent() == 80


def test_non_intel_driver_uses_frequency_backend(tmp_path, monkeypatch) -> None:
    cpufreq = tmp_path / "cpufreq"
    intel = tmp_path / "intel_pstate"

    _write(cpufreq / "policy0" / "scaling_driver", "amd-pstate-epp\n")
    _write(cpufreq / "policy0" / "scaling_max_freq", "3321230\n")
    _write(cpufreq / "policy0" / "amd_pstate_max_freq", "4151538\n")

    monkeypatch.setattr(cpu, "BASE", cpufreq)
    monkeypatch.setattr(cpu, "INTEL_PSTATE_BASE", intel)

    assert cpu.control_mode() == "frequency"
    assert cpu.current_percent() == 80
