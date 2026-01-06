#!/usr/bin/env python3
import json, sys
from pathlib import Path
from slugify import slugify

RAW_DIR = Path("pipeline/raw")
OUT_DIR = Path("pipeline/normalized/works")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def normalize(tmdb_id):
    raw_file = RAW_DIR / f"tmdb_{tmdb_id}.json"
    if not raw_file.exists():
        raise RuntimeError(f"RAW not found: {raw_file}")

    raw = json.loads(raw_file.read_text())
    movie = raw["movie"]
    credits = raw["credits"]

    year = movie.get("release_date", "")[:4]
    work_id = f"work_{slugify(movie['title'])}_{year}"

    work = {
        "id": work_id,
        "type": "film",
        "title": movie["title"],
        "original_title": movie.get("original_title"),
        "year": int(year) if year.isdigit() else None,
        "duration_min": movie.get("runtime"),
        "countries": [c["iso_3166_1"] for c in movie.get("production_countries", [])],
        "languages": [l["iso_639_1"] for l in movie.get("spoken_languages", [])],
        "ids": {
            "tmdb": movie["id"],
            "imdb": movie.get("imdb_id")
        },
        "genres": [g["name"] for g in movie.get("genres", [])],
        "studios": [],
        "people": {
            "director": [],
            "cinematography": [],
            "writer": [],
            "cast": []
        }
    }

    for c in movie.get("production_companies", []):
        work["studios"].append(f"studio_{slugify(c['name'])}")

    for person in credits.get("crew", []):
        job = person.get("job")
        pid = f"person_{slugify(person['name'])}"
        if job == "Director":
            work["people"]["director"].append(pid)
        if job == "Director of Photography":
            work["people"]["cinematography"].append(pid)
        if job == "Writer":
            work["people"]["writer"].append(pid)

    for actor in credits.get("cast", [])[:10]:
        work["people"]["cast"].append(f"person_{slugify(actor['name'])}")

    out_file = OUT_DIR / f"{work_id}.json"
    out_file.write_text(json.dumps(work, indent=2))

    print(f"NORMALIZED work → {out_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: normalize_tmdb_work.py <tmdb_id>")
        sys.exit(1)
    normalize(sys.argv[1])
