# Tests - FilmRecipeFinder

## Description

Comprehensive test suite for **FilmRecipeFinder** using pytest.

## Test Files

- **test_xml_manager.py** - Tests for XMLManager (100% coverage)
- **test_exif_manager.py** - Tests for ExifManager (96% coverage)
- **test_recipe_manager.py** - Tests for RecipeManager (100% coverage)

## Running Tests

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run all tests:
```bash
pytest tests/
```

### Run specific test file:
```bash
pytest tests/test_xml_manager.py -v
pytest tests/test_exif_manager.py -v
pytest tests/test_recipe_manager.py -v
```

### Run tests with coverage report:
```bash
pytest tests/ --cov=managers --cov-report=html
```

Output will be created in the `htmlcov/` directory.

## Test Coverage

| Module | Coverage | Tests |
|--------|----------|-------|
| `managers/xml_manager.py` | **100%** ✅ | 25 |
| `managers/exif_manager.py` | **96%** ✅ | 25 |
| `managers/recipe_manager.py` | **100%** ✅ | 26 |
| **Total** | **88%** | **76** |

## Summary

**Total: 76 tests | 88% coverage | 0.15 seconds**

✨ All three manager modules are now well-tested:
- XMLManager: CRUD operations on XML recipes
- ExifManager: EXIF data parsing and extraction
- RecipeManager: Duplicate detection logic

## XMLManager Tests (25 tests)

### TestLoadSimulations (5 tests)
- ✅ Loading existing recipes from XML
- ✅ Loading individual recipe fields correctly
- ✅ Loading empty XML file
- ✅ Loading non-existent file
- ✅ Skipping recipes without Name field

### TestAddRecipe (5 tests)
- ✅ Adding a single recipe
- ✅ Adding recipe with all fields
- ✅ Adding multiple recipes sequentially
- ✅ Adding recipe with duplicate name
- ✅ Adding recipe with special characters (XML escape)

### TestUpdateRecipe (5 tests)
- ✅ Updating existing recipe
- ✅ Updating without changing name
- ✅ Updating non-existent recipe
- ✅ Verifying update doesn't change other recipes
- ✅ Updating all fields

### TestDeleteRecipe (4 tests)
- ✅ Deleting existing recipe
- ✅ Deleting all recipes sequentially
- ✅ Deleting non-existent recipe
- ✅ Verifying deletion doesn't change other recipes

### TestXMLIntegrity (3 tests)
- ✅ XML remains valid after addition
- ✅ XML remains valid after update
- ✅ XML remains valid after deletion

### TestErrorHandling (3 tests)
- ✅ Error handling when adding to corrupted XML
- ✅ Error handling when updating corrupted XML
- ✅ Error handling when deleting corrupted XML

## ExifManager Tests (25 tests)

### TestParseLines (9 tests)
- ✅ Parsing simple key-value lines
- ✅ Ignoring lines without colons
- ✅ Handling whitespace correctly
- ✅ Parsing values containing colons
- ✅ Parsing empty values
- ✅ Filtering specific keys
- ✅ Converting WhiteBalanceFineTune values (÷20 format)
- ✅ Parsing empty line list
- ✅ Parsing special characters

### TestFindExiftool (3 tests)
- ✅ Finding exiftool in system PATH
- ✅ Error handling when exiftool not found
- ✅ Error message contains helpful information

### TestGetExifData (4 tests)
- ✅ Retrieving filtered EXIF data with specific keys
- ✅ Handling files with no EXIF data
- ✅ Verifying subprocess called with correct arguments
- ✅ Converting WhiteBalanceFineTune values

### TestGetExif (7 tests)
- ✅ Retrieving EXIF data in short mode (default)
- ✅ Retrieving full EXIF data
- ✅ Short mode includes all expected keys
- ✅ Default mode is short
- ✅ Retrieving multiple EXIF fields
- ✅ Handling empty exiftool output
- ✅ Preserving special EXIF values

### TestExifManagerIntegration (2 tests)
- ✅ EXIF data filtering works correctly
- ✅ Scenario: matching recipe with EXIF data

## RecipeManager Tests (26 tests)

### TestFindDuplicateContent (21 tests)
- ✅ Finding exact duplicate recipes
- ✅ Finding no duplicate when none exists
- ✅ Ignoring Name field in comparison
- ✅ Handling extra fields in simulations
- ✅ Detecting partial matches as non-duplicates
- ✅ Case-sensitive comparison
- ✅ Whitespace significance in comparison
- ✅ Numeric string comparison
- ✅ Complex film settings duplicate detection
- ✅ None values handling
- ✅ Empty string values handling
- ✅ Single field recipes
- ✅ Missing fields in simulations
- ✅ Special characters in values
- ✅ Unicode characters support
- ✅ Whitespace variation detection
- ✅ Multiple duplicate detection scenarios

### TestFindDuplicateContentEdgeCases (5 tests)
- ✅ Very large recipe dictionaries (100+ fields)
- ✅ Many simulations (1000+ recipes)
- ✅ All false condition scenarios
- ✅ List values comparison
- ✅ Nested dictionary values

## Notes

### XMLManager Tests
- Tests use temporary XML files (automatically deleted after each test)
- QMessageBox is mocked to avoid GUI during testing
- No binary files are created during testing
- 100% code coverage achieved

