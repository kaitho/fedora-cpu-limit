from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BASE = Path("/sys/devices/system/cpu/cpufreq")


@dataclass(frozen=True)
class CpuPolicy:
    path: Path
    max_freq: int
    current_limit: int


def policy_paths() -> list[Path]:
    return sorted(BASE.glob("policy*/scaling_max_freq"))


def read_int(path: Path) -> int:
    return int(path.read_text().strip())


def policies() -> list[CpuPolicy]:
    result: list[CpuPolicy] = []
    for max_path in policy_paths():
        policy_dir = max_path.parent
        cpuinfo_max = policy_dir / "cpuinfo_max_freq"
        if not cpuinfo_max.exists():
            cpuinfo_max = policy_dir / "amd_pstate_max_freq"
        if not cpuinfo_max.exists():
            continue
        result.append(CpuPolicy(policy_dir, read_int(cpuinfo_max), read_int(max_path)))
    return result


def driver() -> str | None:
    paths = sorted(BASE.glob("policy*/scaling_driver"))
    if not paths:
        return None
    return paths[0].read_text().strip()


def target_frequency(percent: int, maximum: int) -> int:
    if not 1 <= percent <= 100:
        raise ValueError("percent must be between 1 and 100")
    return round(maximum * percent / 100)


def current_percent() -> int | None:
    items = policies()
    if not items:
        return None
    percentages = [round(p.current_limit * 100 / p.max_freq) for p in items]
    return min(percentages)
