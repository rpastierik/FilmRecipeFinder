DARK_THEME = """
    QMainWindow, QWidget {
        background-color: #282828;
        color: #ebdbb2;
        font-family: 'Segoe UI', Arial;
        font-size: 13px;
    }
    QMenuBar {
        background-color: #1d2021;
        color: #ebdbb2;
        padding: 4px;
        font-size: 13px;
    }
    QMenuBar::item:selected {
        background-color: #3c3836;
        border-radius: 4px;
    }
    QMenu {
        background-color: #1d2021;
        color: #ebdbb2;
        border: 1px solid #3c3836;
        min-width: 150px;
    }
    QMenu::item:selected {
        background-color: #3c3836;
    }
    QStatusBar {
        background-color: #1d2021;
        color: #928374;
        font-size: 12px;
        padding: 2px 8px;
    }
    QScrollArea {
        border: none;
        background-color: #282828;
    }
    QScrollBar:vertical {
        background: #1d2021;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #504945;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #665c54;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QLabel#imageLabel {
        border: 2px solid #3c3836;
        border-radius: 8px;
        padding: 4px;
    }
    QFrame#imageCard {
        background-color: #1d2021;
        border: 1px solid #3c3836;
        border-radius: 12px;
        padding: 10px;
    }
    QTextEdit {
        background-color: #1d2021;
        color: #ebdbb2;
        border: 1px solid #3c3836;
        border-radius: 6px;
    }
    QRadioButton {
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid #928374;
        background-color: transparent;
    }
    QRadioButton::indicator:checked {
        border: 2px solid #b8bb26;
        background-color: #b8bb26;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 2px solid #928374;
        background-color: transparent;
    }
    QCheckBox::indicator:checked {
        border: 2px solid #b8bb26;
        background-color: #b8bb26;
    }
    
"""

LIGHT_THEME = """
    QMainWindow, QWidget {
        background-color: #eff1f5;
        color: #4c4f69;
        font-family: 'Segoe UI', Arial;
        font-size: 13px;
    }
    QMenuBar {
        background-color: #dce0e8;
        color: #4c4f69;
        padding: 4px;
        font-size: 13px;
    }
    QMenuBar::item:selected {
        background-color: #ccd0da;
        border-radius: 4px;
    }
    QMenu {
        background-color: #dce0e8;
        color: #4c4f69;
        border: 1px solid #ccd0da;
        min-width: 150px;
    }
    QMenu::item:selected {
        background-color: #ccd0da;
    }
    QStatusBar {
        background-color: #dce0e8;
        color: #6c6f85;
        font-size: 12px;
        padding: 2px 8px;
    }
    QScrollArea {
        border: none;
        background-color: #eff1f5;
    }
    QScrollBar:vertical {
        background: #dce0e8;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #acb0be;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #9ca0b0;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QLabel#imageLabel {
        border: 2px solid #ccd0da;
        border-radius: 8px;
        padding: 4px;
    }
    QFrame#imageCard {
        background-color: #ffffff;
        border: 1px solid #ccd0da;
        border-radius: 12px;
        padding: 10px;
    }
    QTextEdit {
        background-color: #ffffff;
        color: #4c4f69;
        border: 1px solid #ccd0da;
        border-radius: 6px;
    }
    QRadioButton {
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid #4c4f69;
        background-color: transparent;
    }
    QRadioButton::indicator:checked {
        border: 2px solid #4c9a2a;
        background-color: #4c9a2a;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 2px solid #4c4f69;
        background-color: transparent;
    }
    QCheckBox::indicator:checked {
        border: 2px solid #4c9a2a;
        background-color: #4c9a2a;
    }
"""
