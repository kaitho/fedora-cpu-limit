# Fedora CPU Limit

A small KDE-friendly GUI for limiting maximum CPU frequency on Fedora Linux without changing the system power profile.

## Status

**v0.1.1 — development release**

The project targets Linux systems using the `amd-pstate` family of CPU frequency drivers and exposes simple percentage limits such as 100%, 90%, 80%, 70%, 60%, and 50%.

The initial hardware target is a Lenovo ThinkPad E14 Gen 4 with an AMD Ryzen 3 5425U running Fedora Linux 44 and KDE Plasma. The implementation automatically discovers CPU policy domains rather than depending on that specific machine.

## v0.1.1

- PySide6 GUI with 50–100% presets
- Restore 100% button
- Automatic CPU policy and maximum-frequency detection
- Live average CPU frequency telemetry
- Live `k10temp` CPU temperature telemetry when available
- Privileged helper separated from the GUI
- Polkit policy for the installed helper
- Desktop launcher
- Initial unit tests

## Safety model

The GUI is not run as root. Only the small helper that writes `scaling_max_freq` is executed through `pkexec`. The helper validates the requested frequency against the detected CPU maximum and applies the same value to every discovered CPU policy.

## Local installation

Install build dependencies and PySide6 as appropriate for your Fedora setup, then from the repository root run:

```bash
bash packaging/install-local.sh
```

For development, the GUI can also be launched directly with:

```bash
python3 -m fedora_cpu_limit.app
```

The development fallback helper is intended for testing only; an installed system should use `/usr/libexec/fedora-cpu-limit-helper` together with the packaged Polkit policy.

## Roadmap

- KDE system-tray integration
- Battery/AC profiles
- RPM packaging and COPR
- Flatpak packaging
- CI and broader hardware tests
- Optional custom percentage limits

## License

MIT. See [LICENSE](LICENSE).
