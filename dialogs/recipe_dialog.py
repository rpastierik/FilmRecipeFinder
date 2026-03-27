# ──────────────────────────────────────────────
# BASE RECIPE DIALOG
# ──────────────────────────────────────────────
from PIL.ImageChops import screen
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget
)

from constants import Constants
from themes import THEME_BUTTON_COLORS

# Button type → index in THEME_BUTTON_COLORS tuple
BUTTON_TYPES = {
    "primary": 0,   # Save, confirm
    "warning": 1,   # Reset, secondary
    "info":    2,   # From Picture, import
    "purple":  3,   # From Text, special
    "danger":  4,   # Delete, destructive Cancel
    "neutral": 5,   # Cancel, Close
}


def get_button_color(parent, btn_type: str) -> str:
    """Resolve the correct button color from the active theme."""
    theme = getattr(parent, 'current_theme', None)
    # Walk up parent chain if direct parent doesn't have current_theme
    node = parent
    while theme is None and node is not None:
        theme = getattr(node, 'current_theme', None)
        node = getattr(node, 'parent', lambda: None)()
    theme = theme or "Gruvbox Dark"
    colors = THEME_BUTTON_COLORS.get(theme, THEME_BUTTON_COLORS["Gruvbox Dark"])
    idx = BUTTON_TYPES.get(btn_type, 5)
    return colors[idx]


class RecipeDialog(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.widgets = {}

        screen = (
            parent.screen().geometry()
            if parent and parent.screen()
            else QApplication.primaryScreen().geometry()
        )
        self.setMinimumWidth(min(700, int(screen.width() * 0.45)))

        outer = QVBoxLayout(self)
        outer.setSpacing(0)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll.setMinimumHeight(500)  
        scroll.setMaximumHeight(int(screen.height() * 0.75))

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
        self.adjustSize()

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

    def _add_button(self, text, btn_type, slot):
        """
        btn_type: "primary" | "warning" | "info" | "purple" | "danger" | "neutral"
        """
        color = get_button_color(self.parent(), btn_type)
        btn = QPushButton(text)
        btn.setMinimumWidth(130)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: white; "
            f"border-radius: 6px; padding: 6px 14px; }}"
            f"QPushButton:hover {{ background-color: {color}cc; }}"
        )
        btn.clicked.connect(slot)
        self.btn_box.layout().addWidget(btn)
        return btn
