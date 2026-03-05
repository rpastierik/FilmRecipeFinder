# ──────────────────────────────────────────────
# IMAGE CARD WIDGET
# ──────────────────────────────────────────────
import os
import sys

from PIL import Image, ExifTags
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QImage, QPixmap
from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QMenu, QMessageBox, QSizePolicy
)

from managers import ExifManager
from widgets.histogram_widget import HistogramWidget
from widgets.image_detail_dialog import ImageDetailDialog

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from exporters.recipe_card_exporter import export_recipe_card
from themes import THEME_HISTOGRAM_COLORS, DEFAULT_THEME


class ImageCard(QFrame):
    def __init__(self, filename, sim_data, exif_fallback, settings, dark=True):
        super().__init__()
        self.setObjectName("imageCard")
        self.filename = filename
        self.sim_data = sim_data
        self.exif_fallback = exif_fallback
        self.settings = settings
        self.dark = dark
        self.hist = None
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Image ──
        self.img_pil = Image.open(filename)
        exif = self.img_pil.getexif()
        orientation = exif.get(ExifTags.Base.Orientation, 1)
        if orientation == 8:
            self.img_pil = self.img_pil.rotate(90, expand=True)
        elif orientation == 6:
            self.img_pil = self.img_pil.rotate(-90, expand=True)
        elif orientation == 3:
            self.img_pil = self.img_pil.rotate(180, expand=True)

        img_thumb = self.img_pil.copy()
        img_thumb.thumbnail((390, 350), Image.LANCZOS)

        img_rgb = img_thumb.convert("RGB")
        data = img_rgb.tobytes("raw", "RGB")
        bytes_per_line = img_rgb.width * 3
        qimg = QImage(data, img_rgb.width, img_rgb.height,
                      bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        img_label = QLabel()
        img_label.setObjectName("imageLabel")
        img_label.setPixmap(pixmap)
        img_label.setFixedSize(390, 350)
        img_label.setScaledContents(False)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        # ── Info text ──
        info_label = QLabel()
        info_label.setObjectName("infoLabel")
        info_label.setFont(QFont("Courier New", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        info_label.setWordWrap(True)
        info_label.setMinimumWidth(280)
        info_label.setMaximumWidth(390)
        info_label.setFixedHeight(350)
        info_label.setContentsMargins(12, 8, 0, 0)
        info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        text = f"<b>{os.path.basename(filename)}</b><br><br>"
        if sim_data:
            for key, value in sim_data.items():
                text += f"{key}: {value}<br>"
        else:
            text += "<i>No matching simulation found</i><br><br>"
            for key, value in exif_fallback.items():
                text += f"{key}: {value}<br>"

        info_label.setText(text)
        layout.addWidget(info_label)

        # ── Histogram ──
        if settings.get("show_histogram", True):
            theme = settings.get("theme", DEFAULT_THEME)
            hist_bg, hist_fg = THEME_HISTOGRAM_COLORS.get(theme, ("#1d2021", "#ebdbb2"))
            self.hist = HistogramWidget(
                img_thumb,
                rgb=settings.get("rgb_histogram", True),
                hist_type=settings.get("histogram_type", "step"),
                bg=hist_bg, fg=hist_fg
            )
            layout.addWidget(self.hist)

    def update_theme(self):
        if self.hist is not None:
            layout = self.layout()
            layout.removeWidget(self.hist)
            self.hist.deleteLater()
            theme = self.settings.get("theme", DEFAULT_THEME)
            hist_bg, hist_fg = THEME_HISTOGRAM_COLORS.get(theme, ("#1d2021", "#ebdbb2"))
            self.hist = HistogramWidget(
                self.img_pil,
                rgb=self.settings.get("rgb_histogram", True),
                hist_type=self.settings.get("histogram_type", "step"),
                bg=hist_bg, fg=hist_fg
            )
            layout.addWidget(self.hist)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                full_exif = ExifManager.get_exif(self.filename, 'full')
            except Exception:
                full_exif = self.exif_fallback
            dlg = ImageDetailDialog(
                self.parent(), self.filename, self.sim_data,
                full_exif, self.settings, self.dark
            )
            dlg.exec()

    def contextMenuEvent(self, event):                          # ← NEW
        menu = QMenu(self)
        export_action = menu.addAction("📤  Export Recipe Card")
        export_action.setEnabled(bool(self.sim_data))           # sivé ak nie je recept

        action = menu.exec(event.globalPos())

        if action == export_action:
            self._export_card()

    def _export_card(self):                                     # ← NEW
        if not self.sim_data:
            QMessageBox.warning(self, "No Recipe", "No recipe data found for this photo.")
            return

        base = os.path.splitext(os.path.basename(self.filename))[0]
        recipe_name = self.sim_data.get("Name", base).replace(" ", "_")
        suggested = os.path.join(os.path.dirname(self.filename), f"{recipe_name}_card.png")

        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Recipe Card", suggested, "PNG Image (*.png)"
        )
        if not out_path:
            return

        try:
            export_recipe_card(self.filename, self.sim_data, out_path)
            QMessageBox.information(self, "Exported", f"Recipe card saved to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))