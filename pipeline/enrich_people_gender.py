"""
pipeline/enrich_people_gender.py
──────────────────────────────────
Fetches gender from TMDB for all people with tmdb_id.

TMDB gender convention:
  0 = unspecified
  1 = female
  2 = male
  3 = non-binary

Usage:
  python3 pipeline/enrich_people_gender.py
  python3 pipeline/enrich_people_gender.py --dry-run
  python3 pipeline/enrich_people_gender.py --reset   # clear existing and re-fetch all
"""

import os
import sys
import time
import argparse
import requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv(".env.local")
from supabase import create_client

db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
TMDB_KEY = os.environ.get("TMDB_API_KEY") or os.environ.get("PUBLIC_TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
HEADERS = {"User-Agent": "PRISMA-film-db/1.0 (cinematic color catalog; educational project)"}
SLEEP = 0.15


def fetch_tmdb_gender(tmdb_id: int) -> int:
    try:
        r = requests.get(
            f"{TMDB_BASE}/person/{tmdb_id}",
            params={"api_key": TMDB_KEY},
            headers=HEADERS,
            timeout=10,
        )
        if r.status_code != 200:
            return 0
        return r.json().get("gender", 0)
    except Exception:
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't write to DB")
    parser.add_argument("--reset",   action="store_true", help="Re-fetch even for people with gender already set")
    args = parser.parse_args()

    if not TMDB_KEY:
        print("ERROR: TMDB_API_KEY not found in .env.local")
        sys.exit(1)

    # ── Load all people with tmdb_id (paginated — Supabase default limit is 1000) ──
    print("Loading people with tmdb_id (paginated)...")
    all_people = []
    offset = 0
    while True:
        batch = (
            db.table("people")
            .select("id, tmdb_id, gender")
            .not_.is_("tmdb_id", "null")
            .range(offset, offset + 999)
            .execute()
        )
        all_people.extend(batch.data)
        if len(batch.data) < 1000:
            break
        offset += 1000

    print(f"People with TMDB ID: {len(all_people)}\n")

    updated = 0
    skipped = 0
    errors  = 0

    for i, person in enumerate(all_people):
        existing_gender = person.get("gender") or 0

        # Skip if already has gender set (unless --reset)
        if existing_gender != 0 and not args.reset:
            skipped += 1
            continue

        gender = fetch_tmdb_gender(person["tmdb_id"])

        if gender != 0:
            if not args.dry_run:
                try:
                    db.table("people").update({"gender": gender}).eq("id", person["id"]).execute()
                    updated += 1
                except Exception as e:
                    print(f"  DB ERROR for {person['id']}: {e}")
                    errors += 1
            else:
                updated += 1  # count would-be updates
        else:
            skipped += 1

        if i % 100 == 0 and i > 0:
            print(f"  [{i}/{len(all_people)}] updated={updated} skipped={skipped}")

        time.sleep(SLEEP)

    prefix = "DRY RUN — " if args.dry_run else ""
    print(f"\n{prefix}SUMMARY:")
    print(f"  People processed: {len(all_people)}")
    print(f"  Updated:          {updated}")
    print(f"  Skipped:          {skipped}")
    print(f"  Errors:           {errors}")

    if not args.dry_run:
        # Gender distribution
        all_p = db.table("people").select("gender").execute()
        dist = Counter(r["gender"] for r in all_p.data)
        print(f"\nGender distribution:")
        print(f"  Female (1):       {dist[1]}")
        print(f"  Male (2):         {dist[2]}")
        print(f"  Non-binary (3):   {dist[3]}")
        print(f"  Unspecified (0):  {dist[0]}")


if __name__ == "__main__":
    main()
