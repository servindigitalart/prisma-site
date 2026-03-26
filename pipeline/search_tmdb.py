#!/usr/local/bin/python3
"""
TMDB Title Search Utility
Search for films by title and queue them for ingestion.

Usage:
    python pipeline/search_tmdb.py "Portrait of a Lady on Fire"
    python pipeline/search_tmdb.py "Dune" --year 2021
    python pipeline/search_tmdb.py "Blue" --year 1993 --queue
    python pipeline/search_tmdb.py "Mustang" --top
    python pipeline/search_tmdb.py --list
    python pipeline/search_tmdb.py --clear
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

if not API_KEY:
    raise RuntimeError("TMDB_API_KEY not set in .env.local")


def fetch(endpoint, params=None):
    """Make a request to TMDB API"""
    params = params or {}
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB_API}{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def get_director(movie_id):
    """Fetch director name from movie credits"""
    try:
        credits = fetch(f"/movie/{movie_id}/credits")
        crew = credits.get("crew", [])
        directors = [c["name"] for c in crew if c.get("job") == "Director"]
        return directors[0] if directors else "Unknown"
    except Exception:
        return "Unknown"


def search_movies(title, year=None):
    """Search TMDB for movies by title"""
    params = {"query": title, "language": "en-US"}
    if year:
        params["year"] = year
    
    results = fetch("/search/movie", params)
    return results.get("results", [])


def format_movie_result(movie, rank):
    """Format a movie search result for display"""
    title = movie.get("title", "Unknown")
    release_date = movie.get("release_date", "")
    year = release_date[:4] if release_date else "Unknown"
    tmdb_id = movie.get("id")
    popularity = movie.get("popularity", 0)
    
    # Get country from production_countries (requires detail fetch)
    try:
        details = fetch(f"/movie/{tmdb_id}")
        countries = details.get("production_countries", [])
        country = countries[0]["name"] if countries else "Unknown"
    except Exception:
        country = "Unknown"
    
    director = get_director(tmdb_id)
    
    return {
        "rank": rank,
        "title": title,
        "year": year,
        "country": country,
        "tmdb_id": tmdb_id,
        "director": director,
        "popularity": popularity
    }


def display_results(results):
    """Display search results"""
    seen_ids = set()
    unique_results = []
    
    for i, movie in enumerate(results[:3], 1):
        tmdb_id = movie.get("id")
        
        if tmdb_id in seen_ids:
            print(f"  {i}. {movie.get('title')} ({movie.get('release_date', '')[:4]}) — ID: {tmdb_id} [duplicate]")
            continue
        
        seen_ids.add(tmdb_id)
        formatted = format_movie_result(movie, i)
        unique_results.append(formatted)
        
        print(f"  {i}. {formatted['title']} ({formatted['year']}) — {formatted['country']} — ID: {formatted['tmdb_id']}")
        print(f"     Director: {formatted['director']} — TMDB popularity: {formatted['popularity']:.1f}")
    
    return unique_results


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


def save_queue(queue):
    """Save the queue to file"""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def add_to_queue(tmdb_id, title, year):
    """Add a TMDB ID to the queue"""
    queue = load_queue()
    
    # Deduplicate
    if tmdb_id not in queue:
        queue.append(tmdb_id)
        save_queue(queue)
        print(f"✅ Queued: work_{title.lower().replace(' ', '-')}_{year} (TMDB ID: {tmdb_id})")
    else:
        print(f"ℹ️  Already queued: TMDB ID {tmdb_id}")


def list_queue():
    """Display the current queue"""
    queue = load_queue()
    if not queue:
        print("Queue is empty.")
        return
    
    print(f"📋 Current queue ({len(queue)} films):")
    for tmdb_id in queue:
        print(f"  - TMDB ID: {tmdb_id}")


def clear_queue():
    """Clear the queue"""
    if QUEUE_FILE.exists():
        QUEUE_FILE.unlink()
    print("🗑️  Queue cleared.")


def main():
    parser = argparse.ArgumentParser(description="Search TMDB for films and queue for ingestion")
    parser.add_argument("title", nargs="?", help="Film title to search")
    parser.add_argument("--year", type=int, help="Release year for disambiguation")
    parser.add_argument("--queue", action="store_true", help="Skip confirmation and queue immediately")
    parser.add_argument("--top", action="store_true", help="Automatically select the first result")
    parser.add_argument("--list", action="store_true", help="Show current queue contents")
    parser.add_argument("--clear", action="store_true", help="Clear the queue")
    
    args = parser.parse_args()
    
    # Handle queue management commands
    if args.list:
        list_queue()
        return
    
    if args.clear:
        clear_queue()
        return
    
    # Require a title for search
    if not args.title:
        parser.print_help()
        sys.exit(1)
    
    # Search for the film
    year_str = f" ({args.year})" if args.year else ""
    print(f"🔍 Searching TMDB for: \"{args.title}\"{year_str}\n")
    
    results = search_movies(args.title, args.year)
    
    if not results:
        print(f"❌ No results found for \"{args.title}\"{year_str}")
        sys.exit(1)
    
    print("Results:")
    unique_results = display_results(results)
    
    if not unique_results:
        print("❌ No valid results found.")
        sys.exit(1)
    
    print(f"\nFound {len(unique_results)} result{'s' if len(unique_results) > 1 else ''}.")
    
    # Auto-select first result if --top flag
    if args.top:
        selected = unique_results[0]
        add_to_queue(selected["tmdb_id"], selected["title"], selected["year"])
        return
    
    # Skip confirmation if --queue flag
    if args.queue:
        if len(unique_results) == 1:
            selected = unique_results[0]
            add_to_queue(selected["tmdb_id"], selected["title"], selected["year"])
            return
        else:
            print("⚠️  Multiple results found. Please specify which one to queue:")
            choice = input("Enter result number (1-3) or 'n' to cancel: ").strip()
            if choice.lower() == 'n':
                print("Cancelled.")
                return
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(unique_results):
                    selected = unique_results[idx]
                    add_to_queue(selected["tmdb_id"], selected["title"], selected["year"])
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")
            return
    
    # Interactive confirmation
    if len(unique_results) == 1:
        choice = input("Queue this film? [y/n]: ").strip().lower()
        if choice == 'y':
            selected = unique_results[0]
            add_to_queue(selected["tmdb_id"], selected["title"], selected["year"])
        else:
            print("Cancelled.")
    else:
        choice = input("Enter result number to queue (1-3) or 'n' to cancel: ").strip()
        if choice.lower() == 'n':
            print("Cancelled.")
            return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(unique_results):
                selected = unique_results[idx]
                add_to_queue(selected["tmdb_id"], selected["title"], selected["year"])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


if __name__ == "__main__":
    main()
