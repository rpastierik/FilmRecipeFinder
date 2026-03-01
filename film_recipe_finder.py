# ──────────────────────────────────────────────────────────────────────────────
# Film Recipe Finder
# ──────────────────────────────────────────────────────────────────────────────
# Version  : will be read from constants.APP_VERSION at runtime
# Author   : Roman Pastierik
# Date     : March 2026
# License  : GNU General Public License v3
#
# Description:
#   Desktop application for Fujifilm photographers.
#   Identifies film simulation recipes from image EXIF data and matches
#   them against a local XML database of saved recipes.
#
# Dependencies:
#   PyQt6, Pillow, NumPy, Matplotlib, ExifTool (Phil Harvey)
#
# Repository:
#   https://github.com/rpastierik/FilmRecipeFinder
#
# Support:
#   https://ko-fi.com/rpastierik
#
# Uses ExifTool by Phil Harvey (philharvey66@gmail.com)
# ExifTool is licensed under the Artistic License / GPL
# ──────────────────────────────────────────────────────────────────────────────

import os
import sys

from constants import Constants

__version__ = Constants.APP_VERSION

os.environ["QT_LOGGING_RULES"] = "*=false"

import matplotlib
matplotlib.use('QtAgg')

from PyQt6.QtCore import qInstallMessageHandler
from PyQt6.QtWidgets import QApplication

from main_window import MainWindow


def suppress_qt_warnings(msg_type, context, message):
    pass


if __name__ == "__main__":
    qInstallMessageHandler(suppress_qt_warnings)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
