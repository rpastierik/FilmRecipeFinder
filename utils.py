# ──────────────────────────────────────────────
# UTILITY
# ──────────────────────────────────────────────
import os
import re
import sys


def resource_path(relative_path):
    """Return the correct file path, working with a PyInstaller build too."""
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def parse_wbft(raw_value):
    """
    Convert an EXIF WhiteBalanceFineTune value to the display form (÷20).
    e.g. 'Red +60, Blue -100' -> 'Red +3, Blue -5'
    Used only when reading from EXIF; the XML already stores values in the
    correct format.
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