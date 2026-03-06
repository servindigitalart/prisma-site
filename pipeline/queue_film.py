#!/usr/bin/env python3
"""
Film Queue Utility
Simple wrapper to queue films by TMDB ID or title.

Usage:
    # Queue by TMDB ID directly (existing workflow)
    python pipeline/queue_film.py --id 601666

    # Queue by title (new workflow using search_tmdb internally)
    python pipeline/queue_film.py --title "Portrait of a Lady on Fire" --year 2019
    
    # Queue by title with auto-select first result
    python pipeline/queue_film.py --title "Mustang" --year 2015 --top
"""

import argparse
import sys
import subprocess
from pathlib import Path

SEARCH_SCRIPT = Path("pipeline/search_tmdb.py")


def queue_by_id(tmdb_id):
    """Queue a film by TMDB ID directly"""
    import json
    from pathlib import Path
    
    QUEUE_FILE = Path("pipeline/queue/films_to_ingest.json")
    
    # Load existing queue
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, "r") as f:
                queue = json.load(f)
                if not isinstance(queue, list):
                    queue = []
        except (json.JSONDecodeError, FileNotFoundError):
            queue = []
    else:
        queue = []
    
    # Add to queue (deduplicate)
    if tmdb_id not in queue:
        queue.append(tmdb_id)
        QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)
        print(f"✅ Queued: TMDB ID {tmdb_id}")
    else:
        print(f"ℹ️  Already queued: TMDB ID {tmdb_id}")


def queue_by_title(title, year=None, auto_top=False):
    """Queue a film by title using search_tmdb.py"""
    if not SEARCH_SCRIPT.exists():
        print(f"❌ Search script not found: {SEARCH_SCRIPT}")
        sys.exit(1)
    
    # Build command
    cmd = [sys.executable, str(SEARCH_SCRIPT), title, "--queue"]
    if year:
        cmd.extend(["--year", str(year)])
    if auto_top:
        cmd.append("--top")
    
    # Run search script
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Queue films for TMDB ingestion")
    parser.add_argument("--id", type=int, help="Queue by TMDB ID directly")
    parser.add_argument("--title", help="Queue by film title (uses search)")
    parser.add_argument("--year", type=int, help="Release year (for title search)")
    parser.add_argument("--top", action="store_true", help="Auto-select first result (for title search)")
    
    args = parser.parse_args()
    
    if args.id:
        queue_by_id(args.id)
    elif args.title:
        queue_by_title(args.title, args.year, args.top)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
