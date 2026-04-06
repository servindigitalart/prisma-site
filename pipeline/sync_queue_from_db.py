#!/usr/bin/env python3
"""
sync_queue_from_db.py
─────────────────────
Sync pipeline/queue/completed.json to reflect actual Supabase state.

Problem this solves:
    The GitHub Actions runner's completed.json only tracks films ingested
    through ingest_agent.py on that runner. Films migrated locally (e.g. via
    migrate_to_db.py --all) exist in Supabase but are NOT in completed.json.
    The auto-dedup logic in ingest_agent.py checks Supabase, finds these films,
    and removes them from pending.json — which is correct behaviour, but then
    completed.json stays out of sync, making the queue look larger than it is.

    This script closes the gap: for every work in Supabase, if it is NOT already
    in completed.json, it is added so ingest_agent.py has an accurate picture.

Usage:
    python pipeline/sync_queue_from_db.py
    python pipeline/sync_queue_from_db.py --dry-run   # preview without writing

Environment:
    PUBLIC_SUPABASE_URL   or  SUPABASE_URL
    SUPABASE_SERVICE_KEY
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

import os

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR       = Path(__file__).parent.parent
PIPELINE_DIR   = BASE_DIR / "pipeline"
QUEUE_DIR      = PIPELINE_DIR / "queue"
COMPLETED_FILE = QUEUE_DIR / "completed.json"
PENDING_FILE   = QUEUE_DIR / "pending.json"


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync completed.json with the actual Supabase works table."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to completed.json or pending.json.",
    )
    args = parser.parse_args()

    dry_run = args.dry_run

    # ── Connect to Supabase ───────────────────────────────────────────────────
    supabase_url = os.getenv("PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    service_key  = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        print("✗  Missing env vars: PUBLIC_SUPABASE_URL / SUPABASE_URL and SUPABASE_SERVICE_KEY")
        return 1

    try:
        from supabase import create_client  # type: ignore
    except ImportError:
        print("✗  supabase package not installed. Run: pip install supabase")
        return 1

    try:
        db = create_client(supabase_url, service_key)
    except Exception as e:
        print(f"✗  Could not connect to Supabase: {e}")
        return 1

    # ── Fetch all works from Supabase ─────────────────────────────────────────
    print("Fetching works from Supabase…")
    try:
        # Paginate — Supabase default page size is 1000
        all_rows: list[dict] = []
        offset = 0
        page_size = 1000
        while True:
            res = (
                db.table("works")
                .select("id, tmdb_id")
                .not_.is_("tmdb_id", "null")
                .range(offset, offset + page_size - 1)
                .execute()
            )
            batch = res.data or []
            all_rows.extend(batch)
            if len(batch) < page_size:
                break
            offset += page_size

    except Exception as e:
        print(f"✗  Supabase query failed: {e}")
        return 1

    print(f"  Found {len(all_rows)} works in Supabase (with tmdb_id)")

    # ── Load local queues ─────────────────────────────────────────────────────
    completed = load_queue(COMPLETED_FILE)
    pending   = load_queue(PENDING_FILE)

    # Build fast-lookup sets
    completed_tmdb_ids  = {int(c["tmdb_id"]) for c in completed if c.get("tmdb_id") is not None}
    completed_work_ids  = {c["work_id"] for c in completed if c.get("work_id")}
    pending_tmdb_ids    = {int(p["tmdb_id"]) for p in pending if p.get("tmdb_id") is not None}

    print(f"  completed.json : {len(completed)} entries")
    print(f"  pending.json   : {len(pending)} entries")

    # ── Find works in Supabase missing from completed.json ───────────────────
    to_add: list[dict] = []
    for row in all_rows:
        work_id  = row["id"]
        tmdb_id  = int(row["tmdb_id"])

        # Skip if already recorded in completed.json (by either key)
        if tmdb_id in completed_tmdb_ids or work_id in completed_work_ids:
            continue

        to_add.append({
            "tmdb_id":       tmdb_id,
            "work_id":       work_id,
            "completed_at":  "2026-01-01",   # sentinel — migrated before queue tracking
            "checks_passed": 0,
            "checks_total":  15,
            "warnings":      ["synced_from_supabase"],
        })

    print(f"\n  Works to add to completed.json : {len(to_add)}")

    if not to_add:
        print("  ✅ completed.json is already in sync with Supabase — nothing to do.")
        return 0

    if dry_run:
        print("\n  [DRY RUN] Would add the following work_ids:")
        for item in to_add:
            print(f"    tmdb:{item['tmdb_id']:>8}  {item['work_id']}")
        print("\n  Run without --dry-run to apply.")
        return 0

    # ── Write updated completed.json ──────────────────────────────────────────
    completed.extend(to_add)
    save_queue(COMPLETED_FILE, completed)
    print(f"  ✅ completed.json updated — now {len(completed)} entries (+{len(to_add)} synced)")

    # ── Also remove newly-synced films from pending.json ─────────────────────
    synced_tmdb_ids = {item["tmdb_id"] for item in to_add}
    pending_before  = len(pending)
    pending         = [p for p in pending if int(p.get("tmdb_id", -1)) not in synced_tmdb_ids]
    removed_from_pending = pending_before - len(pending)

    if removed_from_pending:
        save_queue(PENDING_FILE, pending)
        print(f"  ✅ pending.json cleaned — removed {removed_from_pending} already-migrated films")
    else:
        print("  ✅ pending.json unchanged (no overlap with synced films)")

    print(f"\n  Summary:")
    print(f"    Supabase works     : {len(all_rows)}")
    print(f"    Synced to completed: {len(to_add)}")
    print(f"    Removed from pending: {removed_from_pending}")
    print(f"    completed.json now : {len(completed)}")
    print(f"    pending.json now   : {len(pending)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
