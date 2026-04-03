"""
pipeline/compute_rankings.py
──────────────────────────────
Computes ranking scores for both works and people.

WORK SCORES (context='global'):
  Prestige driven by award wins/nominations weighted by festival tier.
  Secondary factors: IMDb rating, TMDB popularity, Criterion/MUBI presence.

PERSON SCORES (context=role):
  For each person × role combination:
    score = Σ [ get_award_weight(award_id, role, tier)
                × (1.0 if win else 0.2) × 100 ]
          + (film_count × 0.5)   # small catalog bonus

  Post-processing:
    - Per-film cap: no single film > 40% of total raw score
    - Catalog normalization: penalty for people with only 1-4 films in catalog

  NOTE on actors/actresses:
    The work_people table stores everyone with role='actor'.
    We use the people.gender field to split rankings:
      gender=2 → ranked as 'actor'   (Actors leaderboard)
      gender=1 → ranked as 'actress' (Actresses leaderboard)
      gender=0 → included in 'actor' leaderboard (unknown)

Usage:
  python3 pipeline/compute_rankings.py              # full run
  python3 pipeline/compute_rankings.py --works-only
  python3 pipeline/compute_rankings.py --people-only
  python3 pipeline/compute_rankings.py --dry-run
  python3 pipeline/compute_rankings.py --top 20
"""

import sys
import argparse
import os
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv(".env.local")
from supabase import create_client
from ranking_matrix import get_award_weight, FESTIVAL_TIER_MULTIPLIERS

# ─── Config ───────────────────────────────────────────────────────────────────

WIN_MULTIPLIER     = 1.0
NOM_MULTIPLIER     = 0.2   # FIX 4: was 0.3 — nominations now worth less
FILM_CATALOG_BONUS = 0.5   # added to person score per film in catalog

ROLE_DISPLAY = {
    "director":       "Directors",
    "cinematography": "Cinematographers",
    "writer":         "Writers",
    "actor":          "Actors",
    "actress":        "Actresses",
    "editor":         "Editors",
    "composer":       "Composers",
}

# Gender codes in people.gender (TMDB convention)
GENDER_FEMALE  = 1
GENDER_MALE    = 2
GENDER_UNKNOWN = 0


# ─── Scoring helpers ──────────────────────────────────────────────────────────

def normalize_score(raw_score: float, film_count: int) -> float:
    """
    FIX 1: Catalog-presence normalization.
    Prevents one heavily-awarded film from dominating the ranking.

    catalog_factor:
      1 film  → 0.60  (significant penalty)
      2 films → 0.75
      3 films → 0.85
      4 films → 0.92
      5+ films→ 1.00  (no penalty)
    """
    factors = {1: 0.60, 2: 0.75, 3: 0.85, 4: 0.92}
    factor = factors.get(min(film_count, 4), 1.0)
    return raw_score * factor


def apply_film_cap(film_scores: dict[str, float], cap_ratio: float = 0.40) -> dict[str, float]:
    """
    FIX 3: Per-film contribution cap.
    If any single film contributes more than cap_ratio of total score,
    that film's contribution is capped at cap_ratio × total.
    film_scores: {work_id: raw_score}
    """
    total = sum(film_scores.values())
    if total == 0:
        return film_scores
    capped = {}
    for work_id, score in film_scores.items():
        if score / total > cap_ratio:
            capped[work_id] = total * cap_ratio
        else:
            capped[work_id] = score
    return capped


# ─── Work scoring ─────────────────────────────────────────────────────────────

def compute_work_scores(db, dry_run: bool) -> list[dict]:
    """
    Compute global ranking scores for all works.

    Score = award_prestige × 0.50
          + imdb_rating    × 0.30
          + popularity     × 0.10
          + criterion_bonus× 0.05
          + mubi_bonus     × 0.05
    """
    print("📊 Computing work scores...")

    works_r = db.table("works").select(
        "id, title, tmdb_popularity, imdb_rating, criterion_title, mubi_title"
    ).execute()
    works = {w["id"]: w for w in works_r.data}

    awards_r = db.table("work_awards").select(
        "work_id, award_id, result, awards(tier)"
    ).execute()

    # Award prestige per work: sum of weighted contributions
    work_prestige: dict[str, float] = defaultdict(float)
    for row in awards_r.data:
        tier = (row.get("awards") or {}).get("tier", "C")
        result_mult = WIN_MULTIPLIER if row["result"] == "win" else NOM_MULTIPLIER
        # Use director weight as film-level prestige proxy
        base = get_award_weight(row["award_id"], "director", tier)
        if base == 0.0:
            base = FESTIVAL_TIER_MULTIPLIERS.get(tier, 0.35) * 0.5
        work_prestige[row["work_id"]] += base * result_mult * 10

    scores = []
    for work_id, w in works.items():
        prestige   = work_prestige.get(work_id, 0.0)
        popularity = min((w.get("tmdb_popularity") or 0) / 20.0, 10.0)
        imdb       = float(w.get("imdb_rating") or 0.0)
        crit_bonus = 5.0 if w.get("criterion_title") else 0.0
        mubi_bonus = 3.0 if w.get("mubi_title") else 0.0

        score = (
            prestige   * 0.50
            + imdb     * 0.30
            + popularity * 0.10
            + crit_bonus * 0.05
            + mubi_bonus * 0.05
        )
        scores.append({
            "entity_id":   work_id,
            "entity_type": "work",
            "context":     "global",
            "score":       round(score, 2),
            "rank":        0,
        })

    scores.sort(key=lambda x: x["score"], reverse=True)
    for i, s in enumerate(scores):
        s["rank"] = i + 1

    if not dry_run:
        for i in range(0, len(scores), 100):
            db.table("ranking_scores").upsert(
                scores[i:i+100],
                on_conflict="entity_type,entity_id,context"
            ).execute()
        print(f"   ✅ Upserted {len(scores)} work scores")
    else:
        print(f"   [DRY RUN] Would upsert {len(scores)} work scores")

    print(f"   Top 5 works:")
    for s in scores[:5]:
        title = works.get(s["entity_id"], {}).get("title", s["entity_id"])
        print(f"     #{s['rank']:3d}  {s['score']:7.2f}  {title}")

    return scores


