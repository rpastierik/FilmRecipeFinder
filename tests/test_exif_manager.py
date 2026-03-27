"""
Tests for ExifManager - management of EXIF data from image files.
"""
import os
import subprocess
from unittest.mock import patch, MagicMock, Mock

import pytest

from managers.exif_manager import ExifManager, _find_exiftool, _parse_lines


# ============================================================================
# Tests for _parse_lines function
# ============================================================================

class TestParseLines:
    """Tests for the _parse_lines helper function."""

    def test_parse_simple_lines(self):
        """Test parsing simple key-value lines."""
        lines = [
            "Model : Fujifilm X-T4",
            "ISO : 400",
            "Sharpness : +2"
        ]
        result = _parse_lines(lines)

        assert result["Model"] == "Fujifilm X-T4"
        assert result["ISO"] == "400"
        assert result["Sharpness"] == "+2"

    def test_parse_ignores_lines_without_colons(self):
        """Test that lines without colons are ignored."""
        lines = [
            "Valid Line : Value",
            "InvalidLineWithoutColon",
            "Another Valid : Data"
        ]
        result = _parse_lines(lines)

        assert len(result) == 2
        assert "Valid Line" in result
        assert "Another Valid" in result

    def test_parse_with_whitespace_handling(self):
        """Test that whitespace is properly trimmed."""
        lines = [
            "  Model  :  Fujifilm X-T4  ",
            "ISO : 400",
        ]
        result = _parse_lines(lines)

        assert result["Model"] == "Fujifilm X-T4"
        assert result["ISO"] == "400"

    def test_parse_with_multiple_colons(self):
        """Test parsing values that contain colons."""
        lines = [
            "Description : Time: 12:30:45"
        ]
        result = _parse_lines(lines)

        assert result["Description"] == "Time: 12:30:45"

    def test_parse_empty_value(self):
        """Test parsing empty values."""
        lines = [
            "Description : ",
            "Model : Fujifilm"
        ]
        result = _parse_lines(lines)

        assert result["Description"] == ""
        assert result["Model"] == "Fujifilm"

    def test_parse_with_filter_keys(self):
        """Test filtering specific keys."""
        lines = [
            "Model : Fujifilm X-T4",
            "ISO : 400",
            "Sharpness : +2",
            "FNumber : 2.8"
        ]
        filter_keys = ["Model", "ISO"]
        result = _parse_lines(lines, filter_keys=filter_keys)

        assert "Model" in result
        assert "ISO" in result
        assert "Sharpness" not in result
        assert "FNumber" not in result

    def test_parse_whitebalnancefinetune_conversion(self):
        """Test that WhiteBalanceFineTune values are converted."""
        lines = [
            "WhiteBalanceFineTune : Red +60, Blue -100"
        ]
        result = _parse_lines(lines)

        # The value should be converted via parse_wbft
        assert "WhiteBalanceFineTune" in result
        # parse_wbft converts by dividing by 20: +60 -> +3, -100 -> -5
        assert "+3" in result["WhiteBalanceFineTune"]
        assert "-5" in result["WhiteBalanceFineTune"]

    def test_parse_empty_list(self):
        """Test parsing empty line list."""
        result = _parse_lines([])
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_parse_special_characters(self):
        """Test parsing values with special characters."""
        lines = [
            "Description : Test <image> & 'photo'",
            "Copyright : © 2024"
        ]
        result = _parse_lines(lines)

        assert result["Description"] == "Test <image> & 'photo'"
        assert result["Copyright"] == "© 2024"


# ============================================================================
# Tests for _find_exiftool function
# ============================================================================

class TestFindExiftool:
    """Tests for the _find_exiftool helper function."""

    def test_find_exiftool_in_path(self, monkeypatch):
        """Test finding exiftool in system PATH."""
        monkeypatch.setattr(
            'managers.exif_manager.shutil.which',
            lambda x: '/usr/bin/exiftool' if x == 'exiftool' else None
        )
        result = _find_exiftool()
        assert result == '/usr/bin/exiftool'

    def test_find_exiftool_not_found(self, monkeypatch):
        """Test error when exiftool is not found."""
        monkeypatch.setattr('managers.exif_manager.shutil.which', lambda x: None)
        monkeypatch.setattr('os.path.exists', lambda x: False)
        monkeypatch.setattr('os.listdir', lambda x: [])

        with pytest.raises(FileNotFoundError) as exc_info:
            _find_exiftool()

        assert "ExifTool not found" in str(exc_info.value)

    def test_find_exiftool_error_message_content(self, monkeypatch):
        """Test that error message contains helpful information."""
        def mock_listdir(path):
            return ['file1.txt', 'file2.txt']

        monkeypatch.setattr('managers.exif_manager.shutil.which', lambda x: None)
        monkeypatch.setattr('os.path.exists', lambda x: False)
        monkeypatch.setattr('os.listdir', mock_listdir)

        with pytest.raises(FileNotFoundError) as exc_info:
            _find_exiftool()

        error_msg = str(exc_info.value)
        assert "ExifTool not found" in error_msg
        assert "Searched in" in error_msg


