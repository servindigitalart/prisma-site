"""
pipeline/enrich_awards_wikipedia.py
─────────────────────────────────────
Scrapes award history from Wikipedia for Latin American and other festivals
with limited Wikidata coverage.

Uses requests + BeautifulSoup to parse Wikipedia wikitables.
Does NOT use Playwright — simpler and sufficient for static HTML.

Install dependencies if missing:
  pip install beautifulsoup4 requests --break-system-packages

Usage:
  python3 pipeline/enrich_awards_wikipedia.py             # all festivals
  python3 pipeline/enrich_awards_wikipedia.py --dry-run   # preview
  python3 pipeline/enrich_awards_wikipedia.py --festival ariel
  python3 pipeline/enrich_awards_wikipedia.py --debug     # show parse details
"""

import sys
import time
import re
import argparse
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv(".env.local")

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run:")
    print("  pip install beautifulsoup4 requests --break-system-packages")
    sys.exit(1)

from supabase import create_client

# ─── Config ──────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "PRISMA-film-db/1.0 (educational research; contact via github)",
    "Accept": "text/html,application/xhtml+xml",
}
RATE_LIMIT_SLEEP = 2.0  # seconds between Wikipedia requests

# ─── Festival target definitions ─────────────────────────────────────────────
# Each entry: festival_key → list of (award_id, wikipedia_url, notes)
# Multiple URLs per festival because different award categories live on separate pages.

FESTIVAL_TARGETS: dict[str, list[dict]] = {
    "ariel": [
        {
            "award_id": "award_ariel-best-film",
            "url": "https://en.wikipedia.org/wiki/Ariel_Award_for_Best_Picture",
            "col_year": ["Year", "Ceremony", "Edition"],
            "col_film": ["Film", "Title", "Movie"],
            "col_director": ["Director", "Directors"],
            "result": "win",
            "notes": "Ariel Best Picture — Mexican academy award",
        },
        {
            "award_id": "award_ariel-best-director",
            "url": "https://en.wikipedia.org/wiki/Ariel_Award_for_Best_Director",
            "col_year": ["Year", "Ceremony"],
            "col_film": ["Film", "Title"],
            "col_director": ["Director"],
            "result": "win",
            "notes": "Ariel Best Director",
        },
    ],
    "guadalajara": [
        {
            "award_id": "award_sansebastian-golden-shell",  # FICG uses same award pattern; no FICG award in our DB — store as closest match
            "url": "https://en.wikipedia.org/wiki/Guadalajara_International_Film_Festival",
            "col_year": ["Year"],
            "col_film": ["Film", "Movie", "Title"],
            "col_director": ["Director"],
            "result": "win",
            "notes": "FICG Mayahuel Award — best Ibero-American film",
            "award_id_override": None,  # No FICG-specific award in our DB; skip upsert but log
            "log_only": True,
        },
    ],
    "mar-del-plata": [
        {
            "award_id": "award_fipresci",
            "url": "https://en.wikipedia.org/wiki/Mar_del_Plata_Film_Festival",
            "col_year": ["Year", "Edition"],
            "col_film": ["Film", "Title"],
            "col_director": ["Director"],
            "result": "win",
            "notes": "Mar del Plata Golden Astor",
            "log_only": True,  # No Mar del Plata award in our DB yet — log for catalog expansion
        },
    ],
    "morelia": [
        {
            "award_id": "award_fipresci",
            "url": "https://en.wikipedia.org/wiki/Morelia_International_Film_Festival",
            "col_year": ["Year", "Edition"],
            "col_film": ["Film", "Title"],
            "col_director": ["Director"],
            "result": "win",
            "notes": "Morelia Film Festival — Mexican Cinema award",
            "log_only": True,
        },
    ],
    "havana": [
        {
            "award_id": "award_fipresci",
            "url": "https://en.wikipedia.org/wiki/International_Festival_of_New_Latin_American_Cinema",
            "col_year": ["Year", "Edition"],
            "col_film": ["Film", "Title"],
            "col_director": ["Director"],
            "result": "win",
            "notes": "Havana Film Festival — Coral Award best film",
            "log_only": True,
        },
    ],
}


# ─── Wikipedia scraping ───────────────────────────────────────────────────────

