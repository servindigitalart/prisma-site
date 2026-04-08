#!/usr/bin/env python3
"""
pipeline/sync_queue_from_db.py

Syncs state between the JSON queue files and the candidates table.

Usage:
  python pipeline/sync_queue_from_db.py             # sync everything
  python pipeline/sync_queue_from_db.py --dry-run   # report only
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent.parent / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env")

BASE_DIR       = Path(__file__).parent.parent
PIPELINE_DIR   = BASE_DIR / "pipeline"
QUEUE_DIR      = PIPELINE_DIR / "queue"
COMPLETED_FILE = QUEUE_DIR / "completed.json"
PENDING_FILE   = QUEUE_DIR / "pending.json"
FAILED_FILE    = QUEUE_DIR / "failed.json"


def load_queue(file: Path) -> list[dict]:
    if not file.exists():
        return []
    try:
        data = json.loads(file.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Sync JSON queue <-> candidates table")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = create_client(
        os.environ["PUBLIC_SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )

    # Check table exists
    try:
        db.table("candidates").select("tmdb_id", count="exact").limit(1).execute()
    except Exception as e:
        print(f"candidates table not accessible: {e}")
        print("  Run the CREATE TABLE SQL in Supabase SQL Editor first.")
        sys.exit(1)

    completed_json = load_queue(COMPLETED_FILE)
    pending_json   = load_queue(PENDING_FILE)
    failed_json    = load_queue(FAILED_FILE)

    print(f"JSON queue state:")
    print(f"  completed.json: {len(completed_json)}")
    print(f"  pending.json:   {len(pending_json)}")
    print(f"  failed.json:    {len(failed_json)}")

    # ── 1. Sync completed.json -> candidates ──────────────────────────────────
    print(f"\nSyncing completed.json -> candidates...")
    synced_completed  = 0
    inserted_completed = 0

    for i in range(0, len(completed_json), 200):
        chunk    = completed_json[i:i+200]
        tmdb_ids = [c["tmdb_id"] for c in chunk if c.get("tmdb_id")]
        if not tmdb_ids:
            continue

        ex = db.table("candidates").select("tmdb_id, status").in_("tmdb_id", tmdb_ids).execute()
        existing = {r["tmdb_id"]: r["status"] for r in (ex.data or [])}

        to_mark   = [tid for tid in tmdb_ids if tid in existing and existing[tid] == "pending"]
        to_insert = [c for c in chunk if c.get("tmdb_id") and c["tmdb_id"] not in existing]

        if to_mark and not args.dry_run:
            db.table("candidates").update({"status": "completed", "ingested_at": "now()"}) \
              .in_("tmdb_id", to_mark).execute()
        synced_completed += len(to_mark)

        if to_insert and not args.dry_run:
            rows = []
            for c in to_insert:
                rows.append({
                    "tmdb_id":     c["tmdb_id"],
                    "title":       c.get("work_id") or c.get("title") or str(c["tmdb_id"]),
                    "status":      "completed",
                    "work_id":     c.get("work_id"),
                    "prisma_score": 0,
                    "ingested_at": "now()",
                })
            try:
                db.table("candidates").insert(rows).execute()
                inserted_completed += len(rows)
            except Exception as e:
                for rec in rows:
                    try:
                        db.table("candidates").insert(rec).execute()
                        inserted_completed += 1
                    except Exception:
                        pass

    print(f"  marked completed:    {synced_completed}")
    print(f"  inserted completed:  {inserted_completed}")

    # ── 2. Sync pending.json -> candidates ────────────────────────────────────
    print(f"\nSyncing pending.json -> candidates...")
    inserted_pending = 0

    for i in range(0, len(pending_json), 200):
        chunk    = pending_json[i:i+200]
        tmdb_ids = [c["tmdb_id"] for c in chunk if c.get("tmdb_id")]
        if not tmdb_ids:
            continue

        ex = db.table("candidates").select("tmdb_id").in_("tmdb_id", tmdb_ids).execute()
        existing_ids = {r["tmdb_id"] for r in (ex.data or [])}

        to_insert = [c for c in chunk if c.get("tmdb_id") and c["tmdb_id"] not in existing_ids]
        if to_insert and not args.dry_run:
            rows = [{
                "tmdb_id":      c["tmdb_id"],
                "title":        c.get("title") or str(c["tmdb_id"]),
                "year":         int(c["year"]) if str(c.get("year","")).isdigit() else None,
                "status":       "pending",
                "source":       c.get("source"),
                "prisma_score": 0,
            } for c in to_insert]
            try:
                db.table("candidates").insert(rows).execute()
                inserted_pending += len(rows)
            except Exception:
                for rec in rows:
                    try:
                        db.table("candidates").insert(rec).execute()
                        inserted_pending += 1
                    except Exception:
                        pass

    print(f"  inserted as pending: {inserted_pending}")

    # ── 3. Sync failed.json -> candidates ─────────────────────────────────────
    if failed_json:
        print(f"\nSyncing failed.json -> candidates...")
        synced_failed = 0
        for i in range(0, len(failed_json), 200):
            chunk    = failed_json[i:i+200]
            tmdb_ids = [c["tmdb_id"] for c in chunk if c.get("tmdb_id")]
            if not tmdb_ids:
                continue
            if not args.dry_run:
                db.table("candidates").update({"status": "failed"}) \
                  .in_("tmdb_id", tmdb_ids).execute()
            synced_failed += len(tmdb_ids)
        print(f"  marked failed: {synced_failed}")

    # ── Final state ───────────────────────────────────────────────────────────
    if not args.dry_run:
        r = db.table("candidates").select("status", count="exact").execute()
        print(f"\nFinal candidates table state:")
        print(f"  Total: {r.count}")
        from collections import Counter
        c = Counter(x["status"] for x in (r.data or []))
        for status, cnt in sorted(c.items()):
            print(f"  {status}: {cnt}")
    else:
        print(f"\n[dry-run] No writes made.")

if __name__ == "__main__":
    main()
