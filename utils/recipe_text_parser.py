# ──────────────────────────────────────────────
# RECIPE TEXT PARSER
# Parses pasted recipe text 
# into a dict compatible with Constants.RECIPE_FIELDS
# ──────────────────────────────────────────────
import re


# ── Normalization helpers ───────────────────────

def _norm(s: str) -> str:
    """Lowercase, strip, collapse whitespace."""
    return re.sub(r"\s+", " ", s.strip().lower())


def _extract_number(s: str) -> str:
    """Extract leading +/- number from a string, e.g. '+2' or '-1'."""
    m = re.match(r"([+-]?\d+)", s.strip())
    return m.group(1) if m else s.strip()


# ── Field-specific parsers ──────────────────────

def _parse_grain(value: str) -> tuple[str, str]:
    """'Weak, Small' → ('Weak', 'Small')"""
    parts = [p.strip().title() for p in re.split(r"[,/]", value)]
    roughness = "Off"
    size = "Off"
    for p in parts:
        if p in ("Off",):
            return "Off", "Off"
        if p in ("Weak", "Strong"):
            roughness = p
        if p in ("Small", "Large"):
            size = p
    return roughness, size


def _parse_white_balance(value: str) -> tuple[str, str, str]:
    """
    'Auto Ambience Priority, +1 Red & -3 Blue'
    → wb='Auto', fine_tune='Red +1, Blue -3', color_temp=''
    """
    wb = "Auto"
    fine_tune = "Red +0, Blue +0"
    color_temp = ""

    # Kelvin e.g. "5500K" or "5500"
    k_match = re.search(r"(\d{4,5})\s*[Kk]", value)
    if k_match:
        color_temp = k_match.group(1)
        wb = "Kelvin"

    # Known WB modes
    wb_modes = {
        "auto": "Auto",
        "ambience": "Auto",
        "auto ambience priority": "Auto",
        "daylight": "Daylight",
        "shade": "Shade",
        "fluorescent": "Fluorescent",
        "incandescent": "Incandescent",
        "daylight fluorescent": "Daylight Fluorescent",
    }
    for key, mapped in wb_modes.items():
        if key in _norm(value):
            wb = mapped
            break

    # Fine tune: Red +X, Blue +Y  (various formats)
    red_m  = re.search(r"([+-]?\d+)\s*[Rr]ed|[Rr]ed\s*([+-]?\d+)", value)
    blue_m = re.search(r"([+-]?\d+)\s*[Bb]lue|[Bb]lue\s*([+-]?\d+)", value)
    red_v  = red_m.group(1)  or red_m.group(2)  if red_m  else "0"
    blue_v = blue_m.group(1) or blue_m.group(2) if blue_m else "0"
    r = int(red_v)
    b = int(blue_v)
    fine_tune = f"Red {'+' if r >= 0 else ''}{r}, Blue {'+' if b >= 0 else ''}{b}"

    return wb, fine_tune, color_temp


def _parse_dynamic_range(value: str) -> str:
    m = re.search(r"(\d+)", value)
    return m.group(1) if m else value.strip()


def _parse_tone(value: str) -> str:
    """'+2' or '2' or '-1' → best match from options like '+2 (hard)'"""
    n = _extract_number(value)
    tone_map = {
        "-2": "-2 (soft)", "-1": "-1 (medium soft)", "-0.5": "-0.5",
        "0": "0 (normal)", "+1": "+1 (medium hard)", "+2": "+2 (hard)",
        "+3": "+3 (very hard)", "+4": "+4 (hardest)",
    }
    return tone_map.get(n, n)


def _parse_saturation(value: str) -> str:
    n = _extract_number(value)
    sat_map = {
        "-4": "-4 (lowest)", "-3": "-3 (very low)", "-2": "-2 (low)",
        "-1": "-1 (medium low)", "0": "0 (normal)", "+1": "+1 (medium high)",
        "+2": "+2 (high)", "+3": "+3 (very high)", "+4": "+4 (highest)",
    }
    return sat_map.get(n, value.strip())


def _parse_noise_reduction(value: str) -> str:
    n = _extract_number(value)
    nr_map = {
        "-4": "-4 (weakest)", "-3": "-3 (very weak)", "-2": "-2 (weak)",
        "-1": "-1 (medium weak)", "0": "0 (normal)", "+1": "+1 (medium strong)",
        "+2": "+2 (strong)", "+3": "+3 (very strong)", "+4": "+4 (strongest)",
    }
    return nr_map.get(n, value.strip())


