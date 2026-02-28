# ──────────────────────────────────────────────
# SETTINGS DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QDialog, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QVBoxLayout
)

from constants import Constants
from managers import SettingsManager


class SettingsDialog(QDialog):
    def __init__(self, parent, settings, on_success):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(300)
        self.setModal(True)
        self.settings = settings
        self.on_success = on_success

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Histogram ──
        self.show_hist_cb = QCheckBox("Show Histogram")
        self.show_hist_cb.setChecked(settings.get("show_histogram", True))
        layout.addWidget(self.show_hist_cb)

        self.rgb_hist_cb = QCheckBox("RGB Histogram")
        self.rgb_hist_cb.setChecked(settings.get("rgb_histogram", True))
        layout.addWidget(self.rgb_hist_cb)

        layout.addWidget(QLabel("Histogram Type:"))
        self.btn_group = QButtonGroup(self)
        self.radio_step = QRadioButton("Step")
        self.radio_bar = QRadioButton("Bar")
        self.btn_group.addButton(self.radio_step)
        self.btn_group.addButton(self.radio_bar)
        if settings.get("histogram_type", "step") == "bar":
            self.radio_bar.setChecked(True)
        else:
            self.radio_step.setChecked(True)
        layout.addWidget(self.radio_step)
        layout.addWidget(self.radio_bar)

        # ── Sensor filter ──
        # layout.addWidget(QLabel("Show sensors:"))
        # active = settings.get("active_sensors", Constants.ALL_SENSORS)
        # self.sensor_checks = {}
        # for s in Constants.ALL_SENSORS:
        #     cb = QCheckBox(s)
        #     cb.setChecked(s in active)
        #     layout.addWidget(cb)
        #     self.sensor_checks[s] = cb

        layout.addStretch()

        # ── Buttons ──
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 6px; padding: 6px 18px; }"
        )
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "QPushButton { background-color: #9E9E9E; color: white; border-radius: 6px; padding: 6px 18px; }"
        )
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _save(self):
        self.settings["show_histogram"] = self.show_hist_cb.isChecked()
        self.settings["rgb_histogram"] = self.rgb_hist_cb.isChecked()
        self.settings["histogram_type"] = "bar" if self.radio_bar.isChecked() else "step"
        # self.settings["active_sensors"] = [
        #     s for s, cb in self.sensor_checks.items() if cb.isChecked()
        # ]
        SettingsManager.save(self.settings)
        self.accept()
        self.on_success()
