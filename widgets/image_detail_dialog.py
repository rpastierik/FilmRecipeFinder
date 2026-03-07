# ──────────────────────────────────────────────
# IMAGE DETAIL DIALOG  (updated)
# ──────────────────────────────────────────────
import os

from PIL import Image, ExifTags
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout
)

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from exporters.recipe_card_exporter import export_recipe_card

INFO_PANEL_W = 280
BTN_ROW_H    = 48
MARGINS      = 32   # 16 * 2


class ImageDetailDialog(QDialog):
    def __init__(self, parent, filename, sim_data, full_exif, settings, dark=True):
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(filename))
        self.setMinimumSize(900, 600)
        self.resize(1800, 1150)
        self.setModal(True)

        self._filename = filename
        self._sim_data = sim_data

        # ── Load & orient image ──
        img_pil = Image.open(filename)
        exif = img_pil.getexif()
        orientation = exif.get(ExifTags.Base.Orientation, 1)
        if orientation == 8:
            img_pil = img_pil.rotate(90, expand=True)
        elif orientation == 6:
            img_pil = img_pil.rotate(-90, expand=True)
        elif orientation == 3:
            img_pil = img_pil.rotate(180, expand=True)

        # Keep full-res pixmap for scaling
        img_rgb = img_pil.convert("RGB")
        data = img_rgb.tobytes("raw", "RGB")
        bpl = img_rgb.width * 3
        qimg = QImage(data, img_rgb.width, img_rgb.height, bpl, QImage.Format.Format_RGB888)
        self._full_pixmap = QPixmap.fromImage(qimg)

        # ── Layout ──
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # ── Image label (responsive) ──
        self._img_label = QLabel()
        self._img_label.setObjectName("imageLabel")
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        top_row.addWidget(self._img_label, stretch=1)

        # ── Info panel ──
        right_col = QVBoxLayout()
        right_col.setSpacing(12)

        info_label = QLabel()
        info_label.setFont(QFont("Courier New", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        info_label.setWordWrap(True)
        info_label.setContentsMargins(8, 4, 8, 4)

        text = f"<b>{os.path.basename(filename)}</b><br><br>"
        if sim_data:
            for key, value in sim_data.items():
                text += f"{key}: {value}<br>"
            text += "<br><hr><br>"
        for key, value in full_exif.items():
            text += f"{key}: {value}<br>"
        info_label.setText(text)

        info_scroll = QScrollArea()
        info_scroll.setWidgetResizable(True)
        info_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        info_scroll.setWidget(info_label)
        info_scroll.setFixedWidth(INFO_PANEL_W)
        right_col.addWidget(info_scroll)

        top_row.addLayout(right_col)
        main_layout.addLayout(top_row, stretch=1)

        # ── Button row ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        export_btn = QPushButton("📤  Export Recipe Card")
        export_btn.setStyleSheet(
            "QPushButton { background-color: #D05F3B; color: white; "
            "border-radius: 6px; padding: 7px 24px; font-weight: bold; }"
            "QPushButton:hover { background-color: #E8714A; }"
        )
        export_btn.clicked.connect(self._on_export_card)
        btn_row.addWidget(export_btn)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            "QPushButton { background-color: #9E9E9E; color: white; "
            "border-radius: 6px; padding: 7px 24px; }"
        )
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        main_layout.addLayout(btn_row)

        # Initial render
        self._update_image()

    # ── Responsive image ──────────────────────────────────────────────────

    def _update_image(self):
        """Scale pixmap to fit available space while keeping aspect ratio."""
        available_w = self.width()  - MARGINS - INFO_PANEL_W - 16  # 16 = spacing
        available_h = self.height() - MARGINS - BTN_ROW_H - 12     # 12 = spacing
        if available_w < 1 or available_h < 1:
            return
        scaled = self._full_pixmap.scaled(
            available_w, available_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._img_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_image()

    # ── Export ────────────────────────────────────────────────────────────

    def _on_export_card(self):
        if not self._sim_data:
            QMessageBox.warning(self, "No Recipe", "No recipe data found for this photo.")
            return

        base = os.path.splitext(os.path.basename(self._filename))[0]
        recipe_name = self._sim_data.get("Name", base).replace(" ", "_")
        suggested = os.path.join(os.path.dirname(self._filename), f"{recipe_name}_card.png")

        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Recipe Card", suggested, "PNG Image (*.png)"
        )
        if not out_path:
            return

        try:
            export_recipe_card(self._filename, self._sim_data, out_path)
            QMessageBox.information(self, "Exported", f"Recipe card saved to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))