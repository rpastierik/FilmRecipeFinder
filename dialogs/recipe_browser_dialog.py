# ──────────────────────────────────────────────
# RECIPE BROWSER DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextCharFormat
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout
)

from constants import Constants
from dialogs.add_recipe_dialog import AddRecipeDialog
from dialogs.edit_recipe_dialog import EditRecipeDialog
from dialogs.delete_recipe_dialog import DeleteRecipeDialog


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
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Search recipes...")
        self.search_edit.textChanged.connect(self._filter)
        layout.addWidget(self.search_edit)

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
        parent_settings = getattr(self.parent(), 'settings', {})
        active_sensors = parent_settings.get("active_sensors", Constants.ALL_SENSORS)

        filtered = {
            name: data for name, data in simulations.items()
            if data.get("Sensor", "") in active_sensors
        }

        parent_dark = getattr(self.parent(), 'dark_mode', True)
        name_color   = "#b8bb26" if parent_dark else "#4c9a2a"
        text_color   = "#ebdbb2" if parent_dark else "#4c4f69"
        header_color = "#458588" if parent_dark else "#1e66f5"

        self.text_area.clear()
        cursor = self.text_area.textCursor()

        # ── Header ──
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

        for name, data in sorted(filtered.items()):
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

    def _edit(self):
        EditRecipeDialog(self, self.simulations, self._refresh).exec()

    def _delete(self):
        DeleteRecipeDialog(self, self.simulations, self._refresh).exec()
