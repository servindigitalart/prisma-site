"""
pipeline/enrich_studio_logos.py
─────────────────────────────────
Fetches logo_path for all studios that have a tmdb_id using the TMDB
/company/{id} endpoint, then writes the result to studios.logo_path.

logo_path is a TMDB-style path (e.g. /krQ8RCXPmQHmJ50gTEplxg3p588.png).
Frontend renders it as: https://image.tmdb.org/t/p/w92{logo_path}

Usage:
  python3 pipeline/enrich_studio_logos.py           # full run
  python3 pipeline/enrich_studio_logos.py --dry-run # print without DB write
  python3 pipeline/enrich_studio_logos.py --limit 20
"""

import os
import sys
import time
import argparse
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")
from supabase import create_client

db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
TMDB_KEY = os.environ.get("TMDB_API_KEY") or os.environ.get("PUBLIC_TMDB_API_KEY")
if not TMDB_KEY:
    print("ERROR: TMDB_API_KEY not found in .env.local")
    sys.exit(1)

TMDB_BASE = "https://api.themoviedb.org/3"
HEADERS = {"User-Agent": "PRISMA-film-db/1.0 (cinematic color catalog; educational project)"}
SLEEP = 0.25


def fetch_tmdb_logo(tmdb_id: int) -> str | None:
    try:
        r = requests.get(
            f"{TMDB_BASE}/company/{tmdb_id}",
            params={"api_key": TMDB_KEY},
            headers=HEADERS,
            timeout=10,
        )
        if r.status_code != 200:
            return None
        return r.json().get("logo_path")
    except Exception as e:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true", help="Re-fetch even if logo_path already set")
    args = parser.parse_args()

    print(f"{'DRY RUN — ' if args.dry_run else ''}Enriching studio logos via TMDB\n")

    # Fetch studios with tmdb_id
    studios = db.table("studios").select("id, name, tmdb_id, logo_path").execute()
    candidates = [s for s in studios.data if s.get("tmdb_id")]

    if not args.force:
        candidates = [s for s in candidates if not s.get("logo_path")]

    if args.limit:
        candidates = candidates[:args.limit]

    total = len(candidates)
    print(f"Processing {total} studios (force={args.force})\n")

    found, missing, errors = 0, 0, 0

    for i, studio in enumerate(candidates, 1):
        logo = fetch_tmdb_logo(studio["tmdb_id"])
        status = "✓" if logo else "·"
        print(f"[{i:3}/{total}] {status} {studio['name'][:45]:<45} {logo or ''}")

        if logo:
            found += 1
            if not args.dry_run:
                try:
                    db.table("studios").update({"logo_path": logo}).eq("id", studio["id"]).execute()
                except Exception as e:
                    print(f"    DB ERROR: {e}")
                    errors += 1
        else:
            missing += 1

        time.sleep(SLEEP)

    # Final count from DB
    updated = db.table("studios").select("id", count="exact").not_.is_("logo_path", "null").execute()

    print(f"\n{'DRY RUN ' if args.dry_run else ''}SUMMARY:")
    print(f"  Processed: {total}")
    print(f"  Found logo: {found}")
    print(f"  No logo:    {missing}")
    print(f"  Errors:     {errors}")
    print(f"  Studios with logo_path in DB: {updated.count}")


if __name__ == "__main__":
    main()
