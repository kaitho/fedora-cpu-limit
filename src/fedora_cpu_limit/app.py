from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from .cpu import current_cpu_mhz, current_percent, current_frequency, driver, policies, target_frequency, temperature_c

HELPER = Path(__file__).with_name("helper.py")
PRESETS = (100, 90, 80, 70, 60, 50)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fedora CPU Limit")
        self.resize(430, 430)

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
        telemetry.addRow("Current frequency:", self.freq_label)
        telemetry.addRow("CPU temperature:", self.temp_label)
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

        self.setCentralWidget(root)
        self.refresh()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_telemetry)
        self.timer.start(1000)

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
            f"Driver: {drv}\n"
            f"Policies: {len(items)}\n"
            f"Maximum: {maximum / 1_000_000:.2f} GHz\n"
            f"Current limit: {current if current is not None else '—'}%"
        )
        for button in self.buttons:
            button.setChecked(button.property("percent") == current)
        self.refresh_telemetry()

    def refresh_telemetry(self) -> None:
        freq = current_cpu_mhz()
        temp = temperature_c()
        self.freq_label.setText(f"{freq / 1000:.2f} GHz" if freq is not None else "Unavailable")
        self.temp_label.setText(f"{temp:.1f} °C" if temp is not None else "Unavailable")

    def apply(self) -> None:
        selected = next((int(b.property("percent")) for b in self.buttons if b.isChecked()), None)
        if selected is not None:
            self.apply_percent(selected)

    def apply_percent(self, selected: int) -> None:
        items = policies()
        if not items:
            QMessageBox.critical(self, "CPU Limit", "No CPU policies were found.")
            return
        maximum = max(p.max_freq for p in items)
        frequency = target_frequency(selected, maximum)
        command = [sys.executable, str(HELPER), str(frequency)]
        try:
            result = subprocess.run(["pkexec", *command], text=True, capture_output=True, check=False)
        except FileNotFoundError:
            QMessageBox.critical(self, "CPU Limit", "pkexec is not installed.")
            return
        if result.returncode != 0:
            message = result.stderr.strip() or "The operation was cancelled or failed."
            QMessageBox.warning(self, "CPU Limit", message)
            return
        self.refresh()


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
