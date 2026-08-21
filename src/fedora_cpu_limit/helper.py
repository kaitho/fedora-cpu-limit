from __future__ import annotations

import sys
from pathlib import Path

BASE = Path("/sys/devices/system/cpu/cpufreq")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: helper.py FREQUENCY_KHZ", file=sys.stderr)
        return 2
    try:
        frequency = int(sys.argv[1])
    except ValueError:
        print("frequency must be an integer", file=sys.stderr)
        return 2
    if frequency <= 0:
        print("frequency must be positive", file=sys.stderr)
        return 2

    paths = sorted(BASE.glob("policy*/scaling_max_freq"))
    if not paths:
        print("no CPU policies found", file=sys.stderr)
        return 1

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


if __name__ == "__main__":
    raise SystemExit(main())
