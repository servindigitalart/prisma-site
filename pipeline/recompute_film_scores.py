"""
pipeline/recompute_film_scores.py
──────────────────────────────────
Recomputes numeric_score for all works using the PRISMA scoring formula:

  prisma_score = cultural_weight×0.35 + awards_score×0.30 + imdb_score×0.20 + authorship_score×0.15

Data sources (DB fields are null; using best available proxies):
  cultural_weight  → color_consensus_strength from pipeline/derived/color/*.json (already 0-1)
  awards_score     → sum(scoring_points × result_multiplier) from work_awards, normalized to 0-1
                     using catalog max as ceiling; 0 for works with no awards
  imdb_score       → log1p(tmdb_popularity) / log1p(catalog_max_popularity)
                     proxy for imdb_rating (unavailable: 0/225 works have it)
  authorship_score → color_rank from color_assignments (AI confidence in the iconic color, 0-1)
                     proxy for visual distinctiveness / auteur strength

Also:
  - Writes back cultural_weight, authorship_score, popularity_score, ai_confidence to color_assignments
  - Recomputes tier and tier_rank within each color group
  - Updates ranking_scores table for entity_type='work', context='global'

Usage:
  python3 pipeline/recompute_film_scores.py
  python3 pipeline/recompute_film_scores.py --dry-run
"""

import os
import sys
import math
import json
import glob
import argparse
from math import log1p
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv(".env.local")
from supabase import create_client

WEIGHTS = {
    "cultural": 0.35,
    "awards":   0.30,
    "imdb":     0.20,
    "author":   0.15,
}

# Tier thresholds (applied per-color after ranking)
TIER_THRESHOLDS = [
    ("canon",      95),
    ("core",       85),
    ("strong",     70),
    ("peripheral", 50),
]


def load_consensus_strengths() -> dict[str, float]:
    """Load color_consensus_strength from all derived JSON files."""
    result = {}
    for fp in glob.glob("pipeline/derived/color/*.json"):
        try:
            with open(fp) as f:
                d = json.load(f)
            work_id = d.get("work_id")
            cs = (d.get("cultural_memory") or {}).get("color_consensus_strength")
            if work_id and cs is not None:
                result[work_id] = float(cs)
        except Exception:
            pass
    return result


def compute_raw_award_scores(db) -> dict[str, float]:
    """Compute sum(scoring_points × result_multiplier) per work from work_awards."""
    RESULT_MULT = {"win": 1.0, "nomination": 0.3}
    wa = db.table("work_awards").select("work_id, result, awards(scoring_points, tier)").execute()
    scores: dict[str, float] = defaultdict(float)
    for row in wa.data:
        award = row.get("awards") or {}
        pts = award.get("scoring_points") or 0
        mult = RESULT_MULT.get(row.get("result", "nomination"), 0.3)
        scores[row["work_id"]] += pts * mult
    return dict(scores)


