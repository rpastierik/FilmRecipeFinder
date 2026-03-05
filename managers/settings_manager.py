# ──────────────────────────────────────────────
# SETTINGS MANAGER
# ──────────────────────────────────────────────
import json
import os

from constants import Constants


class SettingsManager:
    @staticmethod
    def load():
        defaults = {
            "theme": "Gruvbox Dark",
            "show_histogram": True,
            "rgb_histogram": True,
            "histogram_type": "step",
            "active_sensors": Constants.ALL_SENSORS,
        }
        if os.path.exists(Constants.SETTINGS_FILE):
            try:
                with open(Constants.SETTINGS_FILE, "r") as f:
                    loaded = json.load(f)
                    # Migrácia zo starého formátu "dark"/"light"
                    if loaded.get("theme") == "dark":
                        loaded["theme"] = "Gruvbox Dark"
                    elif loaded.get("theme") == "light":
                        loaded["theme"] = "Catppuccin Latte"
                    defaults.update(loaded)
            except Exception:
                pass
        return defaults

    @staticmethod
    def save(settings):
        try:
            with open(Constants.SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")