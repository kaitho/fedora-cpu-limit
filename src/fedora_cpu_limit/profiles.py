from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "fedora-cpu-limit"
CONFIG_FILE = CONFIG_DIR / "profiles.json"


@dataclass
class ProfileConfig:
    ac_percent: int = 100
    battery_percent: int = 70
    automatic: bool = False


def load_config() -> ProfileConfig:
    if not CONFIG_FILE.exists():
        return ProfileConfig()
    try:
        data = json.loads(CONFIG_FILE.read_text())
        return ProfileConfig(
            ac_percent=int(data.get("ac_percent", 100)),
            battery_percent=int(data.get("battery_percent", 70)),
            automatic=bool(data.get("automatic", False)),
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return ProfileConfig()


def save_config(config: ProfileConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2) + "\n")


def on_ac_power() -> bool | None:
    base = Path("/sys/class/power_supply")
    mains = []
    for supply in base.glob("*"):
        try:
            supply_type = (supply / "type").read_text().strip()
        except OSError:
            continue
        if supply_type in {"Mains", "USB", "USB_C", "USB_PD"}:
            mains.append(supply)
    if not mains:
        return None
    for supply in mains:
        online = supply / "online"
        try:
            if online.exists() and online.read_text().strip() == "1":
                return True
        except OSError:
            pass
    return False
