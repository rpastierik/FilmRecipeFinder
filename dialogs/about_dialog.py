# ──────────────────────────────────────────────
# ABOUT DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout
)

from utils import resource_path
from constants import Constants


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.setModal(True)
        self.setFixedWidth(340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(12)

        # ── Top row: icon + title ──
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        icon_label = QLabel()
        icon_label.setPixmap(
            QPixmap(resource_path("icon.png")).scaled(
                64, 64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        icon_label.setFixedSize(64, 64)
        top_row.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        ver = Constants.APP_VERSION
        info = QLabel(
            f"<b>Film Recipe Finder</b><br><br>"
            f"Version {ver}&nbsp;&nbsp;(March 2026)<br>"
            f"© 2026 Roman Pastierik<br><br>"
            f"Support development:<br>"
            f"<a href='https://ko-fi.com/rpastierik'>ko-fi.com/rpastierik</a><br><br>"
            f"License: GNU General Public License v3<br><br>"
            f"Uses ExifTool by Phil Harvey<br>"
            f"<a href='mailto:philharvey66@gmail.com'>philharvey66@gmail.com</a>"
        )
        info.setOpenExternalLinks(True)
        info.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        info.setWordWrap(True)
        top_row.addWidget(info)
        layout.addLayout(top_row)

        # ── OK button ──
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignRight)