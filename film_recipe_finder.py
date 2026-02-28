import os
import sys
import subprocess
import json
import xml.etree.ElementTree as ET

from themes import DARK_THEME, LIGHT_THEME

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QStatusBar, QMenuBar, QMenu, QFileDialog,
    QMessageBox, QFrame, QSizePolicy, QDialog, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QDialogButtonBox, QScrollArea as QSA,
    QGroupBox, QGridLayout, QCheckBox, QRadioButton, QButtonGroup, QTextEdit
)
from PyQt6.QtGui import QPixmap, QImage, QAction, QIcon, QFont, QColor, QTextCharFormat, QCursor
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QToolBar, QStyle

import numpy as np
from PIL import Image, ImageTk, ExifTags
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────
class RecipeField:
    def __init__(self, name, default_value, field_type="entry", options=None):
        self.name = name
        self.default_value = default_value
        self.field_type = field_type
        self.options = options or []


class Constants:
    SETTINGS_FILE = "user_settings.json"
    XML_FILE = "film_simulations.xml"

    RECIPE_FIELDS = [
        RecipeField("Name", ""),
        RecipeField("FilmMode", "None", "combo",
                   ["Classic Chrome", "Eterna", "Classic Negative", "Reala ACE", "Nostalgic Neg",
                    "Bleach Bypass", "PRO Neg Hi", "PRO Neg Std", "None", "F0/Standard (Provia)",
                    "F1/Studio Portrait", "F1a/Studio Portrait Enhanced Saturation",
                    "F1b/Studio Portrait Smooth Skin Tone (Astia)", "F1c/Studio Portrait Increased Sharpness",
                    "F2/Fujichrome (Velvia)", "F3/Studio Portrait Ex", "F4/Velvia"]),
        RecipeField("GrainEffectRoughness", "Off", "combo", ["Off", "Weak", "Strong"]),
        RecipeField("GrainEffectSize", "Off", "combo", ["Off", "Small", "Large"]),
        RecipeField("ColorChromeEffect", "Off", "combo", ["Off", "Weak", "Strong"]),
        RecipeField("ColorChromeFXBlue", "Off", "combo", ["Off", "Weak", "Strong"]),
        RecipeField("WhiteBalance", "Auto", "combo",
                   ["Auto", "Daylight", "Shade", "Fluorescent", "Incandescent", "Kelvin", "Daylight Fluorescent"]),
        RecipeField("WhiteBalanceFineTune", "Red +0, Blue +0"),
        RecipeField("ColorTemperature", ""),
        RecipeField("DevelopmentDynamicRange", ""),
        RecipeField("HighlightTone", "0 (normal)", "combo",
                   ["-2 (soft)", "-1.5", "-1 (medium soft)", "-0.5", "0 (normal)", "0.5",
                    "+0.5", "1.5", "+1 (medium hard)", "+2 (hard)", "2.5", "+2.5",
                    "+3 (very hard)", "+3.5", "+4 (hardest)"]),
        RecipeField("ShadowTone", "0 (normal)", "combo",
                   ["-2 (soft)", "-1.5", "-1 (medium soft)", "-0.5", "0 (normal)", "0.5",
                    "+0.5", "1.5", "+1 (medium hard)", "+1.5", "+2 (hard)", "2.5", "+2.5",
                    "+3 (very hard)", "+4 (hardest)"]),
        RecipeField("Saturation", "0 (normal)", "combo",
                   ["-4 (lowest)", "-3 (very low)", "-2 (low)", "-1 (medium low)", "0 (normal)", "+0",
                    "+1 (medium high)", "+2 (high)", "+3 (very high)", "+4 (highest)",
                    "None (B&W)", "Acros", "Acros Green Filter", "Acros Red Filter", "Acros Yellow Filter",
                    "B&W Green Filter", "B&W Red Filter", "B&W Sepia"]),
        RecipeField("Sharpness", "Normal", "combo", ["Soft", "Normal", "Hard", "-0"]),
        RecipeField("NoiseReduction", "0 (normal)", "combo",
                   ["-4 (weakest)", "-3 (very weak)", "-2 (weak)", "-1 (medium weak)",
                    "0 (normal)", "+1 (medium strong)", "+2 (strong)", "+3 (very strong)", "+4 (strongest)"]),
        RecipeField("Clarity", "0"),
        RecipeField("Sensor", "X-Trans V", "combo",
                   ["X-Trans I", "X-Trans II", "X-Trans III", "X-Trans IV", "X-Trans V"])
    ]


# ──────────────────────────────────────────────
# UTILITY
# ──────────────────────────────────────────────
def resource_path(relative_path):
    return os.path.join(os.path.dirname(__file__), relative_path)


