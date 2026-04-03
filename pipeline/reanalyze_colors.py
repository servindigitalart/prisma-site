#!/usr/bin/env python3
"""
reanalyze_colors.py
───────────────────
Re-analyzes a specific list of films and reassigns their iconic color
using the existing Gemini pipeline with a STRICT perception-first prompt.

This script overrides the default prompt with additional rules to prevent
common mis-assignments (e.g. ambar_desertico for dark dramatic films).

Usage:
    python pipeline/reanalyze_colors.py
    python pipeline/reanalyze_colors.py --dry-run

Environment:
    GEMINI_API_KEY        Required — calls Gemini 2.5 Flash
    SUPABASE_URL          Required for DB updates
    SUPABASE_SERVICE_KEY  Required for DB updates
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

# ─── Env + path setup ─────────────────────────────────────────────────────────

BASE_DIR     = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
WORKS_DIR    = PIPELINE_DIR / "normalized" / "works"

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(PIPELINE_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env.local")
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


# ─── Films to reanalyze ───────────────────────────────────────────────────────

FILMS_TO_REANALYZE = [
    "work_goodfellas_1990",
    "work_fight-club_1999",
    "work_chinatown_1974",
    "work_the-godfather_1972",
    "work_the-godfather-part-ii_1974",
    "work_pulp-fiction_1994",
    "work_barton-fink_1991",
    "work_shoplifters_2018",
    "work_secrets-lies_1996",
    "work_wheel-of-fortune-and-fantasy_2021",
    "work_the-souvenir_2019",
    "work_showing-up_2023",
    "work_madeline-s-madeline_2018",
    "work_son-of-saul_2015",
    "work_winter-sleep_2014",
    "work_underground_1995",
    "work_beau-travail_2000",
    "work_the-pianist_2002",
    "work_sans-soleil_1983",
    "work_taste-of-cherry_1997",
]

# ─── Strict prompt prefix ─────────────────────────────────────────────────────

STRICT_PROMPT_PREFIX = """
CRITICAL RULES FOR THIS ANALYSIS:
- ambar_desertico means VISUALLY WARM AMBER/GOLDEN tones dominate 
  40%+ of the actual frames. Examples: Barry Lyndon (candlelight), 
  Days of Heaven (golden fields), Paris Texas (desert sunsets).
  DO NOT use it for dramatic dark films just because they feel 
  "warm" emotionally.
- claroscuro_dramatico means the film is LITERALLY black and white 
  or near-monochrome. Do NOT use for dark color films.
- negro_abismo: dark urban environments, noir, underworld, violence.
  Examples: Goodfellas, The Godfather, Chinatown, Fight Club.
- cian_melancolico: cold emotional distance, contemporary realism,
  muted blue-grey palette. Examples: Shoplifters, Portrait of a Lady
  on Fire, cold Japanese or European contemporary cinema.
- azul_nocturno: night scenes, urban blue light, melancholy.

If you are unsure between ambar_desertico and another color,
choose the OTHER color. ambar_desertico should only be used when
warm golden tones are visually unmistakable and dominant.

