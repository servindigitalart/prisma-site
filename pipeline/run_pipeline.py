#!/usr/local/bin/python3
"""
run_pipeline.py
───────────────
Orchestrate the full Prisma AI pipeline for one or all normalized works.

What this does (in order):
  1. Load normalized work JSON from pipeline/normalized/works/{work_id}.json
  2. Cultural Memory — Perception-based color reasoning via Gemini v5.0 (PERCEPTION-FIRST)
  3. Phase 2D — External research via Gemini (optional enrichment; skipped if no GEMINI_API_KEY)
  4. Phase 3 — Visual identity resolution (tiered threshold logic)
  5. Write derived color JSON → pipeline/derived/color/{work_id}.json
  6. Update work's prisma_palette in the normalized JSON
  7. Optionally migrate to Supabase (--migrate)

Pipeline Architecture v2.0 (March 2024):
  - Removed broken heuristic systems (Phase 2A genre rules, 2B scoring, 2E keyword matching)
  - Single source of truth: Gemini v5.0 perception-based Cultural Memory
  - Fallback: azul_nocturno (neutral), never rojo_pasional
  - Phase 3 tiered thresholds: ≥0.85 cultural wins, 0.75-0.84 blend, <0.75 fallback

Usage:
    python pipeline/run_pipeline.py work_marie-antoinette_2006
    python pipeline/run_pipeline.py --all
    python pipeline/run_pipeline.py --all --migrate
    python pipeline/run_pipeline.py work_xxx --dry-run   (run phases, skip file writes)
    python pipeline/run_pipeline.py --all --skip-existing

Environment variables:
    GEMINI_API_KEY   Optional — enables Cultural Memory + Phase 2D research
    SUPABASE_URL     Required for --migrate
    SUPABASE_SERVICE_KEY  Required for --migrate
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR     = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
WORKS_DIR    = PIPELINE_DIR / "normalized" / "works"
DERIVED_DIR  = PIPELINE_DIR / "derived" / "color"
DERIVED_DIR.mkdir(parents=True, exist_ok=True)

# Add subdirs to sys.path so we can import phase modules
sys.path.insert(0, str(BASE_DIR))          # project root (for pipeline.lib.*)
sys.path.insert(0, str(PIPELINE_DIR))      # pipeline/ (for phase_* packages)


# ─── Lazy imports (after path setup) ─────────────────────────────────────────

def _import_cultural_memory():
    from pipeline.phase_2_cultural_memory.resolver import resolve_cultural_memory
    return resolve_cultural_memory


def _import_phase_2d():
    from phase_2d_external_research.gemini_executor import execute_external_research
    return execute_external_research


def _import_phase_3():
    from phase_3_visual_resolution.resolver import resolve_visual_identity
    from phase_3_visual_resolution.schema import to_dict
    return resolve_visual_identity, to_dict


def _import_phase_2d():
    from phase_2d_external_research.gemini_executor import execute_external_research
    return execute_external_research


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_work(work_id: str) -> dict[str, Any] | None:
    path = WORKS_DIR / f"{work_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def list_all_work_ids() -> list[str]:
    if not WORKS_DIR.exists():
        return []
    return [p.stem for p in sorted(WORKS_DIR.glob("work_*.json"))]


def derived_exists(work_id: str) -> bool:
    return (DERIVED_DIR / f"{work_id}.json").exists()


def print_step(step: str, label: str, ok: bool = True) -> None:
    icon = "✓" if ok else "✗"
    print(f"    [{icon}] {step}: {label}")


def run_migrate_single(work_id: str, dry_run: bool) -> bool:
    """Run migrate_to_db.py for a single work."""
    import subprocess
    cmd = [sys.executable, "pipeline/migrate_to_db.py", "--film", work_id]
    if not dry_run:
        cmd.append("--execute")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
    if result.returncode != 0:
        print(f"    ✗ migrate failed: {result.stderr.strip() or result.stdout.strip()}")
        return False
    print(f"    ✓ migrated → Supabase")
    return True


# ─── Single-work pipeline ─────────────────────────────────────────────────────

def run_for_work(
    work_id: str,
    dry_run: bool = False,
    migrate: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Run the full Prisma pipeline for one work.
    Returns True on success.
    
    New simplified flow:
      1. Load normalized work JSON
      2. Call Cultural Memory (Gemini v5.0) → perception-based color reasoning
      3. Call Phase 3 Visual Identity Resolution → final color + attributes
      4. Write derived color JSON
      5. Update prisma_palette in normalized work JSON
      6. Optionally migrate to Supabase
    """
    print(f"\n  ── {work_id} ──")

    # Load work JSON
    work = load_work(work_id)
    if work is None:
        print(f"    ✗ Work not found: {WORKS_DIR / work_id}.json")
        return False

    title = work.get("title", work_id)
    year  = work.get("year", "")
    print(f"    {title} ({year})")

    # ── Cultural Memory: Perception-Based Color Reasoning (Gemini v5.0) ───────
    print("    [Cultural Memory] Gemini visual perception analysis...")
    cultural_memory = None
    try:
        resolve_cultural_memory = _import_cultural_memory()
        
        # Extract director name from people dict
        director = None
        if work.get("people", {}).get("director"):
            director_data = work["people"]["director"]
            if isinstance(director_data, list) and len(director_data) > 0:
                director = director_data[0].get("name") if isinstance(director_data[0], dict) else director_data[0]
            elif isinstance(director_data, dict):
                director = director_data.get("name")
        
        # Build work dict for Cultural Memory resolver
        work_for_cm = {
            "work_id": work_id,
            "title": title,
            "year": year or 2000,
            "director": director,
            "countries": work.get("countries", []),
            "genres": work.get("genres", [])
        }
        
        cultural_memory = resolve_cultural_memory(work=work_for_cm, use_gemini=True)
        
        color = cultural_memory.iconic_color
        confidence = cultural_memory.color_consensus_strength
        print_step("Cultural Memory", f"color={color}  confidence={confidence:.2f}")
        
    except Exception as e:
        print_step("Cultural Memory", f"FAILED — {e}", ok=False)
        if verbose:
            import traceback; traceback.print_exc()
        
        # Create fallback CulturalMemoryResult with low confidence
        from pipeline.phase_2_cultural_memory.schema import CulturalMemoryResult
        cultural_memory = CulturalMemoryResult(
            work_id=work_id,
            iconic_color="azul_nocturno",
            color_rank=0.30,
            gemini_raw_score=0.30,
            color_rank_reasoning="Gemini failed — neutral fallback assigned",
            secondary_colors=[],
            visual_rhythm="moderado_balanceado",
            emotional_temperature="neutral_contemplativo",
            abstraction_level="realista_con_estilizacion",
            supporting_evidence=["Gemini failed - using neutral fallback"],
            llm_raw_response=f"ERROR: {str(e)}"
        )
        print_step("Cultural Memory", f"fallback → azul_nocturno (neutral)", ok=True)

    # ── Phase 2D: External Research (optional enrichment) ─────────────────────
    external_research: dict[str, Any] | None = None
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        print("    [2D] External research via Gemini...")
        try:
            execute_external_research = _import_phase_2d()
            research_request = {
                "request_metadata": {
                    "work_id": work_id,
                    "trigger_reason": "orchestrator",
                    "title": title,
                    "year": year,
                },
                "work": work,
                "primary_color_candidate": cultural_memory.iconic_color,
            }
            external_research = execute_external_research(research_request, gemini_api_key=gemini_key)
            quality = external_research.get("research_quality", "?")
            print_step("2D", f"research_quality={quality}")
        except Exception as e:
            print_step("2D", f"skipped — {e}", ok=True)  # non-fatal
    else:
        print("    [2D] Skipped (no GEMINI_API_KEY)")

    # ── Phase 3: Visual Identity Resolution ───────────────────────────────────
    print("    [3]  Visual identity resolution...")
    try:
        resolve_visual_identity, to_dict = _import_phase_3()
        resolution = resolve_visual_identity(
            work_id=work_id,
            color_assignment={},  # No longer used - Cultural Memory is the source
            cultural_weight={},   # No longer used
            external_research=external_research,
            cultural_memory=cultural_memory,
            film_title=title,
        )
        resolution_dict = to_dict(resolution)
        print_step("3", f"color_iconico={resolution_dict['color_iconico']}  "
                        f"rank={resolution_dict['color_rank']:.2f}")
    except Exception as e:
        print_step("3", f"FAILED — {e}", ok=False)
        if verbose:
            import traceback; traceback.print_exc()
        # Fall back to Cultural Memory result directly
        resolution_dict = {
            "work_id": work_id,
            "color_iconico": cultural_memory.iconic_color,
            "color_rank": cultural_memory.color_consensus_strength,
            "colores_secundarios": cultural_memory.secondary_colors or [],
            "temperatura_emocional": cultural_memory.emotional_temperature,
            "ritmo_visual": cultural_memory.visual_rhythm,
            "grado_abstraccion_visual": cultural_memory.abstraction_level,
        }
        print_step("3-fallback", f"using Cultural Memory result: {cultural_memory.iconic_color}")

    # ── Write derived output ───────────────────────────────────────────────────
    derived_output = {
        "work_id": work_id,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "2.0",  # Updated version for new architecture
        "cultural_memory": {
            "iconic_color": cultural_memory.iconic_color,
            "color_confidence": cultural_memory.color_confidence,
            "color_consensus_strength": cultural_memory.color_consensus_strength,
            "secondary_colors": cultural_memory.secondary_colors,
            "visual_rhythm": cultural_memory.visual_rhythm,
            "emotional_temperature": cultural_memory.emotional_temperature,
            "abstraction_level": cultural_memory.abstraction_level,
            "supporting_evidence": cultural_memory.supporting_evidence,
        },
        "external_research": external_research,
        "resolution": resolution_dict,
    }

    if not dry_run:
        derived_path = DERIVED_DIR / f"{work_id}.json"
        derived_path.write_text(json.dumps(derived_output, indent=2, default=str))
        print_step("write", f"derived → pipeline/derived/color/{work_id}.json")

        # Update prisma_palette in the normalized work JSON
        work["prisma_palette"] = {
            "primary":   resolution_dict["color_iconico"],
            "secondary": resolution_dict["colores_secundarios"],
            "rank":      resolution_dict["color_rank"],
            "mode": (
                "monochromatic"
                if resolution_dict["color_iconico"] in ("claroscuro_dramatico", "monocromatico_intimo")
                else "color"
            ),
            "source": "cultural_memory",  # Updated source
            "temperatura_emocional":     resolution_dict.get("temperatura_emocional"),
            "ritmo_visual":              resolution_dict.get("ritmo_visual"),
            "grado_abstraccion_visual":  resolution_dict.get("grado_abstraccion_visual"),
        }
        work_path = WORKS_DIR / f"{work_id}.json"
        work_path.write_text(json.dumps(work, indent=2))
        print_step("write", f"prisma_palette → {work_id}.json")
    else:
        print(f"    [DRY RUN] would write derived + update prisma_palette")
        print(f"    [DRY RUN] final color: {resolution_dict['color_iconico']} "
              f"(rank={resolution_dict['color_rank']:.2f})")

    # ── Migrate ───────────────────────────────────────────────────────────────
    if migrate and not dry_run:
        print("    [migrate] Upserting to Supabase...")
        run_migrate_single(work_id, dry_run=False)

    print(f"    ✅ Done: {work_id}")
    return True


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Prisma AI pipeline for one or all normalized works.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "work_id", nargs="?",
        help="work_id to process (e.g. work_marie-antoinette_2006).",
    )
    group.add_argument(
        "--all", action="store_true",
        help="Process all normalized works in pipeline/normalized/works/.",
    )
    parser.add_argument(
        "--migrate", action="store_true",
        help="After running phases, upsert the work to Supabase via migrate_to_db.py.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run all pipeline phases but skip writing files and migrating.",
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip works that already have a derived color file.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print full tracebacks on errors.",
    )
    args = parser.parse_args()

    if args.all:
        work_ids = list_all_work_ids()
        if not work_ids:
            print(f"\n  ✗ No work files found in {WORKS_DIR}\n")
            return 1
        print(f"\n  PRISMA Pipeline — processing {len(work_ids)} work(s)")
    else:
        work_ids = [args.work_id]
        print(f"\n  PRISMA Pipeline")

    if args.dry_run:
        print("  ── DRY RUN: phases run, no files written ──")

    succeeded = []
    failed = []

    for work_id in work_ids:
        if args.skip_existing and derived_exists(work_id):
            print(f"\n  ↷ {work_id}: derived already exists — skipping")
            succeeded.append(work_id)
            continue

        ok = run_for_work(
            work_id,
            dry_run=args.dry_run,
            migrate=args.migrate,
            verbose=args.verbose,
        )
        (succeeded if ok else failed).append(work_id)

    # Summary
    print(f"\n  {'─' * 50}")
    print(f"  Succeeded: {len(succeeded)}")
    print(f"  Failed:    {len(failed)}")
    if failed:
        print(f"\n  Failed works:")
        for wid in failed:
            print(f"    • {wid}")
    print()

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
