#!/usr/bin/env python3
"""
rerun_color_pipeline.py
───────────────────────
Re-runs the full AI color pipeline (Cultural Memory → Phase 3 → Supabase update)
for works whose color_assignments.ai_confidence equals the fallback value 0.8,
ordered by ranking_scores DESC so the highest-ranked films are fixed first.

What this does per film:
  1. Fetches work metadata from Supabase (title, year, director, etc.)
  2. Runs Cultural Memory via Gemini (phase_2_cultural_memory)
  3. Runs Phase 3 visual identity resolution
  4. Writes updated derived color JSON to pipeline/derived/color/
  5. Updates prisma_palette.primary in normalized work JSON
  6. Updates color_assignments row in Supabase

Usage:
    python pipeline/rerun_color_pipeline.py --dry-run     # Show affected works, no writes
    python pipeline/rerun_color_pipeline.py               # Live run (all fallback works)
    python pipeline/rerun_color_pipeline.py --limit 10    # Process only first N works
    python pipeline/rerun_color_pipeline.py --work-id work_blade-runner_1982  # Single work

Environment:
    GEMINI_API_KEY        Required — calls Gemini 2.5 Flash for Cultural Memory
    SUPABASE_URL          Required
    SUPABASE_SERVICE_KEY  Required
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import requests

# ─── Env + path setup ─────────────────────────────────────────────────────────

BASE_DIR     = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
WORKS_DIR    = PIPELINE_DIR / "normalized" / "works"
DERIVED_DIR  = PIPELINE_DIR / "derived" / "color"
DERIVED_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(PIPELINE_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env.local")
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# ─── Fallback sentinel value set by the pipeline when Gemini confidence is
#     unavailable (see recompute_film_scores.py: ai_confidence = cultural_weight,
#     and the migrate_to_db default is 0.8 when no real score exists). ─────────
FALLBACK_AI_CONFIDENCE = 0.8

# Rate-limit between Gemini calls (seconds)
GEMINI_RATE_LIMIT = 3

# TMDB
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
RAW_DIR      = PIPELINE_DIR / "raw"


# ─── TMDB fetch + normalize ───────────────────────────────────────────────────

def fetch_and_normalize(work_id: str, tmdb_id: int, verbose: bool = False) -> bool:
    """
    Fetch raw movie data from TMDB and run normalize_tmdb_work.py.
    Returns True if the normalized work JSON exists afterwards.

    The raw file is cached at pipeline/raw/tmdb_{tmdb_id}.json so subsequent
    re-runs skip the network call.
    """
    raw_path  = RAW_DIR / f"tmdb_{tmdb_id}.json"
    norm_path = WORKS_DIR / f"{work_id}.json"

    # ── 1. Fetch raw from TMDB (unless already cached) ────────────────────────
    # Replicates ingest_tmdb.py's exact format:
    #   {"movie": {...}, "credits": {...}, "videos": {...}, "keywords": {...}, "watch_providers": {...}}
    if not raw_path.exists():
        if not TMDB_API_KEY:
            print(f"    ✗ TMDB_API_KEY not set — cannot fetch raw data")
            return False

        def _tmdb_get(endpoint: str) -> dict:
            r = requests.get(
                f"https://api.themoviedb.org/3{endpoint}",
                params={"api_key": TMDB_API_KEY},
                timeout=15,
            )
            r.raise_for_status()
            return r.json()

        try:
            data = {
                "movie":           _tmdb_get(f"/movie/{tmdb_id}"),
                "credits":         _tmdb_get(f"/movie/{tmdb_id}/credits"),
                "videos":          _tmdb_get(f"/movie/{tmdb_id}/videos"),
                "keywords":        _tmdb_get(f"/movie/{tmdb_id}/keywords"),
                "watch_providers": _tmdb_get(f"/movie/{tmdb_id}/watch/providers"),
            }
        except requests.RequestException as e:
            print(f"    ✗ TMDB request failed: {e}")
            return False
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"    ↓ Fetched raw data → {raw_path.name}")
    else:
        print(f"    ↷ Raw cache hit: {raw_path.name}")

    # ── 2. Normalize ──────────────────────────────────────────────────────────
    result = subprocess.run(
        [sys.executable, "pipeline/normalize_tmdb_work.py", str(tmdb_id)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(BASE_DIR),
    )
    if result.returncode != 0:
        err = (result.stderr.strip() or result.stdout.strip())[:300]
        print(f"    ✗ normalize_tmdb_work.py failed: {err}")
        if verbose:
            print(result.stdout[-500:] if result.stdout else "")
        return False

    if not norm_path.exists():
        # Output might have a different slug — scan for it
        for p in WORKS_DIR.glob("*.json"):
            try:
                d = json.loads(p.read_text())
                if d.get("ids", {}).get("tmdb") == tmdb_id:
                    print(f"    ↺ Normalized file found at different slug: {p.name}")
                    return True
            except Exception:
                continue
        print(f"    ✗ normalize ran OK but {norm_path.name} still missing")
        return False

    print(f"    ✓ Normalized → {norm_path.name}")
    return True


# ─── Supabase helpers ─────────────────────────────────────────────────────────

def _get_supabase():
    from supabase import create_client
    url = os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    return create_client(url, key)


def fetch_fallback_works(db, limit: int | None) -> list[dict]:
    """
    Return works whose ai_confidence == FALLBACK_AI_CONFIDENCE,
    ordered by their global ranking score (best-ranked first).

    Strategy:
      1. Pull all color_assignments with ai_confidence = 0.8
      2. Pull ranking_scores for entity_type='work', context='global'
      3. Left-join and sort by ranking score DESC (unranked films last)
    """
    print("  Fetching works with fallback ai_confidence=0.8 from Supabase…")

    # 1. All color assignments with the fallback confidence
    offset = 0
    ca_rows: list[dict] = []
    while True:
        chunk = (
            db.table("color_assignments")
            .select("work_id, color_iconico, ai_confidence")
            .eq("ai_confidence", FALLBACK_AI_CONFIDENCE)
            .range(offset, offset + 999)
            .execute()
        ).data
        ca_rows.extend(chunk)
        if len(chunk) < 1000:
            break
        offset += 1000

    if not ca_rows:
        print("  No works with fallback ai_confidence found.")
        return []

    print(f"  Found {len(ca_rows)} works with ai_confidence=0.8")

    # 2. Ranking scores (global)
    offset = 0
    rs_rows: list[dict] = []
    while True:
        chunk = (
            db.table("ranking_scores")
            .select("entity_id, score")
            .eq("entity_type", "work")
            .eq("context", "global")
            .range(offset, offset + 999)
            .execute()
        ).data
        rs_rows.extend(chunk)
        if len(chunk) < 1000:
            break
        offset += 1000

    score_map: dict[str, float] = {r["entity_id"]: r["score"] for r in rs_rows}

    # 3. Sort by ranking score DESC (unranked → 0.0)
    ca_rows.sort(key=lambda r: score_map.get(r["work_id"], 0.0), reverse=True)

    if limit:
        ca_rows = ca_rows[:limit]

    # 4. Attach ranking score and published work metadata
    work_ids = [r["work_id"] for r in ca_rows]

    # Fetch work titles/years/tmdb_ids in batches of 100
    work_meta: dict[str, dict] = {}
    for i in range(0, len(work_ids), 100):
        batch_ids = work_ids[i : i + 100]
        rows = (
            db.table("works")
            .select("id, title, year, is_published, tmdb_id")
            .in_("id", batch_ids)
            .execute()
        ).data
        for w in rows:
            work_meta[w["id"]] = w

    # Build final list
    result = []
    for row in ca_rows:
        wid  = row["work_id"]
        meta = work_meta.get(wid, {})
        result.append({
            "work_id":        wid,
            "title":          meta.get("title", wid),
            "year":           meta.get("year", "?"),
            "published":      meta.get("is_published", False),
            "current_color":  row["color_iconico"],
            "ranking_score":  score_map.get(wid, 0.0),
            "tmdb_id":        meta.get("tmdb_id"),
        })

    return result


# ─── Lazy pipeline imports ────────────────────────────────────────────────────

def _import_cultural_memory():
    from pipeline.phase_2_cultural_memory.resolver import resolve_cultural_memory
    return resolve_cultural_memory


def _import_phase_3():
    from phase_3_visual_resolution.resolver import resolve_visual_identity
    from phase_3_visual_resolution.schema import to_dict
    return resolve_visual_identity, to_dict


# ─── Director extraction from normalized JSON ─────────────────────────────────

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


# ─── Per-film pipeline run ────────────────────────────────────────────────────

def run_for_work(
    db,
    work_id: str,
    title: str,
    year,
    tmdb_id: int | None,
    dry_run: bool,
    verbose: bool,
) -> tuple[str | None, str | None]:
    """
    Run the color pipeline for one work.

    Returns:
        (old_color, new_color) — new_color is None on failure.
    """
    # Load normalized JSON — fetch + normalize from TMDB if missing
    work_path = WORKS_DIR / f"{work_id}.json"
    if not work_path.exists():
        if tmdb_id:
            print(f"    ⚠ Normalized JSON missing — fetching from TMDB (id={tmdb_id})…")
            if dry_run:
                print(f"    [DRY RUN] would fetch tmdb_{tmdb_id} and normalize")
                return None, None
            ok = fetch_and_normalize(work_id, tmdb_id, verbose=verbose)
            if not ok:
                print(f"    ✗ Could not normalize {work_id} from TMDB")
                return None, None
            # After normalization the slug might differ — re-scan
            if not work_path.exists():
                for p in WORKS_DIR.glob("*.json"):
                    try:
                        d = json.loads(p.read_text())
                        if d.get("ids", {}).get("tmdb") == tmdb_id:
                            work_path = p
                            break
                    except Exception:
                        continue
            if not work_path.exists():
                print(f"    ✗ Normalized JSON still not found after fetch: {work_path}")
                return None, None
        else:
            print(f"    ✗ Normalized JSON not found and no tmdb_id available: {work_path}")
            return None, None

    work = json.loads(work_path.read_text())
    old_color: str | None = None
    palette = work.get("prisma_palette")
    if isinstance(palette, dict):
        old_color = palette.get("primary")
    if not old_color:
        assignments = work.get("color_assignments")
        if isinstance(assignments, list) and assignments:
            old_color = assignments[0].get("color_iconico")

    director = _extract_director(work)

    # ── Cultural Memory (Gemini) ───────────────────────────────────────────────
    cultural_memory = None
    try:
        resolve_cultural_memory = _import_cultural_memory()
        work_for_cm = {
            "work_id": work_id,
            "title":   title,
            "year":    year or 2000,
            "director":  director,
            "countries": work.get("countries", []),
            "genres":    work.get("genres", []),
        }
        cultural_memory = resolve_cultural_memory(work=work_for_cm, use_gemini=True)
        print(f"    [CM] color={cultural_memory.iconic_color}  "
              f"confidence={cultural_memory.color_consensus_strength:.2f}")
    except Exception as e:
        print(f"    ✗ Cultural Memory failed: {e}")
        if verbose:
            import traceback; traceback.print_exc()
        return old_color, None

    # ── Phase 3 Visual Identity Resolution ────────────────────────────────────
    try:
        resolve_visual_identity, to_dict = _import_phase_3()
        resolution = resolve_visual_identity(
            work_id=work_id,
            color_assignment={},
            cultural_weight={},
            external_research=None,
            cultural_memory=cultural_memory,
            film_title=title,
        )
        resolution_dict = to_dict(resolution)
    except Exception as e:
        print(f"    ✗ Phase 3 failed: {e}")
        if verbose:
            import traceback; traceback.print_exc()
        # Fall back to Cultural Memory output directly
        resolution_dict = {
            "work_id":              work_id,
            "color_iconico":        cultural_memory.iconic_color,
            "color_rank":           cultural_memory.color_consensus_strength,
            "colores_secundarios":  cultural_memory.secondary_colors or [],
            "temperatura_emocional": cultural_memory.emotional_temperature,
            "ritmo_visual":         cultural_memory.visual_rhythm,
            "grado_abstraccion":    cultural_memory.abstraction_level,
            "mode":                 "color",
        }

    new_color: str = resolution_dict["color_iconico"]
    new_rank: float = resolution_dict.get("color_rank", 0.5)

    print(f"    [P3] color_iconico={new_color}  rank={new_rank:.2f}")

    if dry_run:
        return old_color, new_color

    # ── Write derived color JSON ───────────────────────────────────────────────
    derived_path = DERIVED_DIR / f"{work_id}.json"
    derived_path.write_text(json.dumps(resolution_dict, indent=2, ensure_ascii=False))

    # ── Update normalized work JSON ───────────────────────────────────────────
    if isinstance(work.get("prisma_palette"), dict):
        work["prisma_palette"]["primary"] = new_color
    assignments = work.get("color_assignments")
    if isinstance(assignments, list) and assignments:
        assignments[0]["color_iconico"] = new_color
    work_path.write_text(json.dumps(work, indent=2, ensure_ascii=False))

    # ── Update Supabase color_assignments ─────────────────────────────────────
    try:
        db.table("color_assignments").update({
            "color_iconico": new_color,
            "color_rank":    new_rank,
            "ai_confidence": cultural_memory.color_consensus_strength,
            "colores_secundarios": resolution_dict.get("colores_secundarios", []),
            "temperatura_emocional": resolution_dict.get("temperatura_emocional"),
            "ritmo_visual":          resolution_dict.get("ritmo_visual"),
            "pipeline_version":      "rerun_v1.0",
        }).eq("work_id", work_id).execute()
        print(f"    ✓ Supabase updated")
    except Exception as e:
        print(f"    ✗ Supabase update failed: {e}")

    return old_color, new_color


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-run the AI color pipeline for works with fallback ai_confidence=0.8.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what WOULD change; no files or DB rows are written.",
    )
    parser.add_argument(
        "--limit", type=int, default=None, metavar="N",
        help="Process only the first N works (ordered by ranking score DESC).",
    )
    parser.add_argument(
        "--work-id", type=str, default=None, metavar="WORK_ID",
        help="Process a single specific work ID (bypasses ai_confidence filter).",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print tracebacks on errors.",
    )
    args = parser.parse_args()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY is not set — Gemini calls will fail.")
        return 1

    db = _get_supabase()

    if args.dry_run:
        print("\n  ── DRY RUN: no files or DB rows will be written ──\n")
    else:
        print("\n  ── LIVE RUN: changes WILL be written ──\n")

    # ── Build work list ────────────────────────────────────────────────────────
    if args.work_id:
        # Single-work mode: fetch metadata from Supabase
        rows = (
            db.table("works")
            .select("id, title, year, tmdb_id")
            .eq("id", args.work_id)
            .execute()
        ).data
        if not rows:
            print(f"ERROR: work '{args.work_id}' not found in Supabase.")
            return 1
        w = rows[0]
        ca = (
            db.table("color_assignments")
            .select("color_iconico, ai_confidence")
            .eq("work_id", args.work_id)
            .execute()
        ).data
        current_color = ca[0]["color_iconico"] if ca else "unknown"
        works = [{
            "work_id":       w["id"],
            "title":         w["title"],
            "year":          w["year"],
            "published":     True,
            "current_color": current_color,
            "ranking_score": 0.0,
            "tmdb_id":       w.get("tmdb_id"),
        }]
    else:
        works = fetch_fallback_works(db, limit=args.limit)

    if not works:
        print("  Nothing to process.")
        return 0

    print(f"\n  Processing {len(works)} film(s)…\n")

    changed   : list[str] = []
    confirmed : list[str] = []
    failed    : list[str] = []
    new_colors: list[str] = []

    for i, entry in enumerate(works, 1):
        work_id = entry["work_id"]
        title   = entry["title"]
        year    = entry["year"]
        current = entry["current_color"]
        score   = entry["ranking_score"]
        tmdb_id = entry.get("tmdb_id")

        print(f"  [{i}/{len(works)}] {work_id}")
        print(f"    {title} ({year})  |  current={current}  |  score={score:.3f}"
              + (f"  |  tmdb={tmdb_id}" if tmdb_id else ""))

        old_color, new_color = run_for_work(
            db=db,
            work_id=work_id,
            title=title,
            year=year,
            tmdb_id=tmdb_id,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

        if new_color is None:
            failed.append(work_id)
        elif new_color != old_color:
            print(f"    → CHANGED: {old_color} → {new_color}")
            changed.append(work_id)
            new_colors.append(new_color)
        else:
            print(f"    → KEPT: {old_color} (confirmed)")
            confirmed.append(work_id)
            new_colors.append(new_color or "unknown")

        # Rate limit between Gemini calls
        if i < len(works):
            time.sleep(GEMINI_RATE_LIMIT)

    # ── Summary ───────────────────────────────────────────────────────────────
    total = len(works)
    print(f"\n  {'─' * 56}")
    print(f"  SUMMARY")
    print(f"  {'─' * 56}")
    print(f"  Total processed : {total}")
    print(f"  Changed         : {len(changed)}")
    print(f"  Confirmed       : {len(confirmed)}")
    print(f"  Failed          : {len(failed)}")

    if changed:
        print(f"\n  Changed films:")
        for wid in changed:
            print(f"    • {wid}")

    if failed:
        print(f"\n  Failed films:")
        for wid in failed:
            print(f"    ✗ {wid}")

    if new_colors:
        print(f"\n  Color distribution (after re-run):")
        for color, count in sorted(Counter(new_colors).items(), key=lambda x: -x[1]):
            bar = "█" * min(count, 40)
            print(f"    {color:<28}  {bar}  ({count})")

    if args.dry_run:
        print(f"\n  [DRY RUN complete — no changes were written]\n")
    else:
        print(f"\n  [Done — {len(changed)} film(s) updated]\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
