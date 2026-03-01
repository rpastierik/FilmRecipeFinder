# ──────────────────────────────────────────────
# EXIF MANAGER
# ──────────────────────────────────────────────
import os
import shutil
import subprocess
import sys

from utils import resource_path, parse_wbft


def _find_exiftool():
    """Locate the exiftool executable – check PATH, beside the exe or script."""
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
    """Parse lines from exiftool output into a dictionary; convert WBFT ÷20."""
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
        """Load EXIF data relevant for comparison with recipes."""
        exiftool_path = _find_exiftool()
        result = subprocess.run(
            [exiftool_path, '-s', filename],
            capture_output=True, text=True
        )
        return _parse_lines(result.stdout.splitlines(), filter_keys=relevant_keys)

    @staticmethod
    def get_exif(filename, exif_type='short'):
        """Read either a short or full EXIF dump."""
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