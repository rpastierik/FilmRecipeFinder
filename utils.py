# ──────────────────────────────────────────────
# UTILITY
# ──────────────────────────────────────────────
import os
import sys


def resource_path(relative_path):
    """Vráti správnu cestu k súboru — funguje aj pre PyInstaller build."""
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)
