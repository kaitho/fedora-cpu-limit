#!/usr/bin/env python3
"""Privileged helper for Fedora CPU Limit."""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path("/sys/devices/system/cpu/cpufreq")
INTEL_PSTATE_BASE = Path("/sys/devices/system/cpu/intel_pstate")


def _driver() -> str | None:
    paths = sorted(BASE.glob("policy*/scaling_driver"))
    return paths[0].read_text().strip() if paths else None


def _set_frequency(frequency: int) -> int:
    if frequency <= 0:
        print("frequency must be positive", file=sys.stderr)
        return 2

    paths = sorted(BASE.glob("policy*/scaling_max_freq"))
    if not paths:
        print("no CPU policies found", file=sys.stderr)
        return 1

    # Never allow the helper to set a value above the hardware-reported maximum.
    for path in paths:
        policy = path.parent
        max_path = policy / "cpuinfo_max_freq"
        if not max_path.exists():
            max_path = policy / "amd_pstate_max_freq"
        if max_path.exists() and frequency > int(max_path.read_text().strip()):
            print(f"requested frequency exceeds {max_path}", file=sys.stderr)
            return 1

    for path in paths:
        path.write_text(f"{frequency}\n")
    return 0


def _set_intel_percent(percent: int) -> int:
    if not 1 <= percent <= 100:
        print("percent must be between 1 and 100", file=sys.stderr)
        return 2

    status_path = INTEL_PSTATE_BASE / "status"
    max_perf_path = INTEL_PSTATE_BASE / "max_perf_pct"

    try:
        status = status_path.read_text().strip()
    except OSError:
        status = ""

    if _driver() != "intel_pstate" or status != "active" or not max_perf_path.exists():
        print("intel_pstate active mode with max_perf_pct is not available", file=sys.stderr)
        return 1

    max_perf_path.write_text(f"{percent}\n")
    return 0


def main() -> int:
    # Backwards compatibility with v0.2.x helper calls: a single numeric
    # argument is treated as a frequency in kHz.
    if len(sys.argv) == 2:
        mode = "frequency"
        value_text = sys.argv[1]
    elif len(sys.argv) == 3:
        mode = sys.argv[1]
        value_text = sys.argv[2]
    else:
        print("usage: fedora-cpu-limit-helper [frequency|percent] VALUE", file=sys.stderr)
        return 2

    try:
        value = int(value_text)
    except ValueError:
        print("value must be an integer", file=sys.stderr)
        return 2

    if mode == "frequency":
        return _set_frequency(value)
    if mode == "percent":
        return _set_intel_percent(value)

    print("mode must be 'frequency' or 'percent'", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
