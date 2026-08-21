# Fedora CPU Limit

A small KDE-friendly GUI for limiting maximum CPU frequency on Fedora Linux without changing the system power profile.

## Status

**v0.1.0 — initial development release**

The first release targets Linux systems using the `amd-pstate` family of CPU frequency drivers and exposes simple percentage limits such as 100%, 90%, 80%, 70%, 60%, and 50%.

The project was initially developed and tested on a Lenovo ThinkPad E14 Gen 4 with an AMD Ryzen 3 5425U running Fedora Linux 44 and KDE Plasma.

## Goals

- Keep Fedora/KDE Power Profile unchanged.
- Provide a simple GUI for CPU maximum-performance limits.
- Automatically detect CPU policy domains and maximum frequency.
- Apply the same limit consistently across all CPU policies.
- Use a narrowly scoped privileged helper rather than running the GUI as root.
- Eventually provide RPM/Flatpak packaging and optional automatic profiles.

## Planned features

- [ ] Qt/PySide6 GUI
- [ ] 50–100% CPU limit presets
- [ ] Current limit and frequency display
- [ ] Polkit-authenticated privileged helper
- [ ] Restore full performance
- [ ] CPU temperature and frequency monitoring
- [ ] KDE system-tray integration
- [ ] Battery/AC profiles
- [ ] RPM packaging
- [ ] Tests and CI

## Development

This project is being developed on Fedora Linux. The initial implementation uses Python and PySide6.

## License

MIT. See [LICENSE](LICENSE).
