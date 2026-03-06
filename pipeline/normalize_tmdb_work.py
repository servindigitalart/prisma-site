#!/usr/bin/env python3
import json, sys
from pathlib import Path
from slugify import slugify

RAW_DIR = Path("pipeline/raw")
OUT_DIR = Path("pipeline/normalized/works")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _find_trailer_key(videos: list) -> str | None:
    """Return the YouTube key of the first official trailer, or None."""
    for v in videos:
        if v.get("type") == "Trailer" and v.get("site") == "YouTube" and v.get("official", True):
            return v.get("key")
    # Fallback: any trailer on YouTube
    for v in videos:
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
            return v.get("key")
    return None


def _extract_watch_providers(raw_providers: dict) -> dict:
    """
    Transform TMDB watch/providers response into a clean dict.
    Output: { "US": { "flatrate": ["Netflix", ...], "rent": [...], "buy": [...] }, ... }
    Only includes countries that have at least one provider.
    """
    results = raw_providers.get("results", {})
    out: dict = {}
    for country, data in results.items():
        entry: dict = {}
        for mode in ("flatrate", "rent", "buy", "free"):
            providers = data.get(mode, [])
            if providers:
                entry[mode] = [p["provider_name"] for p in providers]
        if entry:
            out[country] = entry
    return out


def normalize(tmdb_id):
    raw_file = RAW_DIR / f"tmdb_{tmdb_id}.json"
    if not raw_file.exists():
        raise RuntimeError(f"RAW not found: {raw_file}")

    raw = json.loads(raw_file.read_text())
    movie = raw["movie"]
    credits = raw["credits"]
    videos = raw.get("videos", {}).get("results", [])
    watch_providers_raw = raw.get("watch_providers", {})

    year = movie.get("release_date", "")[:4]
    work_id = f"work_{slugify(movie['title'])}_{year}"

    work = {
        "id": work_id,
        "type": "film",
        "title": movie["title"],
        "original_title": movie.get("original_title"),
        "year": int(year) if year.isdigit() else None,
        "duration_min": movie.get("runtime"),
        "synopsis": movie.get("overview") or None,
        "tagline": movie.get("tagline") or None,
        "countries": [c["iso_3166_1"] for c in movie.get("production_countries", [])],
        "languages": [l["iso_639_1"] for l in movie.get("spoken_languages", [])],
        "ids": {
            "tmdb": movie["id"],
            "imdb": movie.get("imdb_id"),
        },
        "genres": [g["name"] for g in movie.get("genres", [])],
        "tmdb_popularity": movie.get("popularity"),
        "media": {
            "poster_path": movie.get("poster_path"),
            "backdrop_path": movie.get("backdrop_path"),
            "trailer_key": _find_trailer_key(videos),
        },
        "where_to_watch": _extract_watch_providers(watch_providers_raw),
        "studios": [],
        "people": {
            "director": [],
            "cinematography": [],
            "writer": [],
            "editor": [],
            "composer": [],
            "cast": [],
        },
        # Fields populated by pipeline phases 2A–3
        "prisma_palette": None,
    }

    for c in movie.get("production_companies", []):
        work["studios"].append(f"studio_{slugify(c['name'])}")

    for person in credits.get("crew", []):
        job = person.get("job", "")
        dept = person.get("department", "")
        pid = f"person_{slugify(person['name'])}"
        if job == "Director":
            work["people"]["director"].append(pid)
        elif job == "Director of Photography":
            work["people"]["cinematography"].append(pid)
        elif job in ("Writer", "Screenplay", "Story"):
            if pid not in work["people"]["writer"]:
                work["people"]["writer"].append(pid)
        elif dept == "Editing" and job in ("Editor", "Film Editor"):
            work["people"]["editor"].append(pid)
        elif dept == "Sound" and "Composer" in job:
            work["people"]["composer"].append(pid)

    for actor in credits.get("cast", [])[:10]:
        work["people"]["cast"].append(f"person_{slugify(actor['name'])}")

    out_file = OUT_DIR / f"{work_id}.json"
    out_file.write_text(json.dumps(work, indent=2))

    print(f"NORMALIZED work → {out_file}")
    return work_id, work


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: normalize_tmdb_work.py <tmdb_id>")
        print("       normalize_tmdb_work.py pipeline/raw/tmdb_843796.json  (path also accepted)")
        sys.exit(1)
    arg = sys.argv[1]
    # Accept either a TMDB ID integer or a raw file path like pipeline/raw/tmdb_843796.json
    if arg.endswith(".json"):
        import re as _re
        m = _re.search(r"tmdb_(\d+)\.json$", arg)
        if not m:
            print(f"Cannot extract TMDB ID from path: {arg}")
            sys.exit(1)
        tmdb_id = m.group(1)
    else:
        tmdb_id = arg
    normalize(tmdb_id)
