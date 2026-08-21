#!/usr/bin/env bash
set -euo pipefail

PREFIX="${PREFIX:-/usr}"
LIBEXEC="${PREFIX}/libexec"
POLKIT_DIR="${PREFIX}/share/polkit-1/actions"
DESKTOP_DIR="${PREFIX}/share/applications"

python3 -m pip install --user .
sudo install -Dm755 src/fedora_cpu_limit/helper.py "${LIBEXEC}/fedora-cpu-limit-helper"
sudo install -Dm644 polkit/org.kaitho.fedoracpulimit.policy "${POLKIT_DIR}/org.kaitho.fedoracpulimit.policy"
sudo install -Dm644 packaging/fedora-cpu-limit.desktop "${DESKTOP_DIR}/fedora-cpu-limit.desktop"

echo "Installed Fedora CPU Limit. Launch it from KDE's application menu."