# ──────────────────────────────────────────────
# SETTINGS MANAGER
# ──────────────────────────────────────────────
class SettingsManager:
    @staticmethod
    def load():
        defaults = {
            "theme": "dark",
            "show_histogram": True,
            "rgb_histogram": True,
            "histogram_type": "step"
        }
        if os.path.exists(Constants.SETTINGS_FILE):
            try:
                with open(Constants.SETTINGS_FILE, "r") as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
            except Exception:
                pass
        return defaults

    @staticmethod
    def save(settings):
        try:
            with open(Constants.SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")


# ──────────────────────────────────────────────
# XML MANAGER
# ──────────────────────────────────────────────
class XMLManager:
    @staticmethod
    def load_simulations(filename):
        full_path = resource_path(filename)
        if not os.path.exists(full_path):
            return {}
        with open(full_path, 'r') as f:
            tree = ET.parse(f)
            root = tree.getroot()
        simulations = {}
        for profile in root.findall('profile'):
            name_el = profile.find('Name')
            if name_el is None:
                continue
            sim_name = name_el.text
            simulations[sim_name] = {}
            for param in profile.iter():
                if param.tag != 'profile':
                    simulations[sim_name][param.tag] = param.text
        return simulations

    @staticmethod
    def add_recipe(recipe_data):
        xml_file = resource_path(Constants.XML_FILE)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            new_profile = ET.SubElement(root, 'profile')
            for key, value in recipe_data.items():
                elem = ET.SubElement(new_profile, key)
                elem.text = value
            ET.indent(tree, space="  ", level=0)
            tree.write(xml_file, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to add recipe: {e}")
            return False

    @staticmethod
    def update_recipe(recipe_data):
        xml_file = resource_path(Constants.XML_FILE)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            recipe_name = recipe_data["Name"]
            profile_to_update = None
            for profile in root.findall('profile'):
                name_el = profile.find('Name')
                if name_el is not None and name_el.text == recipe_name:
                    profile_to_update = profile
                    break
            if profile_to_update is None:
                QMessageBox.critical(None, "Error", f"Recipe '{recipe_name}' not found!")
                return False
            profile_to_update.clear()
            for key, value in recipe_data.items():
                elem = ET.SubElement(profile_to_update, key)
                elem.text = value
            ET.indent(tree, space="  ", level=0)
            tree.write(xml_file, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update recipe: {e}")
            return False

    @staticmethod
    def delete_recipe(recipe_name):
        xml_file = resource_path(Constants.XML_FILE)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for profile in root.findall('profile'):
                name_el = profile.find('Name')
                if name_el is not None and name_el.text == recipe_name:
                    root.remove(profile)
                    ET.indent(tree, space="  ", level=0)
                    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
                    return True
            QMessageBox.critical(None, "Error", f"Recipe '{recipe_name}' not found!")
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to delete recipe: {e}")
            return False


# ──────────────────────────────────────────────
# RECIPE MANAGER
# ──────────────────────────────────────────────
class RecipeManager:
    @staticmethod
    def find_duplicate_content(recipe_data, simulations):
        for sim_name, sim_data in simulations.items():
            match = all(
                sim_data.get(k) == v
                for k, v in recipe_data.items() if k != "Name"
            ) and all(
                k == "Name" or k in recipe_data
                for k in sim_data.keys()
            )
            if match:
                return sim_name
        return None


# ──────────────────────────────────────────────
# EXIF MANAGER
# ──────────────────────────────────────────────
class ExifManager:
    @staticmethod
    def get_exif_data(filename, relevant_keys):
        import shutil
        full_path = resource_path(filename)

        exiftool_path = shutil.which('exiftool')
        if exiftool_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            for candidate in [
                os.path.join(script_dir, 'exiftool.exe'),
                os.path.join(script_dir, 'tools', 'exiftool.exe'),
                os.path.join(script_dir, 'bin', 'exiftool.exe'),
            ]:
                if os.path.exists(candidate):
                    exiftool_path = candidate
                    break

        if exiftool_path is None:
            raise FileNotFoundError("ExifTool not found.")

        result = subprocess.run([exiftool_path, '-s', full_path],
                                capture_output=True, text=True)
        exif_data = {}
        for line in result.stdout.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                if key.strip() in relevant_keys:
                    exif_data[key.strip()] = value.strip()
        return exif_data

    @staticmethod
    def get_exif(filename, exif_type='short'):
        full_path = resource_path(filename)
        if exif_type == 'full':
            cmd = ['exiftool', '-s', full_path]
        else:
            cmd = ['exiftool', '-Model', '-PictureControlName', '-Description',
                   '-FilmMode', '-GrainEffectRoughness',
                   '-GrainEffectSize', '-ColorChromeEffect', '-ColorChromeFXBlue',
                   '-WhiteBalance', '-WhiteBalanceFineTune', '-ColorTemperature',
                   '-DevelopmentDynamicRange', '-HighlightTone', '-ShadowTone',
                   '-Saturation', '-Sharpness', '-NoiseReduction', '-Clarity',
                   '-FNumber', '-ISO', '-ExposureTime', '-LensID', full_path]

        result = subprocess.run(cmd, capture_output=True, text=True)
        exif_data = {}
        for line in result.stdout.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                exif_data[key.strip()] = value.strip()
        return exif_data


# ──────────────────────────────────────────────
# HISTOGRAM WIDGET
# ──────────────────────────────────────────────
class HistogramWidget(FigureCanvas):
    def __init__(self, img: Image.Image, rgb=True, hist_type="step", dark=True, size=(390, 350)):
        bg = "#1d2021" if dark else "#dce0e8"
        fg = "#ebdbb2" if dark else "#4c4f69"

        fig = Figure(figsize=(size[0] / 100, size[1] / 100), tight_layout=True)
        fig.patch.set_facecolor(bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg)
        for spine in ax.spines.values():
            spine.set_color(fg)
        ax.tick_params(colors=fg)

        if rgb:
            img_arr = np.array(img.convert("RGB"))
            for i, color in enumerate(['red', 'green', 'blue']):
                ax.hist(img_arr[:, :, i].ravel(), bins=256, range=(0, 256),
                        color=color, alpha=0.5, histtype=hist_type)
        else:
            img_arr = np.array(img.convert("L"))
            ax.hist(img_arr.ravel(), bins=256, range=(0, 256),
                    color=fg, alpha=0.8, histtype=hist_type)

        ax.set_xlim(0, 256)
        ax.set_xticks([])
        ax.set_yticks([])

        super().__init__(fig)
        self.setFixedSize(size[0], size[1])


# ──────────────────────────────────────────────
# IMAGE DETAIL DIALOG
# ──────────────────────────────────────────────
class ImageDetailDialog(QDialog):
    def __init__(self, parent, filename, sim_data, full_exif, settings, dark=True):
        
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(filename))
        self.setMinimumSize(1800, 1150)
        self.setModal(True)

        # Nacitaj a otoc obrazok
        img_pil = Image.open(filename)
        exif = img_pil.getexif()
        orientation = exif.get(ExifTags.Base.Orientation, 1)
        if orientation == 8:
            img_pil = img_pil.rotate(90, expand=True)
        elif orientation == 6:
            img_pil = img_pil.rotate(-90, expand=True)
        elif orientation == 3:
            img_pil = img_pil.rotate(180, expand=True)

        # Hlavny layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Horny riadok – obrazok + info
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # ── Velky obrazok ──
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

        # ── Info + histogram ──
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
        # Vzdy zobraz full exif
        for key, value in full_exif.items():  # exif_fallback je tu full_exif
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

        # ── Close button ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            "QPushButton { background-color: #9E9E9E; color: white; "
            "border-radius: 6px; padding: 7px 24px; }"
        )
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        main_layout.addLayout(btn_row)


# ──────────────────────────────────────────────
# IMAGE CARD WIDGET
# ──────────────────────────────────────────────
class ImageCard(QFrame):
    def __init__(self, filename, sim_data, exif_fallback, settings, dark=True):
        super().__init__()
        self.setObjectName("imageCard")
        self.filename = filename
        self.sim_data = sim_data
        self.exif_fallback = exif_fallback
        self.settings = settings
        self.dark = dark
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
            hist = HistogramWidget(
                img_thumb,
                rgb=settings.get("rgb_histogram", True),
                hist_type=settings.get("histogram_type", "step"),
                dark=dark
            )
            layout.addWidget(hist)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                full_exif = ExifManager.get_exif(self.filename, 'full')
            except Exception:
                full_exif = self.exif_fallback
            dlg = ImageDetailDialog(
                self.parent(), self.filename, self.sim_data,
                full_exif,  # namiesto self.exif_fallback
                self.settings, self.dark
            )
            dlg.exec()


# ──────────────────────────────────────────────
# BASE RECIPE DIALOG
# ──────────────────────────────────────────────
class RecipeDialog(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(560)
        self.setModal(True)
        self.widgets = {}

        outer = QVBoxLayout(self)
        outer.setSpacing(0)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(480)

        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)
        self.form_layout.setSpacing(8)
        self.form_layout.setContentsMargins(20, 16, 20, 16)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        scroll.setWidget(form_widget)
        outer.addWidget(scroll)

        self.btn_box = QWidget()
        btn_layout = QHBoxLayout(self.btn_box)
        btn_layout.setContentsMargins(16, 12, 16, 12)
        outer.addWidget(self.btn_box)

    def _build_fields(self, fields, disabled=False):
        for field in fields:
            label = QLabel(f"{field.name}:")
            label.setMinimumWidth(160)

            if field.field_type == "combo":
                widget = QComboBox()
                widget.addItems(field.options)
                idx = widget.findText(field.default_value)
                if idx >= 0:
                    widget.setCurrentIndex(idx)
                if disabled:
                    widget.setEnabled(False)
            else:
                widget = QLineEdit(field.default_value)
                if disabled:
                    widget.setEnabled(False)

            widget.setMinimumWidth(300)
            self.form_layout.addRow(label, widget)
            self.widgets[field.name] = widget

    def _get_recipe_data(self):
        data = {}
        for name, widget in self.widgets.items():
            if isinstance(widget, QComboBox):
                val = widget.currentText().strip()
            else:
                val = widget.text().strip()
            if val:
                data[name] = val
        return data

    def _set_field_value(self, name, value):
        widget = self.widgets.get(name)
        if widget is None:
            return
        if isinstance(widget, QComboBox):
            idx = widget.findText(value)
            if idx >= 0:
                widget.setCurrentIndex(idx)
            else:
                widget.setCurrentIndex(0)
        else:
            widget.setText(value)

    def _add_button(self, text, color, slot):
        btn = QPushButton(text)
        btn.setMinimumWidth(130)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: white; "
            f"border-radius: 6px; padding: 6px 14px; }}"
        )
        btn.clicked.connect(slot)
        self.btn_box.layout().addWidget(btn)
        return btn