def _parse_film_mode(value: str) -> str:
    mapping = {
        "classic chrome":    "Classic Chrome",
        "classic negative":  "Classic Negative",
        "classic neg":       "Classic Negative",
        "eterna":            "Eterna",
        "eterna cinema":     "Eterna",
        "nostalgic neg":     "Nostalgic Neg",
        "nostalgic negative":"Nostalgic Neg",
        "reala ace":         "Reala ACE",
        "bleach bypass":     "Bleach Bypass",
        "pro neg hi":        "PRO Neg Hi",
        "pro neg std":       "PRO Neg Std",
        "provia":            "F0/Standard (Provia)",
        "standard":          "F0/Standard (Provia)",
        "velvia":            "F2/Fujichrome (Velvia)",
        "astia":             "F1b/Studio Portrait Smooth Skin Tone (Astia)",
        "acros":             "Acros",
    }
    v = _norm(value)
    for key, mapped in mapping.items():
        if key in v:
            return mapped
    return value.strip().title()


# ── Key aliases ────────────────────────────────

KEY_ALIASES = {
    "film simulation":        "FilmMode",
    "film sim":               "FilmMode",
    "film mode":              "FilmMode",
    "grain effect":           "Grain",
    "grain":                  "Grain",
    "color chrome effect":    "ColorChromeEffect",
    "colour chrome effect":   "ColorChromeEffect",
    "color chrome fx blue":   "ColorChromeFXBlue",
    "colour chrome fx blue":  "ColorChromeFXBlue",
    "white balance":          "WhiteBalance",
    "wb":                     "WhiteBalance",
    "dynamic range":          "DevelopmentDynamicRange",
    "dr":                     "DevelopmentDynamicRange",
    "highlight":              "HighlightTone",
    "highlight tone":         "HighlightTone",
    "shadow":                 "ShadowTone",
    "shadow tone":            "ShadowTone",
    "color":                  "Saturation",
    "colour":                 "Saturation",
    "saturation":             "Saturation",
    "sharpness":              "Sharpness",
    "noise reduction":        "NoiseReduction",
    "high iso nr":            "NoiseReduction",
    "iso nr":                 "NoiseReduction",
    "nr":                     "NoiseReduction",
    "clarity":                "Clarity",
}


# ── Main parser ────────────────────────────────

def parse_recipe_text(text: str) -> dict:
    """
    Parse a pasted Fuji X Weekly-style recipe text into a recipe dict.
    Returns a dict with keys matching Constants.RECIPE_FIELDS names.
    """
    result = {}

    # Split into lines; also handle inline format "Key: ValueKey2: Value2"
    # by inserting newline before known keys
    key_pattern = "|".join(re.escape(k) for k in sorted(KEY_ALIASES.keys(), key=len, reverse=True))
    # Normalize separators between fields on same line
    text = re.sub(rf"(?i)({key_pattern})\s*:", r"\n\1:", text)

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        if ":" not in line:
            continue
        key_raw, _, val_raw = line.partition(":")
        key = _norm(key_raw)
        val = val_raw.strip()

        field = KEY_ALIASES.get(key)
        if not field:
            continue

        if field == "FilmMode":
            result["FilmMode"] = _parse_film_mode(val)

        elif field == "Grain":
            r, s = _parse_grain(val)
            result["GrainEffectRoughness"] = r
            result["GrainEffectSize"] = s

        elif field == "WhiteBalance":
            wb, ft, ct = _parse_white_balance(val)
            result["WhiteBalance"] = wb
            result["WhiteBalanceFineTune"] = ft
            if ct:
                result["ColorTemperature"] = ct

        elif field == "DevelopmentDynamicRange":
            result["DevelopmentDynamicRange"] = _parse_dynamic_range(val)

        elif field == "HighlightTone":
            result["HighlightTone"] = _parse_tone(val)

        elif field == "ShadowTone":
            result["ShadowTone"] = _parse_tone(val)

        elif field == "Saturation":
            result["Saturation"] = _parse_saturation(val)

        elif field == "Sharpness":
            result["Sharpness"] = _extract_number(val)

        elif field == "NoiseReduction":
            result["NoiseReduction"] = _parse_noise_reduction(val)

        elif field == "Clarity":
            result["Clarity"] = _extract_number(val)

        elif field in ("ColorChromeEffect", "ColorChromeFXBlue"):
            v = val.strip().title()
            if v not in ("Off", "Weak", "Strong"):
                v = "Off"
            result[field] = v

    return result
