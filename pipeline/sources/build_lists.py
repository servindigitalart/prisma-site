#!/usr/local/bin/python3
"""
pipeline/sources/build_lists.py
────────────────────────────────
Searches TMDB by title+year for each canonical film list and writes
verified TMDB IDs to the source txt files.

Never hardcodes IDs — all IDs are resolved via TMDB search API.

Usage:
    python pipeline/sources/build_lists.py --list palme_dor  --output pipeline/sources/palme_dor_historical.txt
    python pipeline/sources/build_lists.py --list oscar       --output pipeline/sources/oscar_international.txt
    python pipeline/sources/build_lists.py --all              # write both files
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env.local")
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass

import requests

TMDB_API = "https://api.themoviedb.org/3"
API_KEY  = os.getenv("TMDB_API_KEY")

# ─── Canonical film lists ─────────────────────────────────────────────────────

PALME_DOR_WINNERS: list[tuple[str, int]] = [
    # (title_for_search, year) — ordered chronologically descending
    ("Anatomy of a Fall",               2023),
    ("Triangle of Sadness",             2022),
    ("Titane",                          2021),
    ("Parasite",                        2019),
    ("Shoplifters",                     2018),
    ("The Square",                      2017),
    ("I, Daniel Blake",                 2016),
    ("Dheepan",                         2015),
    ("Winter Sleep",                    2014),
    ("Blue Is the Warmest Colour",      2013),
    ("Amour",                           2012),
    ("The Tree of Life",                2011),
    ("Uncle Boonmee Who Can Recall His Past Lives", 2010),
    ("The White Ribbon",                2009),
    ("The Class",                       2008),
    ("4 Months 3 Weeks and 2 Days",     2007),
    ("The Wind That Shakes the Barley", 2006),
    ("L'Enfant",                        2005),
    ("Fahrenheit 9/11",                 2004),
    ("Elephant",                        2003),
    ("The Pianist",                     2002),
    ("The Son's Room",                  2001),
    ("Dancer in the Dark",              2000),
    ("Rosetta",                         1999),
    ("Eternity and a Day",              1998),
    ("The Eel",                         1997),
    ("Secrets and Lies",                1996),
    ("Underground",                     1995),
    ("Pulp Fiction",                    1994),
    ("The Piano",                       1993),
    ("The Best Intentions",             1992),
    ("Barton Fink",                     1991),
    ("Wild at Heart",                   1990),
    ("sex lies and videotape",          1989),
    ("Pelle the Conqueror",             1988),
    ("Under Satan's Sun",               1987),
    ("The Mission",                     1986),
    ("When Father Was Away on Business", 1985),
    ("Paris Texas",                     1984),
    ("The Ballad of Narayama",          1983),
    ("Missing",                         1982),
    ("Man of Iron",                     1981),
    ("Kagemusha",                       1980),
    ("Apocalypse Now",                  1979),
    ("The Tree of Wooden Clogs",        1978),
    ("Padre Padrone",                   1977),
    ("Taxi Driver",                     1976),
    ("Chronicle of the Burning Years",  1975),
    ("The Conversation",                1974),
    ("Scarecrow",                       1973),
    ("The Working Class Goes to Heaven", 1972),
    ("The Go-Between",                  1971),
    ("M*A*S*H",                         1970),
    ("If....",                          1968),
    ("Blow-Up",                         1966),
    ("The Knack ...and How to Get It",  1965),
    ("The Umbrellas of Cherbourg",      1964),
    ("Il Gattopardo",                   1963),
    ("Viridiana",                       1961),
    ("La Dolce Vita",                   1960),
    ("Black Orpheus",                   1959),
    ("The Cranes Are Flying",           1957),
]

OSCAR_INTERNATIONAL_WINNERS: list[tuple[str, int]] = [
    # (title_for_search, year) — film release year, not ceremony year
    ("All Quiet on the Western Front",  2022),
    ("Drive My Car",                    2021),
    ("Another Round",                   2020),
    ("Parasite",                        2019),
    ("Roma",                            2018),
    ("A Fantastic Woman",               2017),
    ("The Salesman",                    2016),
    ("Son of Saul",                     2015),
    ("Ida",                             2013),
    ("The Great Beauty",                2013),
    ("Amour",                           2012),
    ("A Separation",                    2011),
    ("In a Better World",               2010),
    ("The Secret in Their Eyes",        2009),
    ("Departures",                      2008),
    ("The Counterfeiters",              2007),
    ("The Lives of Others",             2006),
    ("Tsotsi",                          2005),
    ("The Sea Inside",                  2004),
    ("The Barbarian Invasions",         2003),
    ("Nowhere in Africa",               2002),
    ("No Man's Land",                   2001),
    ("Crouching Tiger Hidden Dragon",   2000),
    ("All About My Mother",             1999),
    ("Life Is Beautiful",               1997),
    ("Kolya",                           1996),
    ("Antonia's Line",                  1995),
    ("Burnt by the Sun",                1994),
    ("Belle Époque",                    1992),
    ("Indochine",                       1991),
    ("Mediterraneo",                    1991),
    ("Journey of Hope",                 1990),
    ("Cinema Paradiso",                 1988),
]

LISTS = {
    "palme_dor": PALME_DOR_WINNERS,
    "oscar":     OSCAR_INTERNATIONAL_WINNERS,
}

LIST_HEADERS = {
    "palme_dor": "Palme d'Or Winners — Cannes Film Festival\n# Source: festival-cannes.com\n# Built by build_lists.py — all IDs verified via TMDB search API",
    "oscar":     "Oscar Best International Feature Film Winners\n# Source: Academy of Motion Picture Arts and Sciences\n# Built by build_lists.py — all IDs verified via TMDB search API",
}


# ─── TMDB search ─────────────────────────────────────────────────────────────

def search_tmdb(title: str, year: int) -> tuple[int, str, int] | None:
    """
    Search TMDB for title+year. Returns (tmdb_id, found_title, found_year) or None.
    Tries exact year first, then year±1 for safety.
    """
    for search_year in [year, year - 1, year + 1]:
        params = {
            "api_key":  API_KEY,
            "query":    title,
            "year":     search_year,
            "language": "en-US",
        }
        try:
            r = requests.get(f"{TMDB_API}/search/movie", params=params, timeout=10)
            r.raise_for_status()
            results = r.json().get("results", [])
            if results:
                best = results[0]
                found_year = int((best.get("release_date") or "0000")[:4] or "0")
                return best["id"], best.get("title", "?"), found_year
        except Exception as e:
            print(f"    ⚠ TMDB error for '{title}' ({search_year}): {e}")
        time.sleep(0.25)
    return None


# ─── Build one list ───────────────────────────────────────────────────────────

def build_list(list_name: str, output_path: Path) -> tuple[int, int]:
    """
    Build a verified source list file. Returns (found, total).
    """
    films = LISTS[list_name]
    header = LIST_HEADERS[list_name]

    lines = [f"# {header}", "#", "# Format: TMDB_ID  # Title (Year) [verified]", "#"]

    found   = 0
    missing = 0

    print(f"\n  Building {list_name} list ({len(films)} films)…\n")

    for title, year in films:
        result = search_tmdb(title, year)
        if result:
            tmdb_id, found_title, found_year = result
            # Warn if title diverges significantly
            match_note = "" if found_title.lower() == title.lower() else f" [found as: {found_title}]"
            lines.append(f"{tmdb_id:<8}  # {found_title} ({found_year}){match_note}")
            print(f"  ✓  {tmdb_id:<8}  {found_title} ({found_year}){match_note}")
            found += 1
        else:
            lines.append(f"# NOT FOUND: {title} ({year})")
            print(f"  ✗  NOT FOUND: {title} ({year})")
            missing += 1
        time.sleep(0.25)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")

    print(f"\n  ── {list_name}: {found} verified, {missing} not found → {output_path}")
    return found, missing


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build verified TMDB ID source lists via TMDB search API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--list", choices=list(LISTS.keys()),
                        help="Which list to build.")
    source.add_argument("--all", action="store_true",
                        help="Build all lists.")
    parser.add_argument("--output", metavar="FILE",
                        help="Output file path (required with --list).")
    args = parser.parse_args()

    if not API_KEY:
        print("\n  ✗ TMDB_API_KEY is not set.\n")
        return 1

    targets: list[tuple[str, Path]] = []

    if args.all:
        sources_dir = Path(__file__).parent
        targets = [
            ("palme_dor", sources_dir / "palme_dor_historical.txt"),
            ("oscar",     sources_dir / "oscar_international.txt"),
        ]
    else:
        if not args.output:
            print("\n  ✗ --output is required when using --list.\n")
            return 1
        targets = [(args.list, Path(args.output))]

    total_found = total_missing = 0
    for list_name, output_path in targets:
        f, m = build_list(list_name, output_path)
        total_found   += f
        total_missing += m

    print(f"\n  Done. {total_found} IDs verified, {total_missing} not found.\n")
    return 0 if total_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