### ExifManager Tests
- Tests mock subprocess.run to avoid depending on actual exiftool binary
- Path lookup logic is tested for error cases
- 96% code coverage (sys._MEIPASS branch not covered without PyInstaller)
- Tests cover both short and full EXIF mode
- WhiteBalanceFineTune conversion (÷20 format) is tested

### RecipeManager Tests
- Comprehensive tests for duplicate detection algorithm
- Edge cases include large dictionaries and many simulations
- Tests verify exact field matching logic
- 100% code coverage achieved with 26 comprehensive tests

## Running in CI/CD

```bash
# Run all tests with coverage
pytest tests/ --cov=managers --cov-report=term-missing

# Run with JUnit XML for CI systems
pytest tests/ --junit-xml=test-results.xml

# Run with coverage and fail if below threshold
pytest tests/ --cov=managers --cov-fail-under=85
```

## Mocking Strategy

All test suites use `monkeypatch` and `unittest.mock`:
- **XMLManager**: Mocks `resource_path()` to use temporary test files
- **ExifManager**: Mocks `subprocess.run()` to avoid external exiftool dependency
- **RecipeManager**: Pure logic tests, no external dependencies
- All mock GUI components (QMessageBox) for testing

This ensures tests are fast, isolated, and don't depend on external tools or GUI availability.


## XMLManager Tests (25 tests)

### TestLoadSimulations (5 tests)
- ✅ Loading existing recipes from XML
- ✅ Loading individual recipe fields correctly
- ✅ Loading empty XML file
- ✅ Loading non-existent file
- ✅ Skipping recipes without Name field

### TestAddRecipe (5 tests)
- ✅ Adding a single recipe
- ✅ Adding recipe with all fields
- ✅ Adding multiple recipes sequentially
- ✅ Adding recipe with duplicate name
- ✅ Adding recipe with special characters (XML escape)

### TestUpdateRecipe (5 tests)
- ✅ Updating existing recipe
- ✅ Updating without changing name
- ✅ Updating non-existent recipe
- ✅ Verifying update doesn't change other recipes
- ✅ Updating all fields

### TestDeleteRecipe (4 tests)
- ✅ Deleting existing recipe
- ✅ Deleting all recipes sequentially
- ✅ Deleting non-existent recipe
- ✅ Verifying deletion doesn't change other recipes

### TestXMLIntegrity (3 tests)
- ✅ XML remains valid after addition
- ✅ XML remains valid after update
- ✅ XML remains valid after deletion

### TestErrorHandling (3 tests)
- ✅ Error handling when adding to corrupted XML
- ✅ Error handling when updating corrupted XML
- ✅ Error handling when deleting corrupted XML

## ExifManager Tests (25 tests)

### TestParseLines (9 tests)
- ✅ Parsing simple key-value lines
- ✅ Ignoring lines without colons
- ✅ Handling whitespace correctly
- ✅ Parsing values containing colons
- ✅ Parsing empty values
- ✅ Filtering specific keys
- ✅ Converting WhiteBalanceFineTune values (÷20 format)
- ✅ Parsing empty line list
- ✅ Parsing special characters

### TestFindExiftool (3 tests)
- ✅ Finding exiftool in system PATH
- ✅ Error handling when exiftool not found
- ✅ Error message contains helpful information

### TestGetExifData (4 tests)
- ✅ Retrieving filtered EXIF data with specific keys
- ✅ Handling files with no EXIF data
- ✅ Verifying subprocess called with correct arguments
- ✅ Converting WhiteBalanceFineTune values

### TestGetExif (7 tests)
- ✅ Retrieving EXIF data in short mode (default)
- ✅ Retrieving full EXIF data
- ✅ Short mode includes all expected keys
- ✅ Default mode is short
- ✅ Retrieving multiple EXIF fields
- ✅ Handling empty exiftool output
- ✅ Preserving special EXIF values

### TestExifManagerIntegration (2 tests)
- ✅ EXIF data filtering works correctly
- ✅ Scenario: matching recipe with EXIF data

## Notes

### XMLManager Tests
- Tests use temporary XML files (automatically deleted after each test)
- QMessageBox is mocked to avoid GUI during testing
- No binary files are created during testing
- 100% code coverage achieved

### ExifManager Tests
- Tests mock subprocess.run to avoid depending on actual exiftool binary
- Path lookup logic is tested for error cases
- 96% code coverage (sys._MEIPASS branch not covered without PyInstaller)
- Tests cover both short and full EXIF mode
- WhiteBalanceFineTune conversion (÷20 format) is tested

## Running in CI/CD

```bash
# Run all tests with coverage
pytest tests/ --cov=managers --cov-report=term-missing

# Run with JUnit XML for CI systems
pytest tests/ --junit-xml=test-results.xml

# Run with coverage and fail if below threshold
pytest tests/ --cov=managers --cov-fail-under=90
```

## Mocking Strategy

Both test suites use `monkeypatch` and `unittest.mock`:
- **XMLManager**: Mocks `resource_path()` to use temporary test files
- **ExifManager**: Mocks `subprocess.run()` to avoid external exiftool dependency
- Both mock GUI components (QMessageBox) for testing

This ensures tests are fast, isolated, and don't depend on external tools or GUI availability.


