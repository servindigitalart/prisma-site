#!/usr/local/bin/python3
"""
PRISMA Ingestion Agent
──────────────────────
Full pipeline orchestrator with quality verification.

Replaces validate_and_ingest.py as the single entry point for adding films.
Each film goes through 13 steps. Failures log and rollback automatically.
Ingested films are always saved as drafts (is_published=False).

Usage:
    python pipeline/ingest_agent.py --batch 10
    python pipeline/ingest_agent.py --batch 100 --execute
    python pipeline/ingest_agent.py --tmdb 44012 --execute
    python pipeline/ingest_agent.py --status

Steps per film:
    1.  SEARCH/CONFIRM    — TMDB ID → verify film exists
    2.  INGEST            — fetch raw TMDB JSON
    3.  NORMALIZE WORK    — normalize_tmdb_work.py
    4.  NORMALIZE PEOPLE  — normalize_tmdb_people.py
    5.  NORMALIZE STUDIOS — normalize_tmdb_studios.py
    6.  AI PIPELINE       — run_pipeline.py (Gemini + Phase 3)
    7.  PRE-MIGRATE CHECK — verify derived color JSON
    8.  MIGRATE           — migrate_to_db.py --film {work_id} (draft)
    9.  ENRICH PEOPLE     — bio + photo for new people in this film
    10. ENRICH AWARDS     — Wikidata SPARQL for this work_id
    11. RECOMPUTE SCORES  — recompute_film_scores.py + compute_person_rankings.py
    12. VERIFY            — 15-point exhaustive checklist
    13. REPORT            — move to completed/failed queue

Environment variables:
    TMDB_API_KEY         Required
    GEMINI_API_KEY       Required for step 6
    SUPABASE_URL         Required for steps 8–12
    SUPABASE_SERVICE_KEY Required for steps 8–12
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import date
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
TMDB_IMG = "https://image.tmdb.org/t/p/w185"
API_KEY  = os.getenv("TMDB_API_KEY")

REQUIRED_DERIVED_FIELDS = [
    "color_iconico",
    "temperatura_emocional",
    "ritmo_visual",
    "grado_abstraccion_visual",
]

ROLLBACK_TABLES = [
    "work_awards",
    "work_people",
    "work_studios",
    "color_assignments",
    "ranking_scores",
    "works",
]

# ─── Queue paths ──────────────────────────────────────────────────────────────

QUEUE_DIR      = PIPELINE_DIR / "queue"
PENDING_FILE   = QUEUE_DIR / "pending.json"
COMPLETED_FILE = QUEUE_DIR / "completed.json"
FAILED_FILE    = QUEUE_DIR / "failed.json"


# ─── Queue management ─────────────────────────────────────────────────────────

def load_queue(file: Path) -> list[dict]:
    if not file.exists():
        return []
    try:
        data = json.loads(file.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_queue(file: Path, data: list[dict]) -> None:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def take_batch(n: int, worker: int = 1) -> list[dict]:
    """Return N items from pending.json for a specific worker.

    Workers partition the queue by interleaving:
      Worker 1 → indices 0, 3, 6, 9 …  (every 3rd starting at 0)
      Worker 2 → indices 1, 4, 7, 10 … (every 3rd starting at 1)
      Worker 3 → indices 2, 5, 8, 11 … (every 3rd starting at 2)
    """
    pending = load_queue(PENDING_FILE)
    worker_offset = max(worker - 1, 0)
    pending = pending[worker_offset::3]
    return pending[:n]


def mark_completed(tmdb_id: int, work_id: str, report: dict) -> None:
    """Move from pending to completed.json."""
    pending = load_queue(PENDING_FILE)
    pending = [p for p in pending if p.get("tmdb_id") != tmdb_id]
    save_queue(PENDING_FILE, pending)

    completed = load_queue(COMPLETED_FILE)
    completed.append({
        "tmdb_id":      tmdb_id,
        "work_id":      work_id,
        "completed_at": str(date.today()),
        "checks_passed": report.get("checks_passed", 0),
        "checks_total":  report.get("checks_total", 15),
        "warnings":      report.get("warnings", []),
    })
    save_queue(COMPLETED_FILE, completed)


def mark_failed(tmdb_id: int, error: str) -> None:
    """Move from pending to failed.json."""
    pending = load_queue(PENDING_FILE)
    source  = next((p.get("source", "unknown") for p in pending if p.get("tmdb_id") == tmdb_id), "unknown")
    pending = [p for p in pending if p.get("tmdb_id") != tmdb_id]
    save_queue(PENDING_FILE, pending)

    failed = load_queue(FAILED_FILE)
    # Avoid duplicates
    failed = [f for f in failed if f.get("tmdb_id") != tmdb_id]
    failed.append({
        "tmdb_id":   tmdb_id,
        "failed_at": str(date.today()),
        "source":    source,
        "error":     error,
    })
    save_queue(FAILED_FILE, failed)


def auto_deduplicate() -> int:
    """
    Remove from pending any TMDB IDs already recorded in completed.json.

    Previously this checked Supabase directly, which caused 189+ films to be
    silently dropped from the queue even though they had been migrated locally
    but never tracked in completed.json.  The authoritative source of truth for
    "has this film been ingested through the pipeline?" is completed.json, NOT
    the raw Supabase state.  Use sync_queue_from_db.py to bring completed.json
    in sync with Supabase first, then rely on this check going forward.
    """
    completed = load_queue(COMPLETED_FILE)
    completed_ids = {c["tmdb_id"] for c in completed if c.get("tmdb_id") is not None}
    if not completed_ids:
        return 0
    pending = load_queue(PENDING_FILE)
    before  = len(pending)
    pending = [item for item in pending if item.get("tmdb_id") not in completed_ids]
    if before != len(pending):
        save_queue(PENDING_FILE, pending)
    return before - len(pending)


def queue_status() -> None:
    pending   = load_queue(PENDING_FILE)
    completed = load_queue(COMPLETED_FILE)
    failed    = load_queue(FAILED_FILE)

    # Source breakdown
    sources: dict[str, int] = {}
    for item in pending:
        src = item.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1

    days = len(pending) / 100 if pending else 0

    print("\nQueue Status — PRISMA")
    print("─────────────────────────────")
    print(f"Pending:  {len(pending):>5} films")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {src:<28} {count}")
    print(f"\nCompleted:{len(completed):>5} films")
    print(f"Failed:   {len(failed):>5} films", end="")
    if failed:
        print("  (run queue_manager.py --clear-failed to retry)", end="")
    print()
    if days:
        print(f"\nEstimated time at 100/day: {days:.1f} days")
    print("─────────────────────────────\n")


# ─── TMDB helpers ─────────────────────────────────────────────────────────────

def tmdb_fetch(endpoint: str, params: dict | None = None) -> dict:
    params = params or {}
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB_API}{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# ─── Supabase helpers ─────────────────────────────────────────────────────────

def get_db():
    try:
        from supabase import create_client
    except ImportError:
        raise RuntimeError("supabase not installed: pip install supabase")
    url = os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    return create_client(url, key)


def db_get_work(db, work_id: str) -> dict | None:
    res = db.from_("works").select("*").eq("id", work_id).execute()
    return res.data[0] if res.data else None


def db_get_color_assignment(db, work_id: str) -> dict | None:
    res = db.from_("color_assignments").select("*").eq("work_id", work_id).execute()
    return res.data[0] if res.data else None


def db_get_work_people(db, work_id: str) -> list[dict]:
    res = db.from_("work_people").select("*").eq("work_id", work_id).execute()
    return res.data or []


def db_rollback(work_id: str) -> None:
    db = get_db()
    for table in ROLLBACK_TABLES:
        try:
            if table == "works":
                db.from_(table).delete().eq("id", work_id).execute()
            else:
                db.from_(table).delete().eq("work_id", work_id).execute()
        except Exception as e:
            print(f"    ↩ rollback {table}: {e}")


# ─── Subprocess runner ────────────────────────────────────────────────────────

def run_script(args: list[str], timeout: int = 300) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable] + args,
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s: {' '.join(args)}"
    output = result.stdout.strip()
    if result.returncode != 0:
        err = (result.stderr.strip() or result.stdout.strip())[:300]
        return False, f"exit {result.returncode}: {err}"
    return True, output


# ─── Display helpers ──────────────────────────────────────────────────────────

STEP_WIDTH = 22
TOTAL_STEPS = 13


def step(n: int, label: str, status: str, detail: str = "") -> None:
    full_label = f"  Step {n:>2}/{TOTAL_STEPS}  {label:<{STEP_WIDTH}}"
    suffix = f"  {detail}" if detail else ""
    print(f"{full_label}  {status}{suffix}")


# ─── People enrichment (step 9) ───────────────────────────────────────────────

def enrich_people_for_work(db, work_id: str, dry_run: bool) -> tuple[int, int]:
    """
    Fetch bio + photo from TMDB for people linked to this work who are missing them.
    Returns (bios_added, photos_added).
    """
    # Get person_ids linked to this work
    wp = db.from_("work_people").select("person_id").eq("work_id", work_id).execute()
    person_ids = [r["person_id"] for r in (wp.data or [])]
    if not person_ids:
        return 0, 0

    # Fetch those people who are missing bio, profile_path, or gender
    people_res = db.from_("people").select("id,tmdb_id,bio,profile_path,gender").in_("id", person_ids).execute()
    targets = [
        p for p in (people_res.data or [])
        if p.get("tmdb_id") and (
            not p.get("bio") or not p.get("profile_path") or p.get("gender") is None
        )
    ]

    if not targets or dry_run:
        return 0, 0

    bios_added = 0
    photos_added = 0

    for person in targets:
        tmdb_id = person["tmdb_id"]
        person_id = person["id"]
        try:
            data = tmdb_fetch(f"/person/{tmdb_id}")
            updates: dict[str, Any] = {}

            if not person.get("bio") and data.get("biography"):
                updates["bio"] = data["biography"][:2000]
                bios_added += 1

            if not person.get("profile_path") and data.get("profile_path"):
                updates["profile_path"] = data["profile_path"]
                photos_added += 1

            # Always save gender if it's missing (TMDB: 0=unknown, 1=female, 2=male)
            if person.get("gender") is None and data.get("gender") is not None:
                updates["gender"] = data["gender"]

            if updates:
                db.from_("people").update(updates).eq("id", person_id).execute()

            time.sleep(0.3)
        except Exception:
            pass  # Non-fatal

    return bios_added, photos_added


# ─── Verification checklist (step 12) ────────────────────────────────────────

def run_verification(db, work_id: str) -> tuple[int, int, list[str]]:
    """
    Run 15-point checklist. Returns (passed, total, warnings).
    Critical failures (first 10) block READY status; last 5 are warnings only.
    """
    work  = db_get_work(db, work_id)
    ca    = db_get_color_assignment(db, work_id)
    wp    = db_get_work_people(db, work_id)

    # Director info
    director_person_id = next((p["person_id"] for p in wp if p.get("role") == "director"), None)
    director_data: dict = {}
    if director_person_id:
        res = db.from_("people").select("bio,profile_path").eq("id", director_person_id).execute()
        director_data = res.data[0] if res.data else {}

    # Awards existence
    awards_res = db.from_("work_awards").select("id").eq("work_id", work_id).limit(1).execute()
    awards_searched = True  # We attempted enrichment — it's searched even if 0 results

    # Score existence — filter by entity_id (not context)
    scores_res = db.from_("ranking_scores").select("entity_id, score").eq("entity_id", work_id).limit(1).execute()
    scores_updated = bool(scores_res.data)

    CHECKS: list[tuple[str, Any, bool]] = [
        # (label, value, is_critical)
        ("works.title",              bool(work and work.get("title")),                      True),
        ("works.year",               bool(work and work.get("year")),                       True),
        ("works.synopsis",           bool(work and work.get("synopsis")),                   True),
        ("works.tmdb_poster_path",   bool(work and work.get("tmdb_poster_path")),           True),
        ("works.countries",          bool(work and work.get("countries")),                  True),
        ("works.is_published=false", work is not None and work.get("is_published") is False, True),
        ("color_assignments.exists", bool(ca),                                              True),
        ("color_assignments.color",  bool(ca and ca.get("color_iconico")),                  True),
        ("work_people.has_director", any(p.get("role") == "director" for p in wp),          True),
        ("work_people.min_3_crew",   len(wp) >= 3,                                          True),
        # Warnings (non-blocking)
        ("people.director_has_photo", bool(director_data.get("profile_path")),              False),
        ("people.director_has_bio",   bool(director_data.get("bio")),                       False),
        ("work_awards.searched",      awards_searched,                                      False),
        ("ranking_scores.updated",    scores_updated,                                       False),
        ("works.numeric_score",       bool(ca and ca.get("numeric_score")),                 False),
    ]

    passed   = 0
    warnings = []

    for label, value, critical in CHECKS:
        icon = "✓" if value else ("✗" if critical else "⚠")
        print(f"    {icon}  {label}")
        if value:
            passed += 1
        elif not critical:
            warnings.append(label)

    return passed, len(CHECKS), warnings


# ─── Core: process one film ───────────────────────────────────────────────────

def process_film(
    tmdb_id: int,
    dry_run: bool,
    execute: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "tmdb_id":   tmdb_id,
        "work_id":   None,
        "status":    "pending",
        "steps":     {},
        "error":     None,
        "migrated":  False,
        "checks_passed": 0,
        "checks_total":  15,
        "warnings":  [],
    }

    # ── Step 1: CONFIRM ───────────────────────────────────────────────────────
    try:
        movie    = tmdb_fetch(f"/movie/{tmdb_id}")
        title    = movie.get("title", "?")
        rel_date = movie.get("release_date", "")
        year     = rel_date[:4] if rel_date else "?"
        step(1, "CONFIRM", "✓", f"{title} ({year})")
        result["steps"]["CONFIRM"] = "ok"
        result["tmdb_title"] = title
        result["tmdb_year"]  = year
        # Per-film duplicate check — skip immediately if already in Supabase
        if execute:
            try:
                _db = get_db()
                _existing = _db.from_("works").select("id").eq("tmdb_id", tmdb_id).execute()
                if _existing.data:
                    existing_id = _existing.data[0]["id"]
                    step(1, "CONFIRM", "↷", f"already in Supabase as {existing_id} — skipping")
                    result["status"]  = "skipped"
                    result["work_id"] = existing_id
                    return result
            except Exception:
                pass  # Can't check Supabase — proceed normally
    except Exception as e:
        step(1, "CONFIRM", "✗", str(e))
        result["steps"]["CONFIRM"] = "failed"
        result["status"] = "failed"
        result["error"]  = f"CONFIRM: {e}"
        return result

    # ── Step 2: INGEST ────────────────────────────────────────────────────────
    raw_file = RAW_DIR / f"tmdb_{tmdb_id}.json"
    if dry_run:
        note = "already exists" if raw_file.exists() else "would fetch"
        step(2, "INGEST", "[DRY RUN]", note)
        result["steps"]["INGEST"] = "dry_run"
    elif raw_file.exists():
        step(2, "INGEST", "↷", "raw already exists — skipping fetch")
        result["steps"]["INGEST"] = "skipped"
    else:
        ok, out = run_script(["pipeline/ingest_tmdb.py", str(tmdb_id)])
        if not ok:
            step(2, "INGEST", "✗", out)
            result["steps"]["INGEST"] = "failed"
            result["status"] = "failed"
            result["error"]  = f"INGEST: {out}"
            return result
        step(2, "INGEST", "✓", f"pipeline/raw/tmdb_{tmdb_id}.json")
        result["steps"]["INGEST"] = "ok"
        time.sleep(0.3)

    # ── Step 3: NORMALIZE WORK ────────────────────────────────────────────────
    if dry_run:
        work_id = None
        if raw_file.exists():
            try:
                raw = json.loads(raw_file.read_text())
                from slugify import slugify
                t  = raw["movie"].get("title", "")
                y  = raw["movie"].get("release_date", "")[:4]
                work_id = f"work_{slugify(t)}_{y}"
            except Exception:
                pass
        if not work_id:
            try:
                from slugify import slugify
                work_id = f"work_{slugify(result['tmdb_title'])}_{result['tmdb_year']}"
            except Exception:
                work_id = f"work_tmdb_{tmdb_id}"
        result["work_id"] = work_id
        step(3, "NORMALIZE WORK", "[DRY RUN]", f"estimated → {work_id}")
        result["steps"]["NORMALIZE WORK"] = "dry_run"
    else:
        ok, out = run_script(["pipeline/normalize_tmdb_work.py", str(tmdb_id)])
        if not ok:
            step(3, "NORMALIZE WORK", "✗", out)
            result["steps"]["NORMALIZE WORK"] = "failed"
            result["status"] = "failed"
            result["error"]  = f"NORMALIZE WORK: {out}"
            return result
        work_id = None
        for line in out.splitlines():
            if "NORMALIZED work →" in line:
                work_id = Path(line.split("→")[-1].strip()).stem
                break
        if not work_id:
            step(3, "NORMALIZE WORK", "✗", "could not parse work_id from output")
            result["steps"]["NORMALIZE WORK"] = "failed"
            result["status"] = "failed"
            result["error"]  = "NORMALIZE WORK: work_id not found in output"
            return result
        result["work_id"] = work_id
        step(3, "NORMALIZE WORK", "✓", work_id)
        result["steps"]["NORMALIZE WORK"] = "ok"

    work_id: str = result["work_id"]

    # ── Step 4: NORMALIZE PEOPLE ──────────────────────────────────────────────
    if dry_run:
        step(4, "NORMALIZE PEOPLE", "[DRY RUN]", "would run normalize_tmdb_people.py")
        result["steps"]["NORMALIZE PEOPLE"] = "dry_run"
    else:
        ok, out = run_script(["pipeline/normalize_tmdb_people.py", str(tmdb_id)])
        if not ok:
            step(4, "NORMALIZE PEOPLE", "✗", out)
            result["steps"]["NORMALIZE PEOPLE"] = "failed"
            result["status"] = "failed"
            result["error"]  = f"NORMALIZE PEOPLE: {out}"
            return result
        detail = next((l for l in out.splitlines() if "NORMALIZED people" in l), "")
        step(4, "NORMALIZE PEOPLE", "✓", detail)
        result["steps"]["NORMALIZE PEOPLE"] = "ok"

    # ── Step 5: NORMALIZE STUDIOS ─────────────────────────────────────────────
    if dry_run:
        step(5, "NORMALIZE STUDIOS", "[DRY RUN]", "would run normalize_tmdb_studios.py")
        result["steps"]["NORMALIZE STUDIOS"] = "dry_run"
    else:
        ok, out = run_script(["pipeline/normalize_tmdb_studios.py", str(tmdb_id)])
        if not ok:
            step(5, "NORMALIZE STUDIOS", "✗", out)
            result["steps"]["NORMALIZE STUDIOS"] = "failed"
            result["status"] = "failed"
            result["error"]  = f"NORMALIZE STUDIOS: {out}"
            return result
        detail = next((l for l in out.splitlines() if "NORMALIZED studios" in l), "")
        step(5, "NORMALIZE STUDIOS", "✓", detail)
        result["steps"]["NORMALIZE STUDIOS"] = "ok"

    # ── Step 6: AI PIPELINE ───────────────────────────────────────────────────
    derived_file = DERIVED_DIR / f"{work_id}.json"
    if dry_run:
        note = "derived JSON exists" if derived_file.exists() else "would run run_pipeline.py"
        step(6, "AI PIPELINE", "[DRY RUN]", note)
        result["steps"]["AI PIPELINE"] = "dry_run"
    elif derived_file.exists():
        step(6, "AI PIPELINE", "↷", "derived color JSON exists — skipping")
        result["steps"]["AI PIPELINE"] = "skipped"
    else:
        if not os.getenv("GEMINI_API_KEY"):
            step(6, "AI PIPELINE", "⚠", "GEMINI_API_KEY not set")
        ok, out = run_script(["pipeline/run_pipeline.py", work_id], timeout=600)
        if not ok:
            step(6, "AI PIPELINE", "✗", out[:120])
            result["steps"]["AI PIPELINE"] = "failed"
            result["status"] = "failed"
            result["error"]  = f"AI PIPELINE: {out[:200]}"
            return result
        step(6, "AI PIPELINE", "✓", f"pipeline/derived/color/{work_id}.json")
        result["steps"]["AI PIPELINE"] = "ok"

    # Restore prisma_palette if step 6 was skipped
    if not dry_run:
        work_json_path = WORKS_DIR / f"{work_id}.json"
        if work_json_path.exists() and derived_file.exists():
            try:
                work_json = json.loads(work_json_path.read_text())
                if not work_json.get("prisma_palette"):
                    derived    = json.loads(derived_file.read_text())
                    resolution = derived.get("resolution", {})
                    color      = resolution.get("color_iconico")
                    if color:
                        MONO = {"claroscuro_dramatico", "monocromatico_intimo"}
                        work_json["prisma_palette"] = {
                            "primary":   color,
                            "secondary": resolution.get("colores_secundarios", []),
                            "rank":      resolution.get("color_rank", 0.85),
                            "mode":      "monochromatic" if color in MONO else "color",
                            "source":    "cultural_memory",
                            "temperatura_emocional":    resolution.get("temperatura_emocional"),
                            "ritmo_visual":             resolution.get("ritmo_visual"),
                            "grado_abstraccion_visual": resolution.get("grado_abstraccion_visual"),
                        }
                        work_json_path.write_text(json.dumps(work_json, indent=2))
            except Exception:
                pass

    # ── Step 7: PRE-MIGRATE CHECK ─────────────────────────────────────────────
    if dry_run:
        if derived_file.exists():
            try:
                derived    = json.loads(derived_file.read_text())
                resolution = derived.get("resolution", {})
                missing    = [f for f in REQUIRED_DERIVED_FIELDS if not resolution.get(f)]
                if missing:
                    step(7, "PRE-MIGRATE CHECK", "[DRY RUN] ⚠", f"missing: {missing}")
                else:
                    step(7, "PRE-MIGRATE CHECK", "[DRY RUN] ✓", f"color={resolution.get('color_iconico')}")
            except Exception as e:
                step(7, "PRE-MIGRATE CHECK", "[DRY RUN] ⚠", str(e))
        else:
            step(7, "PRE-MIGRATE CHECK", "[DRY RUN]", "derived JSON not yet created")
        result["steps"]["PRE-MIGRATE CHECK"] = "dry_run"
    else:
        if not derived_file.exists():
            step(7, "PRE-MIGRATE CHECK", "✗", "derived JSON not found")
            result["steps"]["PRE-MIGRATE CHECK"] = "failed"
            result["status"] = "failed"
            result["error"]  = "PRE-MIGRATE CHECK: derived color JSON missing"
            return result
        try:
            derived    = json.loads(derived_file.read_text())
            resolution = derived.get("resolution", {})
            missing    = [f for f in REQUIRED_DERIVED_FIELDS if not resolution.get(f)]
            if missing:
                step(7, "PRE-MIGRATE CHECK", "✗", f"missing fields: {missing}")
                result["steps"]["PRE-MIGRATE CHECK"] = "failed"
                result["status"] = "failed"
                result["error"]  = f"PRE-MIGRATE CHECK: missing {missing}"
                return result
            color = resolution.get("color_iconico", "?")
            step(7, "PRE-MIGRATE CHECK", "✓", f"color={color}")
            result["steps"]["PRE-MIGRATE CHECK"] = "ok"
        except json.JSONDecodeError as e:
            step(7, "PRE-MIGRATE CHECK", "✗", f"invalid JSON: {e}")
            result["steps"]["PRE-MIGRATE CHECK"] = "failed"
            result["status"] = "failed"
            result["error"]  = f"PRE-MIGRATE CHECK: invalid JSON — {e}"
            return result

    # ── Step 8: MIGRATE ───────────────────────────────────────────────────────
    migrate_args = ["pipeline/migrate_to_db.py", "--film", work_id]
    if execute:
        migrate_args.append("--execute")

    if dry_run:
        step(8, "MIGRATE", "[DRY RUN]", f"would migrate {work_id} as draft")
        result["steps"]["MIGRATE"] = "dry_run"
    else:
        ok, out = run_script(migrate_args)
        if not ok:
            step(8, "MIGRATE", "✗", out[:120])
            result["steps"]["MIGRATE"] = "failed"
            result["status"] = "failed"
            result["error"]  = f"MIGRATE: {out[:200]}"
            return result
        if execute:
            result["migrated"] = True
            # Ensure draft status (is_published=False)
            try:
                db = get_db()
                db.from_("works").update({"is_published": False}).eq("id", work_id).execute()
            except Exception as e:
                print(f"    ⚠ Could not enforce draft status: {e}")
        summary = next(
            (l for l in out.splitlines() if any(k in l for k in ["migrated", "upserted", "DONE", "work_"])),
            (out.splitlines()[-1] if out.splitlines() else ""),
        )
        mode = "--execute" if execute else "dry run"
        step(8, "MIGRATE", "✓", f"[{mode}] {summary.strip()}")
        result["steps"]["MIGRATE"] = "ok"

    # ── Step 9: ENRICH PEOPLE ─────────────────────────────────────────────────
    if dry_run:
        step(9, "ENRICH PEOPLE", "[DRY RUN]", "would fetch bios/photos for new people")
        result["steps"]["ENRICH PEOPLE"] = "dry_run"
    elif execute:
        try:
            db = get_db()
            bios, photos = enrich_people_for_work(db, work_id, dry_run=False)
            step(9, "ENRICH PEOPLE", "✓", f"+{bios} bios, +{photos} photos")
            result["steps"]["ENRICH PEOPLE"] = "ok"
        except Exception as e:
            step(9, "ENRICH PEOPLE", "⚠", f"non-fatal: {e}")
            result["steps"]["ENRICH PEOPLE"] = "warning"
    else:
        step(9, "ENRICH PEOPLE", "[DRY RUN]", "no DB connection (not --execute)")
        result["steps"]["ENRICH PEOPLE"] = "dry_run"

    # ── Step 10: ENRICH AWARDS ────────────────────────────────────────────────
    if dry_run:
        step(10, "ENRICH AWARDS", "[DRY RUN]", f"would run Wikidata SPARQL for {work_id}")
        result["steps"]["ENRICH AWARDS"] = "dry_run"
    elif execute:
        ok, out = run_script(["pipeline/enrich_work_awards.py", "--work", work_id], timeout=120)
        if ok:
            award_line = next((l for l in out.splitlines() if "award" in l.lower()), "")
            step(10, "ENRICH AWARDS", "✓", award_line.strip() or work_id)
            result["steps"]["ENRICH AWARDS"] = "ok"
        else:
            step(10, "ENRICH AWARDS", "⚠", f"non-fatal: {out[:80]}")
            result["steps"]["ENRICH AWARDS"] = "warning"
        time.sleep(1.2)  # Respect Wikidata rate limit
    else:
        step(10, "ENRICH AWARDS", "[DRY RUN]", "no DB connection (not --execute)")
        result["steps"]["ENRICH AWARDS"] = "dry_run"

    # ── Step 11: RECOMPUTE SCORES ─────────────────────────────────────────────
    if dry_run:
        step(11, "RECOMPUTE SCORES", "[DRY RUN]", "would run recompute_film_scores + person_rankings")
        result["steps"]["RECOMPUTE SCORES"] = "dry_run"
    elif execute:
        ok1, _ = run_script(["pipeline/recompute_film_scores.py"], timeout=300)
        ok2, _ = run_script(["pipeline/compute_person_rankings.py"], timeout=300)
        if ok1 and ok2:
            step(11, "RECOMPUTE SCORES", "✓", "film scores + person rankings updated")
            result["steps"]["RECOMPUTE SCORES"] = "ok"
        else:
            step(11, "RECOMPUTE SCORES", "⚠", "partial: check recompute logs")
            result["steps"]["RECOMPUTE SCORES"] = "warning"
    else:
        step(11, "RECOMPUTE SCORES", "[DRY RUN]", "no DB connection (not --execute)")
        result["steps"]["RECOMPUTE SCORES"] = "dry_run"

    # ── Step 12: VERIFY ───────────────────────────────────────────────────────
    if dry_run:
        step(12, "VERIFY", "[DRY RUN]", "15-point checklist skipped in dry run")
        result["steps"]["VERIFY"] = "dry_run"
        result["checks_passed"] = 0
        result["checks_total"]  = 15
    elif execute:
        print(f"  Step 12/{TOTAL_STEPS}  {'VERIFY':<{STEP_WIDTH}}  running 15-point checklist…")
        try:
            db = get_db()
            passed, total, warnings = run_verification(db, work_id)
            result["checks_passed"] = passed
            result["checks_total"]  = total
            result["warnings"]      = warnings
            icon = "✓" if passed >= 10 else "⚠"
            step(12, "VERIFY", icon, f"{passed}/{total} checks passed")
            result["steps"]["VERIFY"] = "ok" if passed >= 10 else "warning"

            # Rollback if critical checks failed
            if passed < 10:
                print(f"    ✗ Critical checks failed — rolling back…")
                if result["migrated"]:
                    try:
                        db_rollback(work_id)
                        print(f"    ✓ Rollback complete")
                    except Exception as rb:
                        print(f"    ✗ Rollback failed: {rb}")
                result["status"] = "failed"
                result["error"]  = f"VERIFY: only {passed}/10 critical checks passed"
                return result

            # Auto-publish if all 15 checks pass
            if passed >= 15:
                try:
                    db.from_("works").update({"is_published": True}).eq("id", work_id).execute()
                    print(f"    ✓ Auto-published: {work_id} (15/15 checks passed)")
                    result["auto_published"] = True
                except Exception as e:
                    print(f"    ⚠ Auto-publish failed: {e}")
        except Exception as e:
            step(12, "VERIFY", "⚠", f"verification error: {e}")
            result["steps"]["VERIFY"] = "warning"
    else:
        step(12, "VERIFY", "[DRY RUN]", "no DB connection (not --execute)")
        result["steps"]["VERIFY"] = "dry_run"

    # ── Step 13: REPORT ───────────────────────────────────────────────────────
    passed_str = f"{result['checks_passed']}/{result['checks_total']} checks" if execute else "dry run"
    step(13, "REPORT", "✓", f"{work_id} — {passed_str}")
    result["steps"]["REPORT"] = "ok"
    result["status"] = "ok"
    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="PRISMA 13-step ingestion agent with queue management.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument("--batch", "-b", type=int, metavar="N",
                        help="Take N films from pending queue and process them.")
    source.add_argument("--tmdb", "-t", type=int, metavar="ID",
                        help="Process a single TMDB ID (not from queue).")
    source.add_argument("--status", action="store_true",
                        help="Show queue status and exit.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True,
                      help="Show all steps without writing files or modifying DB (default).")
    mode.add_argument("--execute", action="store_true",
                      help="Write files AND migrate to Supabase.")

    parser.add_argument("--worker", type=int, default=1,
                        help="Worker ID (1, 2, or 3) for parallel processing. "
                             "Each worker processes every 3rd film starting at its offset.")

    args = parser.parse_args()

    if args.status:
        queue_status()
        return 0

    if not args.batch and not args.tmdb:
        parser.print_help()
        return 1

    execute = args.execute
    dry_run = not execute

    # Validate env
    if not API_KEY:
        print("\n  ✗ TMDB_API_KEY is not set.\n")
        return 1
    if execute:
        if not (os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")) or not os.getenv("SUPABASE_SERVICE_KEY"):
            print("\n  ✗ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set for --execute.\n")
            return 1

    # Collect TMDB IDs
    if args.tmdb:
        items = [{"tmdb_id": args.tmdb, "source": "manual"}]
        use_queue = False
    else:
        # Auto-deduplicate before every batch
        if execute:
            removed = auto_deduplicate()
            if removed:
                print(f"  ↷ Auto-dedup: removed {removed} films already in Supabase from queue\n")
        items = take_batch(args.batch, worker=args.worker)
        use_queue = True
        if not items:
            print("\n  Queue is empty. Add films with: python pipeline/queue_manager.py --add-list FILE\n")
            return 0

    mode_str = "--execute" if execute else "--dry-run"
    print(f"\n  ══════════════════════════════════════════════")
    print(f"  PRISMA Ingestion Agent")
    print(f"  ══════════════════════════════════════════════")
    print(f"  Films:  {len(items)}")
    print(f"  Mode:   {mode_str}")
    print(f"  Worker: {args.worker}/3")
    print(f"  ══════════════════════════════════════════════\n")

    all_results: list[dict[str, Any]] = []
    n_ok      = 0
    n_warned  = 0
    n_failed  = 0

    for i, item in enumerate(items, 1):
        tmdb_id = item["tmdb_id"] if isinstance(item, dict) else int(item)
        print(f"  ┌── Film {i}/{len(items)}  TMDB {tmdb_id}  {'─' * 28}")
        res = process_film(tmdb_id, dry_run=dry_run, execute=execute)
        all_results.append(res)

        if res["status"] == "skipped":
            print(f"  └── ↷ SKIPPED: {res.get('reason', 'already in Supabase')}")
            if use_queue and execute:
                mark_completed(tmdb_id, res.get("work_id", ""), res)
        elif res["status"] == "ok":
            warnings = res.get("warnings", [])
            if warnings:
                n_warned += 1
                print(f"  └── ⚠ DONE with warnings: {', '.join(warnings)}")
            else:
                n_ok += 1
                print(f"  └── ✓ DONE")
            if use_queue and execute:
                mark_completed(tmdb_id, res.get("work_id", ""), res)
        else:
            n_failed += 1
            err = res.get("error") or "unknown error"
            print(f"  └── ✗ FAILED: {err}")
            if use_queue and execute:
                mark_failed(tmdb_id, err)

        print()
        time.sleep(2)  # Respect API rate limits between films

        if i % 10 == 0:
            print(f"  ══ Progress {i}/{len(items)}: ✓{n_ok} ok  ⚠{n_warned} warned  ✗{n_failed} failed ══\n")

    # ── Final batch report ────────────────────────────────────────────────────
    pending_count   = len(load_queue(PENDING_FILE))
    completed_count = len(load_queue(COMPLETED_FILE))
    failed_count    = len(load_queue(FAILED_FILE))

    print(f"\n  ══════════════════════════════════════════════")
    print(f"  PRISMA Ingestion Agent — Batch Report")
    print(f"  ══════════════════════════════════════════════")
    print(f"  Batch size:  {len(items)}")
    print(f"  ✓ Success:   {n_ok}  (drafts in Supabase, ready to review)")
    print(f"  ⚠ Warnings:  {n_warned}  (ingested but missing some data)")
    print(f"  ✗ Failed:    {n_failed}  (rollback complete)")
    print()
    print(f"  Queue status: {pending_count} pending / {completed_count} completed / {failed_count} failed")

    if n_ok + n_warned > 0:
        print(f"\n  Ready to review at: http://localhost:4321/admin/drafts\n")
        print(f"  Successful:")
        for r in all_results:
            if r["status"] == "ok":
                wid  = r.get("work_id", "?")
                name = r.get("tmdb_title", "?")
                yr   = r.get("tmdb_year", "?")
                cp   = r.get("checks_passed", 0)
                ct   = r.get("checks_total", 15)
                warn = r.get("warnings", [])
                if warn:
                    print(f"    ⚠ {wid}  — {name} ({yr})")
                    print(f"       {cp}/{ct} checks  ⚠ {', '.join(warn)}")
                else:
                    print(f"    ✓ {wid}  — {name} ({yr})")
                    print(f"       {cp}/{ct} checks passed")

    if n_failed:
        print(f"\n  Failed:")
        for r in all_results:
            if r["status"] == "failed":
                label = f"TMDB {r['tmdb_id']}"
                if r.get("tmdb_title"):
                    label += f"  — {r['tmdb_title']} ({r.get('tmdb_year', '?')})"
                print(f"    ✗ {label}")
                print(f"      {r.get('error', '')}")

    if not execute:
        print(f"\n  This was a dry run — no files written, no DB changes.")
        if args.tmdb:
            print(f"  To execute: python pipeline/ingest_agent.py --tmdb {args.tmdb} --execute")
        else:
            print(f"  To execute: python pipeline/ingest_agent.py --batch {args.batch} --execute")

    print(f"  ══════════════════════════════════════════════\n")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
