# ──────────────────────────────────────────────
# DELETE RECIPE DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QCompleter, QDialog, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QVBoxLayout
)

from managers import XMLManager
from dialogs.recipe_dialog import get_button_color


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
        self.recipe_combo.setEditable(True)
        self.recipe_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.recipe_combo.addItem("")
        self.recipe_combo.addItems(sorted(simulations.keys()))
        self.recipe_combo.setMinimumWidth(340)

        completer = QCompleter(sorted(simulations.keys()))
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.recipe_combo.setCompleter(completer)

        layout.addWidget(self.recipe_combo)
        layout.addStretch()

        c_danger  = get_button_color(parent, "danger")
        c_neutral = get_button_color(parent, "neutral")

        btn_row = QHBoxLayout()
        del_btn = QPushButton("Delete Recipe")
        del_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c_danger}; color: white; "
            f"border-radius: 6px; padding: 7px 18px; font-weight: bold; }}"
            f"QPushButton:hover {{ background-color: {c_danger}cc; }}"
        )
        del_btn.clicked.connect(self._delete)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c_neutral}; color: white; "
            f"border-radius: 6px; padding: 7px 18px; }}"
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