# ============================================================================
# Tests for ExifManager.get_exif_data
# ============================================================================

class TestGetExifData:
    """Tests for ExifManager.get_exif_data method."""

    def test_get_exif_data_with_relevant_keys(self, monkeypatch):
        """Test retrieving filtered EXIF data with specific keys."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
ISO : 400
Sharpness : +2
FilmMode : Classic Chrome"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout=exif_output,
                returncode=0
            ))
        )

        relevant_keys = ["Model", "ISO", "Sharpness"]
        result = ExifManager.get_exif_data("test.jpg", relevant_keys)

        assert "Model" in result
        assert result["Model"] == "Fujifilm X-T4"
        assert "ISO" in result
        assert "Sharpness" in result

    def test_get_exif_data_empty_file(self, monkeypatch):
        """Test retrieving EXIF data from file with no EXIF data."""
        mock_exiftool_path = "/usr/bin/exiftool"

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout="",
                returncode=0
            ))
        )

        result = ExifManager.get_exif_data("empty.jpg", [])
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_exif_data_subprocess_called_correctly(self, monkeypatch):
        """Test that subprocess is called with correct arguments."""
        mock_exiftool_path = "/usr/bin/exiftool"
        mock_subprocess = MagicMock(return_value=MagicMock(stdout="", returncode=0))

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr('subprocess.run', mock_subprocess)

        ExifManager.get_exif_data("photo.jpg", ["Model"])

        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert call_args[0][0] == [mock_exiftool_path, '-s', 'photo.jpg']
        assert call_args[1]['capture_output'] is True
        assert call_args[1]['text'] is True

    def test_get_exif_data_with_white_balance_fine_tune(self, monkeypatch):
        """Test EXIF data with WhiteBalanceFineTune conversion."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
WhiteBalanceFineTune : Red +60, Blue -100"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout=exif_output,
                returncode=0
            ))
        )

        result = ExifManager.get_exif_data("test.jpg", None)

        assert "WhiteBalanceFineTune" in result
        # Should be converted by parse_wbft
        assert "+3" in result["WhiteBalanceFineTune"]


# ============================================================================
# Tests for ExifManager.get_exif
# ============================================================================

class TestGetExif:
    """Tests for ExifManager.get_exif method."""

    def test_get_exif_short_mode(self, monkeypatch):
        """Test retrieving EXIF data in short mode (default)."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
ISO : 400
FilmMode : Classic Chrome
Sharpness : +2"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        mock_subprocess = MagicMock(return_value=MagicMock(
            stdout=exif_output,
            returncode=0
        ))
        monkeypatch.setattr('subprocess.run', mock_subprocess)

        result = ExifManager.get_exif("photo.jpg", exif_type='short')

        assert "Model" in result
        assert "FilmMode" in result
        assert "Sharpness" in result

        # Verify correct command was used
        call_args = mock_subprocess.call_args[0][0]
        assert mock_exiftool_path in call_args
        assert '-Model' in call_args
        assert '-FilmMode' in call_args
        assert 'photo.jpg' in call_args

    def test_get_exif_full_mode(self, monkeypatch):
        """Test retrieving full EXIF data."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
