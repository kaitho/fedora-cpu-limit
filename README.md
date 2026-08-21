# Fedora CPU Limit

A small KDE-friendly GUI for limiting maximum CPU frequency on Linux without changing the system power profile.

> **Current focus:** Fedora Linux. Support and packaging for additional Linux distributions are planned for future releases.

## Status

**v0.2.0 — development release, tested on real hardware**

Fedora CPU Limit targets systems using the `amd-pstate` family of CPU frequency drivers and provides simple maximum CPU limits of 100%, 90%, 80%, 70%, 60%, and 50%.

Version 0.2.0 expands the original manual CPU limiter with system-tray integration and automatic AC/battery profiles while preserving the existing privileged-helper safety model.

## Verified hardware

The current version has been successfully tested on:

- Lenovo ThinkPad E14 Gen 4 (21ECS11E00)
- AMD Ryzen 3 5425U with Radeon Graphics
- Fedora Linux 44
- KDE Plasma / Wayland
- Linux kernel 7.1.8
- `amd-pstate-epp`
- 8 CPU policy domains / logical CPUs

On this test system the CPU reports a maximum frequency of 4,151,538 kHz. An 80% limit is calculated as 3,321,230 kHz and was verified under CPU load, with observed frequencies staying at approximately 3.318 GHz.

The implementation automatically discovers CPU policy domains and maximum frequency, so it is not hard-coded to this ThinkPad or CPU.

## What's new in v0.2.0

- KDE/system-tray integration
- Quick tray actions for 50–100% CPU limits
- Close-to-tray behavior
- Persistent AC and battery profile settings
- Automatic CPU-limit switching when the power source changes
- Configurable AC and battery percentages
- Power-source status in the main window
- Desktop notifications when an automatic profile is applied
- Existing manual 50–100% controls remain available
- Restore 100% button
- Automatic CPU policy and maximum-frequency detection
- Live average CPU frequency telemetry
- Live `k10temp` CPU temperature telemetry when available
- Privileged helper separated from the GUI
- Polkit authentication for changing CPU limits
- KDE desktop launcher
- Unit tests and CI groundwork
- Fedora/KDE Power Profile remains unchanged

## Automatic AC and battery profiles

Version 0.2.0 can maintain separate CPU limits for AC power and battery operation. For example, you can configure:

```text
AC power: 100%
Battery:   70%
```

When automatic switching is enabled, Fedora CPU Limit detects power-source changes and applies the configured profile. Connecting AC can restore full CPU performance, while disconnecting AC can automatically apply a lower limit for reduced power consumption and heat.

The manual CPU-limit controls continue to work independently when automatic switching is disabled.

## System tray

Fedora CPU Limit can remain active in the KDE system tray when its main window is closed. The tray menu provides quick access to the CPU-limit presets and lets the application continue watching for AC/battery changes in the background.

Use the tray application's Quit action when you want to exit the program completely.

## Safety model

The GUI itself is never run as root. Only the small helper that writes to `scaling_max_freq` is executed through `pkexec`.

Before changing anything, the helper validates the requested frequency against the maximum frequency reported by each CPU policy. The selected limit is then applied consistently to every discovered `policy*/scaling_max_freq` entry.

## Local installation on Fedora

Clone the repository and install from its root directory:

```bash
git clone https://github.com/kaitho/fedora-cpu-limit.git
cd fedora-cpu-limit
git switch feature/v0.2.0
bash packaging/install-local.sh
```

After installation, launch **Fedora CPU Limit** from KDE's application menu.

To update an existing v0.2.0 development checkout:

```bash
cd ~/fedora-cpu-limit
git switch feature/v0.2.0
git pull
bash packaging/install-local.sh
```

For development, the GUI can also be launched directly with:

```bash
python3 -m fedora_cpu_limit.app
```

## Troubleshooting

### `Exec format error` when applying a CPU limit

An early v0.1.1 development build could show an error similar to:

```text
Error executing /usr/libexec/fedora-cpu-limit-helper: Exec format error
```

The cause was that the installed Python helper was executable but did not contain a Unix shebang. Because Polkit/`pkexec` executes `/usr/libexec/fedora-cpu-limit-helper` directly, Linux did not know which interpreter should run the file.

The helper now begins with:

```python
#!/usr/bin/env python3
```

This is fixed in current source. If you installed an older copy, update and reinstall it:

```bash
cd ~/fedora-cpu-limit
git pull
bash packaging/install-local.sh
```

You can verify the installed helper with:

```bash
head -n 1 /usr/libexec/fedora-cpu-limit-helper
```

Expected output:

```text
#!/usr/bin/env python3
```

### Verify the active CPU limit

```bash
for f in /sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq; do
    echo "$f: $(cat "$f")"
done
```

For the verified Ryzen 3 5425U test system, selecting 80% should report approximately `3321230` for every policy.

### Check the CPU frequency driver

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

The primary tested driver is:

```text
amd-pstate-epp
```

## Distribution support

Fedora is the current development and testing platform, and the installer and desktop integration are currently designed around Fedora/KDE.

**Support for other Linux distributions is planned for future versions.** The core CPU-control approach uses standard Linux sysfs CPU-frequency interfaces, so future work can focus on distro-specific installation, dependencies, Polkit integration, packaging, and testing.

Planned expansion includes evaluating support for distributions such as Ubuntu/Debian, openSUSE, Arch Linux and other compatible Linux systems. These distributions are not yet officially supported or verified.

Contributions and hardware/distro testing reports are welcome as the project expands beyond Fedora.

## Roadmap

- Polish and release v0.2.0
- Optional custom percentage limits
- Autostart / improved KDE session integration
- RPM packaging and Fedora COPR
- Broader AMD hardware testing
- Additional telemetry and profile controls
- Packaging and verified support for additional Linux distributions
- Evaluate Debian/Ubuntu, openSUSE and Arch Linux support
- Flatpak feasibility investigation

## License

MIT. See [LICENSE](LICENSE).
