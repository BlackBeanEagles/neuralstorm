"""Collection point rules are deliberately separate from image recognition."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCATIONS_PATH = ROOT / "config" / "locations.json"


def load_locations() -> list[dict]:
    with LOCATIONS_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)["locations"]


def guidance(location_id: str, material: str, confirmed: bool = False) -> dict:
    location = next((x for x in load_locations() if x["id"] == location_id), None)
    if location is None:
        raise ValueError("Unknown collection point")
    item = location["materials"].get(material)
    if item is None:
        raise ValueError("Unknown material")
    bin_data = location["bins"][item["bin"]]
    source = location.get("source")
    return {
        "location": location["name"],
        "material": material,
        "bin": item["bin"],
        "bin_name": bin_data["name"],
        "bin_name_hi": bin_data.get("name_hi"),
        "bin_color": bin_data["color"],
        "bin_icon": bin_data["icon"],
        "instruction": item["instruction"],
        "instruction_hi": item.get("instruction_hi"),
        "confirmed_by_user": confirmed,
        "source": source,
        "disclaimer": (
            "This follows India's national waste-sorting rules. Your local authority decides the exact bin and collection method."
            if source
            else "These sample rules are for the demo collection point. Follow the signs at your actual location."
        ),
        "disclaimer_hi": (
            "यह भारत के राष्ट्रीय कचरा अलग करने के नियमों पर आधारित है। सही डिब्बा और संग्रह विधि स्थानीय निकाय तय करता है।"
            if source
            else None
        ),
    }
