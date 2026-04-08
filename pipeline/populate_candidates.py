#!/usr/bin/env python3
"""
pipeline/populate_candidates.py

Populates the candidates table from Wikidata award data.
Films are scored by award prestige (scoring_points from awards table).

Usage:
  python pipeline/populate_candidates.py                    # all festivals
  python pipeline/populate_candidates.py --festival oscar   # one festival
  python pipeline/populate_candidates.py --dry-run          # no DB writes
  python pipeline/populate_candidates.py --sync-completed   # mark works as completed
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent.parent / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from enrich_awards_wikidata import AWARD_QUERY_MAP, sparql_query  # type: ignore

# ─── Config ──────────────────────────────────────────────────────────────────

TMDB_API = "https://api.themoviedb.org/3"
TMDB_KEY = os.environ.get("TMDB_API_KEY", "")

TMDB_RATE_LIMIT_SLEEP = 0.26   # 40 req / 10s → ~3.8/s, stay safe at ~3.8
SPARQL_SLEEP          = 2.0    # 2s between SPARQL calls


# ─── Scoring helpers ─────────────────────────────────────────────────────────

def get_scoring_map(db) -> dict[str, int]:
    """Returns {award_id_without_prefix: scoring_points} from awards table.

    awards.id looks like  "award_oscar-best-picture"
    AWARD_QUERY_MAP keys look like "oscar-best-picture"
    We strip the "award_" prefix for matching.
    """
    r = db.table("awards").select("id, scoring_points").execute()
    result = {}
    for row in r.data or []:
        aid = row["id"]
        pts = row.get("scoring_points") or 0
        # Store both with and without prefix so lookups are flexible
        result[aid] = pts
        if aid.startswith("award_"):
            result[aid[len("award_"):]] = pts
    return result


# ─── TMDB helpers ─────────────────────────────────────────────────────────────

def tmdb_from_imdb(imdb_id: str) -> dict | None:
    """Returns {tmdb_id, title, original_title, year} or None."""
    if not TMDB_KEY:
        return None
    try:
        r = requests.get(
            f"{TMDB_API}/find/{imdb_id}",
            params={"api_key": TMDB_KEY, "external_source": "imdb_id"},
            timeout=10,
        )
        if r.status_code == 429:
            print("    TMDB 429 — sleeping 10s")
            time.sleep(10)
            r = requests.get(
                f"{TMDB_API}/find/{imdb_id}",
                params={"api_key": TMDB_KEY, "external_source": "imdb_id"},
                timeout=10,
            )
        r.raise_for_status()
        movies = r.json().get("movie_results", [])
        if not movies:
            return None
        m = movies[0]
        year_str = (m.get("release_date") or "")[:4]
        return {
            "tmdb_id":        m["id"],
            "title":          m.get("title") or imdb_id,
            "original_title": m.get("original_title"),
            "year":           int(year_str) if year_str.isdigit() else None,
        }
    except Exception as e:
        print(f"    TMDB error for {imdb_id}: {e}")
        return None


# ─── Candidate upsert ─────────────────────────────────────────────────────────

def upsert_candidates(db, rows: list[dict], dry_run: bool) -> dict:
    """Upsert a batch of candidates.  On conflict (tmdb_id) update score if higher."""
    if not rows or dry_run:
        return {"upserted": 0, "dry_run": dry_run}

    # Fetch existing scores for conflict resolution client-side
    # (Supabase REST doesn't support UPDATE WHERE prisma_score < excluded.prisma_score)
    tmdb_ids = [r["tmdb_id"] for r in rows]
    existing_map: dict[int, float] = {}
    for i in range(0, len(tmdb_ids), 200):
        chunk = tmdb_ids[i:i+200]
        ex = db.table("candidates").select("tmdb_id, prisma_score").in_("tmdb_id", chunk).execute()
        for rec in ex.data or []:
            existing_map[rec["tmdb_id"]] = float(rec["prisma_score"] or 0)

    to_insert: list[dict] = []
    to_update: list[dict] = []

    for row in rows:
        tid = row["tmdb_id"]
        if tid not in existing_map:
            to_insert.append(row)
        else:
            # Only update if new score is strictly higher
            if float(row["prisma_score"]) > existing_map[tid]:
                to_update.append(row)

    inserted = 0
    updated  = 0

    # Insert new candidates in batches of 50
    for i in range(0, len(to_insert), 50):
        batch = to_insert[i:i+50]
        try:
            db.table("candidates").insert(batch).execute()
            inserted += len(batch)
        except Exception as e:
            # Fall back row-by-row
            for rec in batch:
                try:
                    db.table("candidates").insert(rec).execute()
                    inserted += 1
                except Exception as e2:
                    print(f"    ✗ insert failed TMDB {rec.get('tmdb_id')}: {e2}")

    # Update improved scores
    for rec in to_update:
        try:
            payload = {
                "prisma_score": rec["prisma_score"],
                "award_count":  rec["award_count"],
                "win_count":    rec["win_count"],
                "nom_count":    rec["nom_count"],
                "awards_json":  rec["awards_json"],
            }
            db.table("candidates").update(payload).eq("tmdb_id", rec["tmdb_id"]).execute()
            updated += 1
        except Exception as e:
            print(f"    ✗ update failed TMDB {rec.get('tmdb_id')}: {e}")

    return {"inserted": inserted, "updated": updated}


# ─── sync-completed ───────────────────────────────────────────────────────────

def sync_completed(db, dry_run: bool) -> int:
    """Mark candidates as completed where tmdb_id exists in works table."""
    # Get all tmdb_ids in works
    all_works: list[dict] = []
    offset = 0
    while True:
        batch = (db.table("works")
                   .select("tmdb_id, id")
                   .not_.is_("tmdb_id", "null")
                   .range(offset, offset + 999)
                   .execute().data or [])
        all_works.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    work_map = {w["tmdb_id"]: w["id"] for w in all_works if w.get("tmdb_id")}
    print(f"  Works in Supabase: {len(work_map)}")

    if dry_run:
        print(f"  [dry-run] Would mark {len(work_map)} candidates as completed")
        return len(work_map)

    updated = 0
    ids = list(work_map.keys())
    for i in range(0, len(ids), 200):
        chunk = ids[i:i+200]
        try:
            db.table("candidates").update({
                "status": "completed",
                "ingested_at": "now()",
            }).in_("tmdb_id", chunk).eq("status", "pending").execute()
            updated += len(chunk)
        except Exception as e:
            print(f"    ✗ sync batch error: {e}")

    # Also insert any works NOT yet in candidates at all
    existing_ids: set[int] = set()
    for i in range(0, len(ids), 200):
        chunk = ids[i:i+200]
        ex = db.table("candidates").select("tmdb_id").in_("tmdb_id", chunk).execute()
        for rec in ex.data or []:
            existing_ids.add(rec["tmdb_id"])

    missing = [tid for tid in ids if tid not in existing_ids]
    print(f"  Works missing from candidates: {len(missing)} — inserting as completed")
    inserted = 0
    for i in range(0, len(missing), 50):
        chunk = missing[i:i+50]
        rows = []
        for tid in chunk:
            work_id = work_map.get(tid, "")
            rows.append({
                "tmdb_id":     tid,
                "title":       work_id,   # best we have without extra API call
                "status":      "completed",
                "work_id":     work_id,
                "prisma_score": 0,
            })
        try:
            db.table("candidates").insert(rows).execute()
            inserted += len(rows)
        except Exception as e:
            for rec in rows:
                try:
                    db.table("candidates").insert(rec).execute()
                    inserted += 1
                except Exception:
                    pass
    print(f"  Inserted {inserted} completed candidates for existing works")
    return updated


# ─── Festival processing ──────────────────────────────────────────────────────

def populate_festival(festival: str, db, scoring_map: dict, dry_run: bool) -> dict:
    """Process all awards for one festival. Returns stats dict."""
    targets = {k: v for k, v in AWARD_QUERY_MAP.items()
               if v["festival"] == festival}

    if not targets:
        return {"festival": festival, "error": "unknown festival"}

    # Accumulate per-film across all awards in this festival
    # film_data[imdb_id] = {imdb_id, prisma_score, wins, noms, awards[]}
    film_data: dict[str, dict] = {}

    total_awards = len(targets)
    for idx, (award_key, meta) in enumerate(targets.items(), 1):
        qid      = meta["qid"]
        full_id  = f"award_{award_key}"
        pts      = scoring_map.get(full_id) or scoring_map.get(award_key) or 0

        print(f"  [{idx}/{total_awards}] {award_key}  (QID:{qid}  pts:{pts})")

        results = sparql_query(qid)
        wins = [r for r in results if r["result"] == "win"]
        noms = [r for r in results if r["result"] == "nomination"]
        print(f"    Wikidata: {len(results)} ({len(wins)}W / {len(noms)}N)")

        for rec in results:
            imdb_id = rec["imdb"]
            result  = rec["result"]
            score_contrib = pts if result == "win" else pts * 0.4

            if imdb_id not in film_data:
                film_data[imdb_id] = {
                    "imdb_id":     imdb_id,
                    "prisma_score": 0.0,
                    "win_count":   0,
                    "nom_count":   0,
                    "awards":      [],
                }
            fd = film_data[imdb_id]
            fd["prisma_score"] += score_contrib
            if result == "win":
                fd["win_count"] += 1
            else:
                fd["nom_count"] += 1
            fd["awards"].append({"award_id": full_id, "result": result, "pts": pts})

        time.sleep(SPARQL_SLEEP)

    print(f"\n  Unique films from Wikidata: {len(film_data)}")
    if not film_data:
        return {"festival": festival, "found": 0, "tmdb_resolved": 0, "inserted": 0, "updated": 0}

    # Resolve TMDB IDs
    candidates: list[dict] = []
    no_tmdb = 0
    resolved = 0

    for i, (imdb_id, fd) in enumerate(film_data.items()):
        info = tmdb_from_imdb(imdb_id)
        time.sleep(TMDB_RATE_LIMIT_SLEEP)
        if not info:
            no_tmdb += 1
            if i < 5 or i % 50 == 0:
                print(f"    ✗ No TMDB for {imdb_id}")
            continue
        resolved += 1
        candidates.append({
            "tmdb_id":      info["tmdb_id"],
            "imdb_id":      imdb_id,
            "title":        info["title"],
            "original_title": info.get("original_title"),
            "year":         info.get("year"),
            "prisma_score": round(fd["prisma_score"], 2),
            "award_count":  fd["win_count"] + fd["nom_count"],
            "win_count":    fd["win_count"],
            "nom_count":    fd["nom_count"],
            "awards_json":  fd["awards"],
            "source":       festival,
            "status":       "pending",
        })

    print(f"  TMDB resolved: {resolved}  no_tmdb: {no_tmdb}")

    if dry_run:
        print(f"  [dry-run] Would upsert {len(candidates)} candidates")
        if candidates:
            top5 = sorted(candidates, key=lambda x: -x["prisma_score"])[:5]
            for c in top5:
                print(f"    {c['prisma_score']:6.1f}  {c['title']} ({c['year']})  {c['imdb_id']}")
        return {"festival": festival, "found": len(film_data), "tmdb_resolved": resolved,
                "inserted": 0, "updated": 0, "dry_run": True}

    result = upsert_candidates(db, candidates, dry_run=False)
    print(f"  ✓ inserted={result.get('inserted',0)}  updated={result.get('updated',0)}")
    return {
        "festival":      festival,
        "found":         len(film_data),
        "tmdb_resolved": resolved,
        "no_tmdb":       no_tmdb,
        "inserted":      result.get("inserted", 0),
        "updated":       result.get("updated", 0),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate candidates table from Wikidata award data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--festival", "-f", default=None,
                        help="Festival to run (omit to run all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be inserted without writing to DB")
    parser.add_argument("--sync-completed", action="store_true",
                        help="Mark candidates as completed where tmdb_id exists in works")
    args = parser.parse_args()

    db = create_client(
        os.environ["PUBLIC_SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )

    if args.sync_completed:
        print("Syncing completed films from works table → candidates...")
        n = sync_completed(db, args.dry_run)
        print(f"Done. {n} candidates synced.")
        return

    scoring_map = get_scoring_map(db)
    print(f"Loaded {len(scoring_map)} scoring entries from awards table")

    if args.festival:
        festivals = [args.festival]
    else:
        festivals = sorted(set(v["festival"] for v in AWARD_QUERY_MAP.values()))

    valid_festivals = sorted(set(v["festival"] for v in AWARD_QUERY_MAP.values()))
    unknown = [f for f in festivals if f not in valid_festivals]
    if unknown:
        print(f"Unknown festival(s): {unknown}")
        print(f"Valid: {valid_festivals}")
        return

    totals: dict[str, int] = defaultdict(int)

    for festival in festivals:
        print(f"\n{'═'*56}")
        print(f"  Festival: {festival.upper()}")
        print(f"{'═'*56}")
        stats = populate_festival(festival, db, scoring_map, args.dry_run)
        for k, v in stats.items():
            if isinstance(v, int):
                totals[k] += v

    print(f"\n{'═'*56}")
    print(f"  SUMMARY")
    print(f"{'═'*56}")
    for k, v in totals.items():
        print(f"  {k:<20} {v}")

    if not args.dry_run:
        # Show final candidates state
        r = db.table("candidates").select("status", count="exact").execute()
        print(f"\n  Total candidates in DB: {r.count}")
        from collections import Counter
        c = Counter(x["status"] for x in (r.data or []))
        for status, cnt in sorted(c.items()):
            print(f"    {status}: {cnt}")

        top = (db.table("candidates")
                 .select("title, year, prisma_score, status")
                 .eq("status", "pending")
                 .order("prisma_score", desc=True)
                 .limit(10)
                 .execute())
        print(f"\n  Top 10 pending by prisma_score:")
        for x in top.data or []:
            print(f"    {float(x['prisma_score']):7.1f}  {x['title']} ({x['year']})")


if __name__ == "__main__":
    main()
