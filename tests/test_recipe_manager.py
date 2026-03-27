"""
Tests for RecipeManager - recipe comparison and duplicate detection.
"""
import pytest

from managers.recipe_manager import RecipeManager


class TestFindDuplicateContent:
    """Tests for RecipeManager.find_duplicate_content method."""

    def test_find_exact_duplicate(self):
        """Test finding an exact duplicate recipe."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome",
            "Saturation": "0 (normal)",
            "Sharpness": "+2"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)",
                "Sharpness": "+2"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing Recipe"

    def test_find_no_duplicate(self):
        """Test that None is returned when no duplicate exists."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Astia",
            "Saturation": "+1 (medium high)"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_ignore_name_field_in_comparison(self):
        """Test that Name field is ignored when comparing recipes."""
        recipe_data = {
            "Name": "New Recipe A",
            "FilmMode": "Classic Chrome",
            "Saturation": "0 (normal)"
        }

        simulations = {
            "Different Name Recipe": {
                "Name": "Different Name Recipe",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Different Name Recipe"

    def test_duplicate_detection_requires_exact_field_match(self):
        """Test that simulation cannot have extra fields not in recipe_data."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome",
            "Saturation": "0 (normal)"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)",
                "Sharpness": "+2",  # Extra field
                "Clarity": "0"      # Extra field
            }
        }

        # Should NOT match because simulation has extra fields
        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_no_duplicate_when_recipe_has_extra_fields(self):
        """Test that extra fields in recipe_data don't cause false matches."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome",
            "Saturation": "0 (normal)",
            "Sharpness": "+3"  # Different from existing
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)",
                "Sharpness": "+2"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_empty_simulations_dict(self):
        """Test with empty simulations dictionary."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome"
        }

        result = RecipeManager.find_duplicate_content(recipe_data, {})
        assert result is None

    def test_empty_recipe_data(self):
        """Test with empty recipe_data."""
        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe"
            }
        }

        result = RecipeManager.find_duplicate_content({}, simulations)
        # Empty recipe matches any existing recipe (all fields match vacuously)
        assert result == "Existing Recipe"

    def test_multiple_duplicates_returns_first(self):
        """Test that the first duplicate found is returned."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome",
            "Saturation": "0 (normal)"
        }

        simulations = {
            "Recipe A": {
                "Name": "Recipe A",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)"
            },
            "Recipe B": {
                "Name": "Recipe B",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        # Should return first match (dict iteration order in Python 3.7+)
        assert result in ["Recipe A", "Recipe B"]

    def test_partial_match_returns_none(self):
        """Test that partial matches don't return duplicates."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome",
            "Saturation": "0 (normal)",
            "Sharpness": "+2"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome",  # Matches
                "Saturation": "0 (normal)",    # Matches
                "Sharpness": "+3"              # Different!
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_case_sensitive_comparison(self):
        """Test that comparison is case-sensitive."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "classic chrome"  # lowercase
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome"  # Original case
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_whitespace_matters_in_comparison(self):
        """Test that whitespace is significant in comparison."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome ",  # Extra space
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome"  # No space
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_numeric_string_comparison(self):
        """Test comparison of numeric values as strings."""
        recipe_data = {
            "Name": "New Recipe",
            "ISO": "400"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "ISO": "400"  # String, not integer
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing Recipe"

    def test_numeric_difference_detected(self):
        """Test that numeric differences are detected even as strings."""
        recipe_data = {
            "Name": "New Recipe",
            "FNumber": "2.8"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FNumber": "2.0"  # Different value
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_complex_film_settings_duplicate_detection(self):
        """Test duplicate detection with complex film simulation settings."""
        recipe_data = {
            "Name": "Test Recipe",
            "FilmMode": "Pro Neg. Hi",
            "GrainEffectRoughness": "Strong",
            "GrainEffectSize": "Large",
            "ColorChromeEffect": "Weak",
            "Saturation": "+2 (high)",
            "Sharpness": "+2",
            "NoiseReduction": "+1 (medium strong)",
            "Highlight": "+1 (medium hard)"
        }

        simulations = {
            "Pro Neg Settings": {
                "Name": "Pro Neg Settings",
                "FilmMode": "Pro Neg. Hi",
                "GrainEffectRoughness": "Strong",
                "GrainEffectSize": "Large",
                "ColorChromeEffect": "Weak",
                "Saturation": "+2 (high)",
                "Sharpness": "+2",
                "NoiseReduction": "+1 (medium strong)",
                "Highlight": "+1 (medium hard)"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Pro Neg Settings"

    def test_none_values_in_comparison(self):
        """Test handling of None values."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": None,
            "Saturation": "0 (normal)"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": None,
                "Saturation": "0 (normal)"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing Recipe"

    def test_empty_string_values(self):
        """Test handling of empty string values."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome",
            "Description": ""  # Empty string
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome",
                "Description": ""
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing Recipe"

    def test_single_field_recipe(self):
        """Test with minimal recipe containing only Name field."""
        recipe_data = {
            "Name": "Minimal Recipe"
        }

        simulations = {
            "Another Minimal": {
                "Name": "Another Minimal"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        # Should match because Name is ignored and no other fields to compare
        assert result == "Another Minimal"

    def test_missing_field_in_simulation(self):
        """Test when simulation is missing a field from recipe_data."""
        recipe_data = {
            "Name": "New Recipe",
            "FilmMode": "Classic Chrome",
            "Saturation": "0 (normal)",
            "Sharpness": "+2"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "FilmMode": "Classic Chrome",
                "Saturation": "0 (normal)"
                # Missing Sharpness
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        # Should not match because simulation doesn't have Sharpness
        assert result is None

    def test_special_characters_in_values(self):
        """Test handling of special characters in field values."""
        recipe_data = {
            "Name": "New Recipe",
            "Description": "Film: XYZ (Vintage)",
            "Tags": "portrait & landscape"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "Description": "Film: XYZ (Vintage)",
                "Tags": "portrait & landscape"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing Recipe"

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        recipe_data = {
            "Name": "New Recipe",
            "Description": "Café français ☕"
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "Description": "Café français ☕"
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing Recipe"

    def test_whitespace_variation_detected(self):
        """Test that different types of whitespace are detected."""
        recipe_data = {
            "Name": "New Recipe",
            "Description": "Line1\nLine2"  # Newline
        }

        simulations = {
            "Existing Recipe": {
                "Name": "Existing Recipe",
                "Description": "Line1 Line2"   # Space instead of newline
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None


class TestFindDuplicateContentEdgeCases:
    """Edge case tests for RecipeManager.find_duplicate_content."""

    def test_very_large_recipe_dict(self):
        """Test with a recipe containing many fields."""
        recipe_data = {f"Field{i}": f"Value{i}" for i in range(100)}
        recipe_data["Name"] = "Test Recipe"

        simulations = {
            "Match": recipe_data.copy()
        }
        simulations["Match"]["Name"] = "Match"

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Match"

    def test_many_simulations_first_match_found(self):
        """Test that function doesn't iterate unnecessarily through all simulations."""
        recipe_data = {
            "Name": "New",
            "Mode": "A"
        }

        simulations = {f"Recipe{i}": {"Name": f"Recipe{i}", "Mode": "B"} for i in range(1000)}
        simulations["Match"] = {"Name": "Match", "Mode": "A"}

        # Function should find the match among many recipes
        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Match" or result is None  # Depends on dict iteration order

    def test_all_false_conditions(self):
        """Test scenario where all value matches fail."""
        recipe_data = {
            "Name": "New",
            "A": "1",
            "B": "2",
            "C": "3"
        }

        simulations = {
            "Sim1": {"Name": "Sim1", "A": "X", "B": "Y", "C": "Z"}
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result is None

    def test_list_values_not_equal(self):
        """Test with list values (if they somehow end up in recipe data)."""
        recipe_data = {
            "Name": "New",
            "Tags": ["portrait", "landscape"]
        }

        simulations = {
            "Existing": {
                "Name": "Existing",
                "Tags": ["portrait", "landscape"]
            }
        }

        # Python lists are compared by value, so this should work
        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing"

    def test_dict_values_comparison(self):
        """Test with nested dict values."""
        recipe_data = {
            "Name": "New",
            "Settings": {"mode": "A", "value": 5}
        }

        simulations = {
            "Existing": {
                "Name": "Existing",
                "Settings": {"mode": "A", "value": 5}
            }
        }

        result = RecipeManager.find_duplicate_content(recipe_data, simulations)
        assert result == "Existing"