def assign_tier(score_0_100: float) -> str:
    """Assign tier label from 0-100 score."""
    for tier, threshold in TIER_THRESHOLDS:
        if score_0_100 >= threshold:
            return tier
    return "uncertain"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Compute but don't write to DB")
    args = parser.parse_args()

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    # ── 1. Load all color_assignments ─────────────────────────────────────────
    print("Loading color_assignments...")
    ca_rows = db.table("color_assignments").select(
        "work_id, color_iconico, color_rank, numeric_score"
    ).execute().data
    print(f"  {len(ca_rows)} assignments")

    # Record old scores for before/after comparison
    old_scores: dict[str, float | None] = {r["work_id"]: r.get("numeric_score") for r in ca_rows}

    # ── 2. Load works (tmdb_popularity) ───────────────────────────────────────
    print("Loading works...")
    works_rows = db.table("works").select("id, tmdb_popularity").execute().data
    tmdb_pop: dict[str, float] = {
        w["id"]: float(w["tmdb_popularity"])
        for w in works_rows if w.get("tmdb_popularity") is not None
    }
    max_pop = max(tmdb_pop.values()) if tmdb_pop else 1.0
    print(f"  {len(tmdb_pop)} works with tmdb_popularity (max={max_pop:.2f})")

    # ── 3. Load color_consensus_strength from JSON files ─────────────────────
    print("Loading color_consensus_strength from derived JSON files...")
    consensus = load_consensus_strengths()
    print(f"  {len(consensus)} files parsed")

    # ── 4. Compute raw award scores, normalize ────────────────────────────────
    print("Computing award scores...")
    raw_award = compute_raw_award_scores(db)
    max_award = max(raw_award.values()) if raw_award else 1.0
    print(f"  {len(raw_award)} works with awards (max raw score={max_award:.1f})")

    # ── 5. Compute new prisma_score per work ──────────────────────────────────
    print("\nComputing new prisma_score for each work...")

    # Build color_rank lookup from ca_rows
    color_rank_map: dict[str, float] = {
        r["work_id"]: float(r["color_rank"]) if r.get("color_rank") is not None else 0.75
        for r in ca_rows
    }
    color_iconico_map: dict[str, str] = {
        r["work_id"]: r["color_iconico"]
        for r in ca_rows if r.get("color_iconico")
    }

    new_scores: dict[str, dict] = {}
    catalog_mean_pop = log1p(sum(tmdb_pop.values()) / len(tmdb_pop)) if tmdb_pop else 0.5

    for work_id in {r["work_id"] for r in ca_rows}:
        # cultural_weight: color_consensus_strength (0-1)
        cultural = consensus.get(work_id, 0.80)  # default to 0.80 if JSON missing

        # awards_score: normalized 0-1
        awards_raw = raw_award.get(work_id, 0.0)
        awards = awards_raw / max_award

        # imdb_score: log-normalized tmdb_popularity (proxy)
        pop = tmdb_pop.get(work_id)
        if pop is not None:
            imdb = log1p(pop) / log1p(max_pop)
        else:
            # Use catalog mean as fallback (~0.78 of log-normalized)
            imdb = catalog_mean_pop / log1p(max_pop)

        # authorship_score: color_rank (0-1, AI color assignment confidence)
        author = color_rank_map.get(work_id, 0.75)

        # Weighted sum → 0-1
        prisma = (
            WEIGHTS["cultural"] * cultural
            + WEIGHTS["awards"]  * awards
            + WEIGHTS["imdb"]    * imdb
            + WEIGHTS["author"]  * author
        )
        prisma = round(min(max(prisma, 0.0), 1.0), 4)

        new_scores[work_id] = {
            "work_id":          work_id,
            "prisma_score":     prisma,
            "cultural_weight":  round(cultural, 4),
            "awards_score":     round(awards, 4),
            "imdb_score":       round(imdb, 4),
            "authorship_score": round(author, 4),
        }

    # ── 6. Before/after comparison ────────────────────────────────────────────
    ranked_new = sorted(new_scores.values(), key=lambda x: -x["prisma_score"])

    print("\n─── TOP 20 BEFORE (old numeric_score) ───────────────────────────────")
    old_with_score = [(wid, s) for wid, s in old_scores.items() if s is not None]
    if old_with_score:
        for i, (wid, s) in enumerate(sorted(old_with_score, key=lambda x: -x[1])[:20], 1):
            print(f"  #{i:2d} {wid.replace('work_', ''):<45} {s:.4f}")
    else:
        print("  (all null — no previous scores)")

    print("\n─── TOP 20 AFTER (new prisma_score) ─────────────────────────────────")
    for i, row in enumerate(ranked_new[:20], 1):
        wid = row["work_id"].replace("work_", "")
        s   = row["prisma_score"]
        c   = row["cultural_weight"]
        a   = row["awards_score"]
        p   = row["imdb_score"]
        au  = row["authorship_score"]
        print(f"  #{i:2d} {wid:<43}  {s:.4f}  [C={c:.2f} Aw={a:.2f} P={p:.2f} Au={au:.2f}]")

    if args.dry_run:
        print("\nDRY RUN — not writing to DB.")
        return

    # ── 7. Update color_assignments ───────────────────────────────────────────
    print(f"\nUpdating {len(new_scores)} color_assignments rows...")

    # Group by color for tier_rank computation
    color_groups: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for row in new_scores.values():
        color = color_iconico_map.get(row["work_id"])
        if color:
            color_groups[color].append((row["work_id"], row["prisma_score"]))

    # Score on 0-100 scale for tier assignment
    score_100 = {wid: round(row["prisma_score"] * 100, 2) for wid, row in new_scores.items()}

    # tier_rank: ONLY for canon-tier films, 1-30 max, ranked within each color.
    # NULL for all other tiers (schema constraint: BETWEEN 1 AND 30, manual canon only).
    tier_rank_map: dict[str, int | None] = {}
    for color, entries in color_groups.items():
        entries.sort(key=lambda x: -x[1])
        canon_rank = 0
        for work_id, score in entries:
            if score_100.get(work_id, 0) >= 95:
                canon_rank += 1
                tier_rank_map[work_id] = canon_rank if canon_rank <= 30 else None
            else:
                tier_rank_map[work_id] = None

    # DB stores cultural_weight / authorship_score / popularity_score on 0-100 scale
    batch_size = 50
    items = list(new_scores.values())
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        for row in batch:
            wid = row["work_id"]
            s100 = score_100[wid]
            db.table("color_assignments").update({
                "numeric_score":    s100,
                "cultural_weight":  round(row["cultural_weight"] * 100, 2),
                "authorship_score": round(row["authorship_score"] * 100, 2),
                "popularity_score": round(row["imdb_score"] * 100, 2),
                "ai_confidence":    row["cultural_weight"],  # NUMERIC(4,3): 0-1 range
                "tier":             assign_tier(s100),
                "tier_rank":        tier_rank_map.get(wid),  # None for non-canon
            }).eq("work_id", wid).execute()

    print(f"  color_assignments updated.")

    # ── 8. Update ranking_scores for works ────────────────────────────────────
    print("Updating ranking_scores (entity_type='work', context='global')...")
    db.table("ranking_scores").delete().eq("entity_type", "work").eq("context", "global").execute()

    ranking_rows = []
    for rank, row in enumerate(ranked_new, 1):
        ranking_rows.append({
            "entity_type": "work",
            "entity_id":   row["work_id"],
            "context":     "global",
            "score":       round(row["prisma_score"] * 100, 2),
            "rank":        rank,
        })

    for i in range(0, len(ranking_rows), 200):
        db.table("ranking_scores").insert(ranking_rows[i:i + 200]).execute()

    print(f"  {len(ranking_rows)} ranking rows written.")

    # ── 9. Summary stats ──────────────────────────────────────────────────────
    scores_100 = [v * 100 for v in [r["prisma_score"] for r in new_scores.values()]]
    import statistics
    print(f"\nScore distribution (0-100 scale):")
    print(f"  min={min(scores_100):.2f}  max={max(scores_100):.2f}  "
          f"mean={statistics.mean(scores_100):.2f}  median={statistics.median(scores_100):.2f}")

    tier_dist = defaultdict(int)
    for s in scores_100:
        tier_dist[assign_tier(s)] += 1
    print(f"\nTier distribution:")
    for tier, _ in TIER_THRESHOLDS:
        print(f"  {tier:<12} {tier_dist[tier]:>4}")
    print(f"  {'uncertain':<12} {tier_dist['uncertain']:>4}")


if __name__ == "__main__":
    main()