# ──────────────────────────────────────────────
# ADD RECIPE DIALOG
# ──────────────────────────────────────────────
class AddRecipeDialog(RecipeDialog):
    def __init__(self, parent, simulations, on_success):
        super().__init__(parent, "Add New Recipe")
        self.simulations = simulations
        self.on_success = on_success

        self._build_fields(Constants.RECIPE_FIELDS)

        self._add_button("Save Recipe", "#4CAF50", self._save)
        self._add_button("Reset", "#FF9800", self._reset)
        self._add_button("From Picture", "#00BCD4", self._load_from_picture)
        self.btn_box.layout().addStretch()
        self._add_button("Cancel", "#f44336", self.reject)

    def _reset(self):
        for field in Constants.RECIPE_FIELDS:
            self._set_field_value(field.name, field.default_value)

    def _load_from_picture(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choose picture", "",
            "Pictures (*.jpg *.jpeg *.png *.raf *.nef)"
        )
        if not filename:
            return
        try:
            exif_data = ExifManager.get_exif(filename, 'short')
            mapping = {
                'Film Mode': 'FilmMode',
                'Grain Effect Roughness': 'GrainEffectRoughness',
                'Grain Effect Size': 'GrainEffectSize',
                'Color Chrome Effect': 'ColorChromeEffect',
                'Color Chrome FX Blue': 'ColorChromeFXBlue',
                'White Balance': 'WhiteBalance',
                'White Balance Fine Tune': 'WhiteBalanceFineTune',
                'Color Temperature': 'ColorTemperature',
                'Development Dynamic Range': 'DevelopmentDynamicRange',
                'Highlight Tone': 'HighlightTone',
                'Shadow Tone': 'ShadowTone',
                'Saturation': 'Saturation',
                'Sharpness': 'Sharpness',
                'Noise Reduction': 'NoiseReduction',
                'Clarity': 'Clarity'
            }
            for exif_key, field_name in mapping.items():
                if exif_key in exif_data:
                    self._set_field_value(field_name, exif_data[exif_key])
            self._set_field_value('Sensor', 'X-Trans V')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to extract EXIF: {e}")

    def _save(self):
        recipe_data = self._get_recipe_data()
        name = recipe_data.get("Name", "").strip()

        if not name:
            QMessageBox.warning(self, "Error", "Recipe name is required!")
            return

        name_exists = name in self.simulations
        content_dup = RecipeManager.find_duplicate_content(recipe_data, self.simulations)

        if name_exists or content_dup:
            self._handle_duplicate(recipe_data, name_exists, content_dup)
        else:
            if XMLManager.add_recipe(recipe_data):
                QMessageBox.information(self, "Success", f"Recipe '{name}' added!")
                self.accept()
                self.on_success()

    def _handle_duplicate(self, recipe_data, name_exists, content_dup):
        name = recipe_data["Name"]
        if name_exists and content_dup:
            msg = f"Recipe '{name}' already exists with identical content."
            choices = ["Overwrite", "New Name", "Cancel"]
        elif name_exists:
            msg = f"Recipe name '{name}' already exists."
            choices = ["Overwrite", "New Name", "Cancel"]
        else:
            msg = f"Identical content already exists as '{content_dup}'."
            choices = ["Keep Both", "New Name", "Cancel"]

        dlg = QDialog(self)
        dlg.setWindowTitle("Duplicate Recipe")
        dlg.setMinimumWidth(400)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(msg))

        btn_row = QHBoxLayout()
        colors = ["#4CAF50", "#FF9800", "#f44336"]
        result = [None]

        for i, choice in enumerate(choices):
            btn = QPushButton(choice)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {colors[i]}; color: white; "
                f"border-radius: 5px; padding: 5px 12px; }}"
            )
            btn.clicked.connect(lambda _, c=choice: (result.__setitem__(0, c), dlg.accept()))
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)
        dlg.exec()

        choice = result[0]
        if choice in ("Overwrite", "Keep Both"):
            if choice == "Overwrite":
                if XMLManager.update_recipe(recipe_data):
                    QMessageBox.information(self, "Success", f"Recipe '{name}' updated!")
                    self.accept()
                    self.on_success()
            else:
                if XMLManager.add_recipe(recipe_data):
                    QMessageBox.information(self, "Success", f"Recipe '{name}' added!")
                    self.accept()
                    self.on_success()
        elif choice == "New Name":
            self._prompt_new_name(recipe_data)

    def _prompt_new_name(self, recipe_data):
        dlg = QDialog(self)
        dlg.setWindowTitle("Enter New Name")
        dlg.setMinimumWidth(320)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Enter new recipe name:"))
        name_edit = QLineEdit(recipe_data["Name"])
        layout.addWidget(name_edit)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px 12px;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #f44336; color: white; border-radius: 5px; padding: 5px 12px;")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)
        cancel_btn.clicked.connect(dlg.reject)

        def do_save():
            new_name = name_edit.text().strip()
            if not new_name:
                QMessageBox.warning(dlg, "Error", "Name cannot be empty!")
                return
            if new_name in self.simulations:
                QMessageBox.warning(dlg, "Error", "Name already exists!")
                return
            recipe_data["Name"] = new_name
            if XMLManager.add_recipe(recipe_data):
                QMessageBox.information(self, "Success", f"Recipe '{new_name}' added!")
                dlg.accept()
                self.accept()
                self.on_success()

        save_btn.clicked.connect(do_save)
        dlg.exec()


