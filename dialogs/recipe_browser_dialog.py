# ──────────────────────────────────────────────
# RECIPE BROWSER DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextCharFormat
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QCompleter, QDialog, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QVBoxLayout, QFrame, QInputDialog, QMessageBox, QSizePolicy
)

from constants import Constants
from themes import THEMES, THEME_BROWSER_COLORS
from dialogs.add_recipe_dialog import AddRecipeDialog
from dialogs.edit_recipe_dialog import EditRecipeDialog
from dialogs.delete_recipe_dialog import DeleteRecipeDialog
from dialogs.recipe_dialog import get_button_color
from managers import SettingsManager
from PyQt6.QtWidgets import QTextBrowser


# Fields shown in the advanced filter (subset of recipe fields, most useful for filtering)
FILTER_FIELDS = [
    "FilmMode",
    "GrainEffectRoughness",
    "GrainEffectSize",
    "ColorChromeEffect",
    "ColorChromeFXBlue",
    "WhiteBalance",
    "HighlightTone",
    "ShadowTone",
    "Saturation",
    "Sharpness",
    "NoiseReduction",
    "Clarity",
    "Sensor",
]


def _field_options(field_name):
    """Return the combo options for a given recipe field name."""
    for f in Constants.RECIPE_FIELDS:
        if f.name == field_name and f.options:
            return ["(any)"] + f.options
    return ["(any)"]


class FilterRow(QFrame):
    """One row in the advanced filter: Field | Value combo."""

    def __init__(self, parent_dialog):
        super().__init__()
        self._parent_dialog = parent_dialog
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.field_combo = QComboBox()
        self.field_combo.addItems(FILTER_FIELDS)
        self.field_combo.setMinimumWidth(160)
        self.field_combo.currentTextChanged.connect(self._on_field_changed)
        layout.addWidget(self.field_combo)

        self.value_combo = QComboBox()
        self.value_combo.setEditable(False)
        self.value_combo.setMinimumWidth(200)
        layout.addWidget(self.value_combo)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setToolTip("Remove this filter")
        remove_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #888; font-size: 14px; }"
            "QPushButton:hover { color: #cc4444; }"
        )
        remove_btn.clicked.connect(self._remove)
        layout.addWidget(remove_btn)
        layout.addStretch()

        self._populate_values()

    def _on_field_changed(self):
        self._populate_values()
        self._parent_dialog._apply_advanced_filter()

    def _populate_values(self):
        field = self.field_combo.currentText()
        self.value_combo.blockSignals(True)
        self.value_combo.clear()
        self.value_combo.addItems(_field_options(field))
        self.value_combo.blockSignals(False)
        self.value_combo.currentTextChanged.connect(self._parent_dialog._apply_advanced_filter)

    def _remove(self):
        self._parent_dialog._remove_filter_row(self)

    def get_condition(self):
        """Return (field, value) or None if set to (any)."""
        field = self.field_combo.currentText()
        value = self.value_combo.currentText()
        if value == "(any)":
            return None
        return (field, value)

    def to_dict(self):
        return {"field": self.field_combo.currentText(), "value": self.value_combo.currentText()}

    def from_dict(self, d):
        idx = self.field_combo.findText(d.get("field", ""))
        if idx >= 0:
            self.field_combo.setCurrentIndex(idx)
        self._populate_values()
        idx2 = self.value_combo.findText(d.get("value", "(any)"))
        if idx2 >= 0:
            self.value_combo.setCurrentIndex(idx2)


