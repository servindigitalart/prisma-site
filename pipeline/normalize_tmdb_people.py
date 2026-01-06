#!/usr/bin/env python3
import json, sys
from pathlib import Path
from slugify import slugify

RAW_DIR = Path("pipeline/raw")
OUT_DIR = Path("pipeline/normalized/people")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def normalize(tmdb_id):
    raw_file = RAW_DIR / f"tmdb_{tmdb_id}.json"
    if not raw_file.exists():
        raise RuntimeError(f"RAW not found: {raw_file}")

    raw = json.loads(raw_file.read_text())
    movie = raw["movie"]
    credits = raw["credits"]

    people = {}

    def upsert_person(name, role, tmdb_pid=None):
        pid = f"person_{slugify(name)}"
        if pid not in people:
            people[pid] = {
                "id": pid,
                "name": name,
                "roles": set(),
                "works": [],
                "ids": {}
            }
        people[pid]["roles"].add(role)
        if tmdb_pid:
            people[pid]["ids"]["tmdb"] = tmdb_pid

    for p in credits.get("crew", []):
        job = p.get("job")
        name = p.get("name")
        if not name:
            continue
        if job == "Director":
            upsert_person(name, "director", p.get("id"))
        if job == "Director of Photography":
            upsert_person(name, "cinematography", p.get("id"))
        if job == "Writer":
            upsert_person(name, "writer", p.get("id"))

    for p in credits.get("cast", [])[:20]:
        name = p.get("name")
        if not name:
            continue
        upsert_person(name, "actor", p.get("id"))

    work_id = f"work_{slugify(movie['title'])}_{movie.get('release_date','')[:4]}"

    for person in people.values():
        person["roles"] = sorted(person["roles"])
        person["works"].append(work_id)

        out_file = OUT_DIR / f"{person['id']}.json"
        out_file.write_text(json.dumps(person, indent=2))

    print(f"NORMALIZED people → {len(people)} records")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: normalize_tmdb_people.py <tmdb_id>")
        sys.exit(1)
    normalize(sys.argv[1])
