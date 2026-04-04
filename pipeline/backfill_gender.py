"""
pipeline/backfill_gender.py
────────────────────────────
Backfills the people.gender field for all people who have a tmdb_id but
gender IS NULL in the database.

TMDB gender codes:
  0 = unknown / not set
  1 = female
  2 = male
  3 = non-binary

Usage:
  source venv/bin/activate
  export $(cat .env.local | grep -v '^#' | grep -v '^$' | xargs)
  python pipeline/backfill_gender.py
  python pipeline/backfill_gender.py --dry-run
  python pipeline/backfill_gender.py --limit 100   # test on first 100
"""

from __future__ import annotations

import argparse
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")
from supabase import create_client

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_KEY  = os.environ.get("TMDB_API_KEY", "")

PAGE_SIZE = 1000  # Supabase batch size


def fetch_all_missing(db) -> list[dict]:
    """Fetch all people where gender is 0 (unknown) or NULL and tmdb_id is set."""
    rows: list[dict] = []
    offset = 0
    # gender=0 means "unknown" in TMDB convention — these need backfilling
    # Also catch any true NULLs for completeness
    while True:
        res = (
            db.table("people")
            .select("id, name, tmdb_id, gender")
            .or_("gender.eq.0,gender.is.null")
            .not_.is_("tmdb_id", "null")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = res.data or []
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


def tmdb_gender(tmdb_id: int) -> int | None:
    """Call TMDB /person/{tmdb_id} and return gender int, or None on error."""
    if not TMDB_KEY:
        return None
    try:
        resp = requests.get(
            f"{TMDB_BASE}/person/{tmdb_id}",
            params={"api_key": TMDB_KEY},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("gender")
        if resp.status_code == 404:
            return None
        print(f"    ⚠ TMDB {tmdb_id} → HTTP {resp.status_code}")
        return None
    except Exception as e:
        print(f"    ⚠ TMDB {tmdb_id} error: {e}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill people.gender from TMDB")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--limit", type=int, default=0, metavar="N",
                        help="Process at most N people (0 = all)")
    args = parser.parse_args()

    if not TMDB_KEY:
        print("❌  TMDB_API_KEY not set in environment. Aborting.")
        return

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    targets = fetch_all_missing(db)
    print(f"Found {len(targets):,} people with gender=NULL and a tmdb_id")

    if args.limit:
        targets = targets[: args.limit]
        print(f"Limiting to first {args.limit}")

    updated   = 0
    unknown   = 0
    errors    = 0
    female    = 0
    male      = 0

    for i, person in enumerate(targets, 1):
        tmdb_id   = person["tmdb_id"]
        person_id = person["id"]
        name      = person.get("name", person_id)

        gender = tmdb_gender(tmdb_id)

        label = {0: "unknown", 1: "female ♀", 2: "male ♂", 3: "non-binary"}.get(
            gender, f"unknown({gender})"
        )

        if i % 50 == 0 or i <= 5:
            print(f"  [{i:4d}/{len(targets)}] {name:<40s} tmdb={tmdb_id}  → {label}")

        if gender is None:
            errors += 1
            time.sleep(0.25)
            continue

        if gender == 0:
            # TMDB confirmed unknown — skip writing (already 0 in DB, or confirmed unknown)
            unknown += 1
            time.sleep(0.05)
            continue
        elif gender == 1:
            female += 1
        elif gender == 2:
            male += 1

        # Only write to DB when we have a real gender value (1, 2, or 3)
        if not args.dry_run:
            try:
                db.table("people").update({"gender": gender}).eq("id", person_id).execute()
                updated += 1
            except Exception as e:
                print(f"    ❌ DB update failed for {person_id}: {e}")
                errors += 1
        else:
            updated += 1  # count as would-be-updated

        # Respect TMDB rate limit (~40 req/s allowed on free tier)
        time.sleep(0.05)

    print()
    print("─" * 50)
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Results:")
    print(f"  Total processed : {len(targets):,}")
    print(f"  Updated         : {updated:,}")
    print(f"    female (1)    : {female:,}")
    print(f"    male   (2)    : {male:,}")
    print(f"    unknown (0)   : {unknown:,}")
    print(f"  Errors / skipped: {errors:,}")
    print("─" * 50)
    if not args.dry_run:
        print("✅  Gender backfill complete. Run compute_rankings.py --people-only to refresh scores.")


if __name__ == "__main__":
    main()
