# ──────────────────────────────────────────────
# XML MANAGER
# ──────────────────────────────────────────────
import os
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import QMessageBox

from constants import Constants
from utils import resource_path


class XMLManager:
    @staticmethod
    def load_simulations(filename):
        """Load recipes from the XML; values are stored in ÷20 format."""
        full_path = resource_path(filename)
        if not os.path.exists(full_path):
            return {}
        with open(full_path, 'r') as f:
            tree = ET.parse(f)
            root = tree.getroot()
        simulations = {}
        for profile in root.findall('profile'):
            name_el = profile.find('Name')
            if name_el is None:
                continue
            sim_name = name_el.text
            simulations[sim_name] = {}
            for param in profile.iter():
                if param.tag == 'profile':
                    continue
                simulations[sim_name][param.tag] = param.text or ""
        return simulations

    @staticmethod
    def add_recipe(recipe_data):
        """Add a recipe to the XML; WhiteBalanceFineTune is saved in ÷20 format."""
        xml_file = resource_path(Constants.XML_FILE)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            new_profile = ET.SubElement(root, 'profile')
            for key, value in recipe_data.items():
                elem = ET.SubElement(new_profile, key)
                elem.text = value
            ET.indent(tree, space="  ", level=0)
            tree.write(xml_file, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to add recipe: {e}")
            return False

    @staticmethod
    def update_recipe(recipe_data):
        """Update an existing recipe in the XML."""
        xml_file = resource_path(Constants.XML_FILE)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            recipe_name = recipe_data["Name"]
            profile_to_update = None
            for profile in root.findall('profile'):
                name_el = profile.find('Name')
                if name_el is not None and name_el.text == recipe_name:
                    profile_to_update = profile
                    break
            if profile_to_update is None:
                QMessageBox.critical(None, "Error", f"Recipe '{recipe_name}' not found!")
                return False
            profile_to_update.clear()
            for key, value in recipe_data.items():
                elem = ET.SubElement(profile_to_update, key)
                elem.text = value
            ET.indent(tree, space="  ", level=0)
            tree.write(xml_file, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update recipe: {e}")
            return False

    @staticmethod
    def delete_recipe(recipe_name):
        """Delete a recipe from the XML."""
        xml_file = resource_path(Constants.XML_FILE)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for profile in root.findall('profile'):
                name_el = profile.find('Name')
                if name_el is not None and name_el.text == recipe_name:
                    root.remove(profile)
                    ET.indent(tree, space="  ", level=0)
                    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
                    return True
            QMessageBox.critical(None, "Error", f"Recipe '{recipe_name}' not found!")
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to delete recipe: {e}")
            return False