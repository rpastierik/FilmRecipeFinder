"""
Tests for XMLManager - management of recipes in XML format.
"""
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from managers.xml_manager import XMLManager
from constants import Constants


@pytest.fixture
def temp_xml_file():
    """Create a temporary XML file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<root>
    <profile>
        <Name>Test Recipe 1</Name>
        <FilmMode>Classic Chrome</FilmMode>
        <GrainEffectRoughness>Off</GrainEffectRoughness>
        <Saturation>0 (normal)</Saturation>
    </profile>
    <profile>
        <Name>Test Recipe 2</Name>
        <FilmMode>Eterna</FilmMode>
        <GrainEffectRoughness>Weak</GrainEffectRoughness>
        <Saturation>+2 (high)</Saturation>
    </profile>
</root>
'''
        f.write(xml_content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def empty_xml_file():
    """Create an empty XML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        xml_content = '<?xml version="1.0" encoding="utf-8"?>\n<root>\n</root>'
        f.write(xml_content)
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_resource_path(temp_xml_file, monkeypatch):
    """Mock resource_path to return our test XML."""
    def mock_path(filename):
        return temp_xml_file

    monkeypatch.setattr('managers.xml_manager.resource_path', mock_path)
    return temp_xml_file


@pytest.fixture
def mock_resource_path_empty(empty_xml_file, monkeypatch):
    """Mock resource_path for empty XML."""
    def mock_path(filename):
        return empty_xml_file

    monkeypatch.setattr('managers.xml_manager.resource_path', mock_path)
    return empty_xml_file


@pytest.fixture
def mock_qmessagebox(monkeypatch):
    """Mock QMessageBox to avoid GUI."""
    mock_box = MagicMock()
    monkeypatch.setattr('managers.xml_manager.QMessageBox', mock_box)
    return mock_box


