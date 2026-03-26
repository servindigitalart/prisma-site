#!/usr/local/bin/python3
"""
validate_and_ingest.py
────────────────────────────────────────────────────────────────────────────────
10-step validation-first ingestion pipeline.

Each film goes through all 10 steps. Failures are logged and the batch
continues — the pipeline never crashes entirely. Rollback runs automatically
if the migration step succeeded but the post-migration check failed.

Steps:
  1. CONFIRM         — verify TMDB ID resolves to a real film
  2. INGEST          — fetch raw TMDB JSON (ingest_tmdb.py)
  3. NORMALIZE WORK  — normalize_tmdb_work.py → extract work_id
  4. NORMALIZE PEOPLE— normalize_tmdb_people.py
  5. NORMALIZE STUDIOS — normalize_tmdb_studios.py
  6. AI PIPELINE     — run_pipeline.py {work_id} (Gemini Cultural Memory + Phase 3)
  7. PRE-MIGRATE CHECK — verify derived color JSON has all required fields
  8. MIGRATE         — migrate_to_db.py --film {work_id} [--execute]
  9. POST-MIGRATE CHECK — verify DB record + color_assignments row exists
 10. DONE            — report success per film

Usage:
    python pipeline/validate_and_ingest.py --list pipeline/sight_and_sound_2022.txt --dry-run --limit 3
    python pipeline/validate_and_ingest.py --tmdb 44012 --dry-run
    python pipeline/validate_and_ingest.py --list pipeline/sight_and_sound_2022.txt --execute --limit 10
    python pipeline/validate_and_ingest.py --tmdb 18148 --execute

Flags:
    --list FILE    Path to a TMDB ID list (one ID per line, # comments ok)
    --tmdb ID      Single TMDB ID to process
    --dry-run      Resolve TMDB info; show all steps without writing files or touching DB
    --execute      Write files AND migrate to Supabase (default: --dry-run behavior)
    --limit N      Process only the first N films from the list

Environment variables:
    TMDB_API_KEY         Required for TMDB confirms
    GEMINI_API_KEY       Optional — needed for AI pipeline (step 6)
    SUPABASE_URL         Required for migrate + post-check (steps 8–9)
    SUPABASE_SERVICE_KEY Required for migrate + post-check (steps 8–9)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

import requests

BASE_DIR     = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
RAW_DIR      = PIPELINE_DIR / "raw"
WORKS_DIR    = PIPELINE_DIR / "normalized" / "works"
DERIVED_DIR  = PIPELINE_DIR / "derived" / "color"

TMDB_API = "https://api.themoviedb.org/3"
API_KEY  = os.getenv("TMDB_API_KEY")

# Fields required in pipeline/derived/color/{work_id}.json → resolution dict
REQUIRED_DERIVED_FIELDS = [
    "color_iconico",
    "temperatura_emocional",
    "ritmo_visual",
    "grado_abstraccion_visual",
]


# ─── TMDB helper ──────────────────────────────────────────────────────────────

def tmdb_fetch(endpoint: str, params: dict | None = None) -> dict:
    params = params or {}
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB_API}{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# ─── Supabase helpers ─────────────────────────────────────────────────────────

def get_supabase_client():
    """Return a supabase-py client using service credentials."""
    try:
        from supabase import create_client
    except ImportError:
        raise RuntimeError("supabase-py not installed: pip install supabase")
    url = os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env.local")
    return create_client(url, key)


def db_work_exists(work_id: str) -> bool:
    """Return True if the work exists in Supabase with at least one color_assignment."""
    try:
        db = get_supabase_client()
        res = db.from_("works").select("id").eq("id", work_id).execute()
        if not res.data:
            return False
        ca = db.from_("color_assignments").select("work_id").eq("work_id", work_id).execute()
        return bool(ca.data)
    except Exception as e:
        raise RuntimeError(f"Supabase query failed: {e}")


def db_rollback(work_id: str) -> None:
    """Delete all DB rows for work_id (rollback after failed post-migration check)."""
    db = get_supabase_client()
    # Order matters — FK constraints
    db.from_("work_people").delete().eq("work_id", work_id).execute()
    db.from_("work_studios").delete().eq("work_id", work_id).execute()
    db.from_("color_assignments").delete().eq("work_id", work_id).execute()
    db.from_("works").delete().eq("id", work_id).execute()


# ─── Subprocess runner ────────────────────────────────────────────────────────

def run_script(args: list[str], label: str) -> tuple[bool, str]:
    """
    Run a pipeline script as a subprocess.
    Returns (success, combined_output).
    """
    result = subprocess.run(
        [sys.executable] + args,
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    output = result.stdout.strip()
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        return False, f"FAILED (exit {result.returncode}): {err}"
    return True, output


# ─── ID list parser (same as ingest_batch.py) ─────────────────────────────────

def parse_id_list(list_file: Path) -> list[int]:
    ids: list[int] = []
    with open(list_file) as f:
        for lineno, line in enumerate(f, 1):
            line = line.split("#")[0].strip()
            if not line:
                continue
            try:
                ids.append(int(line))
            except ValueError:
                print(f"  ⚠  Line {lineno}: '{line}' is not a valid ID — skipping")
    return ids


# ─── Per-film pipeline ────────────────────────────────────────────────────────

STEP_WIDTH = 22  # column width for step labels


def step(n: int, label: str, status: str, detail: str = "") -> None:
    full_label = f"  Step {n:>2}/10  {label:<{STEP_WIDTH}}"
    suffix = f"  {detail}" if detail else ""
    print(f"{full_label}  {status}{suffix}")


def process_film(
    tmdb_id: int,
    dry_run: bool,
    execute: bool,
    skip_existing: bool = False,
) -> dict[str, Any]:
    """
    Run all 10 steps for a single TMDB ID.
    Returns a result dict: {tmdb_id, work_id, status, steps, error}.
    """
    result: dict[str, Any] = {
        "tmdb_id":   tmdb_id,
        "work_id":   None,
        "status":    "pending",
        "steps":     {},
        "error":     None,
        "migrated":  False,
    }

    # ── Step 1: CONFIRM ───────────────────────────────────────────────────────
    label = "CONFIRM"
    try:
        movie = tmdb_fetch(f"/movie/{tmdb_id}")
        title    = movie.get("title", "?")
        rel_date = movie.get("release_date", "")
        year     = rel_date[:4] if rel_date else "?"
        step(1, label, "✓", f"{title} ({year})")
        result["steps"][label] = "ok"
        result["tmdb_title"] = title
        result["tmdb_year"]  = year
    except Exception as e:
        step(1, label, "✗", str(e))
        result["steps"][label] = "failed"
        result["status"] = "failed"
        result["error"]  = f"CONFIRM: {e}"
        return result

    # ── --skip-existing check ─────────────────────────────────────────────────
    if skip_existing and execute:
        try:
            from slugify import slugify as _sl
            _expected_id = f"work_{_sl(title)}_{year}"
            if (WORKS_DIR / f"{_expected_id}.json").exists() and db_work_exists(_expected_id):
                step(2, "SKIP (exists)", "↷", f"{_expected_id} already in DB")
                result["work_id"] = _expected_id
                result["status"]  = "skipped"
                return result
        except Exception:
            pass  # Check failed — proceed normally

    # ── Step 2: INGEST ────────────────────────────────────────────────────────
    label = "INGEST"
    raw_file = RAW_DIR / f"tmdb_{tmdb_id}.json"
    if dry_run:
        existing = "already exists" if raw_file.exists() else "would fetch"
        step(2, label, "[DRY RUN]", existing)
        result["steps"][label] = "dry_run"
    elif raw_file.exists():
        step(2, label, "↷", "raw already exists — skipping fetch")
        result["steps"][label] = "skipped"
    else:
        ok, out = run_script(["pipeline/ingest_tmdb.py", str(tmdb_id)], label)
        if not ok:
            step(2, label, "✗", out)
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"INGEST: {out}"
            return result
        step(2, label, "✓", f"pipeline/raw/tmdb_{tmdb_id}.json")
        result["steps"][label] = "ok"
        time.sleep(0.3)

    # ── Step 3: NORMALIZE WORK ────────────────────────────────────────────────
    label = "NORMALIZE WORK"
    if dry_run:
        # Derive work_id from raw file if it exists, otherwise estimate
        work_id = None
        if raw_file.exists():
            try:
                raw = json.loads(raw_file.read_text())
                from slugify import slugify
                t = raw["movie"].get("title", "")
                y = raw["movie"].get("release_date", "")[:4]
                work_id = f"work_{slugify(t)}_{y}"
            except Exception:
                pass
        if work_id is None:
            from slugify import slugify
            work_id = f"work_{slugify(result['tmdb_title'])}_{result['tmdb_year']}"
        result["work_id"] = work_id
        step(3, label, "[DRY RUN]", f"estimated → {work_id}")
        result["steps"][label] = "dry_run"
    else:
        ok, out = run_script(["pipeline/normalize_tmdb_work.py", str(tmdb_id)], label)
        if not ok:
            step(3, label, "✗", out)
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"NORMALIZE WORK: {out}"
            return result
        # Parse work_id from output: "NORMALIZED work → pipeline/normalized/works/work_xxx.json"
        work_id = None
        for line in out.splitlines():
            if "NORMALIZED work →" in line:
                path_str = line.split("→")[-1].strip()
                work_id = Path(path_str).stem
                break
        if not work_id:
            step(3, label, "✗", f"could not parse work_id from: {out!r}")
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = "NORMALIZE WORK: work_id not found in output"
            return result
        result["work_id"] = work_id
        step(3, label, "✓", work_id)
        result["steps"][label] = "ok"

    work_id: str = result["work_id"]

    # ── Step 4: NORMALIZE PEOPLE ──────────────────────────────────────────────
    label = "NORMALIZE PEOPLE"
    if dry_run:
        step(4, label, "[DRY RUN]", "would run normalize_tmdb_people.py")
        result["steps"][label] = "dry_run"
    else:
        ok, out = run_script(["pipeline/normalize_tmdb_people.py", str(tmdb_id)], label)
        if not ok:
            step(4, label, "✗", out)
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"NORMALIZE PEOPLE: {out}"
            return result
        detail = next((l for l in out.splitlines() if "NORMALIZED people" in l), out)
        step(4, label, "✓", detail)
        result["steps"][label] = "ok"

    # ── Step 5: NORMALIZE STUDIOS ─────────────────────────────────────────────
    label = "NORMALIZE STUDIOS"
    if dry_run:
        step(5, label, "[DRY RUN]", "would run normalize_tmdb_studios.py")
        result["steps"][label] = "dry_run"
    else:
        ok, out = run_script(["pipeline/normalize_tmdb_studios.py", str(tmdb_id)], label)
        if not ok:
            step(5, label, "✗", out)
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"NORMALIZE STUDIOS: {out}"
            return result
        detail = next((l for l in out.splitlines() if "NORMALIZED studios" in l), out)
        step(5, label, "✓", detail)
        result["steps"][label] = "ok"

    # ── Step 6: AI PIPELINE ───────────────────────────────────────────────────
    label = "AI PIPELINE"
    derived_file = DERIVED_DIR / f"{work_id}.json"
    if dry_run:
        exists_note = "derived JSON already exists" if derived_file.exists() else "would run run_pipeline.py"
        step(6, label, "[DRY RUN]", exists_note)
        result["steps"][label] = "dry_run"
    elif derived_file.exists():
        step(6, label, "↷", "derived color JSON already exists — skipping")
        result["steps"][label] = "skipped"
        # prisma_palette will be restored in the block below (after step 6)
    else:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            step(6, label, "⚠", "GEMINI_API_KEY not set — AI pipeline will use fallback colors")
        ok, out = run_script(["pipeline/run_pipeline.py", work_id], label)
        if not ok:
            step(6, label, "✗", out[:120])
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"AI PIPELINE: {out[:200]}"
            return result
        step(6, label, "✓", f"pipeline/derived/color/{work_id}.json")
        result["steps"][label] = "ok"

    # ── Restore prisma_palette in normalized JSON (if step 6 was skipped) ─────
    # normalize_tmdb_work.py (step 3) always overwrites the normalized JSON,
    # wiping any prisma_palette written by a previous run_pipeline.py call.
    # If step 6 was skipped (derived JSON already exists), we restore it manually
    # so that transform_color_assignment() in migrate_to_db.py can build the row.
    if not dry_run:
        work_json_path = WORKS_DIR / f"{work_id}.json"
        if work_json_path.exists() and derived_file.exists():
            try:
                work_json = json.loads(work_json_path.read_text())
                if not work_json.get("prisma_palette"):
                    derived = json.loads(derived_file.read_text())
                    resolution = derived.get("resolution", {})
                    color = resolution.get("color_iconico")
                    if color:
                        MONO = {"claroscuro_dramatico", "monocromatico_intimo"}
                        work_json["prisma_palette"] = {
                            "primary":   color,
                            "secondary": resolution.get("colores_secundarios", []),
                            "rank":      resolution.get("color_rank", 0.85),
                            "mode":      "monochromatic" if color in MONO else "color",
                            "source":    "cultural_memory",
                            "temperatura_emocional":       resolution.get("temperatura_emocional"),
                            "ritmo_visual":                resolution.get("ritmo_visual"),
                            "grado_abstraccion_visual":    resolution.get("grado_abstraccion_visual"),
                        }
                        work_json_path.write_text(json.dumps(work_json, indent=2))
                        print(f"  {'':>{STEP_WIDTH + 12}}  ↺ restored prisma_palette from derived JSON ({color})")
            except Exception:
                pass  # Non-fatal — step 7 will catch the missing fields

    # ── Step 7: PRE-MIGRATION CHECK ───────────────────────────────────────────
    label = "PRE-MIGRATE CHECK"
    if dry_run:
        if derived_file.exists():
            try:
                derived = json.loads(derived_file.read_text())
                resolution = derived.get("resolution", {})
                missing = [f for f in REQUIRED_DERIVED_FIELDS if not resolution.get(f)]
                if missing:
                    step(7, label, "[DRY RUN] ⚠", f"derived exists but missing: {missing}")
                else:
                    step(7, label, "[DRY RUN] ✓", f"derived fields ok: color={resolution.get('color_iconico')}")
            except Exception as e:
                step(7, label, "[DRY RUN] ⚠", f"could not read derived JSON: {e}")
        else:
            step(7, label, "[DRY RUN]", "derived JSON not yet created (step 6 was dry run)")
        result["steps"][label] = "dry_run"
    else:
        if not derived_file.exists():
            step(7, label, "✗", f"derived JSON not found: {derived_file}")
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = "PRE-MIGRATE CHECK: derived color JSON missing"
            return result
        try:
            derived = json.loads(derived_file.read_text())
        except json.JSONDecodeError as e:
            step(7, label, "✗", f"invalid JSON: {e}")
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"PRE-MIGRATE CHECK: invalid derived JSON — {e}"
            return result
        resolution = derived.get("resolution", {})
        missing = [f for f in REQUIRED_DERIVED_FIELDS if not resolution.get(f)]
        if missing:
            step(7, label, "✗", f"missing required fields: {missing}")
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"PRE-MIGRATE CHECK: missing fields {missing}"
            return result
        color = resolution.get("color_iconico", "?")
        step(7, label, "✓", f"color={color}, all required fields present")
        result["steps"][label] = "ok"

    # ── Step 8: MIGRATE ───────────────────────────────────────────────────────
    label = "MIGRATE"
    migrate_args = ["pipeline/migrate_to_db.py", "--film", work_id]
    if execute:
        migrate_args.append("--execute")
        mode_note = "--execute"
    else:
        mode_note = "dry run (no --execute flag)"

    if dry_run:
        step(8, label, "[DRY RUN]", f"would run migrate_to_db.py --film {work_id} --execute")
        result["steps"][label] = "dry_run"
    else:
        ok, out = run_script(migrate_args, label)
        if not ok:
            step(8, label, "✗", out[:120])
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"MIGRATE: {out[:200]}"
            return result
        if execute:
            result["migrated"] = True
        # Show a summary line from migrate output
        summary_line = next(
            (l for l in out.splitlines() if any(k in l for k in ["migrated", "upserted", "DONE", "work_"])),
            out.splitlines()[-1] if out.splitlines() else ""
        )
        step(8, label, "✓", f"[{mode_note}] {summary_line.strip()}")
        result["steps"][label] = "ok"

    # ── Step 9: POST-MIGRATION CHECK ──────────────────────────────────────────
    label = "POST-MIGRATE CHECK"
    if dry_run or not execute:
        step(9, label, "[DRY RUN]", "skipped (not in --execute mode)")
        result["steps"][label] = "dry_run"
    else:
        try:
            exists = db_work_exists(work_id)
            if not exists:
                step(9, label, "✗", f"work_id {work_id!r} not found in DB or missing color_assignments")
                result["steps"][label] = "failed"
                result["status"] = "failed"
                result["error"]  = "POST-MIGRATE CHECK: record not found in Supabase"
                # Rollback
                if result["migrated"]:
                    print(f"  {'':>{STEP_WIDTH + 12}}  ↩ rolling back DB…")
                    try:
                        db_rollback(work_id)
                        print(f"  {'':>{STEP_WIDTH + 12}}  ✓ rollback complete")
                    except Exception as rb_err:
                        print(f"  {'':>{STEP_WIDTH + 12}}  ✗ rollback failed: {rb_err}")
                return result
            step(9, label, "✓", f"{work_id} in DB with color_assignments")
            result["steps"][label] = "ok"
        except Exception as e:
            step(9, label, "✗", str(e))
            result["steps"][label] = "failed"
            result["status"] = "failed"
            result["error"]  = f"POST-MIGRATE CHECK: {e}"
            if result["migrated"]:
                print(f"  {'':>{STEP_WIDTH + 12}}  ↩ rolling back DB…")
                try:
                    db_rollback(work_id)
                    print(f"  {'':>{STEP_WIDTH + 12}}  ✓ rollback complete")
                except Exception as rb_err:
                    print(f"  {'':>{STEP_WIDTH + 12}}  ✗ rollback failed: {rb_err}")
            return result

    # ── Step 10: DONE ─────────────────────────────────────────────────────────
    step(10, "DONE", "✓", work_id if work_id else "")
    result["status"] = "ok"
    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validation-first 10-step ingestion pipeline for PRISMA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--list", "-l", metavar="FILE",
                        help="Path to a TMDB ID list (one per line, # comments ok).")
    source.add_argument("--tmdb", "-t", type=int, metavar="ID",
                        help="Single TMDB ID to process.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True,
                      help="Show all steps without writing files or modifying DB (default).")
    mode.add_argument("--execute", action="store_true",
                      help="Write files AND migrate to Supabase.")

    parser.add_argument("--limit", "-n", type=int, metavar="N",
                        help="Process only the first N films from the list.")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip films already present in Supabase (requires --execute).")

    args = parser.parse_args()

    # Resolve mode: --execute wins over the default --dry-run
    execute       = args.execute
    dry_run       = not execute
    skip_existing = args.skip_existing

    # ── Validate prerequisites ────────────────────────────────────────────────
    if not API_KEY:
        print("\n  ✗ TMDB_API_KEY is not set. Add it to .env.local or export in shell.\n")
        return 1

    if execute:
        if not (os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")) or not os.getenv("SUPABASE_SERVICE_KEY"):
            print(
                "\n  ✗ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set for --execute mode.\n"
                "    Add them to .env.local or export in shell.\n"
            )
            return 1

    # ── Collect TMDB IDs ──────────────────────────────────────────────────────
    if args.tmdb:
        tmdb_ids = [args.tmdb]
    else:
        list_path = Path(args.list)
        if not list_path.exists():
            print(f"\n  ✗ List file not found: {list_path}\n")
            return 1
        tmdb_ids = parse_id_list(list_path)
        if not tmdb_ids:
            print(f"\n  ✗ No valid TMDB IDs in {list_path}\n")
            return 1

    if args.limit:
        tmdb_ids = tmdb_ids[: args.limit]

    # ── Header ────────────────────────────────────────────────────────────────
    mode_str = "--execute (writes files + DB)" if execute else "--dry-run (no writes)"
    print(f"\n  PRISMA — Validate & Ingest")
    print(f"  ─────────────────────────────────────────")
    print(f"  Films:   {len(tmdb_ids)}")
    print(f"  Mode:    {mode_str}")
    print(f"  ─────────────────────────────────────────\n")

    # ── Process each film ─────────────────────────────────────────────────────
    all_results: list[dict[str, Any]] = []
    n_ok      = 0
    n_failed  = 0
    n_skipped = 0

    for i, tmdb_id in enumerate(tmdb_ids, 1):
        print(f"  ┌── Film {i}/{len(tmdb_ids)}  TMDB {tmdb_id}  {'─' * 30}")
        res = process_film(tmdb_id, dry_run=dry_run, execute=execute, skip_existing=skip_existing)
        all_results.append(res)
        if res["status"] == "ok":
            n_ok += 1
        elif res["status"] == "skipped":
            n_skipped += 1
        else:
            n_failed += 1
            err = res.get("error") or "unknown error"
            print(f"  └── ✗ FAILED: {err}")
        print()

        # Progress update every 10 films
        if i % 10 == 0:
            print(f"  ══ Progress: {i}/{len(tmdb_ids)}  ✓ {n_ok} ok  ↷ {n_skipped} skipped  ✗ {n_failed} failed  ══\n")

    # ── Final report ──────────────────────────────────────────────────────────
    print(f"  ─────────────────────────────────────────")
    print(f"  Results:  {n_ok} ok  /  {n_skipped} skipped  /  {n_failed} failed  /  {len(tmdb_ids)} total")

    if n_failed:
        print(f"\n  Failed films:")
        for r in all_results:
            if r["status"] == "failed":
                label = f"TMDB {r['tmdb_id']}"
                if r.get("tmdb_title"):
                    label += f" — {r['tmdb_title']} ({r.get('tmdb_year', '?')})"
                print(f"    ✗ {label}")
                print(f"      {r.get('error', '')}")

    if n_ok and execute:
        print(f"\n  Ingested work IDs:")
        for r in all_results:
            if r["status"] == "ok" and r.get("work_id"):
                print(f"    ✓ {r['work_id']}")

    if not execute:
        print(
            f"\n  This was a dry run — no files written, no DB changes.\n"
            f"  To execute for real:\n"
            f"    python pipeline/validate_and_ingest.py "
            + (f"--tmdb {tmdb_ids[0]}" if args.tmdb else f"--list {args.list}")
            + (f" --limit {args.limit}" if args.limit else "")
            + " --execute"
        )
    print()
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
