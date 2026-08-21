# Fedora CPU Limit

A small KDE-friendly GUI for limiting maximum CPU frequency on Linux without changing the system power profile.

> **Current focus:** Fedora Linux. Support and packaging for additional Linux distributions are planned for future releases.

## Status

**v0.2.0 — current release, tested on real hardware**

Fedora CPU Limit targets systems using the `amd-pstate` family of CPU frequency drivers and provides simple maximum CPU limits of 100%, 90%, 80%, 70%, 60%, and 50%.

Version 0.2.0 adds KDE/system-tray integration and automatic AC/battery profiles while preserving the privileged-helper safety model.

## Verified hardware

Successfully tested on:

- Lenovo ThinkPad E14 Gen 4 (21ECS11E00)
- AMD Ryzen 3 5425U with Radeon Graphics
- Fedora Linux 44
- KDE Plasma / Wayland
- Linux kernel 7.1.8
- `amd-pstate-epp`

On this system, 80% maps to 3,321,230 kHz and was verified under load at approximately 3.318 GHz.

## What's new in v0.2.0

- KDE/system-tray integration
- Quick tray actions for 50–100% CPU limits
- Close-to-tray behavior
- Persistent AC and battery profile settings
- Automatic switching when the power source changes
- Configurable AC and battery percentages
- Power-source status in the main window
- Desktop notifications for automatic profile changes
- Manual 50–100% controls remain available
- Restore 100% button
- Live CPU frequency and `k10temp` temperature telemetry
- Polkit-authenticated privileged helper
- Fedora/KDE Power Profile remains unchanged

## Automatic AC and battery profiles

Example configuration:

```text
AC power: 100%
Battery:   70%
```

When automatic switching is enabled, the configured limit is applied when the power source changes.

## System tray

Closing the main window keeps Fedora CPU Limit running in the KDE system tray. Use the tray menu for quick percentage changes or **Quit** to exit completely.

## Safety model

The GUI is never run as root. Only the small helper that writes `scaling_max_freq` is executed through `pkexec`. The helper validates requested frequencies against each CPU policy's reported maximum before applying them.

## Local installation on Fedora

```bash
git clone https://github.com/kaitho/fedora-cpu-limit.git
cd fedora-cpu-limit
bash packaging/install-local.sh
```

Launch **Fedora CPU Limit** from KDE's application menu.

To update:

```bash
cd ~/fedora-cpu-limit
git switch main
git pull
bash packaging/install-local.sh
```

## Troubleshooting

### `Exec format error`

An early v0.1.1 build could show:

```text
Error executing /usr/libexec/fedora-cpu-limit-helper: Exec format error
```

The helper was missing its Python shebang. Current versions begin with:

```python
#!/usr/bin/env python3
```

Verify with:

```bash
head -n 1 /usr/libexec/fedora-cpu-limit-helper
```

### Verify active limits

```bash
for f in /sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq; do
    echo "$f: $(cat "$f")"
done
```

### Check CPU frequency driver

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

The primary verified driver is `amd-pstate-epp`.

## Distribution support

Fedora is the current development and testing platform. **Support for other Linux distributions is planned for future versions.** Future work will cover distro-specific dependencies, Polkit integration, packaging, and testing.

Planned evaluation includes Ubuntu/Debian, openSUSE, Arch Linux, and other compatible Linux systems. These are not yet officially supported or verified.

## Roadmap

- Optional custom percentage limits
- Autostart / improved KDE session integration
- RPM packaging and Fedora COPR
- Broader AMD hardware testing
- Additional telemetry and profile controls
- Packaging and verified support for additional Linux distributions
- Flatpak feasibility investigation

## License

MIT. See [LICENSE](LICENSE).
