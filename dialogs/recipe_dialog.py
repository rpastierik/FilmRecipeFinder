# ──────────────────────────────────────────────
# BASE RECIPE DIALOG
# ──────────────────────────────────────────────
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget
)

from constants import Constants


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
            widget.setCurrentIndex(idx if idx >= 0 else 0)
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
