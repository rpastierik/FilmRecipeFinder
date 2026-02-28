# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────

class RecipeField:
    def __init__(self, name, default_value, field_type="entry", options=None):
        self.name = name
        self.default_value = default_value
        self.field_type = field_type
        self.options = options or []


class Constants:
    SETTINGS_FILE = "user_settings.json"
    XML_FILE = "film_simulations.xml"

    RECIPE_FIELDS = [
        RecipeField("Name", ""),
        RecipeField("FilmMode", "None", "combo",
                   ["Classic Chrome", "Eterna", "Classic Negative", "Reala ACE", "Nostalgic Neg",
                    "Bleach Bypass", "PRO Neg Hi", "PRO Neg Std", "None", "F0/Standard (Provia)",
                    "F1/Studio Portrait", "F1a/Studio Portrait Enhanced Saturation",
                    "F1b/Studio Portrait Smooth Skin Tone (Astia)", "F1c/Studio Portrait Increased Sharpness",
                    "F2/Fujichrome (Velvia)", "F3/Studio Portrait Ex", "F4/Velvia"]),
        RecipeField("GrainEffectRoughness", "Off", "combo", ["Off", "Weak", "Strong"]),
        RecipeField("GrainEffectSize", "Off", "combo", ["Off", "Small", "Large"]),
        RecipeField("ColorChromeEffect", "Off", "combo", ["Off", "Weak", "Strong"]),
        RecipeField("ColorChromeFXBlue", "Off", "combo", ["Off", "Weak", "Strong"]),
        RecipeField("WhiteBalance", "Auto", "combo",
                   ["Auto", "Daylight", "Shade", "Fluorescent", "Incandescent", "Kelvin", "Daylight Fluorescent"]),
        RecipeField("WhiteBalanceFineTune", "Red +0, Blue +0"),
        RecipeField("ColorTemperature", ""),
        RecipeField("DevelopmentDynamicRange", ""),
        RecipeField("HighlightTone", "0 (normal)", "combo",
                   ["-2 (soft)", "-1.5", "-1 (medium soft)", "-0.5", "0 (normal)", "0.5",
                    "+0.5", "1.5", "+1 (medium hard)", "+2 (hard)", "2.5", "+2.5",
                    "+3 (very hard)", "+3.5", "+4 (hardest)"]),
        RecipeField("ShadowTone", "0 (normal)", "combo",
                   ["-2 (soft)", "-1.5", "-1 (medium soft)", "-0.5", "0 (normal)", "0.5",
                    "+0.5", "1.5", "+1 (medium hard)", "+1.5", "+2 (hard)", "2.5", "+2.5",
                    "+3 (very hard)", "+4 (hardest)"]),
        RecipeField("Saturation", "0 (normal)", "combo",
                   ["-4 (lowest)", "-3 (very low)", "-2 (low)", "-1 (medium low)", "0 (normal)", "+0",
                    "+1 (medium high)", "+2 (high)", "+3 (very high)", "+4 (highest)",
                    "None (B&W)", "Acros", "Acros Green Filter", "Acros Red Filter", "Acros Yellow Filter",
                    "B&W Green Filter", "B&W Red Filter", "B&W Sepia"]),
        RecipeField("Sharpness", "Normal", "combo", ["Soft", "Normal", "Hard", "-0"]),
        RecipeField("NoiseReduction", "0 (normal)", "combo",
                   ["-4 (weakest)", "-3 (very weak)", "-2 (weak)", "-1 (medium weak)",
                    "0 (normal)", "+1 (medium strong)", "+2 (strong)", "+3 (very strong)", "+4 (strongest)"]),
        RecipeField("Clarity", "0"),
        RecipeField("Sensor", "X-Trans V", "combo",
                   ["X-Trans I", "X-Trans II", "X-Trans III", "X-Trans IV", "X-Trans V"])
    ]

    ALL_SENSORS = ["X-Trans I", "X-Trans II", "X-Trans III", "X-Trans IV", "X-Trans V"]
