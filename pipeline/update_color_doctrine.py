#!/usr/local/bin/python3
"""
Script to add 3 new colors to color_doctrine.json
Run from prisma-site root directory.
"""
import json
from datetime import date

DOCTRINE_PATH = "pipeline/doctrine/current/color_doctrine.json"

NEW_COLORS = [
    {
        "id": "blanco_polar",
        "hex": "#E8EEF2",
        "name": "Blanco Polar",
        "moods": ["isolation", "void", "clinical", "existential", "minimalism"],
        "genre_associations": ["arthouse", "thriller", "drama", "psychological_horror"],
        "cinematographer_signatures": ["Sven Nykvist", "Edward Lachman"],
        "reference_examples": ["Three Colors: White", "Fargo"],
        "cultural_context": "Moral void, institutional coldness, existential emptiness, winter isolation",
        "cinematographic_notes": "Cold white environments suggesting absence, clinical detachment, or blankness of extreme moral situations"
    },
    {
        "id": "negro_abismo",
        "hex": "#0A0A0F",
        "name": "Negro Abismo",
        "moods": ["darkness", "gothic", "void", "power", "menace"],
        "genre_associations": ["superhero", "noir", "gothic", "thriller"],
        "cinematographer_signatures": ["Gordon Willis", "Bruno Delbonnel"],
        "reference_examples": ["Batman (1989)", "Se7en"],
        "cultural_context": "Gotham darkness, gothic menace, total visual void, noir extremity",
        "cinematographic_notes": "Near-total darkness as aesthetic choice, silhouettes, gothic architecture consumed by shadow"
    },
    {
        "id": "titanio_mecanico",
        "hex": "#8A9199",
        "name": "Titanio Mecánico",
        "moods": ["mechanical", "cold_future", "industrial", "artificial", "inhuman"],
        "genre_associations": ["sci_fi", "dystopia", "cyberpunk", "action"],
        "cinematographer_signatures": ["Douglas Trumbull", "Roger Deakins"],
        "reference_examples": ["Terminator 2", "2001: A Space Odyssey", "Ex Machina"],
        "cultural_context": "Metal bodies, spacecraft interiors, artificial intelligence, industrial dystopia",
        "cinematographic_notes": "Cold metallic grays of machines, robots, and spacecraft — technology as overwhelming physical presence"
    }
]

def update_doctrine():
    with open(DOCTRINE_PATH, 'r', encoding='utf-8') as f:
        doctrine = json.load(f)

    # Check for duplicates
    existing_ids = {c["id"] for c in doctrine["colors"]}
    for color in NEW_COLORS:
        if color["id"] in existing_ids:
            print(f"⚠️  {color['id']} already exists — skipping")
            continue
        doctrine["colors"].append(color)
        print(f"✅ Added {color['id']} ({color['hex']})")

    # Update version and date
    doctrine["version"] = "1.2"
    doctrine["last_updated"] = str(date.today())

    with open(DOCTRINE_PATH, 'w', encoding='utf-8') as f:
        json.dump(doctrine, f, indent=2, ensure_ascii=False)

    total = len(doctrine["colors"])
    print(f"\n✅ color_doctrine.json updated to v1.2")
    print(f"   Total colors: {total}")
    print(f"   New colors: blanco_polar, negro_abismo, titanio_mecanico")

if __name__ == "__main__":
    update_doctrine()
