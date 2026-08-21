from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .cpu import current_cpu_mhz, current_percent, driver, policies, target_frequency, temperature_c
from .profiles import ProfileConfig, load_config, on_ac_power, save_config

INSTALLED_HELPER = Path("/usr/libexec/fedora-cpu-limit-helper")
DEV_HELPER = Path(__file__).with_name("helper.py")
PRESETS = (100, 90, 80, 70, 60, 50)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.config = load_config()
        self.last_power_state: bool | None = None
        self.setWindowTitle("Fedora CPU Limit")
        self.resize(460, 560)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setSpacing(10)

        title = QLabel("Fedora CPU Limit")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(title)

        self.info = QLabel()
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        telemetry = QFormLayout()
        self.freq_label = QLabel("—")
        self.temp_label = QLabel("—")
        self.power_label = QLabel("—")
        telemetry.addRow("Current frequency:", self.freq_label)
        telemetry.addRow("CPU temperature:", self.temp_label)
        telemetry.addRow("Power source:", self.power_label)
        layout.addLayout(telemetry)

        self.buttons: list[QRadioButton] = []
        for percent in PRESETS:
            button = QRadioButton(f"{percent} %")
            button.setProperty("percent", percent)
            self.buttons.append(button)
            layout.addWidget(button)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply)
        layout.addWidget(self.apply_button)

        self.reset_button = QPushButton("Restore 100 %")
        self.reset_button.clicked.connect(lambda: self.apply_percent(100))
        layout.addWidget(self.reset_button)

        profiles = QFormLayout()
        self.auto_checkbox = QCheckBox("Automatically switch by power source")
        self.auto_checkbox.setChecked(self.config.automatic)
        self.auto_checkbox.toggled.connect(self.save_profile_settings)
        layout.addWidget(self.auto_checkbox)

        self.ac_combo = QComboBox()
        self.battery_combo = QComboBox()
        for value in PRESETS:
            self.ac_combo.addItem(f"{value} %", value)
            self.battery_combo.addItem(f"{value} %", value)
        self._select_combo(self.ac_combo, self.config.ac_percent)
        self._select_combo(self.battery_combo, self.config.battery_percent)
        self.ac_combo.currentIndexChanged.connect(self.save_profile_settings)
        self.battery_combo.currentIndexChanged.connect(self.save_profile_settings)
        profiles.addRow("On AC power:", self.ac_combo)
        profiles.addRow("On battery:", self.battery_combo)
        layout.addLayout(profiles)

        self.setCentralWidget(root)
        self.setup_tray()
        self.refresh()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.periodic_refresh)
        self.timer.start(1000)
        QTimer.singleShot(500, self.check_automatic_profile)

    @staticmethod
    def _select_combo(combo: QComboBox, percent: int) -> None:
        index = combo.findData(percent)
        if index >= 0:
            combo.setCurrentIndex(index)

    def setup_tray(self) -> None:
        self.tray = QSystemTrayIcon(QIcon.fromTheme("speedometer"), self)
        self.tray.setToolTip("Fedora CPU Limit")
        menu = QMenu(self)
        show_action = QAction("Show Fedora CPU Limit", self)
        show_action.triggered.connect(self.show_normal)
        menu.addAction(show_action)
        menu.addSeparator()
        for percent in PRESETS:
            action = QAction(f"Set {percent} %", self)
            action.triggered.connect(lambda checked=False, p=percent: self.apply_percent(p))
            menu.addAction(action)
        menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.show_normal() if reason == QSystemTrayIcon.Trigger else None)
        self.tray.show()

    def show_normal(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def refresh(self) -> None:
        items = policies()
        drv = driver() or "unknown"
        if not items:
            self.info.setText("No CPU frequency policies were found.")
            self.apply_button.setEnabled(False)
            self.reset_button.setEnabled(False)
            return
        maximum = max(p.max_freq for p in items)
        current = current_percent()
        self.info.setText(
            f"Driver: {drv}\nPolicies: {len(items)}\n"
            f"Maximum: {maximum / 1_000_000:.2f} GHz\n"
            f"Current limit: {current if current is not None else '—'}%"
        )
        for button in self.buttons:
            button.setChecked(button.property("percent") == current)
        self.refresh_telemetry()

    def periodic_refresh(self) -> None:
        self.refresh_telemetry()
        self.check_automatic_profile()

    def refresh_telemetry(self) -> None:
        freq = current_cpu_mhz()
        temp = temperature_c()
        power = on_ac_power()
        self.freq_label.setText(f"{freq / 1000:.2f} GHz" if freq is not None else "Unavailable")
        self.temp_label.setText(f"{temp:.1f} °C" if temp is not None else "Unavailable")
        self.power_label.setText("AC" if power is True else "Battery" if power is False else "Unknown")

    def save_profile_settings(self) -> None:
        self.config = ProfileConfig(
            ac_percent=int(self.ac_combo.currentData()),
            battery_percent=int(self.battery_combo.currentData()),
            automatic=self.auto_checkbox.isChecked(),
        )
        save_config(self.config)
        if self.config.automatic:
            self.last_power_state = None
            self.check_automatic_profile()

    def check_automatic_profile(self) -> None:
        if not self.config.automatic:
            self.last_power_state = None
            return
        power = on_ac_power()
        if power is None or power == self.last_power_state:
            return
        self.last_power_state = power
        percent = self.config.ac_percent if power else self.config.battery_percent
        self.apply_percent(percent, automatic=True)

    def apply(self) -> None:
        selected = next((int(b.property("percent")) for b in self.buttons if b.isChecked()), None)
        if selected is not None:
            self.apply_percent(selected)

    def apply_percent(self, selected: int, automatic: bool = False) -> None:
        items = policies()
        if not items:
            if not automatic:
                QMessageBox.critical(self, "CPU Limit", "No CPU policies were found.")
            return
        maximum = max(p.max_freq for p in items)
        frequency = target_frequency(selected, maximum)
        command = (
            ["pkexec", str(INSTALLED_HELPER), str(frequency)]
            if INSTALLED_HELPER.exists()
            else ["pkexec", sys.executable, str(DEV_HELPER), str(frequency)]
        )
        try:
            result = subprocess.run(command, text=True, capture_output=True, check=False)
        except FileNotFoundError:
            if not automatic:
                QMessageBox.critical(self, "CPU Limit", "pkexec is not installed.")
            return
        if result.returncode != 0:
            if automatic:
                self.tray.showMessage("Fedora CPU Limit", "Automatic profile change failed or was cancelled.")
            else:
                message = result.stderr.strip() or "The operation was cancelled or failed."
                QMessageBox.warning(self, "CPU Limit", message)
            return
        self.refresh()
        if automatic:
            source = "AC" if self.last_power_state else "battery"
            self.tray.showMessage("Fedora CPU Limit", f"Applied {selected}% for {source} power.")


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
