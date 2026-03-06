"""
pipeline/enrich_festival_logos.py
───────────────────────────────────
Fetches logo images for festivals via the Wikipedia REST API.

Only stores URLs that resolve to actual SVG/vector logos (URLs containing
'.svg'), not generic photos or scene images. Falls back to null for all
others — the frontend uses CSS monograms as fallback.

Usage:
  python3 pipeline/enrich_festival_logos.py
  python3 pipeline/enrich_festival_logos.py --dry-run
"""

import os
import sys
import time
import argparse
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")
from supabase import create_client

db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

HEADERS = {"User-Agent": "PRISMA-film-db/1.0 (cinematic color catalog; educational project)"}
SLEEP = 0.35

# Mapping: festival_id → Wikipedia article title to fetch
WIKI_TITLES = {
    "festival_academy-awards":    "Academy_Awards",
    "festival_cannes":             "Cannes_Film_Festival",
    "festival_berlin":             "Berlin_International_Film_Festival",
    "festival_venice":             "Venice_Film_Festival",
    "festival_bafta":              "BAFTA",
    "festival_toronto":            "Toronto_International_Film_Festival",
    "festival_sundance":           "Sundance_Film_Festival",
    "festival_golden-globe":       "Golden_Globe_Awards",
    "festival_locarno":            "Locarno_Film_Festival",
    "festival_san-sebastian":      "San_Sebastián_International_Film_Festival",
    "festival_rotterdam":          "International_Film_Festival_Rotterdam",
    "festival_new-york":           "New_York_Film_Festival",
    "festival_telluride":          "Telluride_Film_Festival",
    "festival_tribeca":            "Tribeca_Film_Festival",
    "festival_mar-del-plata":      "Mar_del_Plata_International_Film_Festival",
    "festival_morelia":            "Morelia_International_Film_Festival",
    "festival_guadalajara":        "Guadalajara_International_Film_Festival",
    "festival_bafici":             "Buenos_Aires_International_Festival_of_Independent_Cinema",
    "festival_cesar":              "César_Award",
    "festival_goya":               "Goya_Awards",
    "festival_ariel":              "Ariel_Award",
    "festival_david-di-donatello": "David_di_Donatello",
    "festival_japanese-academy":   "Japan_Academy_Film_Prize",
    "festival_korean-film-awards": "Grand_Bell_Awards",
    "festival_bodil":              "Bodil_Award",
    "festival_spirit-awards":      "Film_Independent_Spirit_Awards",
    "festival_sitges":             "Sitges_Film_Festival",
    "festival_sxsw":               "South_by_Southwest",
    "festival_hot-docs":           "Hot_Docs_Canadian_International_Documentary_Festival",
    "festival_idfa":               "International_Documentary_Film_Festival_Amsterdam",
    "festival_fipresci":           "FIPRESCI",
    "festival_cartagena":          "Cartagena_International_Film_Festival",
}


def fetch_wiki_image(title: str) -> str | None:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        # Prefer originalimage over thumbnail for higher quality
        img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
        return img
    except Exception as e:
        print(f"    ERROR fetching {title}: {e}")
        return None


def is_logo_url(url: str | None) -> bool:
    """Only accept URLs that are clearly SVG-based vector logos."""
    if not url:
        return False
    return ".svg" in url.lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print without updating DB")
    args = parser.parse_args()

    print(f"{'DRY RUN — ' if args.dry_run else ''}Enriching festival logos via Wikipedia REST API\n")

    ok, skipped, errors = 0, 0, 0

    for festival_id, wiki_title in WIKI_TITLES.items():
        img_url = fetch_wiki_image(wiki_title)
        logo_url = img_url if is_logo_url(img_url) else None
        status = "✓ SVG" if logo_url else ("~ photo" if img_url else "✗ none")
        display = (logo_url or img_url or "")[:80]
        print(f"  {status:<8} {festival_id.replace('festival_', ''):<25} {display}")

        if not args.dry_run and logo_url:
            try:
                db.table("festivals").update({"logo_path": logo_url}).eq("id", festival_id).execute()
                ok += 1
            except Exception as e:
                print(f"    DB ERROR: {e}")
                errors += 1
        elif logo_url:
            ok += 1  # would update
        else:
            skipped += 1

        time.sleep(SLEEP)

    print(f"\n{'DRY RUN ' if args.dry_run else ''}SUMMARY: {ok} logos stored · {skipped} skipped (no SVG) · {errors} errors")


if __name__ == "__main__":
    main()
