# ──────────────────────────────────────────────
# EDIT RECIPE DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QCompleter, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget
)

from constants import Constants
from managers import XMLManager
from dialogs.recipe_dialog import RecipeDialog


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
        self.recipe_combo.setEditable(True)
        self.recipe_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.recipe_combo.addItem("")
        self.recipe_combo.addItems(sorted(simulations.keys()))
        self.recipe_combo.setMinimumWidth(300)

        completer = QCompleter(sorted(simulations.keys()))
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.recipe_combo.setCompleter(completer)

        self.recipe_combo.currentTextChanged.connect(self._load_recipe)
        selector_layout.addWidget(self.recipe_combo)
        selector_layout.addStretch()

        self.layout().insertWidget(0, selector_widget)

        self._build_fields(Constants.RECIPE_FIELDS, disabled=True)
        name_widget = self.widgets.get("Name")
        if name_widget:
            name_widget.setReadOnly(True)

        self._add_button("Save Changes", "primary", self._save)
        self.btn_box.layout().addStretch()
        self._add_button("Cancel", "neutral", self.reject)

    def _load_recipe(self, name):
        if name == "-- select --" or name not in self.simulations:
            return
        self._clear_fields()
        recipe_data = self.simulations[name]
        for widget in self.widgets.values():
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

    def _clear_fields(self):
        for field in Constants.RECIPE_FIELDS:
            widget = self.widgets.get(field.name)
            if widget is None:
                continue
            if isinstance(widget, QComboBox):
                idx = widget.findText(field.default_value)
                widget.setCurrentIndex(idx if idx >= 0 else 0)
            else:
                widget.setText(field.default_value)