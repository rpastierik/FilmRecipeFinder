# ──────────────────────────────────────────────
# EXIF MANAGER
# ──────────────────────────────────────────────
import os
import shutil
import subprocess
import sys

from utils import resource_path


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


class ExifManager:
    @staticmethod
    def get_exif_data(filename, relevant_keys):
        """Načíta EXIF dáta relevantné pre porovnanie s receptami."""
        exiftool_path = _find_exiftool()
        result = subprocess.run(
            [exiftool_path, '-s', filename],
            capture_output=True, text=True
        )
        exif_data = {}
        for line in result.stdout.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                if key.strip() in relevant_keys:
                    exif_data[key.strip()] = value.strip()
        return exif_data

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
        exif_data = {}
        for line in result.stdout.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                exif_data[key.strip()] = value.strip()
        return exif_data