# ──────────────────────────────────────────────
# EDIT RECIPE DIALOG
# ──────────────────────────────────────────────
class EditRecipeDialog(RecipeDialog):
    def __init__(self, parent, simulations, on_success):
        super().__init__(parent, "Edit Recipe")
        self.simulations = simulations
        self.on_success = on_success

        selector_widget = QWidget()
        selector_layout = QHBoxLayout(selector_widget)
        selector_layout.setContentsMargins(20, 12, 20, 4)
        selector_layout.addWidget(QLabel("Select Recipe:"))
        self.recipe_combo = QComboBox()
        self.recipe_combo.addItem("-- select --")
        self.recipe_combo.addItems(sorted(simulations.keys()))
        self.recipe_combo.setMinimumWidth(300)
        self.recipe_combo.currentTextChanged.connect(self._load_recipe)
        selector_layout.addWidget(self.recipe_combo)
        selector_layout.addStretch()

        self.layout().insertWidget(0, selector_widget)

        self._build_fields(Constants.RECIPE_FIELDS, disabled=True)
        name_widget = self.widgets.get("Name")
        if name_widget:
            name_widget.setReadOnly(True)

        self._add_button("Save Changes", "#4CAF50", self._save)
        self.btn_box.layout().addStretch()
        self._add_button("Cancel", "#f44336", self.reject)

    def _load_recipe(self, name):
        if name == "-- select --" or name not in self.simulations:
            return
        recipe_data = self.simulations[name]
        for field_name, widget in self.widgets.items():
            widget.setEnabled(True)
        name_widget = self.widgets.get("Name")
        if name_widget:
            name_widget.setReadOnly(True)
        for key, value in recipe_data.items():
            self._set_field_value(key, value)

    def _save(self):
        if self.recipe_combo.currentText() == "-- select --":
            QMessageBox.warning(self, "Error", "Please select a recipe first!")
            return
        recipe_data = self._get_recipe_data()
        if XMLManager.update_recipe(recipe_data):
            QMessageBox.information(self, "Success", f"Recipe '{recipe_data['Name']}' updated!")
            self.accept()
            self.on_success()


