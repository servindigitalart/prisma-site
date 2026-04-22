#!/usr/bin/env python3
"""
pipeline/fill_historical_gaps.py

Fills missing historical award winners using a multi-source strategy:
  1. Wikidata SPARQL  → film QID + IMDb ID + title + year
  2. TMDB find by IMDb ID → exact TMDB record (bypasses title matching)
  3. TMDB search by title + year → fallback when no IMDb ID
  4. Wikipedia langlinks → English title for foreign-language films

If the film is already in our catalog  → insert work_award directly.
If not in catalog                       → insert into candidates table.

Usage:
  python pipeline/fill_historical_gaps.py --festival venice
  python pipeline/fill_historical_gaps.py --festival cannes --award palme-dor
  python pipeline/fill_historical_gaps.py --all
  python pipeline/fill_historical_gaps.py --dry-run --festival berlin
  python pipeline/fill_historical_gaps.py --year 1969 --festival venice
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from supabase import create_client

# ── env ───────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent.parent / ".env.local")

TMDB_KEY      = os.environ.get("TMDB_API_KEY") or os.environ.get("VITE_TMDB_API_KEY") or ""
TMDB_API      = "https://api.themoviedb.org/3"
TMDB_SLEEP    = 0.30   # seconds between TMDB calls
WD_SLEEP      = 1.50   # seconds between Wikidata SPARQL calls
WP_SLEEP      = 0.50   # seconds between Wikipedia API calls

SPARQL_URL    = "https://query.wikidata.org/sparql"
WP_API_URL    = "https://en.wikipedia.org/w/api.php"

# ── Award gap registry ────────────────────────────────────────────────────────

AWARD_GAP_MAP: dict[str, dict] = {
    "venice-golden-lion": {
        "award_id":      "award_venice-golden-lion",
        "wikidata_qid":  "Q209459",
        "festival":      "venice",
        "missing_years": [1951,1953,1957,1969,1972,1973,1974,1975,1976,1977,1978,1979,1990,2020],
    },
    "cannes-palme-dor": {
        "award_id":      "award_cannes-palme-dor",
        "wikidata_qid":  "Q179808",
        "festival":      "cannes",
        "missing_years": [1947,1948,1950,1954,1958,1967,1969,1988,2020],
    },
    "cannes-grand-prix": {
        "award_id":      "award_cannes-grand-prix",
        "wikidata_qid":  "Q844804",
        "festival":      "cannes",
        "missing_years": [1952,1956,1957,1958,1964,1965,1966,1968,1971,1975,1977,1978,
                          1985,1998,2000,2004,2008,2011,2020,2022],
    },
    "berlin-golden-bear": {
        "award_id":      "award_berlin-golden-bear",
        "wikidata_qid":  "Q154590",
        "festival":      "berlin",
        "missing_years": [1952,1964,1987,1990,1994,1997,2008],
    },
    "oscar-best-intl-film": {
        "award_id":      "award_oscar-best-intl-film",
        "wikidata_qid":  "Q105304",
        "festival":      "oscar",
        "missing_years": [1956,1964,1967,1971,1974,1983,1989,1998,2002,2014,2019],
    },
    "locarno-golden-leopard": {
        "award_id":      "award_locarno-golden-leopard",
        "wikidata_qid":  "Q1700510",
        "festival":      "locarno",
        "missing_years": [1946,1956,1957,1962,1966,1972,1974,1982,1990,1994,1996,
                          2001,2007,2010,2012,2017,2018,2020,2024],
    },
}

# Map festival key → award keys in AWARD_GAP_MAP
FESTIVAL_TO_AWARDS: dict[str, list[str]] = defaultdict(list)
for _ak, _av in AWARD_GAP_MAP.items():
    FESTIVAL_TO_AWARDS[_av["festival"]].append(_ak)


# ─── Wikidata SPARQL ──────────────────────────────────────────────────────────

SPARQL_QUERY = """
SELECT DISTINCT ?film ?filmLabel ?imdb ?stmtYear ?filmYear WHERE {{
  ?film p:P166 ?stmt .
  ?stmt ps:P166 wd:{award_qid} .
  ?film wdt:P31 wd:Q11424 .
  OPTIONAL {{ ?stmt pq:P585 ?stmtDate . BIND(YEAR(?stmtDate) AS ?stmtYear) }}
  OPTIONAL {{ ?film wdt:P577 ?pubDate  . BIND(YEAR(?pubDate)  AS ?filmYear) }}
  OPTIONAL {{ ?film wdt:P345 ?imdb . FILTER(STRSTARTS(STR(?imdb), "tt")) }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,fr,it,es,de,ja,pt,zh" }}
}}
ORDER BY ?stmtYear ?filmYear
"""


def get_wikidata_winners(award_qid: str) -> list[dict]:
    """
    Query Wikidata for all winners of an award.
    Returns list of {film_qid, title, imdb_id, year} dicts.
    Year is taken from P585 qualifier (ceremony year) first, then P577 (release year).
    """
    query = SPARQL_QUERY.format(award_qid=award_qid)
    headers = {
        "Accept":     "application/sparql-results+json",
        "User-Agent": "PRISMA-pipeline/1.0 (film-ranking; contact@prisma.film)",
    }
    backoff = WD_SLEEP
    for attempt in range(4):
        try:
            r = requests.get(
                SPARQL_URL,
                params={"query": query, "format": "json"},
                headers=headers,
                timeout=30,
            )
            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After", backoff * 2))
                print(f"    [Wikidata] rate-limited — waiting {wait:.0f}s")
                time.sleep(wait)
                backoff *= 2
                continue
            r.raise_for_status()
            bindings = r.json()["results"]["bindings"]
            break
        except Exception as e:
            if attempt == 3:
                print(f"    [Wikidata] SPARQL error: {e}")
                return []
            time.sleep(backoff)
            backoff *= 2
    else:
        return []

    # Deduplicate by film QID — keep best (most complete) entry
    by_qid: dict[str, dict] = {}
    for b in bindings:
        qid   = b["film"]["value"].split("/")[-1]
        title = b.get("filmLabel", {}).get("value", "")
        imdb  = b.get("imdb",      {}).get("value", "")
        stmt_year = b.get("stmtYear", {}).get("value")
        film_year = b.get("filmYear", {}).get("value")
        # Use ceremony/statement year first (P585), fall back to release year (P577)
        year_raw = stmt_year or film_year
        year = int(year_raw) if year_raw and year_raw.isdigit() else None

        # Prefer entries that have an IMDb ID
        if qid not in by_qid or (imdb and not by_qid[qid].get("imdb_id")):
            by_qid[qid] = {
                "film_qid": qid,
                "title":    title,
                "imdb_id":  imdb if imdb.startswith("tt") else "",
                "year":     year,
            }

    return list(by_qid.values())


# ─── Wikipedia langlinks → English title ─────────────────────────────────────

_wp_title_cache: dict[str, Optional[str]] = {}


def get_english_title_from_wikipedia(original_title: str) -> Optional[str]:
    """
    Use Wikipedia API to resolve a foreign-language title to its English equivalent.
    Tries the original title as a Wikipedia page name, then fetches langlinks to 'en'.
    """
    if original_title in _wp_title_cache:
        return _wp_title_cache[original_title]

    try:
        r = requests.get(
            WP_API_URL,
            params={
                "action":   "query",
                "titles":   original_title,
                "prop":     "langlinks",
                "lllang":   "en",
                "lllimit":  5,
                "format":   "json",
                "redirects": True,
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if page.get("pageid", -1) == -1:
                break
            langlinks = page.get("langlinks", [])
            for ll in langlinks:
                if ll.get("lang") == "en":
                    en_title = ll.get("*", "")
                    # Strip disambiguation suffix like "(film)"
                    import re
                    en_title = re.sub(r"\s*\([^)]*\)\s*$", "", en_title).strip()
                    _wp_title_cache[original_title] = en_title
                    return en_title
            # No English langlink — try the page title itself if it looks English
            page_title = page.get("title", "")
            if page_title and page_title == original_title:
                _wp_title_cache[original_title] = page_title
                return page_title
    except Exception as e:
        pass

    time.sleep(WP_SLEEP)
    _wp_title_cache[original_title] = None
    return None


# ─── TMDB resolution ──────────────────────────────────────────────────────────

_tmdb_cache: dict[str, Optional[dict]] = {}


def tmdb_find_by_imdb(imdb_id: str) -> Optional[dict]:
    """
    Use TMDB /find endpoint to get exact movie by IMDb ID.
    Returns {tmdb_id, title, original_title, year} or None.
    """
    if not TMDB_KEY or not imdb_id:
        return None
    cache_key = f"imdb:{imdb_id}"
    if cache_key in _tmdb_cache:
        return _tmdb_cache[cache_key]
    try:
        r = requests.get(
            f"{TMDB_API}/find/{imdb_id}",
            params={"api_key": TMDB_KEY, "external_source": "imdb_id"},
            timeout=10,
        )
        if r.status_code == 429:
            time.sleep(10)
            r = requests.get(
                f"{TMDB_API}/find/{imdb_id}",
                params={"api_key": TMDB_KEY, "external_source": "imdb_id"},
                timeout=10,
            )
        r.raise_for_status()
        movies = r.json().get("movie_results", [])
        if movies:
            m = movies[0]
            release_year = None
            if m.get("release_date"):
                try:
                    release_year = int(m["release_date"][:4])
                except Exception:
                    pass
            result = {
                "tmdb_id":       m["id"],
                "title":         m.get("title", ""),
                "original_title": m.get("original_title", ""),
                "year":          release_year,
            }
            _tmdb_cache[cache_key] = result
            time.sleep(TMDB_SLEEP)
            return result
    except Exception as e:
        pass
    _tmdb_cache[cache_key] = None
    time.sleep(TMDB_SLEEP)
    return None


def tmdb_search_title(title: str, year: int) -> Optional[dict]:
    """
    Search TMDB by title, with ±2 year window. Returns first plausible hit.
    """
    if not TMDB_KEY or not title:
        return None
    cache_key = f"search:{title.lower()}:{year}"
    if cache_key in _tmdb_cache:
        return _tmdb_cache[cache_key]

    import re
    _LEADING = re.compile(
        r"^(The|A|An|El|La|Los|Las|Le|Les|L'|Der|Die|Das|Il|Lo|Gli|Os|As)\s+",
        re.IGNORECASE,
    )

    def _search(query: str, search_year: Optional[int]) -> Optional[dict]:
        params: dict = {
            "api_key":       TMDB_KEY,
            "query":         query,
            "include_adult": False,
            "language":      "en-US",
        }
        if search_year:
            params["year"] = search_year
        try:
            r = requests.get(f"{TMDB_API}/search/movie", params=params, timeout=10)
            if r.status_code == 429:
                time.sleep(10)
                r = requests.get(f"{TMDB_API}/search/movie", params=params, timeout=10)
            r.raise_for_status()
            for m in r.json().get("results", []):
                rel_year = None
                if m.get("release_date"):
                    try:
                        rel_year = int(m["release_date"][:4])
                    except Exception:
                        pass
                if rel_year and abs(rel_year - year) > 2:
                    continue
                return {
                    "tmdb_id":        m["id"],
                    "title":          m.get("title", ""),
                    "original_title": m.get("original_title", ""),
                    "year":           rel_year,
                }
        except Exception:
            pass
        return None

    result = _search(title, year)
    time.sleep(TMDB_SLEEP)
    if not result:
        stripped = _LEADING.sub("", title).strip()
        if stripped and stripped != title:
            result = _search(stripped, year)
            time.sleep(TMDB_SLEEP)
    if not result:
        result = _search(title, None)
        time.sleep(TMDB_SLEEP)

    _tmdb_cache[cache_key] = result
    return result


def resolve_to_tmdb(imdb_id: str, title: str, year: int) -> Optional[dict]:
    """
    Multi-strategy TMDB resolution.
    Strategy 1: find by IMDb ID (most reliable).
    Strategy 2: search by title + year.
    Strategy 3: get English title from Wikipedia, then search.
    """
    # Strategy 1 — IMDb ID (fastest, most accurate)
    if imdb_id:
        result = tmdb_find_by_imdb(imdb_id)
        if result:
            return result

    # Strategy 2 — title search
    if title:
        result = tmdb_search_title(title, year)
        if result:
            return result

    # Strategy 3 — Wikipedia langlink → English title → search
    if title:
        en_title = get_english_title_from_wikipedia(title)
        time.sleep(WP_SLEEP)
        if en_title and en_title.lower() != title.lower():
            result = tmdb_search_title(en_title, year)
            if result:
                return result

    return None


# ─── Catalog helpers ──────────────────────────────────────────────────────────

def load_catalog(db) -> tuple[dict[int, str], dict[str, str], set[tuple[str, str]]]:
    """
    Returns:
      tmdb_map      {tmdb_id (int) → work_id}
      imdb_map      {imdb_id (str) → work_id}
      existing_pairs {(work_id, award_id)} already in work_awards
    """
    works: list = []
    offset = 0
    while True:
        batch = (db.table("works")
                   .select("id,tmdb_id,imdb_id")
                   .range(offset, offset + 999)
                   .execute().data or [])
        works.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    tmdb_map: dict[int, str] = {}
    imdb_map: dict[str, str] = {}
    for r in works:
        if r.get("tmdb_id"):
            tmdb_map[int(r["tmdb_id"])] = r["id"]
        if r.get("imdb_id"):
            imdb_map[r["imdb_id"].strip()] = r["id"]

    existing: list = []
    offset = 0
    while True:
        batch = (db.table("work_awards")
                   .select("work_id,award_id")
                   .range(offset, offset + 999)
                   .execute().data or [])
        existing.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    existing_pairs = {(r["work_id"], r["award_id"]) for r in existing}
    return tmdb_map, imdb_map, existing_pairs


def check_existing_winner(db, award_id: str, year: int) -> bool:
    """
    Returns True if we already have a WIN entry for this award in the given
    ceremony year (checked via the work's year field, ±1 year tolerance).
    """
    rows = (db.table("work_awards")
              .select("work_id")
              .eq("award_id", award_id)
              .eq("result", "win")
              .execute().data or [])
    if not rows:
        return False
    work_ids = [r["work_id"] for r in rows]
    # Check if any of these works has a year matching ±1
    for wid in work_ids:
        w = db.table("works").select("year").eq("id", wid).maybe_single().execute()
        if w and w.data:
            wy = w.data.get("year")
            if wy and abs(int(wy) - year) <= 1:
                return True
    return False


# ─── Core gap-filler ─────────────────────────────────────────────────────────

def fill_gaps_for_award(
    award_key: str,
    db,
    tmdb_map: dict[int, str],
    imdb_map: dict[str, str],
    existing_pairs: set[tuple[str, str]],
    valid_award_ids: set[str],
    dry_run: bool = False,
    target_year: Optional[int] = None,
) -> dict:
    """
    For each missing year in the award's gap list:
      1. Check if already filled.
      2. Query Wikidata for winner.
      3. Resolve to TMDB.
      4. Insert work_award (catalog) or candidate (not in catalog).
    """
    cfg        = AWARD_GAP_MAP[award_key]
    award_id   = cfg["award_id"]
    qid        = cfg["wikidata_qid"]
    festival   = cfg["festival"]
    gap_years  = cfg["missing_years"]

    if target_year is not None:
        gap_years = [y for y in gap_years if y == target_year]

    print(f"\n{'─'*60}")
    print(f"  Award: {award_key}  ({len(gap_years)} years to fill)")
    print(f"  Wikidata QID: {qid}")
    print(f"{'─'*60}")

    # Fetch all Wikidata winners once
    print("  Fetching Wikidata winners...")
    all_winners = get_wikidata_winners(qid)
    time.sleep(WD_SLEEP)
    print(f"  Wikidata returned {len(all_winners)} winner records")

    # Index by year — Wikidata may have multiple entries per year (shared prizes)
    # Use ceremony year (stmtYear / P585) as primary key
    by_year: dict[int, list[dict]] = defaultdict(list)
    for w in all_winners:
        if w.get("year"):
            by_year[w["year"]].append(w)
        # Also index by release year ±0 in case stmtYear is missing
        # (festival year is usually release_year + 0 or + 1)

    stats = {
        "years_checked":       len(gap_years),
        "already_filled":      0,
        "found_wikidata":      0,
        "resolved_tmdb":       0,
        "work_awards_inserted": 0,
        "candidates_added":    0,
        "still_missing":       0,
    }

    for year in sorted(gap_years):
        print(f"\n  [{year}] checking...", end="  ")

        # Step 1 — already have a winner?
        if check_existing_winner(db, award_id, year):
            print("✓ already filled")
            stats["already_filled"] += 1
            continue

        # Step 2 — find in Wikidata results
        # Try ceremony year, then ceremony_year-1 (film released previous year)
        candidates_wd = (by_year.get(year) or
                         by_year.get(year - 1) or
                         by_year.get(year + 1) or [])

        if not candidates_wd:
            print(f"✗ not found in Wikidata")
            stats["still_missing"] += 1
            continue

        # Take first winner (most Wikidata entries have one per year)
        winner = candidates_wd[0]
        stats["found_wikidata"] += 1
        title   = winner["title"]
        imdb_id = winner["imdb_id"]
        w_year  = winner["year"] or year

        print(f"Wikidata → '{title}' ({w_year}, IMDb: {imdb_id or '—'})")

        # Step 3 — resolve to TMDB
        tmdb_info = resolve_to_tmdb(imdb_id, title, year)
        if not tmdb_info:
            print(f"    ✗ TMDB resolution failed — '{title}'")
            stats["still_missing"] += 1
            continue

        stats["resolved_tmdb"] += 1
        tmdb_id_int = int(tmdb_info["tmdb_id"])
        print(f"    TMDB → '{tmdb_info['title']}' (id={tmdb_id_int}, {tmdb_info.get('year')})")

        if dry_run:
            # Check if would be catalog match
            in_catalog = tmdb_id_int in tmdb_map or (imdb_id and imdb_id in imdb_map)
            print(f"    [DRY] in_catalog={in_catalog}  award_id={award_id}")
            continue

        # Step 4a — is it in our catalog?
        work_id = tmdb_map.get(tmdb_id_int)
        if not work_id and imdb_id:
            work_id = imdb_map.get(imdb_id)

        if work_id:
            pair = (work_id, award_id)
            if pair not in existing_pairs and award_id in valid_award_ids:
                try:
                    db.table("work_awards").insert(
                        {"work_id": work_id, "award_id": award_id, "result": "win"}
                    ).execute()
                    existing_pairs.add(pair)
                    stats["work_awards_inserted"] += 1
                    print(f"    ✓ work_award inserted → {work_id}")
                except Exception as e:
                    print(f"    ✗ DB error inserting work_award: {e}")
            else:
                print(f"    — already in work_awards")
                stats["already_filled"] += 1

        else:
            # Step 4b — not in catalog, add to candidates
            try:
                existing_cand = (db.table("candidates")
                                   .select("id,prisma_score")
                                   .eq("tmdb_id", tmdb_id_int)
                                   .maybe_single()
                                   .execute())
                # Use a high score to surface it for ingestion
                from pathlib import Path as _P
                sys.path.insert(0, str(_P(__file__).parent))
                try:
                    from populate_candidates import FESTIVAL_TIER_WEIGHT, DEFAULT_FESTIVAL_WEIGHT
                    fest_weight = FESTIVAL_TIER_WEIGHT.get(festival, DEFAULT_FESTIVAL_WEIGHT)
                except ImportError:
                    fest_weight = 1.0
                high_score = 200.0 * fest_weight  # mark as high-priority gap fill

                if existing_cand and existing_cand.data:
                    # Bump score if ours is higher
                    old_score = float(existing_cand.data.get("prisma_score") or 0)
                    if high_score > old_score:
                        db.table("candidates").update(
                            {"prisma_score": high_score, "win_count": 1}
                        ).eq("id", existing_cand.data["id"]).execute()
                        print(f"    ↑ candidate score bumped → {high_score:.0f}")
                else:
                    db.table("candidates").insert({
                        "tmdb_id":        tmdb_id_int,
                        "imdb_id":        imdb_id or None,
                        "title":          tmdb_info["title"],
                        "original_title": tmdb_info.get("original_title"),
                        "year":           tmdb_info.get("year") or w_year,
                        "prisma_score":   high_score,
                        "award_count":    1,
                        "win_count":      1,
                        "nom_count":      0,
                        "awards_json":    [{"award_id": award_id, "result": "win"}],
                        "source":         f"gap-fill:{festival}",
                        "status":         "pending",
                    }).execute()
                    stats["candidates_added"] += 1
                    print(f"    + candidate added — not yet in catalog")
            except Exception as e:
                print(f"    ✗ DB error adding candidate: {e}")

    return stats


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fill historical award coverage gaps using Wikidata + TMDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--festival", "-f", default=None,
        help="Festival key: cannes, venice, berlin, oscar, locarno")
    parser.add_argument("--award", "-a", default=None,
        help="Specific award key: e.g. palme-dor, golden-lion")
    parser.add_argument("--all", action="store_true",
        help="Process all awards in AWARD_GAP_MAP")
    parser.add_argument("--year", type=int, default=None,
        help="Fill only this specific year")
    parser.add_argument("--dry-run", action="store_true",
        help="Resolve but do NOT write to DB")
    parser.add_argument("--list", action="store_true",
        help="List all award keys and exit")
    args = parser.parse_args()

    if args.list:
        print("Award gap keys:")
        for key, cfg in AWARD_GAP_MAP.items():
            print(f"  {key:<30}  {len(cfg['missing_years'])} years  QID={cfg['wikidata_qid']}")
        return

    if not TMDB_KEY:
        print("✗ TMDB_API_KEY not set — check .env.local")
        sys.exit(1)

    # ── Connect to DB ─────────────────────────────────────────────────────────
    try:
        db = create_client(
            os.environ["PUBLIC_SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    except KeyError as e:
        print(f"✗ Missing env var: {e}")
        sys.exit(1)

    print("Loading catalog...")
    tmdb_map, imdb_map, existing_pairs = load_catalog(db)
    print(f"  {len(tmdb_map):,} works with TMDB id")
    print(f"  {len(imdb_map):,} works with IMDb id")
    print(f"  {len(existing_pairs):,} existing work_award pairs")

    valid_award_ids: set[str] = {
        a["id"] for a in db.table("awards").select("id").execute().data or []
    }
    print(f"  {len(valid_award_ids)} valid award IDs")

    # ── Select awards to process ──────────────────────────────────────────────
    if args.all:
        award_keys = list(AWARD_GAP_MAP.keys())
    elif args.festival:
        award_keys = FESTIVAL_TO_AWARDS.get(args.festival, [])
        if not award_keys:
            print(f"✗ No awards configured for festival '{args.festival}'")
            print(f"  Available festivals: {sorted(FESTIVAL_TO_AWARDS.keys())}")
            sys.exit(1)
        if args.award:
            full_key = f"{args.festival}-{args.award}"
            award_keys = [k for k in award_keys if k == full_key]
            if not award_keys:
                print(f"✗ Award key '{full_key}' not in gap map")
                sys.exit(1)
    elif args.award:
        # Accept bare award key like "palme-dor" or full "cannes-palme-dor"
        award_keys = [k for k in AWARD_GAP_MAP if args.award in k]
        if not award_keys:
            print(f"✗ No award key matching '{args.award}'")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)

    print(f"\n{'═'*60}")
    print(f"  Gap fill: {len(award_keys)} award(s)  dry_run={args.dry_run}")
    print(f"{'═'*60}")

    grand: dict[str, int] = defaultdict(int)

    for award_key in award_keys:
        stats = fill_gaps_for_award(
            award_key, db,
            tmdb_map=tmdb_map,
            imdb_map=imdb_map,
            existing_pairs=existing_pairs,
            valid_award_ids=valid_award_ids,
            dry_run=args.dry_run,
            target_year=args.year,
        )
        for k, v in stats.items():
            grand[k] += v

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("  SUMMARY")
    print(f"{'═'*60}")
    print(f"  Years checked        : {grand['years_checked']}")
    print(f"  Already filled       : {grand['already_filled']}")
    print(f"  Found in Wikidata    : {grand['found_wikidata']}")
    print(f"  Resolved via TMDB    : {grand['resolved_tmdb']}")
    print(f"  work_awards inserted : {grand['work_awards_inserted']}")
    print(f"  Candidates added     : {grand['candidates_added']}")
    print(f"  Still missing        : {grand['still_missing']}")

    if not args.dry_run and grand["work_awards_inserted"] > 0:
        print(f"\n  Recomputing rankings...")
        import subprocess
        script = Path(__file__).parent / "compute_rankings.py"
        subprocess.run([sys.executable, str(script), "--works-only"], check=False)

    if args.dry_run:
        print("\n  [DRY RUN — no changes written to DB]")


if __name__ == "__main__":
    main()
