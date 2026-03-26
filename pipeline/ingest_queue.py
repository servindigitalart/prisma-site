#!/usr/local/bin/python3
"""
Batch TMDB Queue Ingestion
Process all films in the queue and ingest their TMDB data.

Usage:
    python pipeline/ingest_queue.py              # Process entire queue
    python pipeline/ingest_queue.py --limit 5    # Process first 5 films
    python pipeline/ingest_queue.py --keep-queue # Don't clear queue after processing
"""

import os
import json
import sys
import argparse
import requests
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

TMDB_API = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")
QUEUE_FILE = Path("pipeline/queue/films_to_ingest.json")
RAW_DIR = Path("pipeline/raw")

if not API_KEY:
    raise RuntimeError("TMDB_API_KEY not set in .env.local")


def fetch(endpoint, params=None):
    """Make a request to TMDB API"""
    params = params or {}
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB_API}{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def ingest_movie(tmdb_id):
    """Ingest a single movie from TMDB"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        data = {
            "movie": fetch(f"/movie/{tmdb_id}"),
            "credits": fetch(f"/movie/{tmdb_id}/credits"),
            "videos": fetch(f"/movie/{tmdb_id}/videos"),
            "keywords": fetch(f"/movie/{tmdb_id}/keywords"),
            "watch_providers": fetch(f"/movie/{tmdb_id}/watch/providers"),
        }
        
        out_file = RAW_DIR / f"tmdb_{tmdb_id}.json"
        with open(out_file, "w") as f:
            json.dump(data, f, indent=2)
        
        title = data["movie"].get("title", "Unknown")
        year = data["movie"].get("release_date", "")[:4]
        print(f"  ✅ {title} ({year}) → {out_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to ingest TMDB ID {tmdb_id}: {e}")
        return False


def load_queue():
    """Load the current queue"""
    if not QUEUE_FILE.exists():
        return []
    
    try:
        with open(QUEUE_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def clear_queue():
    """Clear the queue"""
    if QUEUE_FILE.exists():
        QUEUE_FILE.unlink()


def main():
    parser = argparse.ArgumentParser(description="Ingest all films from the queue")
    parser.add_argument("--limit", type=int, help="Limit number of films to process")
    parser.add_argument("--keep-queue", action="store_true", help="Don't clear queue after processing")
    
    args = parser.parse_args()
    
    queue = load_queue()
    
    if not queue:
        print("📋 Queue is empty. Nothing to process.")
        sys.exit(0)
    
    to_process = queue[:args.limit] if args.limit else queue
    
    print(f"🎬 Processing {len(to_process)} film(s) from queue...\n")
    
    success_count = 0
    for tmdb_id in to_process:
        if ingest_movie(tmdb_id):
            success_count += 1
    
    print(f"\n✨ Completed: {success_count}/{len(to_process)} films ingested successfully")
    
    if not args.keep_queue:
        clear_queue()
        print("🗑️  Queue cleared.")
    else:
        print("ℹ️  Queue preserved (--keep-queue flag set)")


if __name__ == "__main__":
    main()
