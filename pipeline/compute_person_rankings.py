"""
pipeline/compute_person_rankings.py
─────────────────────────────────────
Computes PRISMA ranking scores for people by role, based on their work_awards.

Score formula per award row:
  points = award.scoring_points × result_multiplier × tier_weight

  result_multiplier: win=1.0, nomination=0.3
  tier_weight:       A=1.0, B=0.7, C=0.4, D=0.2

Award attribution:
  - If work_awards.person_id is set → credit that person in their role(s) for that work
  - If work_awards.person_id is null → credit all people on the film (0.5× multiplier)

Stores results in ranking_scores:
  entity_type='person', entity_id=person_id, context=role

Usage:
  python3 pipeline/compute_person_rankings.py
  python3 pipeline/compute_person_rankings.py --dry-run
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv(".env.local")
from supabase import create_client

RESULT_MULTIPLIER = {"win": 1.0, "nomination": 0.3}
TIER_WEIGHT       = {"A": 1.0, "B": 0.7, "C": 0.4, "D": 0.2}


def paginate(db_query_fn) -> list[dict]:
    """Fetch all rows from a paginated Supabase query."""
    rows = []
    offset = 0
    while True:
        batch = db_query_fn(offset)
        rows.extend(batch.data)
        if len(batch.data) < 1000:
            break
        offset += 1000
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Compute but don't write to DB")
    args = parser.parse_args()

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    # ── 1. Load work_awards with award metadata ────────────────────────────────
    print("Fetching work_awards...")
    all_wa = paginate(
        lambda off: db.table("work_awards")
            .select("work_id, award_id, person_id, result, awards(scoring_points, tier)")
            .range(off, off + 999)
            .execute()
    )
    print(f"  {len(all_wa)} work_awards rows")

    # ── 2. Load work_people (person → role mapping per work) ──────────────────
    print("Fetching work_people...")
    all_wp = paginate(
        lambda off: db.table("work_people")
            .select("work_id, person_id, role")
            .range(off, off + 999)
            .execute()
    )
    print(f"  {len(all_wp)} work_people rows")

    # Build lookup: work_id → [(person_id, role)]
    work_to_people: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for wp in all_wp:
        work_to_people[wp["work_id"]].append((wp["person_id"], wp["role"]))

    # ── 3. Compute scores per (person_id, role) ───────────────────────────────
    person_role_scores: dict[tuple, float] = defaultdict(float)
    person_role_wins:   dict[tuple, int]   = defaultdict(int)
    person_role_noms:   dict[tuple, int]   = defaultdict(int)

    unattributed = 0  # work_awards with no person_id
    attributed   = 0  # work_awards with person_id resolved

    for wa in all_wa:
        award = wa.get("awards") or {}
        scoring_points = award.get("scoring_points") or 0
        tier           = award.get("tier") or "C"
        tier_weight    = TIER_WEIGHT.get(tier, 0.4)
        result         = wa.get("result") or "nomination"
        result_mult    = RESULT_MULTIPLIER.get(result, 0.3)

        base_points = scoring_points * result_mult * tier_weight
        work_id     = wa["work_id"]
        award_pid   = wa.get("person_id")

        if award_pid:
            # Award attributed to a specific person — find their role(s) in this work
            attributed += 1
            roles = [role for pid, role in work_to_people[work_id] if pid == award_pid]
            for role in roles:
                key = (award_pid, role)
                person_role_scores[key] += base_points
                if result == "win":   person_role_wins[key]  += 1
                else:                 person_role_noms[key]  += 1
        else:
            # Film-level award — credit all people on the film at 0.5×
            unattributed += 1
            for pid, role in work_to_people[work_id]:
                key = (pid, role)
                person_role_scores[key] += base_points * 0.5
                if result == "win":   person_role_wins[key]  += 1
                else:                 person_role_noms[key]  += 1

    print(f"\nAttribution: {attributed} person-specific · {unattributed} film-level")
    print(f"Unique (person, role) pairs: {len(person_role_scores)}")

    # ── 4. Rank within each role ──────────────────────────────────────────────
    role_entries: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for (person_id, role), score in person_role_scores.items():
        role_entries[role].append((person_id, score))

    ranking_rows = []
    for role, entries in role_entries.items():
        entries.sort(key=lambda x: -x[1])
        for rank, (person_id, score) in enumerate(entries, 1):
            ranking_rows.append({
                "entity_type": "person",
                "entity_id":   person_id,
                "context":     role,
                "score":       round(score, 2),
                "rank":        rank,
            })

    print(f"Ranking rows to write: {len(ranking_rows)}")

    if args.dry_run:
        print("\nDRY RUN — not writing to DB")
    else:
        # ── 5. Delete existing person rankings, then insert fresh ──────────────
        print("\nClearing existing person rankings...")
        db.table("ranking_scores").delete().eq("entity_type", "person").execute()

        print("Inserting ranking rows...")
        batch_size = 200
        for i in range(0, len(ranking_rows), batch_size):
            db.table("ranking_scores").insert(ranking_rows[i:i + batch_size]).execute()
        print(f"  Inserted {len(ranking_rows)} rows")

    # ── 6. Print top 10 per key role ──────────────────────────────────────────
    print()
    for role in ["director", "actor", "cinematography", "composer"]:
        if role not in role_entries:
            continue
        top = sorted(role_entries[role], key=lambda x: -x[1])[:10]
        print(f"Top {role}s by award score:")
        for i, (pid, score) in enumerate(top, 1):
            key = (pid, role)
            w = person_role_wins.get(key, 0)
            n = person_role_noms.get(key, 0)
            name = pid.replace("person_", "").replace("-", " ").title()
            print(f"  #{i:2d} {name:<30} {score:7.1f}pts  ({w}W/{n}N)")
        print()


if __name__ == "__main__":
    main()
