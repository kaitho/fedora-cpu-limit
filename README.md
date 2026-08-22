# Fedora CPU Limit

A small KDE-friendly GUI for limiting CPU performance on Linux without changing the system power profile.

> **Current focus:** Fedora Linux. Support and packaging for additional Linux distributions are planned for future releases.

## Status

**v0.3.0 — in development**

Fedora CPU Limit now supports both AMD and Intel CPU control paths:

- AMD systems using the `amd-pstate` family continue to use per-policy maximum frequency limits.
- Intel systems using `intel_pstate` in active mode use the native `max_perf_pct` percentage control.

The GUI keeps the same simple 100%, 90%, 80%, 70%, 60%, and 50% controls and automatically selects the correct backend.

## Verified hardware

Successfully tested on real Fedora 44 hardware:

### AMD

- Lenovo ThinkPad E14 Gen 4 (21ECS11E00)
- AMD Ryzen 3 5425U with Radeon Graphics
- Fedora Linux 44
- KDE Plasma / Wayland
- Linux kernel 7.1.8
- `amd-pstate-epp`

On this system, 80% maps to 3,321,230 kHz and was verified under load at approximately 3.318 GHz.

### Intel

- Lenovo ThinkPad E14 Gen 6 (21M7002GMX)
- Intel Core Ultra 5 125U — 12 cores / 14 threads
- Fedora Linux 44
- KDE Plasma / Wayland
- Linux kernel 7.1.9
- `intel_pstate` active mode
- Hardware maximum reported as 4.30 GHz

The native Intel percentage control was verified manually by changing `/sys/devices/system/cpu/intel_pstate/max_perf_pct` from 100 to 80 and back to 100 without rebooting.

## What's new in v0.3.0

- Intel `intel_pstate` active-mode support
- Native Intel `max_perf_pct` backend
- Automatic backend detection
- Existing AMD `amd-pstate` frequency backend preserved
- GUI now shows the active control method
- Intel `coretemp` telemetry support in addition to AMD `k10temp`
- Backwards-compatible privileged helper command handling
- Version metadata synchronized to 0.3.0

## Features

- Manual 50–100% CPU performance controls
- Restore 100% button
- KDE/system-tray integration
- Quick tray actions
- Close-to-tray behavior
- Persistent AC and battery profile settings
- Automatic switching when the power source changes
- Live CPU frequency telemetry
- CPU temperature telemetry on supported AMD and Intel sensors
- Polkit-authenticated privileged helper
- Fedora/KDE Power Profile remains unchanged

## Automatic AC and battery profiles

Example configuration:

```text
AC power: 100%
Battery:   70%
```

When automatic switching is enabled, the configured limit is applied when the power source changes.

## How backend selection works

### Intel

When `intel_pstate` is active and `max_perf_pct` is available, Fedora CPU Limit writes the selected percentage directly to:

```text
/sys/devices/system/cpu/intel_pstate/max_perf_pct
```

For example, selecting 80% writes `80` directly. Intel P-state/HWP remains responsible for selecting actual clock frequencies within that performance ceiling.

### AMD and CPUFreq fallback

For the existing AMD path, the selected percentage is converted to a maximum frequency based on the hardware-reported maximum and written to each CPU policy's `scaling_max_freq`.

## Safety model

The GUI is never run as root. Only the small helper that performs the required sysfs write is executed through `pkexec`.

The helper:

- validates percentage values to the range 1–100 for Intel
- verifies that Intel percentage mode is only used with active `intel_pstate`
- validates frequency limits against the hardware-reported maximum for the CPUFreq backend
- keeps compatibility with the v0.2.x single-frequency helper invocation

## Local installation on Fedora

```bash
git clone https://github.com/kaitho/fedora-cpu-limit.git
cd fedora-cpu-limit
bash packaging/install-local.sh
```

Launch **Fedora CPU Limit** from KDE's application menu.

To update:

```bash
cd ~/Github/fedora-cpu-limit
git switch main
git pull
bash packaging/install-local.sh
```

## Testing the v0.3.0 development branch

```bash
cd ~/Github/fedora-cpu-limit
git fetch origin
git switch feature/intel-pstate-v0.3.0
git pull
bash packaging/install-local.sh
```

Then launch Fedora CPU Limit and verify that the information panel reports:

```text
Driver: intel_pstate
Control: Intel P-state percentage
```

Changing a limit can be verified with:

```bash
cat /sys/devices/system/cpu/intel_pstate/max_perf_pct
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

### Check CPU frequency driver

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

### Intel P-state status

```bash
cat /sys/devices/system/cpu/intel_pstate/status
cat /sys/devices/system/cpu/intel_pstate/max_perf_pct
```

### Verify CPUFreq limits

```bash
for f in /sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq; do
    echo "$f: $(cat "$f")"
done
```

## Distribution support

Fedora is the current development and testing platform. **Support for other Linux distributions is planned for future versions.** Future work will cover distro-specific dependencies, Polkit integration, packaging, and testing.

Planned evaluation includes Ubuntu/Debian, openSUSE, Arch Linux, and other compatible Linux systems. These are not yet officially supported or verified.

## Roadmap

- Optional custom percentage limits
- Autostart / improved KDE session integration
- RPM packaging and Fedora COPR
- Broader AMD and Intel hardware testing
- Additional telemetry and profile controls
- Packaging and verified support for additional Linux distributions
- Flatpak feasibility investigation

## License

MIT. See [LICENSE](LICENSE).
