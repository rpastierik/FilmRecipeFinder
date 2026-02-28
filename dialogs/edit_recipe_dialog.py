# ──────────────────────────────────────────────
# EDIT RECIPE DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget
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
