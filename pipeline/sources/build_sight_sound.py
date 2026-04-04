#!/usr/bin/env python3
"""
pipeline/sources/build_sight_sound.py
──────────────────────────────────────
Searches TMDB for Sight & Sound 2022 top 100, Berlin Golden Bear winners,
and Venice Golden Lion winners. Writes verified TMDB IDs to source txt files.
Skips duplicates already in palme_dor_historical.txt or oscar_international.txt.

Usage:
    python pipeline/sources/build_sight_sound.py
    python pipeline/sources/build_sight_sound.py --dry-run
    python pipeline/sources/build_sight_sound.py --list ss2022
    python pipeline/sources/build_sight_sound.py --list berlin
    python pipeline/sources/build_sight_sound.py --list venice
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    ROOT = Path(__file__).parent.parent.parent
    load_dotenv(ROOT / ".env.local")
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

import requests

TMDB_API = "https://api.themoviedb.org/3"
API_KEY  = os.getenv("TMDB_API_KEY")
SOURCES  = Path(__file__).parent


# ─── Film lists ───────────────────────────────────────────────────────────────

# Sight & Sound 2022 — Top 100 (title, year, director_hint)
# Entries marked None are duplicates/non-applicable — will be skipped
SIGHT_AND_SOUND_2022: list[tuple[str, int, str] | None] = [
    ("Jeanne Dielman, 23 quai du Commerce, 1080 Bruxelles", 1975, "Akerman"),
    ("Vertigo",                                              1958, "Hitchcock"),
    ("Citizen Kane",                                         1941, "Welles"),
    ("Tokyo Story",                                          1953, "Ozu"),
    ("In the Mood for Love",                                 2000, "Wong Kar-wai"),
    ("2001: A Space Odyssey",                                1968, "Kubrick"),
    ("Beau Travail",                                         1999, "Denis"),
    ("Mulholland Drive",                                     2001, "Lynch"),
    ("Man with a Movie Camera",                              1929, "Vertov"),
    ("Singin' in the Rain",                                  1952, "Donen"),
    ("Sunrise: A Song of Two Humans",                        1927, "Murnau"),
    ("The Godfather",                                        1972, "Coppola"),
    ("Ordet",                                                1955, "Dreyer"),
    ("Au hasard Balthazar",                                  1966, "Bresson"),
    ("Apocalypse Now",                                       1979, "Coppola"),
    ("Late Spring",                                          1949, "Ozu"),
    ("Barry Lyndon",                                         1975, "Kubrick"),
    ("L'Atalante",                                           1934, "Vigo"),
    ("Sans Soleil",                                          1983, "Marker"),
    ("Bicycle Thieves",                                      1948, "De Sica"),
    ("The Passion of Joan of Arc",                           1928, "Dreyer"),
    ("Sherlock Jr.",                                         1924, "Keaton"),
    ("Andrei Rublev",                                        1966, "Tarkovsky"),
    ("The General",                                          1926, "Keaton"),
    ("Seven Samurai",                                        1954, "Kurosawa"),
    ("Meshes of the Afternoon",                              1943, "Deren"),
    ("The Rules of the Game",                                1939, "Renoir"),
    ("Ugetsu",                                               1953, "Mizoguchi"),
    ("Close-Up",                                             1990, "Kiarostami"),
    ("Stalker",                                              1979, "Tarkovsky"),
    ("Mirror",                                               1975, "Tarkovsky"),
    ("Sansho the Bailiff",                                   1954, "Mizoguchi"),
    ("City Lights",                                          1931, "Chaplin"),
    ("Breathless",                                           1960, "Godard"),
    ("Parasite",                                             2019, "Bong"),
    ("Portrait of a Lady on Fire",                           2019, "Sciamma"),
    ("8½",                                                   1963, "Fellini"),
    ("Chungking Express",                                    1994, "Wong Kar-wai"),
    ("M",                                                    1931, "Lang"),
    ("Some Like It Hot",                                     1959, "Wilder"),
    ("Night of the Hunter",                                  1955, "Laughton"),
    ("Shoah",                                                1985, "Lanzmann"),
    ("A Matter of Life and Death",                           1946, "Powell"),
    ("Nashville",                                            1975, "Altman"),
    ("Satantango",                                           1994, "Tarr"),
    ("Journey to Italy",                                     1954, "Rossellini"),
    ("L'Avventura",                                          1960, "Antonioni"),
    ("Ali: Fear Eats the Soul",                              1974, "Fassbinder"),
    ("The Wild Bunch",                                       1969, "Peckinpah"),
    ("Chinatown",                                            1974, "Polanski"),
    ("The Apartment",                                        1960, "Wilder"),
    ("Werckmeister Harmonies",                               2000, "Tarr"),
    ("Rear Window",                                          1954, "Hitchcock"),
    ("Blade Runner",                                         1982, "Scott"),
    ("Do the Right Thing",                                   1989, "Lee"),
    ("A Brighter Summer Day",                                1991, "Yang"),
    ("Touki Bouki",                                          1973, "Mambety"),
    ("Spirited Away",                                        2001, "Miyazaki"),
    ("The Searchers",                                        1956, "Ford"),
    ("The Discreet Charm of the Bourgeoisie",                1972, "Bunuel"),
    ("Pierrot le Fou",                                       1965, "Godard"),
    ("Yi Yi",                                                2000, "Yang"),
    ("Tropical Malady",                                      2004, "Apichatpong"),
    ("La Jetée",                                             1962, "Marker"),
    ("Faces",                                                1968, "Cassavetes"),
    None,  # 66 — duplicate Jeanne Dielman
    ("News from Home",                                       1977, "Akerman"),
    ("Histoire(s) du cinéma",                                1988, "Godard"),
    ("The Gleaners and I",                                   2000, "Varda"),
    ("Pickpocket",                                           1959, "Bresson"),
    ("The Great Dictator",                                   1940, "Chaplin"),
    ("Playtime",                                             1967, "Tati"),
    ("Raging Bull",                                          1980, "Scorsese"),
    None,  # 74 — duplicate Jeanne Dielman
    ("Persona",                                              1966, "Bergman"),
    ("Cleo from 5 to 7",                                     1962, "Varda"),
    ("A Woman Under the Influence",                          1974, "Cassavetes"),
    ("Last Year at Marienbad",                               1961, "Resnais"),
    ("Cache",                                                2005, "Haneke"),
    None,  # 80 — not in top 100
    ("Certified Copy",                                       2010, "Kiarostami"),
    ("The Flowers of Shanghai",                              1998, "Hou"),
    ("Daisies",                                              1966, "Chytilova"),
    ("The Color of Pomegranates",                            1969, "Paradjanov"),
    ("Vagabond",                                             1985, "Varda"),
    ("Daughters of the Dust",                                1991, "Dash"),
    ("Ivan the Terrible",                                    1944, "Eisenstein"),
    ("The Long Day Closes",                                  1992, "Davies"),
    ("Killer of Sheep",                                      1977, "Burnett"),
    ("Where Is the Friend's House?",                         1987, "Kiarostami"),
    ("Germany Year Zero",                                    1948, "Rossellini"),
    ("Happy Together",                                       1997, "Wong Kar-wai"),
    ("Kes",                                                  1969, "Loach"),
    ("Uncle Boonmee Who Can Recall His Past Lives",          2010, "Apichatpong"),
    ("Letter from an Unknown Woman",                         1948, "Ophuls"),
    ("Moonlight",                                            2016, "Jenkins"),
    ("Toni Erdmann",                                         2016, "Ade"),
    None,  # 98 — duplicate
    ("First Reformed",                                       2017, "Schrader"),
    ("Ratcatcher",                                           1999, "Ramsay"),
]

# Berlin Golden Bear winners (title, year)
BERLIN_GOLDEN_BEAR: list[tuple[str, int]] = [
    ("Invitation to the Dance",                  1956),
    ("Twelve Angry Men",                         1957),
    ("Wild Strawberries",                        1957),
    ("The Cousins",                              1959),
    ("Lazarillo de Tormes",                      1960),
    ("La Notte",                                 1961),
    ("A Kind of Loving",                         1962),
    ("Il Diavolo",                               1963),
    ("Dry Summer",                               1964),
    ("Alphaville",                               1965),
    ("Cul-de-sac",                               1966),
    ("Le Départ",                                1967),
    ("Ole Dole Doff",                            1968),
    ("Early Works",                              1969),
    ("The Garden of the Finzi-Continis",         1970),
    ("The Canterbury Tales",                     1972),
    ("Distant Thunder",                          1973),
    ("The Apprenticeship of Duddy Kravitz",      1974),
    ("Adoption",                                 1975),
    ("Buffalo Bill and the Indians",             1976),
    ("Ascent",                                   1977),
    ("Las palabras de Max",                      1978),
    ("David",                                    1979),
    ("Heartland",                                1979),
    ("Palermo oder Wolfsburg",                   1980),
    ("Deprisa Deprisa",                          1981),
    ("Veronika Voss",                            1982),
    ("Ascendancy",                               1982),
    ("The Beehive",                              1982),
    ("Love Streams",                             1984),
    ("Wetherby",                                 1985),
    ("Stammheim",                                1986),
    ("The Theme",                                1987),
    ("Red Sorghum",                              1988),
    ("Rain Man",                                 1988),
    ("Music Box",                                1989),
    ("Larks on a String",                        1969),
    ("La casa del sorriso",                      1991),
    ("Grand Canyon",                             1991),
    ("The Women from the Lake of Scented Souls", 1993),
    ("The Wedding Banquet",                      1993),
    ("L'Appât",                                  1995),
    ("Sense and Sensibility",                    1995),
    ("The People vs. Larry Flynt",               1996),
    ("Central Station",                          1998),
    ("The Thin Red Line",                        1998),
    ("Magnolia",                                 1999),
    ("Intimacy",                                 2001),
    ("Spirited Away",                            2001),
    ("Bloody Sunday",                            2002),
    ("In This World",                            2002),
    ("Head-On",                                  2004),
    ("U-Carmen eKhayelitsha",                    2005),
    ("Grbavica",                                 2006),
    ("Tuya's Marriage",                          2007),
    ("Elite Squad",                              2007),
    ("The Milk of Sorrow",                       2009),
    ("Honey",                                    2010),
    ("A Separation",                             2011),
    ("Cesare deve morire",                       2012),
    ("Child's Pose",                             2013),
    ("Black Coal Thin Ice",                      2014),
    ("Taxi",                                     2015),
    ("Fire at Sea",                              2016),
    ("On Body and Soul",                         2017),
    ("Touch Me Not",                             2018),
    ("Synonyms",                                 2019),
    ("There Is No Evil",                         2020),
    ("Bad Luck Banging or Loony Porn",           2021),
    ("Alcarràs",                                 2022),
    ("On the Adamant",                           2023),
]

# Venice Golden Lion winners (title, year)
VENICE_GOLDEN_LION: list[tuple[str, int]] = [
    ("Atlantic City",                                    1980),
    ("The German Sisters",                               1981),
    ("The State of Things",                              1982),
    ("First Name Carmen",                                1983),
    ("The Year of the Quiet Sun",                        1984),
    ("Sans toit ni loi",                                 1985),
    ("The Green Ray",                                    1986),
    ("Au revoir les enfants",                            1987),
    ("The Legend of the Holy Drinker",                   1988),
    ("City of Sadness",                                  1989),
    ("Rosencrantz and Guildenstern Are Dead",            1990),
    ("Urga",                                             1991),
    ("Story of Qiu Ju",                                  1992),
    ("Short Cuts",                                       1993),
    ("Three Colors Blue",                                1993),
    ("Before the Rain",                                  1994),
    ("Vive l'amour",                                     1994),
    ("Cyclo",                                            1995),
    ("Michael Collins",                                  1996),
    ("Hana-bi",                                          1997),
    ("The Way We Laughed",                               1998),
    ("Not One Less",                                     1999),
    ("The Circle",                                       2000),
    ("Lantana",                                          2001),
    ("The Magdalene Sisters",                            2002),
    ("The Return",                                       2003),
    ("Vera Drake",                                       2004),
    ("Brokeback Mountain",                               2005),
    ("Still Life",                                       2006),
    ("Lust Caution",                                     2007),
    ("The Wrestler",                                     2008),
    ("Lebanon",                                          2009),
    ("Somewhere",                                        2010),
    ("Faust",                                            2011),
    ("Pieta",                                            2012),
    ("Sacro GRA",                                        2013),
    ("A Pigeon Sat on a Branch Reflecting on Existence", 2014),
    ("From Afar",                                        2015),
    ("The Woman Who Left",                               2016),
    ("The Shape of Water",                               2017),
    ("Roma",                                             2018),
    ("Joker",                                            2019),
    ("Nomadland",                                        2020),
    ("The Power of the Dog",                             2021),
    ("All the Beauty and the Bloodshed",                 2022),
    ("Poor Things",                                      2023),
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_existing_ids(path: Path) -> set[int]:
    """Load all TMDB IDs already tracked in a source file."""
    ids: set[int] = set()
    if not path.exists():
        return ids
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            try:
                ids.add(int(stripped.split()[0]))
            except (ValueError, IndexError):
                pass
    return ids


def load_all_existing_ids() -> set[int]:
    """Load IDs from all existing source files to skip duplicates."""
    ids: set[int] = set()
    for fname in SOURCES.glob("*.txt"):
        ids |= load_existing_ids(fname)
    return ids


def search_tmdb(title: str, year: int) -> tuple[int, str, int] | None:
    """
    Search TMDB for title+year. Returns (tmdb_id, found_title, found_year) or None.
    Tries exact year, then ±1 for safety (festival vs release year drift).
    """
    if not API_KEY:
        print("  ✗ TMDB_API_KEY not set — cannot search")
        return None

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
            print(f"    ⚠ TMDB error '{title}' ({search_year}): {e}")
        time.sleep(0.25)
    return None


# ─── Build functions ──────────────────────────────────────────────────────────

def build_ss2022(output: Path, existing_ids: set[int], dry_run: bool) -> tuple[int, int, int]:
    """Build Sight & Sound 2022 list. Returns (found, skipped, missing)."""
    header_lines = [
        "# Sight & Sound 2022 — Greatest Films Poll (Top 100)",
        "# Source: British Film Institute / Sight & Sound magazine",
        "# Built by build_sight_sound.py — all IDs verified via TMDB search API",
        "#",
        "# Format: TMDB_ID  # Title (Year) [verified]",
        "#",
    ]

    entries: list[str] = []
    found = skipped = missing = 0

    print(f"\n  Building Sight & Sound 2022 ({sum(1 for e in SIGHT_AND_SOUND_2022 if e)}) films…\n")

    for entry in SIGHT_AND_SOUND_2022:
        if entry is None:
            continue
        title, year, director = entry
        result = search_tmdb(title, year)
        if not result:
            print(f"  ✗ NOT FOUND: {title} ({year})")
            entries.append(f"# NOT FOUND: {title} ({year}) — {director}")
            missing += 1
            continue

        tmdb_id, found_title, found_year = result
        if tmdb_id in existing_ids:
            print(f"  ↷ SKIP (dup): [{tmdb_id}] {title} ({year})")
            skipped += 1
            continue

        entries.append(f"{tmdb_id:<10}# {found_title} ({found_year}) [{director}]")
        existing_ids.add(tmdb_id)  # track within session too
        found += 1
        print(f"  ✓ [{tmdb_id}] {found_title} ({found_year})")
        time.sleep(0.15)

    print(f"\n  → {found} found, {skipped} skipped (dup), {missing} not found\n")

    if not dry_run:
        output.write_text("\n".join(header_lines + entries) + "\n")
        print(f"  Wrote {output}")

    return found, skipped, missing


def build_festival_list(
    name: str,
    films: list[tuple[str, int]],
    output: Path,
    header_lines: list[str],
    existing_ids: set[int],
    dry_run: bool,
) -> tuple[int, int, int]:
    """Generic festival list builder. Returns (found, skipped, missing)."""
    entries: list[str] = []
    found = skipped = missing = 0

    print(f"\n  Building {name} ({len(films)} films)…\n")

    for title, year in films:
        result = search_tmdb(title, year)
        if not result:
            print(f"  ✗ NOT FOUND: {title} ({year})")
            entries.append(f"# NOT FOUND: {title} ({year})")
            missing += 1
            continue

        tmdb_id, found_title, found_year = result
        if tmdb_id in existing_ids:
            print(f"  ↷ SKIP (dup): [{tmdb_id}] {title} ({year})")
            skipped += 1
            continue

        entries.append(f"{tmdb_id:<10}# {found_title} ({found_year})")
        existing_ids.add(tmdb_id)
        found += 1
        print(f"  ✓ [{tmdb_id}] {found_title} ({found_year})")
        time.sleep(0.15)

    print(f"\n  → {found} found, {skipped} skipped (dup), {missing} not found\n")

    if not dry_run:
        output.write_text("\n".join(header_lines + entries) + "\n")
        print(f"  Wrote {output}")

    return found, skipped, missing


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Build PRISMA source lists from S&S 2022, Berlin, Venice")
    parser.add_argument("--list",    choices=["ss2022", "berlin", "venice"], help="Build only one list")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing files")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: TMDB_API_KEY is not set. Source .env.local first.")
        return 1

    dry_run = args.dry_run
    if dry_run:
        print("  [DRY RUN — no files will be written]\n")

    # Load all existing IDs from all source files to skip duplicates
    existing_ids = load_all_existing_ids()
    print(f"  Loaded {len(existing_ids)} existing IDs from source files (will skip duplicates)\n")

    total_found = total_skipped = total_missing = 0

    run_all  = args.list is None
    run_ss   = run_all or args.list == "ss2022"
    run_bert = run_all or args.list == "berlin"
    run_ven  = run_all or args.list == "venice"

    if run_ss:
        f, s, m = build_ss2022(
            output=SOURCES / "sight_and_sound_2022.txt",
            existing_ids=existing_ids,
            dry_run=dry_run,
        )
        total_found += f; total_skipped += s; total_missing += m

    if run_bert:
        f, s, m = build_festival_list(
            name="Berlin Golden Bear",
            films=BERLIN_GOLDEN_BEAR,
            output=SOURCES / "berlin_golden_bear.txt",
            header_lines=[
                "# Berlin Golden Bear — Historical Winners",
                "# Source: Berlinale",
                "# Built by build_sight_sound.py — all IDs verified via TMDB search API",
                "#",
                "# Format: TMDB_ID  # Title (Year) [verified]",
                "#",
            ],
            existing_ids=existing_ids,
            dry_run=dry_run,
        )
        total_found += f; total_skipped += s; total_missing += m

    if run_ven:
        f, s, m = build_festival_list(
            name="Venice Golden Lion",
            films=VENICE_GOLDEN_LION,
            output=SOURCES / "venice_golden_lion.txt",
            header_lines=[
                "# Venice Golden Lion — Historical Winners",
                "# Source: Venice Film Festival",
                "# Built by build_sight_sound.py — all IDs verified via TMDB search API",
                "#",
                "# Format: TMDB_ID  # Title (Year) [verified]",
                "#",
            ],
            existing_ids=existing_ids,
            dry_run=dry_run,
        )
        total_found += f; total_skipped += s; total_missing += m

    print("  ══════════════════════════════════════════════")
    print(f"  TOTAL: {total_found} found, {total_skipped} skipped (dup), {total_missing} not found")
    if dry_run:
        print("  [DRY RUN — run without --dry-run to write files]")
    print("  ══════════════════════════════════════════════\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
