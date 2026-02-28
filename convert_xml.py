"""
Jednorazový skript na konverziu WhiteBalanceFineTune hodnôt v XML.
Vydelí všetky hodnoty číslom 20.

Napr. "Red +60, Blue -100"  ->  "Red +3, Blue -5"
      "Red +160, Blue -160" ->  "Red +8, Blue -8"

Spusti raz z koreňového adresára projektu:
    python convert_xml.py
"""

import re
import xml.etree.ElementTree as ET


XML_FILE = "film_simulations.xml"


def convert_value(raw):
    matches = re.findall(r'(Red|Blue)\s*([+-]?\d+)', raw)
    if not matches:
        return raw
    parts = []
    for name, val in matches:
        converted = int(val) // 20
        sign = "+" if converted >= 0 else ""
        parts.append(f"{name} {sign}{converted}")
    return ", ".join(parts)


def main():
    ET.register_namespace('', '')
    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    count = 0
    for profile in root.findall('profile'):
        wbft = profile.find('WhiteBalanceFineTune')
        if wbft is not None and wbft.text:
            original = wbft.text
            converted = convert_value(original)
            if original != converted:
                wbft.text = converted
                name = profile.findtext('Name', '?')
                print(f"  {name}: {original}  ->  {converted}")
                count += 1

    ET.indent(tree, space="  ", level=0)
    tree.write(XML_FILE, encoding='utf-8', xml_declaration=True)
    print(f"\nHotovo — upravených {count} profilov.")


if __name__ == "__main__":
    main()
