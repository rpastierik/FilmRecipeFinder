# ──────────────────────────────────────────────
# EXIF MANAGER
# ──────────────────────────────────────────────
import os
import shutil
import subprocess
import sys

from utils import resource_path, parse_wbft


def _find_exiftool():
    """Nájde exiftool — v PATH, vedľa exe alebo vedľa skriptu."""
    path = shutil.which('exiftool')
    if path:
        return path

    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        base = os.path.dirname(base)  # vystup z managers/ do rootu

    for candidate in [
        os.path.join(base, 'exiftool.exe'),
        os.path.join(base, 'tools', 'exiftool.exe'),
        os.path.join(base, 'bin', 'exiftool.exe'),
    ]:
        if os.path.exists(candidate):
            return candidate

    raise FileNotFoundError(
        f"ExifTool not found!\nSearched in: {base}\n"
        f"Directory contents: {os.listdir(base)}"
    )


def _parse_lines(lines, filter_keys=None):
    """Parsuje riadky exiftool výstupu do slovníka, konvertuje WBFT ÷20."""
    exif_data = {}
    for line in lines:
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        if filter_keys and key not in filter_keys:
            continue
        if key == 'WhiteBalanceFineTune':
            value = parse_wbft(value)
        exif_data[key] = value
    return exif_data


class ExifManager:
    @staticmethod
    def get_exif_data(filename, relevant_keys):
        """Načíta EXIF dáta relevantné pre porovnanie s receptami."""
        exiftool_path = _find_exiftool()
        result = subprocess.run(
            [exiftool_path, '-s', filename],
            capture_output=True, text=True
        )
        return _parse_lines(result.stdout.splitlines(), filter_keys=relevant_keys)

    @staticmethod
    def get_exif(filename, exif_type='short'):
        """Načíta krátky alebo plný EXIF výpis."""
        exiftool_path = _find_exiftool()

        if exif_type == 'full':
            cmd = [exiftool_path, '-s', filename]
        else:
            cmd = [
                exiftool_path,
                '-Model', '-PictureControlName', '-Description',
                '-FilmMode', '-GrainEffectRoughness',
                '-GrainEffectSize', '-ColorChromeEffect', '-ColorChromeFXBlue',
                '-WhiteBalance', '-WhiteBalanceFineTune', '-ColorTemperature',
                '-DevelopmentDynamicRange', '-HighlightTone', '-ShadowTone',
                '-Saturation', '-Sharpness', '-NoiseReduction', '-Clarity',
                '-FNumber', '-ISO', '-ExposureTime', '-LensID',
                filename
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return _parse_lines(result.stdout.splitlines())