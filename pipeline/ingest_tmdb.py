#!/usr/local/bin/python3
import os, json, sys, requests
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

TMDB_API = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise RuntimeError("TMDB_API_KEY not set")

def fetch(endpoint, params=None):
    params = params or {}
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB_API}{endpoint}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def ingest_movie(tmdb_id):
    out_dir = Path("pipeline/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "movie": fetch(f"/movie/{tmdb_id}"),
        "credits": fetch(f"/movie/{tmdb_id}/credits"),
        "videos": fetch(f"/movie/{tmdb_id}/videos"),
        "keywords": fetch(f"/movie/{tmdb_id}/keywords"),
        "watch_providers": fetch(f"/movie/{tmdb_id}/watch/providers"),
    }

    out_file = out_dir / f"tmdb_{tmdb_id}.json"
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"RAW saved → {out_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ingest_tmdb.py <tmdb_id>")
        sys.exit(1)
    ingest_movie(sys.argv[1])
