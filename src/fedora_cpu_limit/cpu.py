from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BASE = Path("/sys/devices/system/cpu/cpufreq")
INTEL_PSTATE_BASE = Path("/sys/devices/system/cpu/intel_pstate")


@dataclass(frozen=True)
class CpuPolicy:
    path: Path
    max_freq: int
    current_limit: int


def policy_paths() -> list[Path]:
    return sorted(BASE.glob("policy*/scaling_max_freq"))


def read_int(path: Path) -> int:
    return int(path.read_text().strip())


def _maximum_path(policy_dir: Path) -> Path | None:
    for name in ("cpuinfo_max_freq", "amd_pstate_max_freq"):
        path = policy_dir / name
        if path.exists():
            return path
    return None


def policies() -> list[CpuPolicy]:
    result: list[CpuPolicy] = []
    for max_path in policy_paths():
        maximum_path = _maximum_path(max_path.parent)
        if maximum_path is None:
            continue
        result.append(CpuPolicy(max_path.parent, read_int(maximum_path), read_int(max_path)))
    return result


def driver() -> str | None:
    paths = sorted(BASE.glob("policy*/scaling_driver"))
    return paths[0].read_text().strip() if paths else None


def intel_pstate_active() -> bool:
    status = INTEL_PSTATE_BASE / "status"
    max_perf = INTEL_PSTATE_BASE / "max_perf_pct"
    try:
        return driver() == "intel_pstate" and status.read_text().strip() == "active" and max_perf.exists()
    except OSError:
        return False


def control_mode() -> str:
    """Return the preferred limiting backend for the current CPU driver."""
    if intel_pstate_active():
        return "intel_percent"
    return "frequency"


def control_description() -> str:
    if control_mode() == "intel_percent":
        return "Intel P-state percentage"
    drv = driver() or "unknown"
    return f"CPUFreq frequency ({drv})"


def target_frequency(percent: int, maximum: int) -> int:
    if not 1 <= percent <= 100:
        raise ValueError("percent must be between 1 and 100")
    return round(maximum * percent / 100)


def current_percent() -> int | None:
    if intel_pstate_active():
        try:
            return read_int(INTEL_PSTATE_BASE / "max_perf_pct")
        except (OSError, ValueError):
            return None

    items = policies()
    if not items:
        return None
    return min(round(p.current_limit * 100 / p.max_freq) for p in items)


def current_frequency() -> int | None:
    items = policies()
    return min(p.current_limit for p in items) if items else None


def current_cpu_mhz() -> float | None:
    values: list[float] = []
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("cpu MHz"):
                values.append(float(line.split(":", 1)[1].strip()))
    except (OSError, ValueError):
        return None
    return sum(values) / len(values) if values else None


def temperature_c() -> float | None:
    preferred_names = ("k10temp", "coretemp")
    hwmons = sorted(Path("/sys/class/hwmon").glob("hwmon*"))

    for preferred in preferred_names:
        for hwmon in hwmons:
            try:
                name = (hwmon / "name").read_text().strip()
            except OSError:
                continue
            if name != preferred:
                continue
            for path in sorted(hwmon.glob("temp*_input")):
                try:
                    return read_int(path) / 1000.0
                except (OSError, ValueError):
                    continue
    return None
