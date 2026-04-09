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


# ─── Festival tier weights ────────────────────────────────────────────────────
# Tier 1 — world peak          : cannes, oscar        → 1.0
# Tier 2 — great European      : venice, berlin       → 0.9
# Tier 3 — respected art       : sundance, locarno…   → 0.8
# Tier 4 — regional important  : cesar, bafta…        → 0.7
# Tier 5 — Latin American      : ariel, ficg…         → 0.6

FESTIVAL_TIER_WEIGHT: dict[str, float] = {
    "oscar":          1.0,
    "cannes":         1.0,
    "venice":         0.9,
    "berlin":         0.9,
    "sundance":       0.8,
    "san-sebastian":  0.8,
    "locarno":        0.8,
    "cesar":          0.7,
    "goya":           0.7,
    "bafta":          0.7,
    "golden-globe":   0.7,
    "ariel":          0.6,
    "ficg":           0.6,
    "ficm":           0.6,
    "mar-del-plata":  0.6,
}

DEFAULT_FESTIVAL_WEIGHT:  float = 0.6

# ─── Category multipliers ─────────────────────────────────────────────────────
# Grand prize / Best Film          → 1.0
# Best Director                    → 0.8
# Best Screenplay                  → 0.7
# Documentary / Animation / Intl   → 0.5
# Best Actor / Actress             → 0.4
# Supporting / Cinematography      → 0.3
# Technical (score, sound…)        → 0.1 / 0.05
# Legacy duplicate IDs             → 0.0  (skip — already counted elsewhere)