def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """Fetch a Wikipedia page and return a BeautifulSoup object."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.Timeout:
        print(f"    [HTTP] Timeout fetching {url}", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as e:
        print(f"    [HTTP] Error {e.response.status_code} for {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    [HTTP] Unexpected error for {url}: {e}", file=sys.stderr)
        return None


def find_wikitables(soup: BeautifulSoup) -> list:
    """Return all wikitable elements from the page."""
    return soup.find_all("table", class_=lambda c: c and "wikitable" in c)


def normalize_header(text: str) -> str:
    """Clean a table header for matching."""
    return re.sub(r"\s+", " ", text.strip()).strip()


def find_column_index(headers: list[str], candidates: list[str]) -> Optional[int]:
    """Find the index of the first matching candidate in headers (case-insensitive)."""
    headers_norm = [h.lower().strip() for h in headers]
    for candidate in candidates:
        c = candidate.lower().strip()
        for i, h in enumerate(headers_norm):
            if c in h or h in c:
                return i
    return None


def extract_cell_text(cell) -> str:
    """Extract clean text from a table cell, following links if needed."""
    # Remove footnote references [1], [2], etc.
    for sup in cell.find_all("sup"):
        sup.decompose()
    text = cell.get_text(separator=" ", strip=True)
    # Remove parenthetical country codes like "(Mexico)"
    text = re.sub(r"\s*\([^)]{1,30}\)", "", text)
    return text.strip()


def extract_year(text: str) -> Optional[int]:
    """Extract a 4-digit year from text."""
    m = re.search(r"\b(19[0-9]{2}|20[0-2][0-9])\b", text)
    return int(m.group(1)) if m else None


def parse_wikitable(table, target: dict, debug: bool = False) -> list[dict]:
    """
    Parse a wikitable and extract award records.
    Returns list of {film_label, year, director, result}.
    """
    rows = table.find_all("tr")
    if not rows:
        return []

    # Find header row
    header_row = None
    for row in rows[:5]:
        headers = [normalize_header(th.get_text()) for th in row.find_all(["th", "td"])]
        if len(headers) >= 2:
            header_row = headers
            break

    if not header_row:
        if debug:
            print(f"    [PARSE] No header row found in table")
        return []

    if debug:
        print(f"    [PARSE] Headers: {header_row[:6]}")

    col_year = find_column_index(header_row, target["col_year"])
    col_film = find_column_index(header_row, target["col_film"])
    col_dir = find_column_index(header_row, target.get("col_director", ["Director"]))

    if col_film is None:
        if debug:
            print(f"    [PARSE] Film column not found in {header_row}")
        return []

    records = []
    current_year: Optional[int] = None

    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        def get_cell(idx: Optional[int]) -> str:
            if idx is None or idx >= len(cells):
                return ""
            return extract_cell_text(cells[idx])

        # Year: use column if available, else carry forward last year seen
        if col_year is not None:
            year_text = get_cell(col_year)
            y = extract_year(year_text)
            if y:
                current_year = y

        film_text = get_cell(col_film)
        if not film_text or len(film_text) < 2:
            continue

        director_text = get_cell(col_dir) if col_dir is not None else ""

        records.append({
            "film_label": film_text,
            "year": current_year,
            "director": director_text,
            "result": target.get("result", "win"),
        })

    return records


def scrape_festival_page(target: dict, debug: bool) -> list[dict]:
    """
    Fetch a Wikipedia page and extract award records from its wikitables.
    Returns the best matching table's records.
    """
    url = target["url"]
    print(f"   Fetching: {url}")
    soup = fetch_page(url)
    if not soup:
        return []

    tables = find_wikitables(soup)
    if not tables:
        print(f"   ⚠  No wikitables found on page")
        return []

    if debug:
        print(f"   Found {len(tables)} wikitable(s)")

    # Try each table, take the one with most records
    best_records = []
    for i, table in enumerate(tables):
        try:
            records = parse_wikitable(table, target, debug=debug)
            if debug:
                print(f"   Table {i}: {len(records)} records parsed")
            if len(records) > len(best_records):
                best_records = records
        except Exception as e:
            if debug:
                print(f"   Table {i}: parse error — {e}")
            continue

    return best_records


# ─── Work matching (same as wikidata script) ─────────────────────────────────

def build_works_index(db) -> dict[tuple, str]:
    r = db.table("works").select("id, title, year").execute()
    index: dict[tuple, str] = {}
    for w in r.data:
        norm = w["title"].lower().strip()
        year = w.get("year")
        index[(norm, year)] = w["id"]
        if (norm, None) not in index:
            index[(norm, None)] = w["id"]
    return index


def match_film(film_label: str, year: Optional[int], works_index: dict) -> Optional[str]:
    norm = film_label.lower().strip()
    if year and (norm, year) in works_index:
        return works_index[(norm, year)]
    if year:
        for delta in (-1, 1):
            if (norm, year + delta) in works_index:
                return works_index[(norm, year + delta)]
    if (norm, None) in works_index:
        return works_index[(norm, None)]
    return None


# ─── DB upsert ────────────────────────────────────────────────────────────────

def upsert_award_rows(db, rows: list[dict], dry_run: bool) -> tuple[int, int]:
    inserted = skipped = 0
    for row in rows:
        if dry_run:
            print(f"    [DRY RUN] {row['work_id']} | {row['award_id']} | {row['result']} | {row.get('year')}")
            inserted += 1
            continue
        try:
            existing = (
                db.table("work_awards")
                .select("id")
                .eq("work_id", row["work_id"])
                .eq("award_id", row["award_id"])
                .eq("result", row["result"])
                .execute()
            )
            if existing.data:
                skipped += 1
                continue
            db.table("work_awards").insert(row).execute()
            inserted += 1
        except Exception as e:
            print(f"    [DB] Error: {e}", file=sys.stderr)
            skipped += 1
    return inserted, skipped


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Enrich work_awards from Wikipedia")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--festival", help="Process only this festival key (e.g. ariel)")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("📥 Loading works index from DB...")
    works_index = build_works_index(db)
    print(f"   {len(works_index)//2} works indexed\n")

    targets_to_process = FESTIVAL_TARGETS
    if args.festival:
        if args.festival not in FESTIVAL_TARGETS:
            print(f"❌ Unknown festival: {args.festival}")
            print(f"   Known: {', '.join(sorted(FESTIVAL_TARGETS.keys()))}")
            sys.exit(1)
        targets_to_process = {args.festival: FESTIVAL_TARGETS[args.festival]}

    total_fetched = total_inserted = total_skipped = total_unmatched = 0

    for festival_key, target_list in targets_to_process.items():
        print(f"🎬 Festival: {festival_key}")

        for target in target_list:
            print(f"  Award: {target['award_id']} — {target.get('notes','')}")
            records = scrape_festival_page(target, debug=args.debug)
            time.sleep(RATE_LIMIT_SLEEP)

            if not records:
                print(f"  ℹ  No records extracted\n")
                continue

            print(f"  → {len(records)} records parsed")
            total_fetched += len(records)

            # Skip insert for log_only targets (no matching award_id in DB)
            if target.get("log_only"):
                matched_count = sum(
                    1 for r in records
                    if match_film(r["film_label"], r["year"], works_index)
                )
                print(f"  ℹ  LOG ONLY (no award_id in DB yet): {matched_count}/{len(records)} would match")
                if args.debug:
                    for r in records[:5]:
                        wid = match_film(r["film_label"], r["year"], works_index)
                        print(f"    {r['film_label']!r:40s} {r.get('year')} → {wid or 'NO MATCH'}")
                print()
                continue

            # Match to works
            rows_to_insert = []
            unmatched = []
            for r in records:
                work_id = match_film(r["film_label"], r["year"], works_index)
                if work_id:
                    rows_to_insert.append({
                        "work_id": work_id,
                        "award_id": target["award_id"],
                        "year": r["year"],
                        "category": target.get("notes", target["award_id"]),
                        "result": r["result"],
                        "person_id": None,
                    })
                else:
                    unmatched.append(r)

            total_unmatched += len(unmatched)
            if args.debug and unmatched:
                print(f"  ⚠  Unmatched ({len(unmatched)}):")
                for u in unmatched[:8]:
                    print(f"    {u['film_label']!r:40s} {u.get('year')}")

            if rows_to_insert:
                inserted, skipped = upsert_award_rows(db, rows_to_insert, args.dry_run)
                total_inserted += inserted
                total_skipped += skipped
                print(f"  ✅ {inserted} inserted, {skipped} existed, {len(unmatched)} unmatched\n")
            else:
                print(f"  ℹ  No catalog matches found\n")

    print("─" * 60)
    print("SUMMARY")
    print(f"  Records parsed : {total_fetched}")
    print(f"  Inserted       : {total_inserted}")
    print(f"  Already existed: {total_skipped}")
    print(f"  No work match  : {total_unmatched}")
    if args.dry_run:
        print("  (DRY RUN — no changes made)")


if __name__ == "__main__":
    main()
