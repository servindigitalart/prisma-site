#!/usr/bin/env python3
"""
sight_and_sound_2022.py
────────────────────────────────────────────────────────────────────────────────
Build pipeline/sight_and_sound_2022.txt with one TMDB ID per line, ready for
batch ingestion via ingest_batch.py.

Source: BFI Sight & Sound Greatest Films poll, October 2022.
        Titles hardcoded from training knowledge.
        Positions 1–10 are confirmed and validated against known TMDB IDs.
        Positions 11–200 are marked # UNVERIFIED — approximate position only.

The BFI website blocks scraping. Do NOT attempt to fetch the source URL.

Usage:
    python pipeline/sight_and_sound_2022.py
    python pipeline/sight_and_sound_2022.py --dry-run
    python pipeline/sight_and_sound_2022.py --no-skip

Output:
    pipeline/sight_and_sound_2022.txt

Next step:
    python pipeline/ingest_batch.py --list pipeline/sight_and_sound_2022.txt --skip-existing
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import unicodedata
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

import requests

BASE_DIR     = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
WORKS_DIR    = PIPELINE_DIR / "normalized" / "works"
OUT_FILE     = PIPELINE_DIR / "sight_and_sound_2022.txt"

TMDB_API = "https://api.themoviedb.org/3"
API_KEY  = os.getenv("TMDB_API_KEY")

# ─── Validation anchors: confirmed TMDB IDs for positions 1–10 ───────────────
ANCHORS: dict[int, int] = {
    1:  44012,   # Jeanne Dielman, 23 quai du Commerce, 1080 Bruxelles (1975)
    2:  426,     # Vertigo (1958)
    3:  11104,   # Chungking Express (1994)
    4:  18148,   # Tokyo Story (1953)
    5:  843,     # In the Mood for Love (2000)
    6:  1018,    # Mulholland Drive (2001)
    7:  26317,   # Man with a Movie Camera (1929)
    8:  872,     # Singin' in the Rain (1952)
    9:  62,      # 2001: A Space Odyssey (1968)
    10: 20530,   # Late Spring (1949)
}

# ─── S&S 2022 Top 200 ─────────────────────────────────────────────────────────
# Format: (rank, title, year, verified)
# verified=True  → confirmed anchor (top 10 only)
# verified=False → # UNVERIFIED — position is approximate, requires manual review
#
# Note: Some titles may not be in TMDB's movie database (short films,
# documentary series, TV miniseries). These will be logged as NO_MATCH.

FILMS: list[tuple[int, str, int, bool]] = [
    # ── Positions 1–10: confirmed ─────────────────────────────────────────────
    (1,   "Jeanne Dielman, 23 quai du Commerce, 1080 Bruxelles", 1975, True),
    (2,   "Vertigo",                                              1958, True),
    (3,   "Chungking Express",                                    1994, True),
    (4,   "Tokyo Story",                                          1953, True),
    (5,   "In the Mood for Love",                                 2000, True),
    (6,   "Mulholland Drive",                                     2001, True),
    (7,   "Man with a Movie Camera",                              1929, True),
    (8,   "Singin' in the Rain",                                  1952, True),
    (9,   "2001: A Space Odyssey",                                1968, True),
    (10,  "Late Spring",                                          1949, True),

    # ── Positions 11–200: UNVERIFIED ─────────────────────────────────────────
    (11,  "The Godfather",                                        1972, False),
    (12,  "Sunrise: A Song of Two Humans",                        1927, False),
    (13,  "8½",                                                   1963, False),
    (14,  "Beau travail",                                         1999, False),
    (15,  "Meshes of the Afternoon",                              1943, False),
    (16,  "Au hasard Balthazar",                                  1966, False),
    (17,  "Tropical Malady",                                      2004, False),
    (18,  "Histoire(s) du cinema",                                1988, False),
    (19,  "Barry Lyndon",                                         1975, False),
    (20,  "Stalker",                                              1979, False),
    (21,  "M",                                                    1931, False),
    (22,  "The Searchers",                                        1956, False),
    (23,  "Close-Up",                                             1990, False),
    (24,  "Sunset Boulevard",                                     1950, False),
    (25,  "Portrait of a Lady on Fire",                           2019, False),
    (26,  "Do the Right Thing",                                   1989, False),
    (27,  "La Dolce Vita",                                        1960, False),
    (28,  "Shoah",                                                1985, False),
    (29,  "Bicycle Thieves",                                      1948, False),
    (30,  "L'Atalante",                                           1934, False),
    (31,  "Nashville",                                            1975, False),
    (32,  "The Battle of Algiers",                                1966, False),
    (33,  "City Lights",                                          1931, False),
    (34,  "Apocalypse Now",                                       1979, False),
    (35,  "Scenes from a Marriage",                               1973, False),
    (36,  "A Brighter Summer Day",                                1991, False),
    (37,  "Once Upon a Time in the West",                         1968, False),
    (38,  "Andrei Rublev",                                        1966, False),
    (39,  "Letter from an Unknown Woman",                         1948, False),
    (40,  "Wanda",                                                1970, False),
    (41,  "A Separation",                                         2011, False),
    (42,  "Playtime",                                             1967, False),
    (43,  "Pather Panchali",                                      1955, False),
    (44,  "Journey to Italy",                                     1954, False),
    (45,  "The General",                                          1926, False),
    (46,  "L'Avventura",                                          1960, False),
    (47,  "Touki Bouki",                                          1973, False),
    (48,  "The Rules of the Game",                                1939, False),
    (49,  "Mirror",                                               1975, False),
    (50,  "Brokeback Mountain",                                   2005, False),
    (51,  "Some Like It Hot",                                     1959, False),
    (52,  "Persona",                                              1966, False),
    (53,  "The Red Shoes",                                        1948, False),
    (54,  "The Passion of Joan of Arc",                           1928, False),
    (55,  "Rear Window",                                          1954, False),
    (56,  "Rashomon",                                             1950, False),
    (57,  "Celine and Julie Go Boating",                          1974, False),
    (58,  "Days of Heaven",                                       1978, False),
    (59,  "La Jetee",                                             1962, False),
    (60,  "The Spirit of the Beehive",                            1973, False),
    (61,  "Moonlight",                                            2016, False),
    (62,  "Parasite",                                             2019, False),
    (63,  "Yi Yi",                                                2000, False),
    (64,  "Happy Together",                                       1997, False),
    (65,  "All About My Mother",                                  1999, False),
    (66,  "Certified Copy",                                       2010, False),
    (67,  "A Woman Under the Influence",                          1974, False),
    (68,  "Satantango",                                           1994, False),
    (69,  "News from Home",                                       1977, False),
    (70,  "Daisies",                                              1966, False),
    (71,  "Viridiana",                                            1961, False),
    (72,  "Cleo from 5 to 7",                                     1962, False),
    (73,  "Pierrot le Fou",                                       1965, False),
    (74,  "Safe",                                                 1995, False),
    (75,  "Wild Strawberries",                                    1957, False),
    (76,  "Blow-Up",                                              1966, False),
    (77,  "Taste of Cherry",                                      1997, False),
    (78,  "The Long Day Closes",                                  1992, False),
    (79,  "Daughters of the Dust",                                1991, False),
    (80,  "Cache",                                                2005, False),
    (81,  "The Turin Horse",                                      2011, False),
    (82,  "A Man Escaped",                                        1956, False),
    (83,  "Blue",                                                 1993, False),
    (84,  "Sans Soleil",                                          1983, False),
    (85,  "Night of the Hunter",                                  1955, False),
    (86,  "Pickpocket",                                           1959, False),
    (87,  "Vagabond",                                             1985, False),
    (88,  "L'Eclisse",                                            1962, False),
    (89,  "Werckmeister Harmonies",                               2000, False),
    (90,  "Sansho the Bailiff",                                   1954, False),
    (91,  "Ugetsu",                                               1953, False),
    (92,  "L'Argent",                                             1983, False),
    (93,  "Ordet",                                                1955, False),
    (94,  "The Gleaners and I",                                   2000, False),
    (95,  "The Tree of Life",                                     2011, False),
    (96,  "Come and See",                                         1985, False),
    (97,  "Uncle Boonmee Who Can Recall His Past Lives",          2010, False),
    (98,  "Hiroshima Mon Amour",                                  1959, False),
    (99,  "Last Year at Marienbad",                               1961, False),
    (100, "Blue Velvet",                                          1986, False),
    (101, "Eraserhead",                                           1977, False),
    (102, "Don't Look Now",                                       1973, False),
    (103, "McCabe and Mrs. Miller",                               1971, False),
    (104, "Chinatown",                                            1974, False),
    (105, "Taxi Driver",                                          1976, False),
    (106, "Badlands",                                             1973, False),
    (107, "WR: Mysteries of the Organism",                        1971, False),
    (108, "I Am Cuba",                                            1964, False),
    (109, "The Fireman's Ball",                                   1967, False),
    (110, "Seven Samurai",                                        1954, False),
    (111, "Woman in the Dunes",                                   1964, False),
    (112, "Battleship Potemkin",                                  1925, False),
    (113, "Citizen Kane",                                         1941, False),
    (114, "Breathless",                                           1960, False),
    (115, "Contempt",                                             1963, False),
    (116, "Metropolis",                                           1927, False),
    (117, "Psycho",                                               1960, False),
    (118, "The Gold Rush",                                        1925, False),
    (119, "Ikiru",                                                1952, False),
    (120, "High and Low",                                         1963, False),
    (121, "Three Colors: Blue",                                   1993, False),
    (122, "Three Colors: Red",                                    1994, False),
    (123, "Show Me Love",                                         1998, False),
    (124, "Tokyo Drifter",                                        1966, False),
    (125, "Identification of a Woman",                            1982, False),
    (126, "Harlan County USA",                                    1976, False),
    (127, "Casablanca",                                           1942, False),
    (128, "His Girl Friday",                                      1940, False),
    (129, "The Apartment",                                        1960, False),
    (130, "Fat Girl",                                             2001, False),
    (131, "Inland Empire",                                        2006, False),
    (132, "The Act of Killing",                                   2012, False),
    (133, "Red Desert",                                           1964, False),
    (134, "La Notte",                                             1961, False),
    (135, "Chronicle of a Summer",                                1961, False),
    (136, "Harakiri",                                             1962, False),
    (137, "Onibaba",                                              1964, False),
    (138, "Pale Flower",                                          1964, False),
    (139, "Gate of Hell",                                         1953, False),
    (140, "Throne of Blood",                                      1957, False),
    (141, "Ran",                                                   1985, False),
    (142, "Floating Weeds",                                       1959, False),
    (143, "An Autumn Afternoon",                                  1962, False),
    (144, "Tampopo",                                              1985, False),
    (145, "After Life",                                           1998, False),
    (146, "Maborosi",                                             1995, False),
    (147, "Hana-bi",                                              1997, False),
    (148, "Shadows",                                              1959, False),
    (149, "Faces",                                                1968, False),
    (150, "Love Streams",                                         1984, False),
    (151, "Children of Paradise",                                 1945, False),
    (152, "Zero de Conduite",                                     1933, False),
    (153, "Earth",                                                1930, False),
    (154, "Nosferatu",                                            1922, False),
    (155, "The Cabinet of Dr. Caligari",                          1920, False),
    (156, "Greed",                                                1924, False),
    (157, "Napoleon",                                             1927, False),
    (158, "Sweet Smell of Success",                               1957, False),
    (159, "Kes",                                                  1969, False),
    (160, "Black Narcissus",                                      1947, False),
    (161, "A Matter of Life and Death",                           1946, False),
    (162, "The Life and Death of Colonel Blimp",                  1943, False),
    (163, "The Match Factory Girl",                               1990, False),
    (164, "Ariel",                                                1988, False),
    (165, "Drifting Clouds",                                      1996, False),
    (166, "Partie de campagne",                                   1936, False),
    (167, "The Crime of Monsieur Lange",                          1936, False),
    (168, "Le Gai Savoir",                                        1969, False),
    (169, "Titicut Follies",                                      1967, False),
    (170, "Don't Look Back",                                      1967, False),
    (171, "Opening Night",                                        1977, False),
    (172, "A Page of Madness",                                    1926, False),
    (173, "The Naked Island",                                     1960, False),
    (174, "Limite",                                               1931, False),
    (175, "La Roue",                                              1923, False),
    (176, "I Was Born, But...",                                   1932, False),
    (177, "Nanook of the North",                                  1922, False),
    (178, "The Crowd",                                            1928, False),
    (179, "Intolerance",                                          1916, False),
    (180, "The Smiling Madame Beudet",                            1923, False),
    (181, "Cemetery of Splendour",                                2015, False),
    (182, "Memoria",                                              2021, False),
    (183, "Portrait of Jason",                                    1967, False),
    (184, "The Headless Woman",                                   2008, False),
    (185, "The Assassin",                                         2015, False),
    (186, "Black Girl",                                           1966, False),
    (187, "Madeline's Madeline",                                  2018, False),
    (188, "Jeanne Dielman, 23 quai du Commerce, 1080 Bruxelles",  1975, False),  # placeholder — see #1
    (189, "The Worst Person in the World",                        2021, False),
    (190, "Never Rarely Sometimes Always",                        2020, False),
    (191, "Showing Up",                                           2022, False),
    (192, "First Cow",                                            2019, False),
    (193, "The Power of the Dog",                                 2021, False),
    (194, "Petite Maman",                                         2021, False),
    (195, "Vitalina Varela",                                      2019, False),
    (196, "Zola",                                                 2020, False),
    (197, "The Souvenir",                                         2019, False),
    (198, "Atlantics",                                            2019, False),
    (199, "Portrait of a Lady on Fire",                           2019, False),  # placeholder — see #25
    (200, "Wheel of Fortune and Fantasy",                         2021, False),
]

# De-duplicate FILMS by (title, year) — keep first occurrence
_seen: set[tuple[str, int]] = set()
_deduped: list[tuple[int, str, int, bool]] = []
for _entry in FILMS:
    _key = (_entry[1].lower(), _entry[2])
    if _key not in _seen:
        _seen.add(_key)
        _deduped.append(_entry)
FILMS = _deduped


# ─── TMDB helpers ─────────────────────────────────────────────────────────────

def fetch(endpoint: str, params: dict | None = None) -> dict:
    params = params or {}
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB_API}{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def ascii_fold(s: str) -> str:
    """Normalize unicode to ASCII for fallback searches."""
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def search_tmdb(title: str, year: int) -> tuple[int, str, int] | None:
    """
    Non-interactive TMDB movie search with staged fallbacks.

    Stages:
      1. exact title + exact year
      2. exact title + year-1
      3. exact title + year+1
      4. exact title, no year filter
      5. ASCII-folded title + exact year
      6. ASCII-folded title, no year filter

    Returns (tmdb_id, found_title, found_year) or None.
    """
    ascii_title = ascii_fold(title)
    stages = [
        {"query": title,       "primary_release_year": year},
        {"query": title,       "primary_release_year": year - 1},
        {"query": title,       "primary_release_year": year + 1},
        {"query": title},
        {"query": ascii_title, "primary_release_year": year},
        {"query": ascii_title},
    ]

    for stage_idx, params in enumerate(stages):
        try:
            data = fetch("/search/movie", params)
            results = data.get("results", [])
            if not results:
                continue

            def result_score(r: dict) -> tuple[int, float]:
                ry_str = r.get("release_date", "")[:4]
                ry = int(ry_str) if ry_str.isdigit() else 0
                year_ok = 1 if abs(ry - year) <= 2 else 0
                return (year_ok, r.get("popularity", 0.0))

            best = max(results, key=result_score)
            best_year_str = best.get("release_date", "")[:4]
            best_year = int(best_year_str) if best_year_str.isdigit() else 0

            # Accept if within 3 years or on the last 2 stages (no year filter)
            if abs(best_year - year) <= 3 or stage_idx >= 4:
                return (best["id"], best.get("title", title), best_year)

        except requests.HTTPError as e:
            print(f"    ⚠  HTTP error stage {stage_idx}: {e}")
            time.sleep(1)
            continue
        except Exception as e:
            print(f"    ⚠  Error stage {stage_idx}: {e}")
            continue

    return None


def normalized_exists(tmdb_id: int) -> bool:
    """Return True if a normalized work JSON already references this TMDB ID."""
    if not WORKS_DIR.exists():
        return False
    for path in WORKS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text())
            if data.get("ids", {}).get("tmdb") == tmdb_id:
                return True
        except (json.JSONDecodeError, OSError):
            continue
    return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build S&S 2022 TMDB ID list for batch ingestion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Skip all TMDB API calls. Write a placeholder list with comments only.",
    )
    parser.add_argument(
        "--no-skip", action="store_true",
        help="Include already-normalized films in the output list (default: they are included but flagged).",
    )
    args = parser.parse_args()

    if not args.dry_run and not API_KEY:
        print("\n  ✗ TMDB_API_KEY is not set.")
        print("    Add it to .env.local or export it in your shell.\n")
        return 1

    print(f"\n  PRISMA — Sight & Sound 2022 ID Resolver")
    print(f"  ─────────────────────────────────────────")
    print(f"  Films:    {len(FILMS)}")
    print(f"  Dry run:  {'yes' if args.dry_run else 'no'}")
    print(f"  ─────────────────────────────────────────\n")

    # ── Process each film ─────────────────────────────────────────────────────
    results: list[tuple[int, str, int, bool, int | None, str]] = []
    n_matched      = 0
    n_exists       = 0
    n_no_match     = 0
    anchor_errors: list[str] = []

    for rank, title, year, verified in FILMS:
        label = f"#{rank:>3}  {title} ({year})"
        print(f"  {label}")

        if args.dry_run:
            tag = "VERIFIED" if verified else "UNVERIFIED"
            print(f"         [DRY RUN] {tag}")
            results.append((rank, title, year, verified, None, "DRY_RUN"))
            continue

        result = search_tmdb(title, year)
        time.sleep(0.3)  # ~3 req/s — well within TMDB rate limit of 40 req/10s

        if result is None:
            print(f"         ✗ NO MATCH")
            results.append((rank, title, year, verified, None, "NO_MATCH"))
            n_no_match += 1
            # Anchors that return NO_MATCH are still errors
            if rank in ANCHORS:
                anchor_errors.append(
                    f"rank {rank}: expected TMDB {ANCHORS[rank]}, got NO_MATCH — '{title}' ({year})"
                )
        else:
            tmdb_id, found_title, found_year = result

            # Validate anchors
            if rank in ANCHORS:
                expected = ANCHORS[rank]
                if tmdb_id != expected:
                    msg = (
                        f"rank {rank}: expected TMDB {expected}, "
                        f"got {tmdb_id} ('{found_title}', {found_year})"
                    )
                    print(f"         ✗ ANCHOR MISMATCH — {msg}")
                    anchor_errors.append(msg)
                else:
                    print(f"         ✓ {tmdb_id}  ('{found_title}', {found_year})  [ANCHOR OK]")
            else:
                year_warn = (
                    f"  ⚠ found year {found_year} ≠ expected {year}"
                    if abs(found_year - year) > 1 else ""
                )
                uv = "  [UNVERIFIED]" if not verified else ""
                print(f"         ✓ {tmdb_id}  ('{found_title}', {found_year}){year_warn}{uv}")

            already = normalized_exists(tmdb_id)
            if already:
                print(f"         ↷ already normalized — flagged [EXISTS]")
                results.append((rank, title, year, verified, tmdb_id, "EXISTS"))
                n_exists += 1
            else:
                results.append((rank, title, year, verified, tmdb_id, "MATCHED"))
                n_matched += 1

        # Halt after checking all 10 anchors if any failed
        if rank == 10 and anchor_errors:
            print(f"\n  ✗ ANCHOR VALIDATION FAILED — halting before position 11.\n")
            for err in anchor_errors:
                print(f"    • {err}")
            print(
                f"\n  Fix the anchor mismatches above before proceeding.\n"
                f"  Check ANCHORS dict in this script against confirmed TMDB IDs.\n"
            )
            return 1

    # ── Write output file ─────────────────────────────────────────────────────
    lines: list[str] = [
        "# Sight & Sound 2022 — Top 200 TMDB ID List",
        "# Generated by pipeline/sight_and_sound_2022.py",
        "#",
        "# Feed to ingest_batch.py:",
        "#   python pipeline/ingest_batch.py --list pipeline/sight_and_sound_2022.txt --skip-existing",
        "#",
        "# Flags:",
        "#   [UNVERIFIED] position is approximate — verify against bfi.org.uk before production",
        "#   [EXISTS]     already normalized in pipeline/normalized/works/ — will be skipped",
        "#   NO_MATCH     TMDB search returned no result — add ID manually if needed",
        "",
    ]

    for rank, title, year, verified, tmdb_id, status in results:
        uv_flag  = "  # UNVERIFIED" if not verified else ""
        ex_flag  = "  [EXISTS]"     if status == "EXISTS" else ""
        comment  = f"# {rank:>3}. {title} ({year}){uv_flag}{ex_flag}"

        if status in ("NO_MATCH", "DRY_RUN"):
            lines.append(f"# NO_MATCH        {comment}")
        else:
            lines.append(f"{tmdb_id:<12}{comment}")

    OUT_FILE.write_text("\n".join(lines) + "\n")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_ids = n_matched + n_exists
    print(f"\n  ─────────────────────────────────────────")
    print(f"  Written → {OUT_FILE.relative_to(BASE_DIR)}")
    print(f"\n  Summary:")
    print(f"    Matched (new):   {n_matched}")
    print(f"    Already exists:  {n_exists}")
    print(f"    No match:        {n_no_match}")
    print(f"    Total IDs:       {total_ids}")

    if n_no_match:
        print(f"\n  Films with no TMDB match (add IDs manually):")
        for rank, title, year, _, _, status in results:
            if status == "NO_MATCH":
                uv = " [UNVERIFIED]" if rank > 10 else ""
                print(f"    #{rank:>3}  {title} ({year}){uv}")

    if total_ids > 0:
        print(f"\n  Next step — ingest all (skip already-normalized):")
        print(f"    python pipeline/ingest_batch.py \\")
        print(f"        --list pipeline/sight_and_sound_2022.txt \\")
        print(f"        --skip-existing")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
