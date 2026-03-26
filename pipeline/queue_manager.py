#!/usr/local/bin/python3
"""
Queue Manager — populate and manage pipeline/queue/pending.json

Usage:
    python pipeline/queue_manager.py --add-tmdb 44012
    python pipeline/queue_manager.py --add-list pipeline/sources/palme_dor_historical.txt --source palme_dor
    python pipeline/queue_manager.py --add-title "Portrait of a Lady on Fire" --year 2019
    python pipeline/queue_manager.py --status
    python pipeline/queue_manager.py --clear-failed
    python pipeline/queue_manager.py --deduplicate
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

import requests

BASE_DIR     = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
QUEUE_DIR    = PIPELINE_DIR / "queue"
PENDING_FILE   = QUEUE_DIR / "pending.json"
COMPLETED_FILE = QUEUE_DIR / "completed.json"
FAILED_FILE    = QUEUE_DIR / "failed.json"

TMDB_API = "https://api.themoviedb.org/3"
API_KEY  = os.getenv("TMDB_API_KEY")


# ─── Queue I/O ────────────────────────────────────────────────────────────────

def load_queue(file: Path) -> list[dict]:
    if not file.exists():
        return []
    try:
        data = json.loads(file.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_queue(file: Path, data: list[dict]) -> None:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def pending_tmdb_ids() -> set[int]:
    return {item["tmdb_id"] for item in load_queue(PENDING_FILE) if "tmdb_id" in item}


def completed_tmdb_ids() -> set[int]:
    return {item["tmdb_id"] for item in load_queue(COMPLETED_FILE) if "tmdb_id" in item}


# ─── Supabase work lookup ─────────────────────────────────────────────────────

def get_db_tmdb_ids() -> set[int]:
    """Return set of tmdb_ids already in Supabase works table."""
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            return set()
        db  = create_client(url, key)
        res = db.from_("works").select("tmdb_id").not_.is_("tmdb_id", "null").execute()
        return {r["tmdb_id"] for r in (res.data or []) if r.get("tmdb_id")}
    except Exception:
        return set()


# ─── TMDB helpers ─────────────────────────────────────────────────────────────

def tmdb_confirm(tmdb_id: int) -> tuple[str, str] | None:
    """Return (title, year) or None if not found."""
    try:
        r = requests.get(
            f"{TMDB_API}/movie/{tmdb_id}",
            params={"api_key": API_KEY},
            timeout=10,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        data = r.json()
        title = data.get("title", "?")
        year  = (data.get("release_date") or "")[:4] or "?"
        return title, year
    except Exception:
        return None


def tmdb_search(title: str, year: int | None = None) -> list[dict]:
    """Search TMDB by title. Returns list of {tmdb_id, title, year, popularity}."""
    params: dict = {"api_key": API_KEY, "query": title, "language": "en-US"}
    if year:
        params["year"] = year
    try:
        r = requests.get(f"{TMDB_API}/search/movie", params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        return [
            {
                "tmdb_id":    item["id"],
                "title":      item.get("title", "?"),
                "year":       (item.get("release_date") or "")[:4] or "?",
                "popularity": item.get("popularity", 0),
            }
            for item in results[:5]
        ]
    except Exception:
        return []


# ─── ID list parser ───────────────────────────────────────────────────────────

def parse_id_list(list_file: Path) -> list[int]:
    ids: list[int] = []
    with open(list_file) as f:
        for lineno, line in enumerate(f, 1):
            line = line.split("#")[0].strip()
            if not line:
                continue
            try:
                ids.append(int(line))
            except ValueError:
                print(f"  ⚠  Line {lineno}: '{line}' is not a valid ID — skipping")
    return ids


# ─── Add operations ───────────────────────────────────────────────────────────

def add_tmdb_id(tmdb_id: int, source: str = "manual") -> bool:
    """Add a single TMDB ID to pending queue. Returns True if added, False if duplicate."""
    pending = load_queue(PENDING_FILE)
    existing_ids = {item["tmdb_id"] for item in pending if "tmdb_id" in item}

    if tmdb_id in existing_ids:
        return False

    if tmdb_id in completed_tmdb_ids():
        print(f"  ↷  TMDB {tmdb_id} already completed — skipping")
        return False

    # Confirm with TMDB
    info = tmdb_confirm(tmdb_id)
    if not info:
        print(f"  ✗  TMDB {tmdb_id} not found on TMDB")
        return False

    title, year = info
    pending.append({
        "tmdb_id":  tmdb_id,
        "title":    title,
        "year":     year,
        "source":   source,
        "added_at": str(date.today()),
    })
    save_queue(PENDING_FILE, pending)
    print(f"  ✓  Queued: TMDB {tmdb_id}  — {title} ({year})  [{source}]")
    return True


# ─── Status ───────────────────────────────────────────────────────────────────

def print_status() -> None:
    pending   = load_queue(PENDING_FILE)
    completed = load_queue(COMPLETED_FILE)
    failed    = load_queue(FAILED_FILE)

    sources: dict[str, int] = {}
    for item in pending:
        src = item.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1

    days = len(pending) / 100 if pending else 0

    print("\nQueue Status — PRISMA")
    print("─────────────────────────────")
    print(f"Pending:  {len(pending):>5} films")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {src:<28} {count}")
    print(f"\nCompleted:{len(completed):>5} films")
    print(f"Failed:   {len(failed):>5} films", end="")
    if failed:
        print("  (run --clear-failed to retry)", end="")
    print()
    if days:
        print(f"\nEstimated time at 100/day: {days:.1f} days")
    print("─────────────────────────────\n")


# ─── Main ──────────────────────────────────────────────────────────────��──────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="PRISMA Queue Manager — populate and manage pending.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--add-tmdb", type=int, metavar="ID",
                        help="Add a single TMDB ID to the queue.")
    parser.add_argument("--add-list", metavar="FILE",
                        help="Add TMDB IDs from a text file (one per line).")
    parser.add_argument("--add-title", metavar="TITLE",
                        help="Search TMDB by title and add the best match.")
    parser.add_argument("--year", type=int, metavar="YEAR",
                        help="Year hint for --add-title search.")
    parser.add_argument("--source", default="manual", metavar="SRC",
                        help="Source label for this batch (e.g. palme_dor, letterboxd).")
    parser.add_argument("--status", action="store_true",
                        help="Show pending/completed/failed counts.")
    parser.add_argument("--clear-failed", action="store_true",
                        help="Move all failed entries back to pending for retry.")
    parser.add_argument("--deduplicate", action="store_true",
                        help="Remove IDs already in Supabase from pending queue.")
    parser.add_argument("--clear-source", metavar="SRC",
                        help="Remove all pending films from a specific source label.")

    args = parser.parse_args()

    if args.status:
        print_status()
        return 0

    if args.clear_failed:
        failed  = load_queue(FAILED_FILE)
        pending = load_queue(PENDING_FILE)
        existing_ids = {item["tmdb_id"] for item in pending if "tmdb_id" in item}
        moved = 0
        for item in failed:
            if item.get("tmdb_id") and item["tmdb_id"] not in existing_ids:
                pending.append({
                    "tmdb_id":  item["tmdb_id"],
                    "source":   item.get("source", "retry"),
                    "added_at": str(date.today()),
                })
                moved += 1
        save_queue(PENDING_FILE, pending)
        save_queue(FAILED_FILE, [])
        print(f"  ✓  Moved {moved} failed films back to pending.")
        return 0

    if args.clear_source:
        pending = load_queue(PENDING_FILE)
        before  = len(pending)
        pending = [item for item in pending if item.get("source") != args.clear_source]
        save_queue(PENDING_FILE, pending)
        removed = before - len(pending)
        print(f"  ✓  Removed {removed} films with source '{args.clear_source}' from pending queue.")
        return 0

    if args.deduplicate:
        print("  Fetching Supabase TMDB IDs…")
        db_ids  = get_db_tmdb_ids()
        pending = load_queue(PENDING_FILE)
        before  = len(pending)
        pending = [item for item in pending if item.get("tmdb_id") not in db_ids]
        after   = len(pending)
        save_queue(PENDING_FILE, pending)
        print(f"  ✓  Removed {before - after} films already in Supabase. {after} remain pending.")
        return 0

    if not API_KEY:
        print("\n  ✗ TMDB_API_KEY is not set.\n")
        return 1

    if args.add_tmdb:
        add_tmdb_id(args.add_tmdb, source=args.source)
        return 0

    if args.add_list:
        list_path = Path(args.add_list)
        if not list_path.exists():
            print(f"\n  ✗ File not found: {list_path}\n")
            return 1
        ids = parse_id_list(list_path)
        if not ids:
            print(f"\n  ✗ No valid TMDB IDs in {list_path}\n")
            return 1
        print(f"\n  Adding {len(ids)} films from {list_path.name}  (source: {args.source})\n")
        added = 0
        skipped = 0
        for tmdb_id in ids:
            if add_tmdb_id(tmdb_id, source=args.source):
                added += 1
            else:
                skipped += 1
        print(f"\n  ✓ {added} added, {skipped} skipped (duplicates/not found).\n")
        return 0

    if args.add_title:
        results = tmdb_search(args.add_title, year=args.year)
        if not results:
            print(f"\n  ✗ No results for '{args.add_title}'\n")
            return 1
        print(f"\n  Search results for '{args.add_title}':")
        for i, r in enumerate(results, 1):
            print(f"    {i}. {r['title']} ({r['year']}) — TMDB {r['tmdb_id']}  popularity={r['popularity']:.1f}")
        if len(results) == 1:
            choice = 1
        else:
            try:
                raw = input("\n  Select [1] or number: ").strip() or "1"
                choice = int(raw)
            except (ValueError, EOFError):
                choice = 1
        if 1 <= choice <= len(results):
            picked = results[choice - 1]
            add_tmdb_id(picked["tmdb_id"], source=args.source)
        else:
            print("  Cancelled.")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
