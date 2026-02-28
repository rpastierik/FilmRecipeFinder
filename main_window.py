# ──────────────────────────────────────────────
# MAIN WINDOW
# ──────────────────────────────────────────────
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QCursor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QLabel, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QStatusBar,
    QToolBar, QVBoxLayout, QWidget
)

from constants import Constants
from managers import ExifManager, SettingsManager, XMLManager
from themes import DARK_THEME, LIGHT_THEME
from utils import resource_path
from widgets import ImageCard
from dialogs import (
    AddRecipeDialog, DeleteRecipeDialog, EditRecipeDialog,
    RecipeBrowserDialog, SettingsDialog
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.setWindowTitle("Film Recipe Finder")
        self.resize(1200, 850)

        self.settings    = SettingsManager.load()
        self.simulations = XMLManager.load_simulations(Constants.XML_FILE)
        self.dark_mode   = self.settings.get("theme", "dark") == "dark"
        self.last_dir    = self.settings.get("last_dir", "")

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

        self.scroll_area.setWidget(self.cards_widget)
        main_layout.addWidget(self.scroll_area)

        self.placeholder = QLabel("⬇  Drag & Drop pictures here  ⬇")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #504945; padding: 350px; font-size: 20px;")
        self.cards_layout.insertWidget(0, self.placeholder)
        self.cards_layout.addStretch()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_label)

    def _refresh_cards(self):
        for i in range(self.cards_layout.count()):
            widget = self.cards_layout.itemAt(i).widget()
            if isinstance(widget, ImageCard):
                widget.update_theme(self.dark_mode)

    def _build_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        toolbar.setStyleSheet("")
        self.addToolBar(toolbar)

        hover_color   = "#3c3836" if self.dark_mode else "#ccd0da"
        pressed_color = "#504945" if self.dark_mode else "#bcc0cc"

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
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 18px;
                    border: none;
                    background: transparent;
                    border-radius: 6px;
                    padding: 4px;
                }}
                QPushButton:hover   {{ background-color: {hover_color}; }}
                QPushButton:pressed {{ background-color: {pressed_color}; }}
            """)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)

        # ── Sensor filter ──
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("  Sensor: "))

        self.sensor_combo = QComboBox()
        self.sensor_combo.addItem("All")
        self.sensor_combo.addItems(Constants.ALL_SENSORS)
        self.sensor_combo.setMinimumWidth(120)

        active = self.settings.get("active_sensors", Constants.ALL_SENSORS)
        if len(active) == 1:
            idx = self.sensor_combo.findText(active[0])
            if idx >= 0:
                self.sensor_combo.setCurrentIndex(idx)

        self.sensor_combo.currentTextChanged.connect(self._on_sensor_combo_changed)
        toolbar.addWidget(self.sensor_combo)

    # ── MENU BUILD ────────────────────────────
    def _build_menu(self):
        menubar = self.menuBar()

        recipes_menu = menubar.addMenu("Recipes")
        recipes_menu.addAction(self._action("Identify Recipe",  self.identify_recipe))
        recipes_menu.addAction(self._action("Show All Recipes", self.open_recipe_browser))
        recipes_menu.addSeparator()
        recipes_menu.addAction(self._action("Add New Recipe",   self.open_add_recipe))
        recipes_menu.addAction(self._action("Edit Recipe",      self.open_edit_recipe))
        recipes_menu.addAction(self._action("Delete Recipe",    self.open_delete_recipe))
        recipes_menu.addSeparator()
        recipes_menu.addAction(self._action("Exit", self.close))

        view_menu = menubar.addMenu("View")
        self.theme_action = QAction(
            "Switch to Light Mode" if self.dark_mode else "Switch to Dark Mode", self
        )
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

    # ── SENSOR COMBO ──────────────────────────
    def _on_sensor_combo_changed(self, text):
        if text == "All":
            self.settings["active_sensors"] = Constants.ALL_SENSORS
        else:
            self.settings["active_sensors"] = [text]
        SettingsManager.save(self.settings)
        for widget in self.findChildren(RecipeBrowserDialog):
            widget._filter(widget.search_edit.text())

    # ── THEME ─────────────────────────────────
    def _apply_theme(self):
        QApplication.instance().setStyleSheet(DARK_THEME if self.dark_mode else LIGHT_THEME)
        self._refresh_cards()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings["theme"] = "dark" if self.dark_mode else "light"
        SettingsManager.save(self.settings)
        self.theme_action.setText(
            "Switch to Light Mode" if self.dark_mode else "Switch to Dark Mode"
        )
        for toolbar in self.findChildren(QToolBar):
            self.removeToolBar(toolbar)
            toolbar.deleteLater()
        self._build_toolbar()
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
        self.status_label.setText(f"{recipes_text}     |     {self.last_dir}   ")

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

    # ── IDENTIFY RECIPE ───────────────────────
    def identify_recipe(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Choose pictures", self.last_dir,
            "Pictures (*.jpg *.jpeg *.png *.raf *.nef)"
        )
        if not filenames:
            return
        self._process_files(filenames)

    # ── DRAG & DROP ───────────────────────────
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        filenames = [
            url.toLocalFile() for url in event.mimeData().urls()
            if url.toLocalFile().lower().endswith(('.jpg', '.jpeg', '.png', '.raf', '.nef'))
        ]
        if filenames:
            self._process_files(filenames)

    # ── PROCESS FILES (shared logic) ──────────
    def _process_files(self, filenames):
        self.placeholder.hide()
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
                sim_name  = self._compare(exif_data)
                sim_data  = self.simulations.get(sim_name) if sim_name else None
                exif_fallback = {} if sim_data else ExifManager.get_exif(filename, 'short')
                card = ImageCard(filename, sim_data, exif_fallback,
                                 self.settings, dark=self.dark_mode)
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            except Exception as e:
                QMessageBox.warning(
                    self, "Error",
                    f"Failed to process {os.path.basename(filename)}:\n{e}"
                )
        self._update_status()

    # ── RECIPE CRUD ───────────────────────────
    def open_add_recipe(self):
        AddRecipeDialog(self, self.simulations, self._refresh_simulations).exec()

    def open_edit_recipe(self):
        EditRecipeDialog(self, self.simulations, self._refresh_simulations).exec()

    def open_delete_recipe(self):
        DeleteRecipeDialog(self, self.simulations, self._refresh_simulations).exec()

    def open_recipe_browser(self):
        RecipeBrowserDialog(self, self.simulations, self._refresh_simulations).show()

    def _refresh_simulations(self):
        self.simulations = XMLManager.load_simulations(Constants.XML_FILE)
        self._update_status()

    # ── SETTINGS ──────────────────────────────
    def open_settings(self):
        SettingsDialog(self, self.settings, self._on_settings_saved).exec()

    def _on_settings_saved(self):
        active = self.settings.get("active_sensors", [])
        if hasattr(self, 'sensor_combo'):
            if len(active) == 1:
                idx = self.sensor_combo.findText(active[0])
                self.sensor_combo.setCurrentIndex(idx if idx >= 0 else 0)
            else:
                self.sensor_combo.setCurrentIndex(0)

    # ── ABOUT ─────────────────────────────────
    def _about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        msg.setWindowIcon(QIcon(resource_path("icon.png")))
        msg.setIconPixmap(QPixmap(resource_path("icon.png")).scaled(
            64, 64,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        msg.setText(
            "Film Recipe Finder\n\n"
            "Version 0.3.1  (February 2026)\n"
            "© 2026 Roman Pastierik\n\n"
            "Support development:\n"
            "Ko-fi: ko-fi.com/rpastierik\n\n"
            "License: GNU General Public License v3\n\n"
            "Uses ExifTool by Phil Harvey\n"
            "philharvey66@gmail.com"
        )
        msg.exec()