class RecipeBrowserDialog(QDialog):
    def __init__(self, parent, simulations, on_change):
        super().__init__(parent)
        self.setWindowTitle("Recipe Browser")
        screen = (
            parent.screen().geometry()
            if parent and parent.screen()
            else QApplication.primaryScreen().geometry()
        )
        
        self.setMinimumSize(
            min(640, int(screen.width()  * 0.50)),
            min(750, int(screen.height() * 0.85)),
        )
        
        self.setModal(False)
        self.simulations = simulations
        self.on_change = on_change
        self._filter_rows = []

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
        self.search_edit.currentTextChanged.connect(self._apply_advanced_filter)
        self.search_edit.lineEdit().textEdited.connect(self._apply_advanced_filter)
        search_row.addWidget(self.search_edit)

        _fav_color = get_button_color(parent, "primary")
        self.fav_btn = QPushButton("Favourites only")
        self.fav_btn.setCheckable(True)
        self.fav_btn.setChecked(False)
        self.fav_btn.setFixedHeight(30)
        self.fav_btn.setMinimumWidth(120)
        self.fav_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid #888;
                border-radius: 5px;
                padding: 2px 10px;
                background: transparent;
                font-size: 12px;
            }}
            QPushButton:checked {{
                background-color: {_fav_color};
                color: white;
                border-color: {_fav_color};
                font-weight: bold;
            }}
            QPushButton:hover {{ border-color: {_fav_color}; }}
        """)
        self.fav_btn.clicked.connect(self._apply_advanced_filter)
        search_row.addWidget(self.fav_btn)

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

        # ── Advanced filter panel ──
        adv_frame = QFrame()
        adv_frame.setObjectName("advFilterFrame")
        adv_frame.setFrameShape(QFrame.Shape.StyledPanel)
        adv_layout = QVBoxLayout(adv_frame)
        adv_layout.setContentsMargins(8, 6, 8, 6)
        adv_layout.setSpacing(4)

        # Header row
        header_row = QHBoxLayout()
        header_lbl = QLabel("Advanced Filter")
        header_lbl.setStyleSheet("font-weight: bold;")
        header_row.addWidget(header_lbl)
        header_row.addStretch()

        add_row_btn = QPushButton("＋ Add condition")
        add_row_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 12px; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        add_row_btn.clicked.connect(self._add_filter_row)
        header_row.addWidget(add_row_btn)

        adv_layout.addLayout(header_row)

        # Container for filter rows
        self._filter_rows_layout = QVBoxLayout()
        self._filter_rows_layout.setSpacing(3)
        adv_layout.addLayout(self._filter_rows_layout)

        # Saved filters row
        saved_row = QHBoxLayout()
        saved_row.addWidget(QLabel("Saved:"))

        self.saved_combo = QComboBox()
        self.saved_combo.setMinimumWidth(160)
        self.saved_combo.setPlaceholderText("— select —")
        self._populate_saved_combo()
        self.saved_combo.currentTextChanged.connect(self._load_saved_filter)
        saved_row.addWidget(self.saved_combo)

        save_btn = QPushButton("💾 Save")
        save_btn.setFixedHeight(26)
        save_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 12px; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        save_btn.clicked.connect(self._save_current_filter)
        saved_row.addWidget(save_btn)

        delete_saved_btn = QPushButton("🗑 Delete")
        delete_saved_btn.setFixedHeight(26)
        delete_saved_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 12px; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        delete_saved_btn.clicked.connect(self._delete_saved_filter)
        saved_row.addWidget(delete_saved_btn)

        clear_btn = QPushButton("✕ Clear")
        clear_btn.setFixedHeight(26)
        clear_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 12px; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        clear_btn.clicked.connect(self._clear_filter)
        saved_row.addWidget(clear_btn)

        saved_row.addStretch()
        adv_layout.addLayout(saved_row)

        layout.addWidget(adv_frame)

        # ── Recipe list ──
        self.text_area = QTextBrowser()
        self.text_area.setFont(QFont("Courier New", 10))
        self.text_area.setOpenExternalLinks(True)
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

        self._apply_advanced_filter()

    # ── Filter rows ───────────────────────────────────────────────────────

    def _add_filter_row(self):
        row = FilterRow(self)
        self._filter_rows.append(row)
        self._filter_rows_layout.addWidget(row)
        self._apply_advanced_filter()

    def _remove_filter_row(self, row):
        self._filter_rows.remove(row)
        self._filter_rows_layout.removeWidget(row)
        row.deleteLater()
        self._apply_advanced_filter()

    def _clear_filter(self):
        for row in list(self._filter_rows):
            self._filter_rows_layout.removeWidget(row)
            row.deleteLater()
        self._filter_rows.clear()
        self.saved_combo.blockSignals(True)
        self.saved_combo.setCurrentIndex(-1)
        self.saved_combo.blockSignals(False)
        self._apply_advanced_filter()

    # ── Apply filter ──────────────────────────────────────────────────────

    def _apply_advanced_filter(self, *_):
        """Combine text search (OR across all fields) with advanced filter rows (AND between rows)."""
        query = self.search_edit.currentText().strip() if hasattr(self, 'search_edit') else ""

        # Collect active conditions grouped by field { field: [val1, val2, ...] }
        # Multiple rows with the same field → OR between them
        # Different fields → AND between them
        conditions: dict[str, list[str]] = {}
        for row in self._filter_rows:
            cond = row.get_condition()
            if cond:
                field, value = cond
                conditions.setdefault(field, []).append(value)

        fav_only = hasattr(self, 'fav_btn') and self.fav_btn.isChecked()

        filtered = {}
        for name, data in self.simulations.items():
            # Favourites toggle
            if fav_only and data.get("Favourite") != "Yes":
                continue
            # Text search
            if query:
                match = query.lower() in name.lower() or any(
                    query.lower() in str(v).lower() for v in data.values()
                )
                if not match:
                    continue
            # Advanced conditions (AND between fields, OR within field)
            ok = True
            for field, values in conditions.items():
                recipe_val = str(data.get(field, ""))
                if not any(v.lower() == recipe_val.lower() for v in values):
                    ok = False
                    break
            if ok:
                filtered[name] = data

        self._display(filtered)

    # ── Saved filters ─────────────────────────────────────────────────────

    def _get_saved_filters(self) -> dict:
        parent_settings = getattr(self.parent(), 'settings', {})
        return parent_settings.get("saved_filters", {})

    def _set_saved_filters(self, filters: dict):
        parent = self.parent()
        if hasattr(parent, 'settings'):
            parent.settings["saved_filters"] = filters
            SettingsManager.save(parent.settings)

    def _populate_saved_combo(self):
        self.saved_combo.blockSignals(True)
        self.saved_combo.clear()
        for name in sorted(self._get_saved_filters().keys()):
            self.saved_combo.addItem(name)
        self.saved_combo.setCurrentIndex(-1)
        self.saved_combo.blockSignals(False)

    def _save_current_filter(self):
        conditions = [row.to_dict() for row in self._filter_rows if row.get_condition()]
        if not conditions:
            QMessageBox.information(self, "Save Filter", "No active conditions to save.")
            return
        name, ok = QInputDialog.getText(self, "Save Filter", "Filter name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        saved = self._get_saved_filters()
        saved[name] = conditions
        self._set_saved_filters(saved)
        self._populate_saved_combo()
        # Select the just-saved filter
        idx = self.saved_combo.findText(name)
        if idx >= 0:
            self.saved_combo.blockSignals(True)
            self.saved_combo.setCurrentIndex(idx)
            self.saved_combo.blockSignals(False)

    def _load_saved_filter(self, name: str):
        if not name:
            return
        saved = self._get_saved_filters()
        conditions = saved.get(name, [])
        # Clear existing rows
        for row in list(self._filter_rows):
            self._filter_rows_layout.removeWidget(row)
            row.deleteLater()
        self._filter_rows.clear()
        # Recreate rows from saved data
        for d in conditions:
            row = FilterRow(self)
            row.from_dict(d)
            self._filter_rows.append(row)
            self._filter_rows_layout.addWidget(row)
        self._apply_advanced_filter()

    def _delete_saved_filter(self):
        name = self.saved_combo.currentText()
        if not name:
            return
        saved = self._get_saved_filters()
        if name in saved:
            del saved[name]
            self._set_saved_filters(saved)
            self._populate_saved_combo()
            self._apply_advanced_filter()

    # ── Display ───────────────────────────────────────────────────────────

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

        # Počet zodpovedá reálne zobrazeným receptom (po Favourites filtri)
        cursor.insertText(f"  Showing: {sensor_label}  ({len(items)} recipes)\n\n", header_fmt)

        for name, data in items:
            cursor.insertText(f"  # {name}\n", bold_fmt)
            for key, value in data.items():
                if key == "URL" and value.startswith("http"):
                    url_fmt = QTextCharFormat()
                    url_fmt.setFontWeight(QFont.Weight.Normal)
                    url_fmt.setForeground(QColor("#458588"))
                    url_fmt.setFontUnderline(True)
                    url_fmt.setAnchor(True)
                    url_fmt.setAnchorHref(value)
                    cursor.insertText(f"    - {key}: ", normal_fmt)
                    cursor.insertText(f"{value}\n", url_fmt)
                else:
                    cursor.insertText(f"    - {key}: {value}\n", normal_fmt)
            cursor.insertText("\n", normal_fmt)

        self.text_area.setTextCursor(cursor)
        self.text_area.moveCursor(self.text_area.textCursor().MoveOperation.Start)

    # ── CRUD ──────────────────────────────────────────────────────────────

    def _refresh(self):
        self.on_change()
        self.simulations = self.parent().simulations
        self._apply_advanced_filter()

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
        self._apply_advanced_filter()