class TestLoadSimulations:
    """Tests for XMLManager.load_simulations()"""

    def test_load_existing_recipes(self, mock_resource_path):
        """Test loading existing recipes from XML."""
        result = XMLManager.load_simulations(Constants.XML_FILE)

        assert len(result) == 2
        assert "Test Recipe 1" in result
        assert "Test Recipe 2" in result
        assert result["Test Recipe 1"]["FilmMode"] == "Classic Chrome"
        assert result["Test Recipe 2"]["FilmMode"] == "Eterna"

    def test_load_recipe_fields(self, mock_resource_path):
        """Test whether all recipe fields are loaded correctly."""
        result = XMLManager.load_simulations(Constants.XML_FILE)
        recipe = result["Test Recipe 1"]

        assert recipe["Name"] == "Test Recipe 1"
        assert recipe["GrainEffectRoughness"] == "Off"
        assert recipe["Saturation"] == "0 (normal)"

    def test_load_empty_xml(self, mock_resource_path_empty):
        """Test loading empty XML."""
        result = XMLManager.load_simulations(Constants.XML_FILE)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_load_nonexistent_file(self, monkeypatch):
        """Test loading a non-existent file."""
        def mock_path(filename):
            return "/tmp/nonexistent_file_xyz_12345.xml"

        monkeypatch.setattr('managers.xml_manager.resource_path', mock_path)
        result = XMLManager.load_simulations("nonexistent.xml")

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_load_handles_missing_name_field(self, monkeypatch):
        """Test whether recipes without Name field are skipped correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<root>
    <profile>
        <FilmMode>Classic Chrome</FilmMode>
    </profile>
    <profile>
        <Name>Valid Recipe</Name>
        <FilmMode>Eterna</FilmMode>
    </profile>
</root>
'''
            f.write(xml_content)
            temp_path = f.name

        try:
            def mock_path(filename):
                return temp_path

            monkeypatch.setattr('managers.xml_manager.resource_path', mock_path)
            result = XMLManager.load_simulations(Constants.XML_FILE)

            # Only "Valid Recipe" should be loaded
            assert len(result) == 1
            assert "Valid Recipe" in result
        finally:
            os.unlink(temp_path)


class TestAddRecipe:
    """Tests for XMLManager.add_recipe()"""

    def test_add_single_recipe(self, mock_resource_path, mock_qmessagebox):
        """Test adding a new recipe."""
        new_recipe = {
            "Name": "New Recipe",
            "FilmMode": "Astia",
            "Saturation": "+1 (medium high)"
        }

        result = XMLManager.add_recipe(new_recipe)
        assert result is True

        # Verify whether it's added
        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert "New Recipe" in recipes
        assert recipes["New Recipe"]["FilmMode"] == "Astia"

    def test_add_recipe_with_all_fields(self, mock_resource_path, mock_qmessagebox):
        """Test adding a recipe with all fields."""
        new_recipe = {
            "Name": "Complete Recipe",
            "FilmMode": "Pro Neg. Hi",
            "GrainEffectRoughness": "Strong",
            "GrainEffectSize": "Large",
            "ColorChromeEffect": "Weak",
            "Saturation": "+2 (high)",
            "Sharpness": "+2",
            "NoiseReduction": "+1 (medium strong)",
            "Favourite": "Yes",
            "Description": "This is a test recipe",
            "URL": "http://example.com"
        }

        result = XMLManager.add_recipe(new_recipe)
        assert result is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        recipe = recipes["Complete Recipe"]

        assert recipe["FilmMode"] == "Pro Neg. Hi"
        assert recipe["GrainEffectSize"] == "Large"
        assert recipe["Description"] == "This is a test recipe"
        assert recipe["URL"] == "http://example.com"

    def test_add_multiple_recipes(self, mock_resource_path, mock_qmessagebox):
        """Test adding multiple recipes sequentially."""
        recipe1 = {"Name": "Recipe A", "FilmMode": "Classic Chrome"}
        recipe2 = {"Name": "Recipe B", "FilmMode": "Eterna"}

        result1 = XMLManager.add_recipe(recipe1)
        result2 = XMLManager.add_recipe(recipe2)

        assert result1 is True
        assert result2 is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert len(recipes) == 4  # 2 original + 2 new
        assert "Recipe A" in recipes
        assert "Recipe B" in recipes

    def test_add_recipe_with_duplicate_name(self, mock_resource_path, mock_qmessagebox):
        """Test adding a recipe with the same name as existing."""
        # XMLManager does not allow duplicate names at the application level,
        # but here we test that XML operation works with identical names
        new_recipe = {"Name": "Test Recipe 1", "FilmMode": "Astia"}

        result = XMLManager.add_recipe(new_recipe)
        assert result is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        # Now there should be 2 recipes with the same name
        # (expected behavior of XML without unique constraints)
        assert "Test Recipe 1" in recipes

    def test_add_recipe_with_special_characters(self, mock_resource_path, mock_qmessagebox):
        """Test adding a recipe with special characters."""
        new_recipe = {
            "Name": "Recipe_with_ASCII",
            "FilmMode": "Classic Chrome",
            "Description": "Special chars: <>&\""
        }

        result = XMLManager.add_recipe(new_recipe)
        assert result is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        # Verify that the recipe is saved (XML escape characters are handled correctly)
        assert "Recipe_with_ASCII" in recipes
        assert recipes["Recipe_with_ASCII"]["Description"] == "Special chars: <>&\""


class TestUpdateRecipe:
    """Tests for XMLManager.update_recipe()"""

    def test_update_existing_recipe(self, mock_resource_path, mock_qmessagebox):
        """Test updating an existing recipe."""
        updated_recipe = {
            "Name": "Updated Recipe 1",
            "FilmMode": "Bleach Bypass",
            "Saturation": "+3 (very high)"
        }

        result = XMLManager.update_recipe(updated_recipe, original_name="Test Recipe 1")
        assert result is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert "Updated Recipe 1" in recipes
        assert recipes["Updated Recipe 1"]["FilmMode"] == "Bleach Bypass"

    def test_update_recipe_keep_same_name(self, mock_resource_path, mock_qmessagebox):
        """Test updating a recipe without changing the name."""
        updated_recipe = {
            "Name": "Test Recipe 1",
            "FilmMode": "Pro Neg. Hi",
            "Saturation": "+2 (high)"
        }

        result = XMLManager.update_recipe(updated_recipe)
        assert result is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert recipes["Test Recipe 1"]["FilmMode"] == "Pro Neg. Hi"

    def test_update_nonexistent_recipe(self, mock_resource_path, mock_qmessagebox):
        """Test updating a non-existent recipe."""
        updated_recipe = {
            "Name": "Nonexistent",
            "FilmMode": "Astia"
        }

        result = XMLManager.update_recipe(updated_recipe, original_name="Nonexistent")
        assert result is False
        mock_qmessagebox.critical.assert_called()

    def test_update_preserves_other_recipes(self, mock_resource_path, mock_qmessagebox):
        """Test whether update doesn't change other recipes."""
        initial_recipes = XMLManager.load_simulations(Constants.XML_FILE)
        recipe2_before = initial_recipes["Test Recipe 2"].copy()

        updated_recipe = {
            "Name": "Test Recipe 1",
            "FilmMode": "Astia"
        }

        XMLManager.update_recipe(updated_recipe)

        updated_recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert updated_recipes["Test Recipe 2"] == recipe2_before

    def test_update_with_all_fields(self, mock_resource_path, mock_qmessagebox):
        """Test updating all fields."""
        updated_recipe = {
            "Name": "Test Recipe 1",
            "FilmMode": "Pro Neg. Std",
            "GrainEffectRoughness": "Strong",
            "GrainEffectSize": "Large",
            "Saturation": "+3 (very high)",
            "Sharpness": "+3",
            "Favourite": "Yes",
            "Description": "Updated description"
        }

        result = XMLManager.update_recipe(updated_recipe)
        assert result is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        recipe = recipes["Test Recipe 1"]
        assert recipe["FilmMode"] == "Pro Neg. Std"
        assert recipe["Favourite"] == "Yes"
        assert recipe["Description"] == "Updated description"