# ─── Person scoring ───────────────────────────────────────────────────────────

def compute_person_scores(db, dry_run: bool, top_n: int = 10) -> list[dict]:
    """
    Compute ranking scores for each person × role combination.

    For every (person, role) pair:
      1. Collect all films they worked on in that role
      2. Compute per-film award score (weight × win/nom multiplier × 100)
      3. Apply per-film cap (no film > 40% of raw total) — FIX 3
      4. Add catalog bonus: film_count × 0.5
      5. Apply catalog-presence normalization — FIX 1

    FIX 2: actors stored with role='actor' are split into 'actor' / 'actress'
    sub-rankings based on people.gender (1=female → 'actress', 2=male → 'actor').
    """
    print("👤 Computing person scores...")

    wp_r = db.table("work_people").select("person_id, work_id, role").execute()

    # person_id → role → [work_ids]
    person_works: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in wp_r.data:
        person_works[row["person_id"]][row["role"]].append(row["work_id"])

    awards_r = db.table("work_awards").select(
        "work_id, award_id, result, awards(tier)"
    ).execute()

    # work_id → [award rows]
    work_awards: dict[str, list[dict]] = defaultdict(list)
    for row in awards_r.data:
        work_awards[row["work_id"]].append(row)

    # FIX 2: Load gender for all people so we can split actor → actor/actress
    people_r = db.table("people").select("id, name, gender").execute()
    person_gender: dict[str, int] = {p["id"]: (p.get("gender") or 0) for p in people_r.data}
    person_names:  dict[str, str] = {p["id"]: p["name"] for p in people_r.data}

    scores: list[dict] = []

    for person_id, role_map in person_works.items():
        gender = person_gender.get(person_id, GENDER_UNKNOWN)

        for role, film_ids in role_map.items():
            # Determine the effective weight-lookup role:
            # Female actors must be scored using "actress" weights so that
            # best-actress award patterns (weight=1.0) apply to them.
            if role == "actor" and gender == GENDER_FEMALE:
                weight_role = "actress"
                ranking_role = "actress"
            else:
                weight_role = role
                ranking_role = role

            # ── Compute per-film award scores ──────────────────────────────
            film_scores: dict[str, float] = defaultdict(float)
            for work_id in film_ids:
                for award_row in work_awards.get(work_id, []):
                    tier = (award_row.get("awards") or {}).get("tier", "C")
                    result_mult = WIN_MULTIPLIER if award_row["result"] == "win" else NOM_MULTIPLIER
                    weight = get_award_weight(award_row["award_id"], weight_role, tier)
                    film_scores[work_id] += weight * result_mult * 100

            # ── FIX 3: Cap any single film at 40% of raw total ─────────────
            film_scores = apply_film_cap(dict(film_scores))
            award_score = sum(film_scores.values())

            # ── Catalog bonus ──────────────────────────────────────────────
            catalog_bonus = len(film_ids) * FILM_CATALOG_BONUS

            # ── FIX 1: Catalog-presence normalization ──────────────────────
            raw_total = award_score + catalog_bonus
            total = round(normalize_score(raw_total, len(film_ids)), 2)

            if total <= 0 and len(film_ids) < 3:
                continue

            scores.append({
                "entity_id":   person_id,
                "entity_type": "person",
                "context":     ranking_role,
                "score":       total,
                "rank":        0,
            })

    # ── Assign ranks per role ──────────────────────────────────────────────
    role_groups: dict[str, list[dict]] = defaultdict(list)
    for s in scores:
        role_groups[s["context"]].append(s)

    all_ranked: list[dict] = []
    for role, role_scores in role_groups.items():
        role_scores.sort(key=lambda x: x["score"], reverse=True)
        for i, s in enumerate(role_scores):
            s["rank"] = i + 1
        all_ranked.extend(role_scores)

    if not dry_run:
        for i in range(0, len(all_ranked), 100):
            db.table("ranking_scores").upsert(
                all_ranked[i:i+100],
                on_conflict="entity_type,entity_id,context"
            ).execute()
        print(f"   ✅ Upserted {len(all_ranked)} person scores across {len(role_groups)} roles")
    else:
        print(f"   [DRY RUN] Would upsert {len(all_ranked)} person scores")

    # ── Print top N per role ───────────────────────────────────────────────
    for role in sorted(role_groups.keys()):
        top = role_groups[role][:top_n]
        print(f"\n   Top {min(top_n, len(top))} — {ROLE_DISPLAY.get(role, role.title())}:")
        for s in top:
            name = person_names.get(s["entity_id"], s["entity_id"])
            print(f"     #{s['rank']:3d}  {s['score']:8.2f}  {name}")

    return all_ranked


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compute PRISMA ranking scores")
    parser.add_argument("--works-only",  action="store_true")
    parser.add_argument("--people-only", action="store_true")
    parser.add_argument("--dry-run",     action="store_true")
    parser.add_argument("--top",         type=int, default=10, metavar="N")
    args = parser.parse_args()

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    if not args.people_only:
        compute_work_scores(db, args.dry_run)
        print()

    if not args.works_only:
        compute_person_scores(db, args.dry_run, top_n=args.top)
        print()

    print("✅ Rankings complete")


if __name__ == "__main__":
    main()
