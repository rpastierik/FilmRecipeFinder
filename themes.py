# ──────────────────────────────────────────────
# THEMES
# ──────────────────────────────────────────────

def _build_theme(
    bg, bg2, bg3,
    fg, fg2,
    border, border2,
    accent, scroll_handle, scroll_bg
):
    """Build a QSS theme string from color tokens."""
    return f"""
    QMainWindow, QWidget {{
        background-color: {bg};
        color: {fg};
        font-family: 'Segoe UI', Arial;
        font-size: 13px;
    }}
    QMenuBar {{
        background-color: {bg2};
        color: {fg};
        padding: 4px;
        font-size: 13px;
    }}
    QMenuBar::item:selected {{
        background-color: {bg3};
        border-radius: 4px;
    }}
    QMenu {{
        background-color: {bg2};
        color: {fg};
        border: 1px solid {border};
        min-width: 150px;
    }}
    QMenu::item:selected {{
        background-color: {bg3};
    }}
    QStatusBar {{
        background-color: {bg2};
        color: {fg2};
        font-size: 12px;
        padding: 2px 8px;
    }}
    QScrollArea {{
        border: none;
        background-color: {bg};
    }}
    QScrollBar:vertical {{
        background: {scroll_bg};
        width: 12px;
        border-radius: 7px;
    }}
    QScrollBar::handle:vertical {{
        background: {scroll_handle};
        border-radius: 7px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {fg};
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: {border};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QLabel#imageLabel {{
        border: 2px solid {border};
        border-radius: 8px;
        padding: 4px;
    }}
    QFrame#imageCard {{
        background-color: {bg2};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 10px;
    }}
    QTextEdit {{
        background-color: {bg2};
        color: {fg};
        border: 1px solid {border};
        border-radius: 6px;
    }}
    QRadioButton {{ spacing: 8px; }}
    QRadioButton::indicator {{
        width: 16px; height: 16px;
        border-radius: 8px;
        border: 2px solid {fg2};
        background-color: transparent;
    }}
    QRadioButton::indicator:checked {{
        border: 2px solid {accent};
        background-color: {accent};
    }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border-radius: 3px;
        border: 2px solid {fg2};
        background-color: transparent;
    }}
    QCheckBox::indicator:checked {{
        border: 2px solid {accent};
        background-color: {accent};
    }}
    """


# ── Theme definitions ───────────────────────────────────────────────────────
#                     bg        bg2       bg3       fg        fg2
#                     border    border2   accent    scroll_h  scroll_bg

DARK_THEME = _build_theme(
    "#282828", "#1d2021", "#3c3836",
    "#ebdbb2", "#928374",
    "#3c3836", "#504945",
    "#b8bb26", "#928374", "#1d2021"
)

LIGHT_THEME = _build_theme(
    "#eff1f5", "#dce0e8", "#ccd0da",
    "#4c4f69", "#6c6f85",
    "#ccd0da", "#bcc0cc",
    "#4c9a2a", "#6c6f85", "#dce0e8"
)

NORD_THEME = _build_theme(
    "#2e3440", "#242932", "#3b4252",
    "#eceff4", "#9099a6",
    "#3b4252", "#434c5e",
    "#88c0d0", "#81a1c1", "#242932"
)

DRACULA_THEME = _build_theme(
    "#282a36", "#1e1f29", "#383a47",
    "#f8f8f2", "#6272a4",
    "#383a47", "#44475a",
    "#bd93f9", "#6272a4", "#1e1f29"
)

TOKYO_NIGHT_THEME = _build_theme(
    "#1a1b2e", "#13141f", "#242637",
    "#c0caf5", "#565f89",
    "#242637", "#2f3047",
    "#7aa2f7", "#565f89", "#13141f"
)

SOLARIZED_LIGHT_THEME = _build_theme(
    "#fdf6e3", "#eee8d5", "#e0dac8",
    "#657b83", "#93a1a1",
    "#e0dac8", "#d4cebb",
    "#268bd2", "#93a1a1", "#eee8d5"
)

MONOCHROME_THEME = _build_theme(
    "#1a1a1a", "#111111", "#2a2a2a",
    "#e0e0e0", "#888888",
    "#2a2a2a", "#333333",
    "#ffffff", "#666666", "#111111"
)


# ── Registry ────────────────────────────────────────────────────────────────

THEMES = {
    "Gruvbox Dark":      DARK_THEME,
    "Catppuccin Latte":  LIGHT_THEME,
    "Nord":              NORD_THEME,
    "Dracula":           DRACULA_THEME,
    "Tokyo Night":       TOKYO_NIGHT_THEME,
    "Solarized Light":   SOLARIZED_LIGHT_THEME,
    "Monochrome Dark":   MONOCHROME_THEME,
}

DEFAULT_THEME = "Gruvbox Dark"

# bg, fg pre histogram
THEME_HISTOGRAM_COLORS = {
    "Gruvbox Dark":     ("#1d2021", "#ebdbb2"),
    "Catppuccin Latte": ("#dce0e8", "#4c4f69"),
    "Nord":             ("#242932", "#eceff4"),
    "Dracula":          ("#1e1f29", "#f8f8f2"),
    "Tokyo Night":      ("#13141f", "#c0caf5"),
    "Solarized Light":  ("#eee8d5", "#657b83"),
    "Monochrome Dark":  ("#111111", "#e0e0e0"),
}