CATEGORY_FILM_MULTIPLIER: dict[str, float] = {
    # ── Grand prizes / Best Film ───────────────────────────────────────────
    "oscar-best-picture":             1.0,
    "oscar-best-intl-film":           1.0,
    "cannes-palme-dor":               1.0,
    "cannes-grand-prix":              1.0,
    "cannes-jury-prize":              1.0,
    "cannes-special-jury":            1.0,
    "cannes-un-certain-regard":       1.0,
    "cannes-camera-dor":              1.0,
    "berlin-golden-bear":             1.0,
    "berlin-silver-bear-jury":        1.0,
    "berlin-grand-jury-prize":        1.0,
    "venice-golden-lion":             1.0,
    "venice-grand-jury":              1.0,
    "venice-special-jury":            1.0,
    "bafta-best-film":                1.0,
    "bafta-best-intl-film":           1.0,
    "locarno-golden-leopard":         1.0,
    "locarno-special-jury":           1.0,
    "sansebastian-golden-shell":      1.0,
    "sundance-grand-jury-drama":      1.0,
    "sundance-grand-jury-doc":        1.0,
    "sundance-world-cinema-drama":    1.0,
    "toronto-peoples-choice":         1.0,
    "toronto-platform":               1.0,
    "cesar-best-film":                1.0,
    "goya-best-film":                 1.0,
    "ariel-best-film":                1.0,
    "ficg-best-iberoamerican-film":   1.0,
    "ficg-best-mexican-film":         1.0,
    "ficm-best-mexican-film":         1.0,
    "mar-del-plata-golden-astor":     1.0,
    "mar-del-plata-silver-astor":     1.0,
    "gg-best-film-drama":             1.0,
    "gg-best-intl-film":              1.0,
    "gg-best-comedy":                 1.0,
    "rotterdam-tiger":                1.0,
    "fipresci":                       1.0,
    "fipresci-cannes":                1.0,
    "fipresci-berlin":                1.0,
    "fipresci-venice":                1.0,
    # ── Direction ─────────────────────────────────────────────────────────
    "oscar-best-director":            0.8,
    "cannes-best-director":           0.8,
    "berlin-silver-bear-director":    0.8,
    "venice-best-director":           0.8,
    "venice-silver-lion-director":    0.8,
    "bafta-best-director":            0.8,
    "cesar-best-director":            0.8,
    "goya-best-director":             0.8,
    "ariel-best-director":            0.8,
    "locarno-best-director":          0.8,
    "sansebastian-silver-director":   0.8,
    "sansebastian-silver-shell-actor": 0.8,
    "gg-best-director":               0.8,
    "sundance-directing-drama":       0.8,
    # ── Screenplay ────────────────────────────────────────────────────────
    "oscar-best-original-screenplay": 0.7,
    "oscar-best-adapted-screenplay":  0.7,
    "cannes-best-screenplay":         0.7,
    "cesar-best-screenplay":          0.7,
    "ariel-best-screenplay":          0.7,
    "bafta-best-original-screenplay": 0.7,
    "bafta-best-adapted-screenplay":  0.7,
    # ── Documentary / Animation / International ────────────────────────────
    "oscar-best-documentary":         0.5,
    "oscar-best-animated":            0.5,
    "bafta-best-documentary":         0.5,
    "bafta-best-animated":            0.5,
    "ariel-best-documentary":         0.5,
    "ariel-best-animated":            0.5,
    "ariel-best-intl-film":           0.5,
    "cesar-best-animated":            0.5,
    "goya-best-animated":             0.5,
    "goya-best-documentary":          0.5,
    "goya-best-iberoamerican-film":   0.5,
    "ficm-best-documentary":          0.5,
    "ficg-best-documentary":          0.5,
    "ficg-best-iberoamerican-doc":    0.5,
    "gg-best-animated":               0.5,
    "cesar-best-intl-film":           0.5,
    # ── Acting ────────────────────────────────────────────────────────────
    "oscar-best-actress":             0.4,
    "oscar-best-actor":               0.4,
    "cannes-best-actress":            0.4,
    "cannes-best-actor":              0.4,
    "venice-best-actress":            0.4,
    "venice-best-actor":              0.4,
    "venice-volpi-cup-actress":       0.4,
    "venice-volpi-cup-actor":         0.4,
    "berlin-silver-bear-actress":     0.4,
    "berlin-silver-bear-actor":       0.4,
    "bafta-best-actress":             0.4,
    "bafta-best-actor":               0.4,
    "cesar-best-actress":             0.4,
    "cesar-best-actor":               0.4,
    "goya-best-actress":              0.4,
    "goya-best-actor":                0.4,
    "ariel-best-actress":             0.4,
    "ariel-best-actor":               0.4,
    "sansebastian-silver-actress":    0.4,
    "sansebastian-silver-actor":      0.4,
    "sansebastian-silver-shell-actress": 0.4,
    "gg-best-actress-drama":          0.4,
    "gg-best-actor-drama":            0.4,
    # ── Supporting acting ─────────────────────────────────────────────────
    "oscar-best-supporting-actor":    0.3,
    "oscar-best-supporting-actress":  0.3,
    # ── Cinematography ────────────────────────────────────────────────────
    "oscar-best-cinematography":      0.3,
    "bafta-best-cinematography":      0.3,
    "ariel-best-cinematography":      0.3,
    # ── Technical ─────────────────────────────────────────────────────────
    "oscar-best-original-score":      0.1,
    "oscar-best-sound":               0.05,
    "oscar-best-film-editing":        0.1,
    "oscar-best-production-design":   0.1,
    "ariel-best-score":               0.1,
    "ariel-best-editing":             0.1,
    "ficm-best-short":                0.1,
    # ── Legacy duplicate IDs — skip entirely (0.0) ────────────────────────
    "palme_dor":            0.0,
    "golden_lion":          0.0,
    "golden_bear":          0.0,
    "bafta_film":           0.0,
    "bafta_cinematography": 0.0,
    "oscar_picture":        0.0,
    "oscar_director":       0.0,
    "oscar_cinematography": 0.0,
    "oscar_cin_nom":        0.0,
    "sundance_grand_jury":  0.0,
    "cannes_best_director": 0.0,
    "berlin_silver_bear":   0.0,
    "cannes_grand_prix":    0.0,
    "venice_silver_lion":   0.0,
    "tiff_platform":        0.0,
    "asc_award":            0.0,
}