class TestDeleteRecipe:
    """Tests for XMLManager.delete_recipe()"""

    def test_delete_existing_recipe(self, mock_resource_path, mock_qmessagebox):
        """Test deleting an existing recipe."""
        result = XMLManager.delete_recipe("Test Recipe 1")
        assert result is True

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert "Test Recipe 1" not in recipes
        assert len(recipes) == 1

    def test_delete_all_recipes_one_by_one(self, mock_resource_path, mock_qmessagebox):
        """Test deleting all recipes sequentially."""
        XMLManager.delete_recipe("Test Recipe 1")
        XMLManager.delete_recipe("Test Recipe 2")

        recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert len(recipes) == 0

    def test_delete_nonexistent_recipe(self, mock_resource_path, mock_qmessagebox):
        """Test deleting a non-existent recipe."""
        result = XMLManager.delete_recipe("Nonexistent Recipe")
        assert result is False
        mock_qmessagebox.critical.assert_called()

    def test_delete_preserves_other_recipes(self, mock_resource_path, mock_qmessagebox):
        """Test whether deletion doesn't change other recipes."""
        initial_recipes = XMLManager.load_simulations(Constants.XML_FILE)
        recipe2_before = initial_recipes["Test Recipe 2"].copy()

        XMLManager.delete_recipe("Test Recipe 1")

        remaining_recipes = XMLManager.load_simulations(Constants.XML_FILE)
        assert remaining_recipes["Test Recipe 2"] == recipe2_before


class TestXMLIntegrity:
    """Tests for verifying XML file integrity."""

    def test_xml_remains_valid_after_add(self, mock_resource_path):
        """Test whether XML remains valid after adding a recipe."""
        XMLManager.add_recipe({"Name": "XML Test", "FilmMode": "Astia"})

        # XML should be parseable
        tree = ET.parse(mock_resource_path)
        root = tree.getroot()
        assert root.tag == "root"
        assert len(root.findall('profile')) > 0

    def test_xml_remains_valid_after_update(self, mock_resource_path):
        """Test whether XML remains valid after update."""
        XMLManager.update_recipe({"Name": "Test Recipe 1", "FilmMode": "Updated"})

        tree = ET.parse(mock_resource_path)
        root = tree.getroot()
        assert root.tag == "root"

    def test_xml_remains_valid_after_delete(self, mock_resource_path):
        """Test whether XML remains valid after deletion."""
        XMLManager.delete_recipe("Test Recipe 1")

        tree = ET.parse(mock_resource_path)
        root = tree.getroot()
        assert root.tag == "root"


class TestErrorHandling:
    """Tests for error handling."""

    def test_add_recipe_handles_corrupted_xml(self, monkeypatch, mock_qmessagebox):
        """Test error handling with corrupted XML."""
        def mock_path(filename):
            return "/tmp/definitely_not_existing_file_12345.xml"

        monkeypatch.setattr('managers.xml_manager.resource_path', mock_path)
        result = XMLManager.add_recipe({"Name": "Test"})

        # Should return False and call error dialog
        assert result is False
        mock_qmessagebox.critical.assert_called()

    def test_update_recipe_handles_corrupted_xml(self, monkeypatch, mock_qmessagebox):
        """Test error handling when updating corrupted XML."""
        def mock_path(filename):
            return "/tmp/definitely_not_existing_file_12345.xml"

        monkeypatch.setattr('managers.xml_manager.resource_path', mock_path)
        result = XMLManager.update_recipe({"Name": "Test"})

        assert result is False
        mock_qmessagebox.critical.assert_called()

    def test_delete_recipe_handles_corrupted_xml(self, monkeypatch, mock_qmessagebox):
        """Test error handling when deleting corrupted XML."""
        def mock_path(filename):
            return "/tmp/definitely_not_existing_file_12345.xml"

        monkeypatch.setattr('managers.xml_manager.resource_path', mock_path)
        result = XMLManager.delete_recipe("Test")

        assert result is False
        mock_qmessagebox.critical.assert_called()
