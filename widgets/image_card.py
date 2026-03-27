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

CARD_HEIGHT  = 350
THUMB_WIDTH  = 390
INFO_MIN_W   = 280
INFO_MAX_W   = 390

RAW_EXTENSIONS = ('.raf', '.nef', '.cr2', '.arw', '.dng')


class TooltipImageLabel(QLabel):
    """Custom QLabel that loads EXIF tooltip lazily on first hover."""
    def __init__(self, filename, img_pil):
        super().__init__()
        self.filename = filename
        self.img_pil = img_pil
        self._exif_loaded = False

    def enterEvent(self, event):
        """Load and set EXIF tooltip on first mouse enter."""
        if not self._exif_loaded:
            try:
                exif_data = ExifManager.get_exif_data(
                    self.filename,
                    ['Model', 'ISO', 'FNumber', 'ExposureTime', 'FocalLength']
                )
                tooltip = self._format_exif_tooltip(exif_data, self.img_pil)
                self.setToolTip(tooltip)
            except Exception:
                self.setToolTip("No EXIF data")
            self._exif_loaded = True
        super().enterEvent(event)

    def _format_exif_tooltip(self, exif_data, img_pil):
        """Format camera parameters for tooltip display."""
        if not exif_data:
            return "No EXIF data"

        lines = []

        # Camera model
        if 'Model' in exif_data:
            lines.append(f"Camera: {exif_data['Model']}")

        # Image dimensions (original)
        width, height = img_pil.size
        lines.append(f"Resolution: {width}x{height}")

        # Camera parameters
        if 'ISO' in exif_data:
            lines.append(f"ISO: {exif_data['ISO']}")
        if 'FNumber' in exif_data:
            lines.append(f"Aperture: {exif_data['FNumber']}")
        if 'ExposureTime' in exif_data:
            lines.append(f"Shutter: {exif_data['ExposureTime']}")
        if 'FocalLength' in exif_data:
            lines.append(f"Focal Length: {exif_data['FocalLength']}")

        return "\n".join(lines) if lines else "No data"


def _open_image(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in RAW_EXTENSIONS:
        return Image.open(filename)
    try:
        import rawpy
        import numpy as np
        with rawpy.imread(filename) as raw:
            rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=False, output_bps=8)
        return Image.fromarray(rgb)
    except ImportError:
        raise RuntimeError(
            "rawpy is required to open RAW files.\n"
            "Install it with: pip install rawpy"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to open RAW file: {e}")


def _fix_orientation(img_pil, filename):
    try:
        exif = img_pil.getexif()
        orientation = exif.get(ExifTags.Base.Orientation, 1)
        if orientation == 8:
            img_pil = img_pil.rotate(90, expand=True)
        elif orientation == 6:
            img_pil = img_pil.rotate(-90, expand=True)
        elif orientation == 3:
            img_pil = img_pil.rotate(180, expand=True)
    except Exception:
        pass
    return img_pil


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
        self.img_pil = _open_image(filename)
        self.img_pil = _fix_orientation(self.img_pil, filename)

        img_thumb = self.img_pil.copy()
        img_thumb.thumbnail((THUMB_WIDTH, CARD_HEIGHT), Image.LANCZOS)

        img_rgb = img_thumb.convert("RGB")
        data = img_rgb.tobytes("raw", "RGB")
        bytes_per_line = img_rgb.width * 3
        qimg = QImage(data, img_rgb.width, img_rgb.height,
                      bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        self.img_label = TooltipImageLabel(filename, self.img_pil)
        img_label = self.img_label
        img_label.setObjectName("imageLabel")
        img_label.setPixmap(pixmap)
        img_label.setFixedSize(THUMB_WIDTH, CARD_HEIGHT)
        img_label.setScaledContents(False)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(img_label)

        # ── Info text ──
        info_label = QLabel()
        info_label.setObjectName("infoLabel")
        info_label.setFont(QFont("Courier New", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        info_label.setWordWrap(True)
        info_label.setMinimumWidth(INFO_MIN_W)
        info_label.setMaximumWidth(INFO_MAX_W)
        info_label.setFixedHeight(CARD_HEIGHT)
        info_label.setContentsMargins(12, 8, 0, 0)
        info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        text = ""
        filename_base = os.path.basename(filename)

        if sim_data:
            # Display recipe name in header
            recipe_name = sim_data.get("Name", "Unknown Recipe")
            text = f"<b>{recipe_name}</b><br><br>"
            text += f"File: {filename_base}<br>"
            # Display all recipe data except Name (already in header)
            for key, value in sim_data.items():
                if key != "Name":
                    text += f"{key}: {value}<br>"
        else:
            text = f"<b>File: {filename_base}</b><br><br>"
            text += "<i>No matching simulation found</i><br><br>"
            for key, value in exif_fallback.items():
                text += f"{key}: {value}<br>"

        info_label.setText(text)
        layout.addWidget(info_label)

        # ── Histogram ──
        if settings.get("show_histogram", True):
            self._add_histogram(layout, img_thumb)

    def _add_histogram(self, layout, img_thumb):
        theme = self.settings.get("theme", DEFAULT_THEME)
        hist_bg, hist_fg = THEME_HISTOGRAM_COLORS.get(theme, ("#1d2021", "#ebdbb2"))
        self.hist = HistogramWidget(
            img_thumb,
            rgb=self.settings.get("rgb_histogram", True),
            hist_type=self.settings.get("histogram_type", "step"),
            bg=hist_bg, fg=hist_fg,
            size=(INFO_MAX_W, CARD_HEIGHT),
            show_grid=self.settings.get("histogram_grid", True)
        )
        self.hist.setMinimumWidth(INFO_MIN_W)
        self.hist.setMaximumWidth(INFO_MAX_W)
        self.hist.setFixedHeight(CARD_HEIGHT)
        self.hist.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.hist, 0, Qt.AlignmentFlag.AlignBottom)

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
                bg=hist_bg, fg=hist_fg,
                size=(INFO_MAX_W, CARD_HEIGHT),
                show_grid=self.settings.get("histogram_grid", True)
            )
            self.hist.setMinimumWidth(INFO_MIN_W)
            self.hist.setMaximumWidth(INFO_MAX_W)
            self.hist.setFixedHeight(CARD_HEIGHT)
            self.hist.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout.addWidget(self.hist)

    def update_histogram(self, settings):
        """Show or hide histogram based on settings; also refreshes theme/type changes."""
        self.settings = settings
        show = settings.get("show_histogram", True)
        layout = self.layout()
        if not show:
            if self.hist is not None:
                layout.removeWidget(self.hist)
                self.hist.deleteLater()
                self.hist = None
        else:
            img_thumb = self.img_pil.copy()
            img_thumb.thumbnail((THUMB_WIDTH, CARD_HEIGHT), Image.LANCZOS)
            if self.hist is not None:
                layout.removeWidget(self.hist)
                self.hist.deleteLater()
                self.hist = None
            self._add_histogram(layout, img_thumb)

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

    def contextMenuEvent(self, event):
        # Show context menu only when right-clicking on the image
        if not self.img_label.geometry().contains(event.pos()):
            event.ignore()
            return

        menu = QMenu(self)
        export_action = menu.addAction("📤  Export Recipe Card")
        export_action.setEnabled(bool(self.sim_data))

        action = menu.exec(event.globalPos())
        if action == export_action:
            self._export_card()

    def _export_card(self):
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