"""


# ─── Gemini call ──────────────────────────────────────────────────────────────

def call_gemini_strict(work_id: str, work: dict) -> str:
    """
    Call Gemini with the strict perception-first prompt.
    Prepends STRICT_PROMPT_PREFIX to the standard cultural memory prompt,
    then returns only the iconic_color string.

    Args:
        work_id: The work identifier (filename stem, e.g. work_goodfellas_1990).
        work:    The normalized JSON dict loaded from disk.
                 Note: the key inside the JSON is 'id', not 'work_id'.
    """
    from google import genai
    from pipeline.phase_2_cultural_memory.gemini_prompter import (
        SYSTEM_PROMPT,
        build_cultural_memory_prompt,
        extract_perception_response,
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")

    title    = work.get("title", work_id)
    year     = work.get("year", 0)
    director = _extract_director(work)

    film_prompt = build_cultural_memory_prompt(
        work_id=work_id,
        title=title,
        year=year,
        director=director,
        countries=work.get("countries", []),
        genres=work.get("genres", []),
    )

    # Prepend strict rules to the film-specific prompt (after the system prompt)
    strict_film_prompt = STRICT_PROMPT_PREFIX + film_prompt

    full_prompt = SYSTEM_PROMPT + "\n\n" + strict_film_prompt

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )

    if not response.text:
        raise ValueError("Empty response from Gemini")

    text = response.text.strip()
    # Strip markdown fences if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    parsed = extract_perception_response(text)
    return parsed["iconic_color"]


def _extract_director(work: dict) -> str | None:
    director_data = work.get("people", {}).get("director")
    if not director_data:
        return None
    if isinstance(director_data, list) and director_data:
        first = director_data[0]
        return first.get("name") if isinstance(first, dict) else first
    if isinstance(director_data, dict):
        return director_data.get("name")
    return None


# ─── Supabase update ──────────────────────────────────────────────────────────

def update_supabase(work_id: str, new_color: str) -> None:
    """Update color_iconico in Supabase color_assignments table."""
    from supabase import create_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set")

    client = create_client(url, key)
    client.table("color_assignments").update(
        {"color_iconico": new_color}
    ).eq("work_id", work_id).execute()


# ─── Normalized JSON update ───────────────────────────────────────────────────

def update_normalized_json(work_id: str, work: dict, new_color: str) -> None:
    """
    Update color in the normalized JSON file.

    The script supports two storage locations:
      - work['prisma_palette']['primary']         (current pipeline format)
      - work['color_assignments'][0]['color_iconico']  (legacy format, per spec)
    Both are updated if they exist.
    """
    path = WORKS_DIR / f"{work_id}.json"

    # Update prisma_palette.primary (current format)
    if "prisma_palette" in work and isinstance(work["prisma_palette"], dict):
        work["prisma_palette"]["primary"] = new_color

    # Update color_assignments[0].color_iconico (legacy format)
    color_assignments = work.get("color_assignments")
    if isinstance(color_assignments, list) and color_assignments:
        color_assignments[0]["color_iconico"] = new_color

    path.write_text(json.dumps(work, indent=2, ensure_ascii=False))


# ─── Current color helper ─────────────────────────────────────────────────────

def get_current_color(work: dict) -> str | None:
    """Return the current iconic color from the normalized work dict."""
    # Try prisma_palette first (current format)
    palette = work.get("prisma_palette")
    if isinstance(palette, dict):
        primary = palette.get("primary")
        if primary:
            return primary

    # Try color_assignments (legacy format)
    color_assignments = work.get("color_assignments")
    if isinstance(color_assignments, list) and color_assignments:
        return color_assignments[0].get("color_iconico")

    return None


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-analyze film colors using strict Gemini perception prompt.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what WOULD change without writing anything.",
    )
    args = parser.parse_args()

    dry_run = args.dry_run

    if dry_run:
        print("\n  ── DRY RUN: no files or DB rows will be written ──\n")
    else:
        print("\n  ── LIVE RUN: changes will be written ──\n")

    changed   = []
    confirmed = []
    errors    = []
    new_colors: list[str] = []

    for work_id in FILMS_TO_REANALYZE:
        path = WORKS_DIR / f"{work_id}.json"

        # Load normalized JSON
        if not path.exists():
            print(f"  ✗ NOT FOUND: {work_id}")
            errors.append(work_id)
            continue

        work = json.loads(path.read_text())
        old_color = get_current_color(work)

        print(f"  → {work_id}  (current: {old_color or 'none'})")

        try:
            new_color = call_gemini_strict(work_id, work)
        except Exception as e:
            print(f"  ✗ GEMINI ERROR: {work_id}: {e}")
            errors.append(work_id)
            time.sleep(2)
            continue

        if new_color != old_color:
            print(f"  CHANGE: {work_id}: {old_color} → {new_color}")
            changed.append(work_id)
            new_colors.append(new_color)

            if not dry_run:
                update_normalized_json(work_id, work, new_color)
                try:
                    update_supabase(work_id, new_color)
                    print(f"    ✓ Supabase updated")
                except Exception as e:
                    print(f"    ✗ Supabase update failed: {e}")
        else:
            print(f"  KEEP:   {work_id}: {old_color} (confirmed)")
            confirmed.append(work_id)
            new_colors.append(old_color or "unknown")

        # Rate limit: 2 seconds between Gemini calls
        time.sleep(2)

    # ─── Summary ──────────────────────────────────────────────────────────────

    total = len(FILMS_TO_REANALYZE)
    print(f"\n  {'─' * 56}")
    print(f"  SUMMARY")
    print(f"  {'─' * 56}")
    print(f"  Total analyzed : {total}")
    print(f"  Changed        : {len(changed)}")
    print(f"  Confirmed      : {len(confirmed)}")
    if errors:
        print(f"  Errors         : {len(errors)}")

    if changed:
        print(f"\n  Changed films:")
        for wid in changed:
            print(f"    • {wid}")

    if new_colors:
        print(f"\n  Color distribution (after reanalysis):")
        for color, count in sorted(Counter(new_colors).items(), key=lambda x: -x[1]):
            bar = "█" * count
            print(f"    {color:<28}  {bar}  ({count})")

    if dry_run:
        print(f"\n  [DRY RUN complete — no changes were written]\n")
    else:
        print(f"\n  [Done — {len(changed)} film(s) updated]\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
