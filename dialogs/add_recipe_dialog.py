# ──────────────────────────────────────────────
# ADD RECIPE DIALOG
# ──────────────────────────────────────────────
from utils import parse_wbft

from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout
)

from constants import Constants
from managers import ExifManager, RecipeManager, XMLManager
from dialogs.recipe_dialog import RecipeDialog
from utils.recipe_text_parser import parse_recipe_text          # ← NEW


class AddRecipeDialog(RecipeDialog):
    def __init__(self, parent, simulations, on_success):
        super().__init__(parent, "Add New Recipe")
        self.simulations = simulations
        self.on_success = on_success

        self._build_fields(Constants.RECIPE_FIELDS)
        self._add_button("Save Recipe",   "#4CAF50", self._save)
        self._add_button("Reset",         "#FF9800", self._reset)
        self._add_button("From Picture",  "#00BCD4", self._load_from_picture)
        self._add_button("From Text",     "#9C27B0", self._load_from_text)  # ← NEW
        self.btn_box.layout().addStretch()
        self._add_button("Cancel",        "#f44336", self.reject)

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
                'Clarity': 'Clarity',
            }
            for exif_key, field_name in mapping.items():
                if exif_key in exif_data:
                    value = exif_data[exif_key]
                    if field_name == 'WhiteBalanceFineTune':
                        value = parse_wbft(value)
                    self._set_field_value(field_name, value)
            self._set_field_value('Sensor', 'X-Trans V')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to extract EXIF: {e}")

    def _load_from_text(self):                                   # ← NEW
        dlg = QDialog(self)
        dlg.setWindowTitle("Import Recipe from Text")
        dlg.setMinimumSize(500, 340)
        layout = QVBoxLayout(dlg)

        lbl = QLabel("Paste recipe text below (e.g. from Fuji X Weekly):")
        layout.addWidget(lbl)

        text_edit = QTextEdit()
        text_edit.setPlaceholderText(
            "Film Simulation: Classic Chrome\n"
            "Grain Effect: Weak, Small\n"
            "White Balance: Auto, +1 Red & -3 Blue\n"
            "..."
        )
        layout.addWidget(text_edit)

        btn_row = QHBoxLayout()
        import_btn = QPushButton("Import")
        import_btn.setStyleSheet(
            "QPushButton { background-color: #9C27B0; color: white; "
            "border-radius: 6px; padding: 6px 18px; font-weight: bold; }"
            "QPushButton:hover { background-color: #AB47BC; }"
        )
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "QPushButton { background-color: #9E9E9E; color: white; "
            "border-radius: 6px; padding: 6px 18px; }"
        )
        btn_row.addStretch()
        btn_row.addWidget(import_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        cancel_btn.clicked.connect(dlg.reject)

        def do_import():
            raw = text_edit.toPlainText().strip()
            if not raw:
                QMessageBox.warning(dlg, "Empty", "Please paste some recipe text first.")
                return
            parsed = parse_recipe_text(raw)
            if not parsed:
                QMessageBox.warning(dlg, "Parse Error", "Could not find any recognizable recipe fields.")
                return
            for field, value in parsed.items():
                self._set_field_value(field, value)
            dlg.accept()

        import_btn.clicked.connect(do_import)
        dlg.exec()

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
        if choice == "Overwrite":
            if XMLManager.update_recipe(recipe_data):
                QMessageBox.information(self, "Success", f"Recipe '{name}' updated!")
                self.accept()
                self.on_success()
        elif choice == "Keep Both":
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