# ──────────────────────────────────────────────
# DELETE RECIPE DIALOG
# ──────────────────────────────────────────────
class DeleteRecipeDialog(QDialog):
    def __init__(self, parent, simulations, on_success):
        super().__init__(parent)
        self.setWindowTitle("Delete Recipe")
        self.setMinimumWidth(420)
        self.setModal(True)
        self.simulations = simulations
        self.on_success = on_success

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Delete Film Simulation Recipe")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addWidget(QLabel("Select recipe to delete:"))

        self.recipe_combo = QComboBox()
        self.recipe_combo.addItem("-- select --")
        self.recipe_combo.addItems(sorted(simulations.keys()))
        self.recipe_combo.setMinimumWidth(340)
        layout.addWidget(self.recipe_combo)

        layout.addStretch()

        btn_row = QHBoxLayout()
        del_btn = QPushButton("Delete Recipe")
        del_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; "
            "border-radius: 6px; padding: 7px 18px; font-weight: bold; }"
        )
        del_btn.clicked.connect(self._delete)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "QPushButton { background-color: #9E9E9E; color: white; "
            "border-radius: 6px; padding: 7px 18px; }"
        )
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(del_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _delete(self):
        name = self.recipe_combo.currentText()
        if name == "-- select --":
            QMessageBox.warning(self, "Warning", "Please select a recipe!")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete:\n\n'{name}'?\n\nThis cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if XMLManager.delete_recipe(name):
                QMessageBox.information(self, "Success", f"Recipe '{name}' deleted!")
                self.accept()
                self.on_success()


# ──────────────────────────────────────────────
# SETTINGS DIALOG
# ──────────────────────────────────────────────
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
        layout.addStretch()

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 6px; padding: 6px 18px; }")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("QPushButton { background-color: #9E9E9E; color: white; border-radius: 6px; padding: 6px 18px; }")
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
        SettingsManager.save(self.settings)
        self.accept()
        self.on_success()


# ──────────────────────────────────────────────
# RECIPE BROWSER DIALOG
# ──────────────────────────────────────────────
class RecipeBrowserDialog(QDialog):
    def __init__(self, parent, simulations, on_change):
        super().__init__(parent)
        self.setWindowTitle("All Recipes")
        self.setMinimumSize(600, 700)
        self.setModal(False)
        self.simulations = simulations
        self.on_change = on_change

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ── Search ──
        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Search recipes...")
        self.search_edit.textChanged.connect(self._filter)
        search_row.addWidget(self.search_edit)
        layout.addLayout(search_row)

        # ── Recipe list ──
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Courier New", 10))
        layout.addWidget(self.text_area)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        for text, color, slot in [
            ("Add Recipe",    "#4CAF50", self._add),
            ("Edit Recipe",   "#FF9800", self._edit),
            ("Delete Recipe", "#f44336", self._delete),
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; color: white; "
                f"border-radius: 6px; padding: 6px 14px; }}"
            )
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)

        btn_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            "QPushButton { background-color: #9E9E9E; color: white; "
            "border-radius: 6px; padding: 6px 14px; }"
        )
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._show_all()

    def _show_all(self):
        self._display(self.simulations)

    def _filter(self, query):
        if not query.strip():
            self._display(self.simulations)
            return
        filtered = {
            name: data for name, data in self.simulations.items()
            if query.lower() in name.lower() or
               any(query.lower() in str(v).lower() for v in data.values())
        }
        self._display(filtered)

    def _display(self, simulations):
        parent_dark = getattr(self.parent(), 'dark_mode', True)
        name_color = "#b8bb26" if parent_dark else "#4c9a2a"
        text_color = "#ebdbb2" if parent_dark else "#4c4f69"

        self.text_area.clear()
        cursor = self.text_area.textCursor()

        bold_fmt = QTextCharFormat()
        bold_fmt.setFontWeight(QFont.Weight.Bold)
        bold_fmt.setForeground(QColor(name_color))

        normal_fmt = QTextCharFormat()
        normal_fmt.setFontWeight(QFont.Weight.Normal)
        normal_fmt.setForeground(QColor(text_color))

        for name, data in sorted(simulations.items()):
            cursor.insertText(f"  # {name}\n", bold_fmt)
            for key, value in data.items():
                cursor.insertText(f"    - {key}: {value}\n", normal_fmt)
            cursor.insertText("\n", normal_fmt)

        self.text_area.setTextCursor(cursor)
        self.text_area.moveCursor(
            self.text_area.textCursor().MoveOperation.Start
        )

    def _refresh(self):
        self.on_change()
        self.simulations = self.parent().simulations
        self._filter(self.search_edit.text())

    def _add(self):
        dlg = AddRecipeDialog(self, self.simulations, self._refresh)
        dlg.exec()

    def _edit(self):
        dlg = EditRecipeDialog(self, self.simulations, self._refresh)
        dlg.exec()

    def _delete(self):
        dlg = DeleteRecipeDialog(self, self.simulations, self._refresh)
        dlg.exec()


