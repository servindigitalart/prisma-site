#!/usr/bin/env python3
"""
fix_work_people.py
──────────────────
Finds all works in Supabase with no work_people rows, reads each
pipeline/normalized/works/{work_id}.json, and inserts the missing
junction rows.

USAGE:
    python3 pipeline/fix_work_people.py [--dry-run]
"""
import os
import sys
import json
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
except ImportError:
    pass

from supabase import create_client

WORKS_DIR = Path("pipeline/normalized/works")

ROLE_MAP = {
    "director":       "director",
    "cinematography": "cinematography",
    "writer":         "writer",
    "cast":           "actor",
    "editor":         "editor",
    "composer":       "composer",
}

def main(dry_run: bool):
    db = create_client(
        os.environ["PUBLIC_SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )

    # 1. Find works without any work_people rows
    all_works = db.table("works").select("id").execute()
    linked = db.table("work_people").select("work_id").execute()
    linked_ids = {r["work_id"] for r in linked.data}
    missing_work_ids = [w["id"] for w in all_works.data if w["id"] not in linked_ids]

    print(f"Works without people: {len(missing_work_ids)}")

    # 2. Get all person IDs that exist in people table (to avoid FK violations)
    # Paginate because Supabase returns max 1000 rows by default
    known_people: set[str] = set()
    offset = 0
    PAGE = 1000
    while True:
        resp = db.table("people").select("id").range(offset, offset + PAGE - 1).execute()
        if not resp.data:
            break
        for r in resp.data:
            known_people.add(r["id"])
        if len(resp.data) < PAGE:
            break
        offset += PAGE
    print(f"People in Supabase: {len(known_people)}")

    # 3. Build rows for each missing work
    rows_to_insert: list[dict] = []
    works_fixed = 0
    works_no_file = 0
    works_no_people = 0
    people_skipped = 0

    for work_id in missing_work_ids:
        work_path = WORKS_DIR / f"{work_id}.json"
        if not work_path.exists():
            print(f"  ⚠️  No file: {work_id}")
            works_no_file += 1
            continue

        with open(work_path, encoding="utf-8") as f:
            work = json.load(f)

        people_section = work.get("people", {})
        work_rows: list[dict] = []

        for source_role, db_role in ROLE_MAP.items():
            person_ids = people_section.get(source_role, [])
            if not isinstance(person_ids, list):
                continue
            for i, person_id in enumerate(person_ids):
                if not isinstance(person_id, str) or not person_id:
                    continue
                if person_id not in known_people:
                    people_skipped += 1
                    continue
                work_rows.append({
                    "work_id":       work_id,
                    "person_id":     person_id,
                    "role":          db_role,
                    "billing_order": (i + 1) if source_role == "cast" else None,
                })

        if work_rows:
            rows_to_insert.extend(work_rows)
            works_fixed += 1
        else:
            works_no_people += 1

    print(f"\nWorks to fix:           {works_fixed}")
    print(f"Works with no JSON:     {works_no_file}")
    print(f"Works with no matches:  {works_no_people}")
    print(f"People skipped (not in DB): {people_skipped}")
    print(f"Rows to insert:         {len(rows_to_insert)}")

    if not rows_to_insert:
        print("\nNothing to insert.")
        return

    if dry_run:
        print("\n[DRY RUN] — no changes written.")
        print("First 5 rows:")
        for r in rows_to_insert[:5]:
            print(f"  {r}")
        return

    # 4. Upsert in batches of 500
    BATCH = 500
    inserted = 0
    for i in range(0, len(rows_to_insert), BATCH):
        batch = rows_to_insert[i : i + BATCH]
        db.table("work_people").upsert(
            batch,
            on_conflict="work_id,person_id,role",
        ).execute()
        inserted += len(batch)
        print(f"  Upserted {inserted}/{len(rows_to_insert)} rows...")

    print(f"\n✅ Done. Inserted {inserted} work_people rows for {works_fixed} works.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