DEFAULT_CATEGORY_MULTIPLIER: float = 0.6


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
    """Accumulate award scores across festivals.

    - New film  → INSERT with initial score.
    - Existing pending film → ADD new points to existing score + merge awards_json.
    - Existing completed film → skip (already ingested, score irrelevant).
    """
    if not rows:
        return {"inserted": 0, "updated": 0}

    tmdb_ids = [r["tmdb_id"] for r in rows]

    # Fetch existing rows (score + counts + awards_json + status)
    existing: dict[int, dict] = {}
    for i in range(0, len(tmdb_ids), 50):
        chunk = tmdb_ids[i:i + 50]
        res = (
            db.table("candidates")
            .select("tmdb_id, prisma_score, award_count, win_count, nom_count, awards_json, status")
            .in_("tmdb_id", chunk)
            .execute()
        )
        for rec in res.data or []:
            existing[rec["tmdb_id"]] = rec

    to_insert: list[dict] = []
    to_update: list[dict] = []

    for row in rows:
        tid = row["tmdb_id"]
        if tid not in existing:
            to_insert.append(row)
        else:
            ex = existing[tid]
            # Skip films already ingested — their score column is historical
            if ex.get("status") == "completed":
                continue
            # Accumulate
            new_score  = float(ex.get("prisma_score") or 0) + float(row["prisma_score"])
            new_wins   = int(ex.get("win_count")   or 0) + int(row["win_count"])
            new_noms   = int(ex.get("nom_count")   or 0) + int(row["nom_count"])
            new_awards = int(ex.get("award_count") or 0) + int(row["award_count"])
            merged_json = (ex.get("awards_json") or []) + (row.get("awards_json") or [])
            to_update.append({
                "tmdb_id":      tid,
                "prisma_score": round(new_score, 2),
                "win_count":    new_wins,
                "nom_count":    new_noms,
                "award_count":  new_awards,
                "awards_json":  merged_json,
            })

    inserted = 0
    updated  = 0

    if dry_run:
        return {"inserted": len(to_insert), "updated": len(to_update), "dry_run": True}

    # Insert new candidates in batches of 50
    for i in range(0, len(to_insert), 50):
        batch = to_insert[i:i + 50]
        try:
            db.table("candidates").insert(batch).execute()
            inserted += len(batch)
        except Exception as e:
            # Fall back row-by-row on batch failure
            for rec in batch:
                try:
                    db.table("candidates").insert(rec).execute()
                    inserted += 1
                except Exception as e2:
                    print(f"    ✗ insert failed TMDB {rec.get('tmdb_id')}: {e2}")

    # Update accumulated scores one-by-one (Supabase REST has no batch UPDATE)
    for upd in to_update:
        try:
            db.table("candidates").update({
                "prisma_score": upd["prisma_score"],
                "win_count":    upd["win_count"],
                "nom_count":    upd["nom_count"],
                "award_count":  upd["award_count"],
                "awards_json":  upd["awards_json"],
            }).eq("tmdb_id", upd["tmdb_id"]).execute()
            updated += 1
        except Exception as e:
            print(f"    ✗ update failed TMDB {upd['tmdb_id']}: {e}")

    return {"inserted": inserted, "updated": updated}


# ─── sync-completed ───────────────────────────────────────────────────────────

