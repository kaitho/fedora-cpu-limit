# Fedora CPU Limit

A small KDE-friendly GUI for limiting maximum CPU frequency on Fedora Linux without changing the system power profile.

## Status

**v0.1.1 — development release, tested on real hardware**

The project targets Linux systems using the `amd-pstate` family of CPU frequency drivers and exposes simple percentage limits: 100%, 90%, 80%, 70%, 60%, and 50%.

### Verified hardware

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

## v0.1.1 features

- PySide6 / Qt GUI with 50–100% presets
- Restore 100% button
- Automatic CPU policy and maximum-frequency detection
- Live average CPU frequency telemetry
- Live `k10temp` CPU temperature telemetry when available
- Privileged helper separated from the GUI
- Polkit authentication for changing the CPU limit
- KDE desktop launcher
- Initial unit tests and CI
- Keeps the Fedora/KDE Power Profile unchanged

## Safety model

The GUI itself is never run as root. Only the small helper that writes to `scaling_max_freq` is executed through `pkexec`.

Before changing anything, the helper validates the requested frequency against the maximum frequency reported by each CPU policy. The selected limit is then applied consistently to every discovered `policy*/scaling_max_freq` entry.

## Local installation

Clone the repository and install from its root directory:

```bash
git clone https://github.com/kaitho/fedora-cpu-limit.git
cd fedora-cpu-limit
bash packaging/install-local.sh
```

After installation, launch **Fedora CPU Limit** from KDE's application menu.

To update an existing clone:

```bash
cd ~/fedora-cpu-limit
git pull
bash packaging/install-local.sh
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

This is fixed in the current source. If you installed an older copy, update and reinstall it:

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

To inspect all CPU policy limits:

```bash
for f in /sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq; do
    echo "$f: $(cat "$f")"
done
```

For the verified Ryzen 3 5425U test system, selecting 80% should report approximately:

```text
3321230
```

for every policy.

### Check the CPU frequency driver

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

The primary tested driver is:

```text
amd-pstate-epp
```

## Development

For development, install the package in your preferred Python environment and launch the GUI with:

```bash
python3 -m fedora_cpu_limit.app
```

The development fallback helper is intended for testing only. An installed system should use `/usr/libexec/fedora-cpu-limit-helper` together with the packaged Polkit policy.

## Roadmap

- KDE system-tray integration
- Automatic battery/AC profiles
- RPM packaging and COPR
- Flatpak packaging
- Broader AMD hardware testing
- Optional custom percentage limits
- Additional telemetry and profile controls

## License

MIT. See [LICENSE](LICENSE).