# ──────────────────────────────────────────────
# MAIN WINDOW
# ──────────────────────────────────────────────
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.setWindowTitle("Film Recipe Finder")
        self.resize(1200, 850)

        self.settings = SettingsManager.load()
        self.simulations = XMLManager.load_simulations(Constants.XML_FILE)
        self.dark_mode = self.settings.get("theme", "dark") == "dark"
        self.last_dir = self.settings.get("last_dir", "")

        self._build_ui()
        self._build_menu()
        self._build_toolbar() 
        self._apply_theme()
        self._update_status()
        self.setAcceptDrops(True)

    # ── UI BUILD ──────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setContentsMargins(8, 8, 8, 8)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Placeholder text
        self.placeholder = QLabel("⬇  Drag & Drop pictures here  ⬇")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #504945; padding: 350px; font-size: 20px;")       
        self.cards_layout.insertWidget(0, self.placeholder)
        self.cards_layout.addStretch()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_label)
    
    def _build_toolbar(self):
        from PyQt6.QtWidgets import QToolBar

        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(toolbar)

        # Nastav velkost pisma pre toolbar
        toolbar.setStyleSheet("QToolButton { font-size: 18px; padding: 1px 1px; }")

        actions = [
            ("🔍", "Identify Recipe",  self.identify_recipe),
            ("📋", "Show All Recipes", self.open_recipe_browser),
            None,
            ("➕", "Add Recipe",       self.open_add_recipe),
            ("✏️", "Edit Recipe",      self.open_edit_recipe),
            ("🗑️", "Delete Recipe",    self.open_delete_recipe),
            None,
            ("⚙️", "Settings",         self.open_settings),
            ("🌙", "Toggle Theme",     self.toggle_theme),
            
        ]

        for item in actions:
            if item is None:
                toolbar.addSeparator()
                continue
            symbol, tooltip, slot = item
            btn = QPushButton(symbol)
            btn.setToolTip(tooltip)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("QPushButton { font-size: 18px; border: none; background: transparent; }")
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)

    # ── MENU BUILD ────────────────────────────
    def _build_menu(self):
        menubar = self.menuBar()

        recipes_menu = menubar.addMenu("Recipes")
        recipes_menu.addAction(self._action("Identify Recipe", self.identify_recipe))
        recipes_menu.addAction(self._action("Show All Recipes", self.open_recipe_browser))
        recipes_menu.addSeparator()
        recipes_menu.addAction(self._action("Add New Recipe", self.open_add_recipe))
        recipes_menu.addAction(self._action("Edit Recipe", self.open_edit_recipe))
        recipes_menu.addAction(self._action("Delete Recipe", self.open_delete_recipe))
        recipes_menu.addSeparator()
        recipes_menu.addAction(self._action("Exit", self.close))

        # exif_menu = menubar.addMenu("Exif")
        # exif_menu.addAction(self._action("Show Full Exif", lambda: self.show_exif(full=True)))
        # exif_menu.addAction(self._action("Show Short Exif", lambda: self.show_exif(full=False)))

        view_menu = menubar.addMenu("View")
        self.theme_action = QAction("Switch to Light Mode" if self.dark_mode else "Switch to Dark Mode", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
        view_menu.addSeparator()
        view_menu.addAction(self._action("Settings", self.open_settings))

        help_menu = menubar.addMenu("Help")
        help_menu.addAction(self._action("About", self._about))

    def _action(self, name, slot):
        action = QAction(name, self)
        action.triggered.connect(slot)
        return action

    # ── THEME ─────────────────────────────────
    def _apply_theme(self):
        QApplication.instance().setStyleSheet(DARK_THEME if self.dark_mode else LIGHT_THEME)
        self._refresh_cards()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings["theme"] = "dark" if self.dark_mode else "light"
        SettingsManager.save(self.settings)
        self.theme_action.setText("Switch to Light Mode" if self.dark_mode else "Switch to Dark Mode")
        self._apply_theme()

    # ── STATUS BAR ────────────────────────────
    def _update_status(self):
        counts = {}
        for sim_data in self.simulations.values():
            sensor = sim_data.get("Sensor", "")
            if sensor:
                counts[sensor] = counts.get(sensor, 0) + 1
        recipes_text = "Recipes:  " + ",  ".join(
            f"{k} ({v})" for k, v in sorted(counts.items())
        )
        last_dir = getattr(self, 'last_dir', os.getcwd())
        self.status_label.setText(f"{recipes_text}     |     {last_dir}   ")

    # ── COMPARE ───────────────────────────────
    def _compare(self, exif_data):
        skip = {"Name", "FilmMode", "DevelopmentDynamicRange", "Sensor", "Clarity", "Sharpness"}
        for sim_name, sim_data in self.simulations.items():
            if all(exif_data.get(k) == v for k, v in sim_data.items() if k not in skip):
                return sim_name
        return None

    # ── CLEAR CARDS ───────────────────────────
    def _clear_cards(self):
        self.placeholder.show()
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget() and item.widget() is not self.placeholder:
                item.widget().deleteLater()

    def _refresh_cards(self):
        pass

    # ── IDENTIFY RECIPE ───────────────────────
    def identify_recipe(self):
        self.placeholder.hide()
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Choose pictures", self.last_dir,
            "Pictures (*.jpg *.jpeg *.png *.raf *.nef)"
        )
        if not filenames:
            return

        self.last_dir = os.path.dirname(filenames[0])
        self.settings["last_dir"] = self.last_dir
        SettingsManager.save(self.settings)
        self._clear_cards()

        relevant_keys = set()
        for sim_data in self.simulations.values():
            relevant_keys.update(sim_data.keys())

        for filename in filenames:
            try:
                exif_data = ExifManager.get_exif_data(filename, relevant_keys)
                sim_name = self._compare(exif_data)
                sim_data = self.simulations.get(sim_name) if sim_name else None
                exif_fallback = {} if sim_data else ExifManager.get_exif(filename, 'short')

                card = ImageCard(filename, sim_data, exif_fallback,
                                 self.settings, dark=self.dark_mode)
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process {os.path.basename(filename)}:\n{e}")

        self._update_status()

    # ── SHOW EXIF ─────────────────────────────
    def show_exif(self, full=False):
        self.placeholder.hide()
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Choose picture(s)", self.last_dir,
            "Pictures (*.jpg *.jpeg *.png *.raf *.nef)"
        )
        if not filenames:
            return

        self.last_dir = os.path.dirname(filenames[0])
        self.settings["last_dir"] = self.last_dir
        SettingsManager.save(self.settings)
        self._clear_cards()

        for filename in filenames:
            try:
                exif_data = ExifManager.get_exif(filename, 'full' if full else 'short')
                card = ImageCard(filename, None, exif_data,
                                 self.settings, dark=self.dark_mode)
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load {os.path.basename(filename)}:\n{e}")

        self._update_status()

    # ── RECIPE CRUD ───────────────────────────
    def open_add_recipe(self):
        dlg = AddRecipeDialog(self, self.simulations, self._refresh_simulations)
        dlg.exec()

    def open_edit_recipe(self):
        dlg = EditRecipeDialog(self, self.simulations, self._refresh_simulations)
        dlg.exec()

    def open_delete_recipe(self):
        dlg = DeleteRecipeDialog(self, self.simulations, self._refresh_simulations)
        dlg.exec()

    def open_recipe_browser(self):
        dlg = RecipeBrowserDialog(self, self.simulations, self._refresh_simulations)
        dlg.show()

    def _refresh_simulations(self):
        self.simulations = XMLManager.load_simulations(Constants.XML_FILE)
        self._update_status()

    def open_settings(self):
        dlg = SettingsDialog(self, self.settings, lambda: None)
        dlg.exec()

    # ── ABOUT ─────────────────────────────────
    def _about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        msg.setWindowIcon(QIcon(resource_path("icon.png")))
        msg.setIconPixmap(QPixmap(resource_path("icon.png")).scaled(
            64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        msg.setText(
            "Film Recipe Finder\n\n"
            "Version 0.2.0  (February 2026)\n"
            "© 2026 Roman Pastierik\n\n"
            "Support development:\n"
            "Ko-fi: ko-fi.com/rpastierik\n\n"
            "License: GNU General Public License v3\n\n"
            "Uses ExifTool by Phil Harvey\n"
            "philharvey66@gmail.com"
        )
        msg.exec()

    # ── DRAG & DROP ───────────────────────────
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.placeholder.hide()
        filenames = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.jpg', '.jpeg', '.png', '.raf', '.nef')):
                filenames.append(path)

        if not filenames:
            return

        self.last_dir = os.path.dirname(filenames[0])
        self.settings["last_dir"] = self.last_dir
        SettingsManager.save(self.settings)
        self._clear_cards()

        relevant_keys = set()
        for sim_data in self.simulations.values():
            relevant_keys.update(sim_data.keys())

        for filename in filenames:
            try:
                exif_data = ExifManager.get_exif_data(filename, relevant_keys)
                sim_name = self._compare(exif_data)
                sim_data = self.simulations.get(sim_name) if sim_name else None
                exif_fallback = {} if sim_data else ExifManager.get_exif(filename, 'short')
                card = ImageCard(filename, sim_data, exif_fallback,
                                 self.settings, dark=self.dark_mode)
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process {os.path.basename(filename)}:\n{e}")

        self._update_status()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
