# Changelog
All notable changes to this project will be documented in this file.

## [0.5.7] - 2026.03.22
- Changed: Recipe Card Exporter output aspect ratio changed to 4:5 portrait (900×1125 px)

## [0.5.6] - 2026.03.21
- Fixed: Histogram in step mode no longer renders fill – only the outline is drawn

## [0.5.5] - 2026.03.11
- Fixed: Recipe identification broken after adding Favourite, Description and URL fields – added to comparison skip list

## [0.5.4] - 2026.03.09
- Added: Favourite field for recipes – use "Favourites" sort in Recipe Browser to show only favourite recipes
- Added: Description and URL fields for recipes
- Added: URL field in Recipe Browser is clickable and opens in default browser
- Added: Edit Recipe and Delete Recipe dialogs pre-select the recipe when exactly one is shown/searched in Recipe Browser
- Fixed: Recipe Browser sort preference is now saved and restored between sessions
- Fixed: Edit Recipe dialog clears all fields correctly when switching between recipes
- Changed: Recipe name is now editable in Edit Recipe dialog
- Changed: Sharpness values changed from Hard/Soft/Normal to numeric scale (-4 to +4)
- Fixed: Dynamic Range import from text now saves as plain number (400) instead of DR400
- Removed: Dead code – LIGHT_THEMES constant and _is_dark() method removed from Recipe Browser
- Fixed: Recipe Browser crashed after editing a recipe due to .text() called on QComboBox instead of .currentText()

## [0.5.3] - 2026.03.07
- Added: About dialog with clickable Ko-fi and email links
- Added: Gradient fill for histogram channels (RGB and luminance)
- Changed: Detail view image now scales responsively with window resize
- Changed: Export Recipe Card context menu now only activates on the photo, not on histogram or info panel

## [0.5.2] - 2026.03.07
- Changed: Histogram rewritten as pure Qt widget (QPainter) – matplotlib and numpy dependencies removed
- Changed: Histogram background color now reflects the active theme
- Changed: RGB channel colors adapt to dark/light theme for better contrast
- Changed: Button colors in all dialogs now reflect the active theme
- Added: Histogram tooltip – hover to see pixel counts per channel at any brightness value
- Added: Click on histogram to toggle between RGB and luminance mode
- Added: Histogram grid overlay with brightness and percentage markers (toggleable in Settings)
- Added: Histogram computations run in background thread (QThread) – UI stays responsive
- Fixed: Button text contrast in Dracula, Nord, and Monochrome Dark themes
- Fixed: Histogram baseline aligned with image and info panel

## [0.5.1] - 2026.03.07
- Added: Sort dropdown in Recipe Browser (XML order, XML reversed, Name A-Z/Z-A, Sensor, Film Simulation)
- Added: Search/autocomplete in Recipe Browser
- Changed: Settings moved from View menu to Tools menu
- Changed: Add Recipe and Edit Recipe dialogs are now taller to show all fields without scrolling

## [0.5.0] - 2026.03.05
- Added: Multiple themes – Nord, Dracula, Tokyo Night, Solarized Light, Monochrome Dark
- Added: Theme dropdown in Settings dialog
- Added: Theme name displayed in status bar
- Changed: Histogram colors now reflect active theme
- Fixed: `resource_path` now resolves correctly from `utils/` subdirectory
- Fixed: `WhiteBalanceFineTune` conversion applied consistently during recipe identification
- Fixed: Search/autocomplete added to Edit Recipe and Delete Recipe dropdowns

## [0.4.1] - 2026.03.04
- Added: Import recipe from text (From Text button in Add Recipe dialog)

## [0.4.0] - 2026.03.03
- Added: Recipe Card Exporter – export stylized PNG card via right-click or detail view

## [0.3.2] - 2026.03.01
- Changed: Minor fixes

## [0.3.1] - 2026.02.28
- Changed: WhiteBalanceFineTune logic

## [0.3.0] - 2026.02.28
- Changed: File structure

## [0.2.1] - 2026.02.28
- Added: Sensors

## [0.2.0] - 2026.02.27
- Added: Image Detail Dialog

## [0.1.0] - 2026.02.25
- Added: Basic GUI built on PyQT6
- Changed: Complete rewrite from tkinter to PyQt6