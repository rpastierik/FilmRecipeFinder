# ──────────────────────────────────────────────
# IMAGE DETAIL DIALOG  (updated)
# ──────────────────────────────────────────────
import os

from PIL import Image, ExifTags
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QScrollArea, QVBoxLayout
)

from exporters.recipe_card_exporter import export_recipe_card   # ← NEW


class ImageDetailDialog(QDialog):
    def __init__(self, parent, filename, sim_data, full_exif, settings, dark=True):
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(filename))
        self.setMinimumSize(1800, 1150)
        self.setModal(True)

        self._filename = filename       # ← NEW  (potrebujeme pri exporte)
        self._sim_data = sim_data       # ← NEW

        img_pil = Image.open(filename)
        exif = img_pil.getexif()
        orientation = exif.get(ExifTags.Base.Orientation, 1)
        if orientation == 8:
            img_pil = img_pil.rotate(90, expand=True)
        elif orientation == 6:
            img_pil = img_pil.rotate(-90, expand=True)
        elif orientation == 3:
            img_pil = img_pil.rotate(180, expand=True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # ── Large image ──
        img_big = img_pil.copy()
        img_big.thumbnail((1600, 1067), Image.LANCZOS)
        img_rgb = img_big.convert("RGB")
        data = img_rgb.tobytes("raw", "RGB")
        bpl = img_rgb.width * 3
        qimg = QImage(data, img_rgb.width, img_rgb.height, bpl, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        img_label = QLabel()
        img_label.setObjectName("imageLabel")
        img_label.setPixmap(pixmap)
        img_label.setFixedSize(1600, 1067)
        img_label.setScaledContents(False)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(img_label)

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
        info_scroll.setFixedWidth(280)
        right_col.addWidget(info_scroll)

        top_row.addLayout(right_col)
        main_layout.addLayout(top_row)

        # ── Button row ──────────────────────────────── ← ZMENENÉ
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        export_btn = QPushButton("📤  Export Recipe Card")    # ← NEW
        export_btn.setStyleSheet(
            "QPushButton { background-color: #D05F3B; color: white; "
            "border-radius: 6px; padding: 7px 24px; font-weight: bold; }"
            "QPushButton:hover { background-color: #E8714A; }"
        )
        export_btn.clicked.connect(self._on_export_card)     # ← NEW
        btn_row.addWidget(export_btn)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            "QPushButton { background-color: #9E9E9E; color: white; "
            "border-radius: 6px; padding: 7px 24px; }"
        )
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        main_layout.addLayout(btn_row)

    # ── Export slot ──────────────────────────────── ← NEW
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