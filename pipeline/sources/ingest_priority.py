"""
pipeline/sources/ingest_priority.py
─────────────────────────────────────
Generates a prestige-ordered list of TMDB IDs to ingest, prioritising
films that have the most award-relevant wins/nominations across all
festivals in our DB — but are NOT yet in the catalog.

Strategy:
  1. Query Wikidata for all winners/nominees of every award in AWARD_QUERY_MAP
     (wins-only for speed; adjust --nominations to include nominations too).
  2. Score each film by award prestige:
       win  × tier_multiplier  (A=1.0, B=0.6, C=0.35)
       nom  × tier_multiplier × 0.3
  3. Resolve TMDB IDs via IMDb ID (fast, exact) or TMDB title+year search.
  4. Cross-check against works already in catalog (by tmdb_id or imdb_id).
  5. Output ranked list → pipeline/sources/most_awarded_not_in_catalog.txt
     Format: TMDB_ID  # Title (Year) — score: N.N  [awards: X wins, Y noms]

Usage:
  python pipeline/sources/ingest_priority.py
  python pipeline/sources/ingest_priority.py --nominations       # include noms
  python pipeline/sources/ingest_priority.py --limit 200         # top N films
  python pipeline/sources/ingest_priority.py --tier A            # only tier-A awards
  python pipeline/sources/ingest_priority.py --dry-run           # print, don't write
  python pipeline/sources/ingest_priority.py --output custom.txt
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env.local")
load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from supabase import create_client
from pipeline.enrich_awards_wikidata import (
    AWARD_QUERY_MAP,
    fetch_award_winners,
    fetch_award_nominees,
    RATE_LIMIT_SLEEP,
)

# ─── Config ──────────────────────────────────────────────────────────────────

TMDB_API_KEY  = os.environ.get("TMDB_API_KEY", "")
TMDB_SEARCH   = "https://api.themoviedb.org/3/search/movie"
TMDB_FIND     = "https://api.themoviedb.org/3/find/{imdb_id}"

TIER_WIN_WEIGHT = {"A": 1.0, "B": 0.6, "C": 0.35}
NOM_MULTIPLIER  = 0.3

DEFAULT_OUTPUT  = Path(__file__).parent / "most_awarded_not_in_catalog.txt"
DEFAULT_LIMIT   = 300

# ─── Data structures ─────────────────────────────────────────────────────────

@dataclass
class AwardedFilm:
    """Aggregates award data for a single film from Wikidata."""
    film_label: str
    year:       int | None
    film_qid:   str | None
    imdb_id:    str | None
    score:      float = 0.0
    wins:       int   = 0
    noms:       int   = 0
    award_ids:  list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        """Canonical dedup key — prefer Wikidata QID, fall back to normalised title+year."""
        if self.film_qid:
            return self.film_qid
        norm = re.sub(r"[^a-z0-9]", "", self.film_label.lower())
        return f"{norm}_{self.year or 'x'}"


# ─── TMDB resolution ─────────────────────────────────────────────────────────

def tmdb_find_by_imdb(imdb_id: str) -> int | None:
    """Use TMDB /find endpoint to resolve IMDb ID → TMDB movie ID."""
    try:
        r = requests.get(
            TMDB_FIND.format(imdb_id=imdb_id),
            params={"api_key": TMDB_API_KEY, "external_source": "imdb_id"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json().get("movie_results", [])
        if results:
            return results[0]["id"]
    except Exception as e:
        print(f"    [TMDB/find] {imdb_id}: {e}", file=sys.stderr)
    return None


def tmdb_search_by_title(title: str, year: int | None) -> tuple[int | None, str]:
    """Search TMDB by title+year. Returns (tmdb_id, resolved_title)."""
    params: dict = {"api_key": TMDB_API_KEY, "query": title, "include_adult": "false"}
    if year:
        params["year"] = year
    try:
        r = requests.get(TMDB_SEARCH, params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            top = results[0]
            return top["id"], top.get("title", title)
        # Retry without year if no result
        if year and "year" in params:
            del params["year"]
            r2 = requests.get(TMDB_SEARCH, params=params, timeout=10)
            r2.raise_for_status()
            results2 = r2.json().get("results", [])
            if results2:
                top = results2[0]
                return top["id"], top.get("title", title)
    except Exception as e:
        print(f"    [TMDB/search] {title!r} ({year}): {e}", file=sys.stderr)
    return None, title


# ─── Catalog index ────────────────────────────────────────────────────────────

def load_catalog_index(db) -> tuple[set[int], set[str]]:
    """
    Returns (catalog_tmdb_ids, catalog_imdb_ids) — the films already ingested.
    """
    r = db.table("works").select("tmdb_id, imdb_id").execute()
    tmdb_ids: set[int]  = set()
    imdb_ids: set[str]  = set()
    for row in r.data:
        if row.get("tmdb_id"):
            tmdb_ids.add(int(row["tmdb_id"]))
        if row.get("imdb_id"):
            imdb_ids.add(row["imdb_id"])
    return tmdb_ids, imdb_ids


# ─── Award fetching + scoring ─────────────────────────────────────────────────

def build_award_film_map(
    tier_filter: str | None,
    include_nominations: bool,
) -> dict[str, AwardedFilm]:
    """
    Fetch all awarded films from Wikidata for every award in AWARD_QUERY_MAP.
    Returns a dict keyed by AwardedFilm.key.
    """
    films: dict[str, AwardedFilm] = {}

    awards = {
        aid: meta for aid, meta in AWARD_QUERY_MAP.items()
        if tier_filter is None or meta["tier"] == tier_filter
    }

    total = len(awards)
    for i, (award_id, meta) in enumerate(awards.items(), 1):
        qid   = meta["qid"]
        tier  = meta["tier"]
        label = meta["label"]
        win_w = TIER_WIN_WEIGHT[tier]
        nom_w = win_w * NOM_MULTIPLIER

        print(f"  [{i:3d}/{total}] {award_id} (QID: {qid}, tier: {tier})")

        # ── Wins ──
        wins = fetch_award_winners(qid)
        print(f"         → {len(wins)} wins")
        time.sleep(RATE_LIMIT_SLEEP)

        for rec in wins:
            _add_record(films, rec, award_id, win_w, is_win=True)

        # ── Nominations (optional) ──
        if include_nominations:
            noms = fetch_award_nominees(qid)
            print(f"         → {len(noms)} nominations")
            time.sleep(RATE_LIMIT_SLEEP)
            for rec in noms:
                _add_record(films, rec, award_id, nom_w, is_win=False)

    return films


def _add_record(
    films: dict[str, AwardedFilm],
    rec:   dict,
    award_id: str,
    weight: float,
    is_win: bool,
) -> None:
    """Upsert a Wikidata record into the films dict, accumulating score."""
    af = AwardedFilm(
        film_label=rec["film_label"],
        year=rec.get("year"),
        film_qid=rec.get("film_qid"),
        imdb_id=rec.get("imdb_id"),
    )
    key = af.key
    if key not in films:
        films[key] = af
    else:
        af = films[key]
        # Update IMDb ID if we got one now
        if not af.imdb_id and rec.get("imdb_id"):
            af.imdb_id = rec["imdb_id"]

    af.score += weight
    if is_win:
        af.wins += 1
    else:
        af.noms += 1
    if award_id not in af.award_ids:
        af.award_ids.append(award_id)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate prestige-ordered TMDB ingest list from award data"
    )
    parser.add_argument("--nominations", action="store_true",
                        help="Include nominations (slower, more results)")
    parser.add_argument("--tier", choices=["A", "B", "C"], default=None,
                        help="Only process awards of this tier")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"Max films to output (default: {DEFAULT_LIMIT})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output file path")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print to stdout, do not write file")
    args = parser.parse_args()

    db = create_client(
        os.environ["PUBLIC_SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )

    # ── 1. Load catalog ──────────────────────────────────────────────────────
    print("📚 Loading catalog index from DB...")
    catalog_tmdb, catalog_imdb = load_catalog_index(db)
    print(f"   {len(catalog_tmdb)} works in catalog "
          f"({len(catalog_imdb)} with IMDb ID)")

    # ── 2. Fetch award data from Wikidata ────────────────────────────────────
    tier_label = args.tier or "all tiers"
    nom_label  = "+ nominations" if args.nominations else "wins only"
    print(f"\n🔍 Fetching award winners from Wikidata "
          f"({tier_label}, {nom_label})...")
    films = build_award_film_map(
        tier_filter=args.tier,
        include_nominations=args.nominations,
    )
    print(f"\n   {len(films)} unique awarded films found in Wikidata\n")

    # ── 3. Filter out films already in catalog ───────────────────────────────
    not_in_catalog: list[AwardedFilm] = []
    for af in films.values():
        in_cat = False
        if af.imdb_id and af.imdb_id in catalog_imdb:
            in_cat = True
        # We don't have TMDB ID yet here — will resolve below only for candidates
        if not in_cat:
            not_in_catalog.append(af)

    print(f"   {len(not_in_catalog)} films not yet in catalog")

    # ── 4. Sort by prestige score ─────────────────────────────────────────────
    not_in_catalog.sort(key=lambda af: af.score, reverse=True)
    candidates = not_in_catalog[:args.limit * 2]  # resolve more than we need

    # ── 5. Resolve TMDB IDs ───────────────────────────────────────────────────
    print(f"\n🎬 Resolving TMDB IDs for top {len(candidates)} candidates...")
    resolved: list[tuple[int, AwardedFilm, str]] = []  # (tmdb_id, film, resolved_title)

    for i, af in enumerate(candidates, 1):
        if len(resolved) >= args.limit:
            break

        tmdb_id: int | None = None
        resolved_title = af.film_label

        # Try IMDb → TMDB first (fastest, most accurate)
        if af.imdb_id:
            tmdb_id = tmdb_find_by_imdb(af.imdb_id)
            time.sleep(0.25)

        # Fall back to title+year search
        if not tmdb_id:
            tmdb_id, resolved_title = tmdb_search_by_title(af.film_label, af.year)
            time.sleep(0.25)

        if not tmdb_id:
            print(f"    [{i:4d}] ⚠  No TMDB ID: {af.film_label!r} ({af.year})")
            continue

        # Double-check against catalog TMDB IDs
        if tmdb_id in catalog_tmdb:
            continue

        resolved.append((tmdb_id, af, resolved_title))
        print(
            f"    [{i:4d}] ✅  {resolved_title!r:<45s} "
            f"({af.year or '?'})  score={af.score:.2f}  "
            f"[{af.wins}W/{af.noms}N]  tmdb={tmdb_id}"
        )

    # ── 6. Build output lines ─────────────────────────────────────────────────
    lines: list[str] = [
        "# PRISMA — Prestige-ordered ingest list",
        "# Generated by: pipeline/sources/ingest_priority.py",
        f"# Tier filter: {tier_label}  |  Mode: {nom_label}",
        f"# Total candidates after catalog dedup: {len(not_in_catalog)}",
        f"# Output limit: {args.limit}",
        f"# Format: TMDB_ID  # Title (Year) — score: N.N  [Nw wins, Nn noms]",
        "#",
        "# Run:  python pipeline/queue_manager.py --add-list "
        "pipeline/sources/most_awarded_not_in_catalog.txt --source awards",
        "",
    ]
    for tmdb_id, af, res_title in resolved:
        award_snippet = ", ".join(af.award_ids[:3])
        if len(af.award_ids) > 3:
            award_snippet += f" +{len(af.award_ids)-3} more"
        lines.append(
            f"{tmdb_id}"
            f"  # {res_title} ({af.year or '?'})"
            f" — score: {af.score:.2f}"
            f"  [{af.wins} wins, {af.noms} noms]"
            f"  [{award_snippet}]"
        )

    output_text = "\n".join(lines) + "\n"

    # ── 7. Write / print ──────────────────────────────────────────────────────
    if args.dry_run:
        print("\n" + "─" * 70)
        print(output_text)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text, encoding="utf-8")
        print(f"\n✅ Written {len(resolved)} films → {args.output}")

    print(f"\nSUMMARY")
    print(f"  Wikidata films found    : {len(films)}")
    print(f"  Not in catalog          : {len(not_in_catalog)}")
    print(f"  TMDB IDs resolved       : {len(resolved)}")
    print(f"  Output                  : {'stdout (dry-run)' if args.dry_run else args.output}")


if __name__ == "__main__":
    main()
