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

EVERFOREST_THEME = _build_theme(
    "#2d353b", "#232a2e", "#3d484d",
    "#d3c6aa", "#859289",
    "#3d484d", "#475258",
    "#a7c080", "#859289", "#232a2e"
)

ROSE_PINE_THEME = _build_theme(
    "#191724", "#1f1d2e", "#2a2737",
    "#e0def4", "#6e6a86",
    "#2a2737", "#393552",
    "#ebbcba", "#6e6a86", "#1f1d2e"
)

ONE_DARK_THEME = _build_theme(
    "#282c34", "#21252b", "#2c313c",
    "#abb2bf", "#5c6370",
    "#2c313c", "#3e4452",
    "#98c379", "#5c6370", "#21252b"
)

KANAGAWA_THEME = _build_theme(
    "#1f1f28", "#16161d", "#2a2a37",
    "#dcd7ba", "#727169",
    "#2a2a37", "#363646",
    "#7e9cd8", "#727169", "#16161d"
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
    "Everforest":        EVERFOREST_THEME,
    "Rose Pine":         ROSE_PINE_THEME,
    "One Dark":          ONE_DARK_THEME,
    "Kanagawa":          KANAGAWA_THEME,
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
    "Everforest":       ("#232a2e", "#d3c6aa"),
    "Rose Pine":        ("#1f1d2e", "#e0def4"),
    "One Dark":         ("#21252b", "#abb2bf"),
    "Kanagawa":         ("#16161d", "#dcd7ba"),
}

# name_color, text_color, header_color
THEME_BROWSER_COLORS = {
    "Gruvbox Dark":     ("#b8bb26", "#ebdbb2", "#458588"),
    "Catppuccin Latte": ("#4c9a2a", "#4c4f69", "#1e66f5"),
    "Nord":             ("#a3be8c", "#eceff4", "#88c0d0"),
    "Dracula":          ("#50fa7b", "#f8f8f2", "#bd93f9"),
    "Tokyo Night":      ("#9ece6a", "#c0caf5", "#7aa2f7"),
    "Solarized Light":  ("#859900", "#657b83", "#268bd2"),
    "Monochrome Dark":  ("#ffffff", "#e0e0e0", "#aaaaaa"),
    "Everforest":       ("#a7c080", "#d3c6aa", "#7fbbb3"),
    "Rose Pine":        ("#ebbcba", "#e0def4", "#c4a7e7"),
    "One Dark":         ("#98c379", "#abb2bf", "#61afef"),
    "Kanagawa":         ("#98bb6c", "#dcd7ba", "#7e9cd8"),
}

# Button colors per theme: primary, warning, info, purple, danger, neutral
THEME_BUTTON_COLORS = {
    #                    primary     warning     info        purple      danger      neutral
    "Gruvbox Dark":     ("#98971a", "#d79921", "#458588", "#b16286", "#cc241d", "#7c6f64"),
    "Catppuccin Latte": ("#4c9a2a", "#df8e1d", "#209fb5", "#8839ef", "#d20f39", "#8c8fa1"),
    "Nord":             ("#3d6b30", "#8a6200", "#88c0d0", "#b48ead", "#bf616a", "#616e88"),
    "Dracula":          ("#28a745", "#c8a000", "#8be9fd", "#bd93f9", "#ff5555", "#6272a4"),
    "Tokyo Night":      ("#9ece6a", "#e0af68", "#7dcfff", "#bb9af7", "#f7768e", "#565f89"),
    "Solarized Light":  ("#859900", "#b58900", "#268bd2", "#6c71c4", "#dc322f", "#93a1a1"),
    "Monochrome Dark":  ("#555555", "#444444", "#666666", "#777777", "#222222", "#3a3a3a"),
    "Everforest":       ("#a7c080", "#dbbc7f", "#7fbbb3", "#d699b6", "#e67e80", "#859289"),
    "Rose Pine":        ("#31748f", "#f6c177", "#ebbcba", "#c4a7e7", "#eb6f92", "#6e6a86"),
    "One Dark":         ("#98c379", "#e5c07b", "#61afef", "#c678dd", "#e06c75", "#5c6370"),
    "Kanagawa":         ("#98bb6c", "#dca561", "#7e9cd8", "#957fb8", "#e46876", "#727169"),
}