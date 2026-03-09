# ──────────────────────────────────────────────
# RECIPE BROWSER DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextCharFormat
from PyQt6.QtWidgets import (
    QComboBox, QCompleter, QDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout
)

from constants import Constants
from themes import THEMES, THEME_BROWSER_COLORS
from dialogs.add_recipe_dialog import AddRecipeDialog
from dialogs.edit_recipe_dialog import EditRecipeDialog
from dialogs.delete_recipe_dialog import DeleteRecipeDialog
from dialogs.recipe_dialog import get_button_color
from managers import SettingsManager


class RecipeBrowserDialog(QDialog):
    def __init__(self, parent, simulations, on_change):
        super().__init__(parent)
        self.setWindowTitle("Recipe Browser")
        self.setMinimumSize(600, 700)
        self.setModal(False)
        self.simulations = simulations
        self.on_change = on_change

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ── Search + Sort ──
        search_row = QHBoxLayout()

        self.search_edit = QComboBox()
        self.search_edit.setEditable(True)
        self.search_edit.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.search_edit.addItem("")
        self.search_edit.addItems(sorted(simulations.keys()))
        self.search_edit.lineEdit().setPlaceholderText("🔍  Search recipes...")

        all_values = sorted(set(
            item
            for name, data in simulations.items()
            for item in [name] + [str(v) for v in data.values()]
        ))
        completer = QCompleter(all_values)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search_edit.setCompleter(completer)
        self.search_edit.currentTextChanged.connect(self._filter)
        self.search_edit.lineEdit().textEdited.connect(self._filter)
        search_row.addWidget(self.search_edit)

        search_row.addStretch()
        search_row.addWidget(QLabel("Sort:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Default (XML order)", "Default (XML reversed)", "Name (A-Z)", "Name (Z-A)", "Sensor", "Film Simulation"])
        saved_sort = getattr(self.parent(), 'settings', {}).get("recipe_browser_sort", "Default (XML order)")
        idx = self.sort_combo.findText(saved_sort)
        if idx >= 0:
            self.sort_combo.setCurrentIndex(idx)
        self.sort_combo.setMinimumWidth(150)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        search_row.addWidget(self.sort_combo)

        layout.addLayout(search_row)

        # ── Recipe list ──
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Courier New", 10))
        layout.addWidget(self.text_area)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        for text, btn_type, slot in [
            ("Add Recipe",    "primary", self._add),
            ("Edit Recipe",   "warning", self._edit),
            ("Delete Recipe", "danger",  self._delete),
        ]:
            color = get_button_color(parent, btn_type)
            btn = QPushButton(text)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; color: white; "
                f"border-radius: 6px; padding: 6px 14px; }}"
                f"QPushButton:hover {{ background-color: {color}cc; }}"
            )
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)

        btn_row.addStretch()
        c_neutral = get_button_color(parent, "neutral")
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c_neutral}; color: white; "
            f"border-radius: 6px; padding: 6px 14px; }}"
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
        parent_settings = getattr(self.parent(), 'settings', {})
        active_sensors  = parent_settings.get("active_sensors", Constants.ALL_SENSORS)

        filtered = {
            name: data for name, data in simulations.items()
            if data.get("Sensor", "") in active_sensors
        }

        theme = getattr(self.parent(), 'current_theme', 'Gruvbox Dark')
        name_color, text_color, header_color = THEME_BROWSER_COLORS.get(
            theme, ("#b8bb26", "#ebdbb2", "#458588")
        )

        self.text_area.clear()
        cursor = self.text_area.textCursor()

        header_fmt = QTextCharFormat()
        header_fmt.setFontWeight(QFont.Weight.Bold)
        header_fmt.setFontPointSize(11)
        header_fmt.setForeground(QColor(header_color))

        if len(active_sensors) == len(Constants.ALL_SENSORS):
            sensor_label = "All sensors"
        elif len(active_sensors) == 1:
            sensor_label = active_sensors[0]
        else:
            sensor_label = ", ".join(active_sensors)

        cursor.insertText(f"  Showing: {sensor_label}  ({len(filtered)} recipes)\n\n", header_fmt)

        bold_fmt = QTextCharFormat()
        bold_fmt.setFontWeight(QFont.Weight.Bold)
        bold_fmt.setForeground(QColor(name_color))

        normal_fmt = QTextCharFormat()
        normal_fmt.setFontWeight(QFont.Weight.Normal)
        normal_fmt.setForeground(QColor(text_color))

        sort = getattr(self, 'sort_combo', None)
        sort_key = sort.currentText() if sort else "Name (A-Z)"

        if sort_key == "Default (XML order)":
            items = list(filtered.items())
        elif sort_key == "Default (XML reversed)":
            items = list(reversed(list(filtered.items())))
        elif sort_key == "Name (A-Z)":
            items = sorted(filtered.items(), key=lambda x: x[0].lower())
        elif sort_key == "Name (Z-A)":
            items = sorted(filtered.items(), key=lambda x: x[0].lower(), reverse=True)
        elif sort_key == "Sensor":
            sensor_order = {s: i for i, s in enumerate(Constants.ALL_SENSORS)}
            items = sorted(filtered.items(), key=lambda x: sensor_order.get(x[1].get("Sensor", ""), 99))
        elif sort_key == "Film Simulation":
            items = sorted(filtered.items(), key=lambda x: x[1].get("FilmMode", "").lower())
        else:
            items = sorted(filtered.items())

        for name, data in items:
            cursor.insertText(f"  # {name}\n", bold_fmt)
            for key, value in data.items():
                cursor.insertText(f"    - {key}: {value}\n", normal_fmt)
            cursor.insertText("\n", normal_fmt)

        self.text_area.setTextCursor(cursor)
        self.text_area.moveCursor(self.text_area.textCursor().MoveOperation.Start)

    def _refresh(self):
        self.on_change()
        self.simulations = self.parent().simulations
        self._filter(self.search_edit.text())

    def _add(self):
        AddRecipeDialog(self, self.simulations, self._refresh).exec()

    def _get_selected_recipe(self):
        query = self.search_edit.currentText().strip()
        if query and query in self.simulations:
            return query
        return None

    def _edit(self):
        EditRecipeDialog(self, self.simulations, self._refresh, preselect=self._get_selected_recipe()).exec()

    def _delete(self):
        DeleteRecipeDialog(self, self.simulations, self._refresh, preselect=self._get_selected_recipe()).exec()
        
    def _on_sort_changed(self, value):
        parent = self.parent()
        if hasattr(parent, 'settings'):
            parent.settings["recipe_browser_sort"] = value
            SettingsManager.save(parent.settings)
        self._filter(self.search_edit.currentText())