ISO : 400
ExifTool Version : 12.0
Software : Fujifilm X-T4 Ver. 4.00"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        mock_subprocess = MagicMock(return_value=MagicMock(
            stdout=exif_output,
            returncode=0
        ))
        monkeypatch.setattr('subprocess.run', mock_subprocess)

        result = ExifManager.get_exif("photo.jpg", exif_type='full')

        assert "Model" in result

        # Verify -s flag was used for short output
        call_args = mock_subprocess.call_args[0][0]
        assert call_args == [mock_exiftool_path, '-s', 'photo.jpg']

    def test_get_exif_short_mode_has_all_keys(self, monkeypatch):
        """Test that short mode includes the expected EXIF keys."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
FilmMode : Classic Chrome
Saturation : 0 (normal)"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        mock_subprocess = MagicMock(return_value=MagicMock(
            stdout=exif_output,
            returncode=0
        ))
        monkeypatch.setattr('subprocess.run', mock_subprocess)

        ExifManager.get_exif("photo.jpg", exif_type='short')

        call_args = mock_subprocess.call_args[0][0]
        # Verify that short mode includes these standard keys
        expected_keys = [
            '-Model', '-PictureControlName', '-FilmMode',
            '-GrainEffectRoughness', '-Saturation', '-ISO'
        ]
        for key in expected_keys:
            assert key in call_args

    def test_get_exif_default_mode_is_short(self, monkeypatch):
        """Test that default exif_type is 'short'."""
        mock_exiftool_path = "/usr/bin/exiftool"

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        mock_subprocess = MagicMock(return_value=MagicMock(
            stdout="Model : Fujifilm",
            returncode=0
        ))
        monkeypatch.setattr('subprocess.run', mock_subprocess)

        ExifManager.get_exif("photo.jpg")

        # Verify that the default call uses short mode flags
        call_args = mock_subprocess.call_args[0][0]
        assert '-Model' in call_args

    def test_get_exif_with_multiple_exif_fields(self, monkeypatch):
        """Test retrieving multiple EXIF fields."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
ISO : 400
FNumber : F2.8
ExposureTime : 1/250
FilmMode : Classic Chrome
Saturation : +1 (medium high)
Sharpness : +2
NoiseReduction : 0 (normal)"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout=exif_output,
                returncode=0
            ))
        )

        result = ExifManager.get_exif("photo.jpg")

        assert len(result) >= 4
        assert result["ISO"] == "400"
        assert result["FNumber"] == "F2.8"
        assert result["FilmMode"] == "Classic Chrome"

    def test_get_exif_handles_empty_output(self, monkeypatch):
        """Test handling of empty exiftool output."""
        mock_exiftool_path = "/usr/bin/exiftool"

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout="",
                returncode=0
            ))
        )

        result = ExifManager.get_exif("photo.jpg")
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_exif_preserves_special_values(self, monkeypatch):
        """Test that special EXIF values are preserved correctly."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
Sharpness : +4
HighlightTone : +2 (hard)
ShadowTone : -1 (medium soft)
WhiteBalance : Kelvin"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout=exif_output,
                returncode=0
            ))
        )

        result = ExifManager.get_exif("photo.jpg")

        assert result["Sharpness"] == "+4"
        assert result["HighlightTone"] == "+2 (hard)"
        assert result["WhiteBalance"] == "Kelvin"


# ============================================================================
# Integration Tests
# ============================================================================

class TestExifManagerIntegration:
    """Integration tests for ExifManager."""

    def test_get_exif_data_filters_correctly(self, monkeypatch):
        """Test that get_exif_data properly filters EXIF keys."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
ISO : 400
Sharpness : +2
ExifTool Version : 12.0"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout=exif_output,
                returncode=0
            ))
        )

        # Filter to only get specific keys
        result = ExifManager.get_exif_data("photo.jpg", ["Model", "Sharpness"])

        assert "Model" in result
        assert "Sharpness" in result
        assert "ExifTool Version" not in result

    def test_matching_recipe_with_exif(self, monkeypatch):
        """Test scenario where EXIF data is retrieved and compared with recipe."""
        mock_exiftool_path = "/usr/bin/exiftool"
        exif_output = """Model : Fujifilm X-T4
FilmMode : Classic Chrome
Saturation : 0 (normal)
Sharpness : +2
ISO : 400"""

        monkeypatch.setattr(
            'managers.exif_manager._find_exiftool',
            lambda: mock_exiftool_path
        )
        monkeypatch.setattr(
            'subprocess.run',
            MagicMock(return_value=MagicMock(
                stdout=exif_output,
                returncode=0
            ))
        )

        # Get EXIF data
        recipe_keys = ["FilmMode", "Saturation", "Sharpness"]
        exif_data = ExifManager.get_exif_data("photo.jpg", recipe_keys)

        # Simulate recipe matching
        assert exif_data["FilmMode"] == "Classic Chrome"
        assert exif_data["Saturation"] == "0 (normal)"
        assert exif_data["Sharpness"] == "+2"
