#!/usr/local/bin/python3
import json, sys
from pathlib import Path
from slugify import slugify

RAW_DIR = Path("pipeline/raw")
OUT_DIR = Path("pipeline/normalized/studios")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def normalize(tmdb_id):
    raw_file = RAW_DIR / f"tmdb_{tmdb_id}.json"
    if not raw_file.exists():
        raise RuntimeError(f"RAW not found: {raw_file}")

    raw = json.loads(raw_file.read_text())
    movie = raw["movie"]

    year = movie.get("release_date", "")[:4]
    work_id = f"work_{slugify(movie['title'])}_{year}"

    studios = {}

    for s in movie.get("production_companies", []):
        name = s.get("name")
        if not name:
            continue

        sid = f"studio_{slugify(name)}"
        if sid not in studios:
            studios[sid] = {
                "id": sid,
                "name": name,
                "country": s.get("origin_country"),
                "works": [],
                "ids": {
                    "tmdb": s.get("id")
                }
            }

        studios[sid]["works"].append(work_id)

    for studio in studios.values():
        out_file = OUT_DIR / f"{studio['id']}.json"
        out_file.write_text(json.dumps(studio, indent=2))

    print(f"NORMALIZED studios → {len(studios)} records")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: normalize_tmdb_studios.py <tmdb_id>")
        sys.exit(1)
    normalize(sys.argv[1])