def sync_completed(db, dry_run: bool) -> dict:
    """Ensure every tmdb_id in the works table is marked completed in candidates.

    Three cases handled:
      A. tmdb_id in works but NOT in candidates  → INSERT as completed
      B. tmdb_id in works AND in candidates with status != 'completed' → UPDATE
      C. tmdb_id in works AND in candidates already completed → skip
    """
    # ── 1. Fetch ALL tmdb_ids + work_ids from works table ────────────────────
    all_works: list[dict] = []
    offset = 0
    while True:
        batch = (
            db.table("works")
            .select("tmdb_id, id")
            .not_.is_("tmdb_id", "null")
            .range(offset, offset + 999)
            .execute()
            .data or []
        )
        all_works.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    work_map: dict[int, str] = {w["tmdb_id"]: w["id"] for w in all_works if w.get("tmdb_id")}
    work_ids = list(work_map.keys())
    print(f"  Works in Supabase:     {len(work_map)}")

    if not work_ids:
        print("  Nothing to sync.")
        return {"updated": 0, "inserted": 0}

    # ── 2. Fetch ALL tmdb_ids + status from candidates table ─────────────────
    existing: dict[int, str] = {}  # tmdb_id → status
    for i in range(0, len(work_ids), 200):
        chunk = work_ids[i:i + 200]
        res = db.table("candidates").select("tmdb_id, status").in_("tmdb_id", chunk).execute()
        for rec in res.data or []:
            existing[rec["tmdb_id"]] = rec["status"]

    print(f"  Already in candidates: {len(existing)}")

    # ── 3. Partition into insert / update groups ──────────────────────────────
    to_insert: list[int] = []  # in works, missing from candidates
    to_update: list[int] = []  # in candidates but not yet completed

    for tid in work_ids:
        if tid not in existing:
            to_insert.append(tid)
        elif existing[tid] != "completed":
            to_update.append(tid)
        # else: already completed — skip

    print(f"  To insert (new):       {len(to_insert)}")
    print(f"  To update (complete):  {len(to_update)}")
    print(f"  Already completed:     {len(work_ids) - len(to_insert) - len(to_update)}")

    if dry_run:
        print("  [dry-run] No changes written.")
        return {"inserted": len(to_insert), "updated": len(to_update), "dry_run": True}

    # ── 4a. INSERT missing rows as completed ──────────────────────────────────
    inserted = 0
    for i in range(0, len(to_insert), 50):
        chunk = to_insert[i:i + 50]
        rows = [
            {
                "tmdb_id":      tid,
                "title":        work_map[tid],   # work_id is the best title proxy we have
                "status":       "completed",
                "work_id":      work_map[tid],
                "prisma_score": 0,
            }
            for tid in chunk
        ]
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

    # ── 4b. UPDATE pending/failed rows → completed ────────────────────────────
    updated = 0
    for i in range(0, len(to_update), 200):
        chunk = to_update[i:i + 200]
        try:
            db.table("candidates").update({
                "status":      "completed",
                "work_id":     None,   # will be filled by individual update below
                "ingested_at": "now()",
            }).in_("tmdb_id", chunk).execute()
            updated += len(chunk)
        except Exception as e:
            print(f"    ✗ bulk update error: {e}")
            # Fall back one-by-one
            for tid in chunk:
                try:
                    db.table("candidates").update({
                        "status":      "completed",
                        "work_id":     work_map.get(tid),
                        "ingested_at": "now()",
                    }).eq("tmdb_id", tid).execute()
                    updated += 1
                except Exception:
                    pass

    print(f"  ✓ Inserted {inserted} new completed rows")
    print(f"  ✓ Updated  {updated} rows → completed")
    return {"inserted": inserted, "updated": updated}


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

            # ── Tiered scoring ────────────────────────────────────────────
            clean_key   = award_key  # e.g. "oscar-best-picture"
            fest_weight = FESTIVAL_TIER_WEIGHT.get(festival, DEFAULT_FESTIVAL_WEIGHT)
            cat_mult    = CATEGORY_FILM_MULTIPLIER.get(clean_key, DEFAULT_CATEGORY_MULTIPLIER)

            if cat_mult == 0.0:
                continue  # legacy duplicate ID — skip entirely

            if result == "win":
                score_contrib = pts * fest_weight * cat_mult
            else:
                score_contrib = pts * fest_weight * cat_mult * 0.4
            # ─────────────────────────────────────────────────────────────

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
            fd["awards"].append({
                "award_id":  full_id,
                "result":    result,
                "pts":       pts,
                "fest_w":    fest_weight,
                "cat_mult":  cat_mult,
                "contrib":   round(score_contrib, 3),
            })

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
        result = sync_completed(db, args.dry_run)
        ins = result.get("inserted", 0)
        upd = result.get("updated", 0)
        print(f"Done. inserted={ins}  updated={upd}")
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
