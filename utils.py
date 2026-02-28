# ──────────────────────────────────────────────
# UTILITY
# ──────────────────────────────────────────────
import os
import re
import sys


def resource_path(relative_path):
    """Vráti správnu cestu k súboru — funguje aj pre PyInstaller build."""
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def parse_wbft(raw_value):
    """
    Konvertuje EXIF hodnotu WhiteBalanceFineTune na display hodnotu (÷20).
    Napr. 'Red +60, Blue -100' -> 'Red +3, Blue -5'
    Používa sa len pri čítaní z EXIF — XML má hodnoty už v správnom formáte.
    """
    try:
        matches = re.findall(r'(Red|Blue)\s*([+-]?\d+)', raw_value)
        parts = []
        for name, val in matches:
            converted = int(val) // 20
            sign = "+" if converted >= 0 else ""
            parts.append(f"{name} {sign}{converted}")
        return ", ".join(parts) if parts else raw_value
    except Exception:
        return raw_value