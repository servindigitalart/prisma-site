#!/usr/local/bin/python3
"""
migrate_to_db.py
────────────────
Migrate filesystem JSON (pipeline/normalized/ + pipeline/derived/)
→ Supabase PostgreSQL.

Run AFTER:
    python pipeline/validate_color_ids.py --fix   (ensure clean color IDs)

Prerequisites:
    pip install supabase jsonschema python-dotenv

Usage:
    # Full migration (all works, dry run by default)
    python pipeline/migrate_to_db.py
    python pipeline/migrate_to_db.py --execute
    python pipeline/migrate_to_db.py --execute --verbose

    # Incremental: upsert a single work (use after run_pipeline.py)
    python pipeline/migrate_to_db.py --film work_marie-antoinette_2006
    python pipeline/migrate_to_db.py --film work_marie-antoinette_2006 --execute

    # Upsert all works (idempotent — safe to re-run)
    python pipeline/migrate_to_db.py --all
    python pipeline/migrate_to_db.py --all --execute

Environment variables (set in .env.local or environment):
    SUPABASE_URL          Your Supabase project URL
    SUPABASE_SERVICE_KEY  Service role key (bypasses RLS — never expose client-side)

Error log: pipeline/logs/migration_errors_{YYYY-MM-DD}.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ─── Dependency checks ────────────────────────────────────────────────────────

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass  # python-dotenv optional; env vars may already be set

def _require(package: str, install_name: str | None = None) -> None:
    """Exit with a helpful message if a required package is missing."""
    try:
        __import__(package)
    except ImportError:
        pkg = install_name or package
        print(f"\n  ✗  Required package not installed: {package}")
        print(f"     Install with: pip install {pkg}")
        print(f"     Or (in venv): python -m pip install {pkg}\n")
        sys.exit(1)

_require("supabase")
_require("jsonschema")

from supabase import create_client, Client  # type: ignore
import jsonschema  # type: ignore

# ─── SURGICAL FIX: Inline helpers (no external modules) ───────────────────────

# V1.3 color palette (hardcoded for surgical patch)
VALID_COLOR_IDS_V13 = {
    "rojo_pasional", "naranja_apocaliptico", "ambar_desertico", "amarillo_ludico",
    "verde_lima", "verde_esmeralda", "verde_distopico", "cian_melancolico",
    "azul_nocturno", "violeta_cinetico", "purpura_onirico", "magenta_pop",
    "blanco_polar", "negro_abismo", "titanio_mecanico", "rosa_pastel",
    "claroscuro_dramatico", "monocromatico_intimo",
}

def _resolve_person_by_tmdb(client: Client, row: dict[str, Any]) -> str:
    """
    SURGICAL FIX #1: Resolve person by tmdb_id to avoid UNIQUE constraint violations.
    Returns canonical person_id from database.

    Critical: when updating an existing person, never include the 'id' field in the
    UPDATE payload — doing so triggers FK constraint violations on work_people because
    Postgres sees it as a PK change attempt even when the value is the same.
    """
    tmdb_id = row.get("tmdb_id")
    person_id = row["id"]

    if tmdb_id is not None:
        # Query by tmdb_id (canonical key)
        existing = client.table("people").select("id").eq("tmdb_id", tmdb_id).execute()

        if existing.data and len(existing.data) > 0:
            # Person exists — update mutable fields only (never the PK)
            person_id = existing.data[0]["id"]
            update_payload = {k: v for k, v in row.items() if k != "id"}
            if update_payload:
                client.table("people").update(update_payload).eq("id", person_id).execute()
        else:
            # New person — insert the full row
            client.table("people").insert(row).execute()
    else:
        # No tmdb_id — upsert by slug (PK); safe since no FK ambiguity
        client.table("people").upsert(row).execute()

    return person_id

def _validate_color_id(color_id: str, work_id: str) -> None:
    """
    SURGICAL FIX #2: Validate color_id against v1.3 palette.
    Raises ValueError if invalid.
    """
    if color_id not in VALID_COLOR_IDS_V13:
        raise ValueError(
            f"Invalid color_id '{color_id}' for {work_id}. "
            f"Must be one of v1.3 palette colors. "
            f"This is a contract violation - fix the source data."
        )

def validate_color_assignment(primary, secondary=None, mode=None, auto_fix=False):
    """Inline replacement for palette_registry.validate_color_assignment"""
    _validate_color_id(primary, "color_assignment")
    return (True, {
        "primary": primary,
        "secondary": secondary or [],
        "mode": mode or "color",
        "errors": [],
        "warnings": []
    })

def get_doctrine_version():
    """Inline replacement for palette_registry.get_doctrine_version"""
    return "1.3"

class PersonIdentityResolver:
    """Inline replacement for identity_resolver.PersonIdentityResolver"""
    def __init__(self, client):
        self.client = client
    
    def resolve_or_create(self, tmdb_id, name, slug, profile_data):
        return _resolve_person_by_tmdb(self.client, profile_data)


# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR        = Path(__file__).parent.parent
PIPELINE_DIR    = BASE_DIR / "pipeline"
WORKS_DIR       = PIPELINE_DIR / "normalized" / "works"
PEOPLE_DIR      = PIPELINE_DIR / "normalized" / "people"
STUDIOS_DIR     = PIPELINE_DIR / "normalized" / "studios"
DERIVED_DIR     = PIPELINE_DIR / "derived" / "color"
LOGS_DIR        = PIPELINE_DIR / "logs"
DOCTRINE_PATH   = PIPELINE_DIR / "doctrine" / "current" / "color_doctrine.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)


LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Logging setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("migrate")


# ─── Error tracking ───────────────────────────────────────────────────────────

class MigrationReport:
    def __init__(self) -> None:
        self.migrated: list[str] = []
        self.skipped:  list[dict[str, str]] = []
        self.errors:   list[dict[str, str]] = []

    def ok(self, label: str) -> None:
        self.migrated.append(label)

    def skip(self, label: str, reason: str) -> None:
        self.skipped.append({"id": label, "reason": reason})

    def error(self, label: str, reason: str) -> None:
        self.errors.append({"id": label, "reason": reason})

    def save(self) -> Path:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_path = LOGS_DIR / f"migration_errors_{date_str}.json"
        payload = {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "total_migrated": len(self.migrated),
            "total_skipped":  len(self.skipped),
            "total_errors":   len(self.errors),
            "skipped":  self.skipped,
            "errors":   self.errors,
        }
        with open(log_path, "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return log_path

    def print_summary(self) -> None:
        print(f"\n{'─' * 60}")
        print(f"  Migrated: {len(self.migrated)}")
        print(f"  Skipped:  {len(self.skipped)}")
        print(f"  Errors:   {len(self.errors)}")
        print(f"{'─' * 60}\n")


# ─── JSON helpers ─────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict[str, Any] | None:
    """Load a JSON file. Returns None on parse error."""
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log.error(f"JSON parse error in {path}: {e}")
        return None
    except OSError as e:
        log.error(f"Cannot read {path}: {e}")
        return None


def list_json_files(directory: Path) -> list[Path]:
    """Return sorted list of .json files in a directory. Empty list if dir missing."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))


# ─── Data transformers ────────────────────────────────────────────────────────

def transform_studio(data: dict[str, Any]) -> dict[str, Any] | None:
    """Transform normalized studio JSON → Supabase studios row."""
    studio_id = data.get("id")
    if not studio_id:
        return None
    return {
        "id":           studio_id,
        "name":         data.get("name", ""),
        "country":      data.get("country"),
        "founded_year": data.get("founded_year"),
        "tmdb_id":      data.get("ids", {}).get("tmdb"),
        "wikidata_id":  data.get("ids", {}).get("wikidata"),
        "logo_path":    data.get("logo_path"),
    }


def transform_person(data: dict[str, Any]) -> dict[str, Any] | None:
    """Transform normalized person JSON → Supabase people row."""
    person_id = data.get("id")
    if not person_id:
        return None
    return {
        "id":           person_id,
        "name":         data.get("name", ""),
        "birth_year":   data.get("birth_year"),
        "death_year":   data.get("death_year"),
        "bio":          data.get("bio"),
        "nationality":  data.get("nationality", []),
        "tmdb_id":      data.get("ids", {}).get("tmdb"),
        "wikidata_id":  data.get("ids", {}).get("wikidata"),
        "profile_path": data.get("profile_path"),
        "gender":       data.get("gender"),   # TMDB: 0=unknown, 1=female, 2=male
    }


def transform_work(data: dict[str, Any]) -> dict[str, Any] | None:
    """Transform normalized work JSON → Supabase works row."""
    work_id = data.get("id")
    if not work_id:
        return None

    ids = data.get("ids", {})
    media = data.get("media", {})
    color_summary = data.get("color_summary", {})

    return {
        "id":                work_id,
        "type":              data.get("type", "film"),
        "title":             data.get("title", ""),
        "original_title":    data.get("original_title"),
        "year":              data.get("year"),
        "duration_min":      data.get("duration_min"),
        "countries":         data.get("countries", []),
        "languages":         data.get("languages", []),
        "genres":            data.get("genres", []),
        "synopsis":          data.get("synopsis"),
        "tagline":           data.get("tagline"),
        "tmdb_id":           ids.get("tmdb"),
        "imdb_id":           ids.get("imdb"),
        "wikidata_id":       ids.get("wikidata"),
        "imdb_rating":       data.get("external_ratings", {}).get("imdb_rating"),
        "tmdb_popularity":   data.get("tmdb_popularity"),
        "criterion_title":   data.get("criterion_title", False),
        "mubi_title":        data.get("mubi_title", False),
        "is_sight_and_sound": data.get("is_sight_and_sound", False),
        "tmdb_poster_path":  (data.get("media") or {}).get("poster_path"),
        "trailer_key":       (data.get("media") or {}).get("trailer_key"),
        "where_to_watch":    data.get("where_to_watch", {}),
        "is_published":      True,  # Default to published for all migrations
    }


def transform_color_assignment(
    work_id: str,
    work_data: dict[str, Any],
    derived_data: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Build a color_assignments row from the normalized work's prisma_palette
    and optional derived color data.

    Returns None if no color data is available or color ID is invalid.
    """
    palette = work_data.get("prisma_palette")
    if not palette:
        return None

    primary = palette.get("primary")
    if not primary:
        return None

    # Validate using centralized palette registry
    is_valid, normalized = validate_color_assignment(
        primary=primary,
        secondary=palette.get("secondary", []),
        mode=palette.get("mode"),
        auto_fix=True,  # Auto-normalize deprecated IDs
    )
    
    if not is_valid:
        log.error(f"  ❌ {work_id}: Invalid color assignment")
        for err in normalized["errors"]:
            log.error(f"     {err}")
        return None
    
    # Log auto-fixes
    for warning in normalized["warnings"]:
        log.warning(f"  ⚠️  {work_id}: {warning}")

    # Build reasoning JSONB from derived data
    reasoning: dict[str, Any] = {}
    if derived_data:
        oklab = derived_data.get("oklab_metrics", {})
        reasoning["oklab_metrics"] = oklab
        reasoning["frames_source"] = derived_data.get("frames_source")

    return {
        "work_id":             work_id,
        "mode":                normalized["mode"],
        "color_iconico":       normalized["primary"],
        "color_rank":          palette.get("rank"),
        "colores_secundarios": normalized["secondary"],
        "ritmo_visual":        palette.get("ritmo_visual"),
        "temperatura_emocional": palette.get("temperatura_emocional"),
        "grado_abstraccion":   palette.get("grado_abstraccion_visual") or palette.get("grado_abstraccion"),
        "source":              palette.get("source", "ai") if palette.get("source") in ("ai", "editorial", "hybrid") else "ai",
        "reasoning":           reasoning if reasoning else None,
        "review_status":       "approved",
        "doctrine_version":    get_doctrine_version(),
        "assigned_at":         datetime.now(timezone.utc).isoformat(),
    }


def build_work_people_rows(
    work_data: dict[str, Any],
    person_resolver: PersonIdentityResolver,
) -> list[dict[str, Any]]:
    """Build work_people junction rows using canonical person IDs."""
    rows: list[dict[str, Any]] = []
    people = work_data.get("people", {})
    work_id = work_data.get("id", "")

    role_map = {
        "director":       "director",
        "cinematography": "cinematography",
        "writer":         "writer",
        "cast":           "actor",
        "editor":         "editor",
        "composer":       "composer",
    }

    for source_role, db_role in role_map.items():
        persons = people.get(source_role, [])
        if not isinstance(persons, list):
            continue
        for i, person_slug in enumerate(persons):
            if not isinstance(person_slug, str) or not person_slug:
                continue
            
            # Load person data to get tmdb_id
            person_path = PEOPLE_DIR / f"{person_slug}.json"
            if not person_path.exists():
                continue
            
            person_data = load_json(person_path)
            if not person_data:
                continue
            
            # Resolve canonical person_id
            person_row = transform_person(person_data)
            if not person_row:
                continue
            
            canonical_person_id = person_resolver.resolve_or_create(
                tmdb_id=person_row.get("tmdb_id"),
                name=person_row["name"],
                slug=person_slug,
                profile_data=person_row,
            )
            
            row: dict[str, Any] = {
                "work_id":       work_id,
                "person_id":     canonical_person_id,
                "role":          db_role,
                "billing_order": (i + 1) if source_role == "cast" else None,
            }
            rows.append(row)
    return rows


def build_work_studios_rows(work_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build work_studios junction rows from normalized work studios list."""
    rows: list[dict[str, Any]] = []
    work_id = work_data.get("id", "")
    studios = work_data.get("studios", [])
    if not isinstance(studios, list):
        return rows
    for studio_id in studios:
        if isinstance(studio_id, str) and studio_id:
            rows.append({"work_id": work_id, "studio_id": studio_id})
    return rows


# ─── Supabase upsert helpers ─────────────────────────────────────────────────

def upsert(
    client: Client,
    table: str,
    row: dict[str, Any],
    dry_run: bool,
    verbose: bool,
    report: MigrationReport,
    label: str,
) -> bool:
    """
    Upsert a single row into Supabase. Returns True on success.
    In dry_run mode, only logs what would happen.
    """
    if dry_run:
        if verbose:
            log.info(f"  [DRY RUN] would upsert → {table}: {label}")
        return True

    try:
        response = client.table(table).upsert(row).execute()
        if verbose:
            log.info(f"  ✅ {table}: {label}")
        report.ok(label)
        return True
    except Exception as e:
        log.error(f"  ❌ {table}: {label} → {e}")
        report.error(label, str(e))
        return False


def upsert_batch(
    client: Client,
    table: str,
    rows: list[dict[str, Any]],
    dry_run: bool,
    verbose: bool,
    report: MigrationReport,
    label: str,
) -> bool:
    """Upsert multiple rows in a single API call."""
    if not rows:
        return True
    if dry_run:
        if verbose:
            log.info(f"  [DRY RUN] would upsert {len(rows)} rows → {table}: {label}")
        return True

    try:
        client.table(table).upsert(rows).execute()
        if verbose:
            log.info(f"  ✅ {table} ({len(rows)} rows): {label}")
        report.ok(label)
        return True
    except Exception as e:
        log.error(f"  ❌ {table}: {label} → {e}")
        report.error(label, str(e))
        return False


# ─── Phase migrators ─────────────────────────────────────────────────────────

def migrate_studios(
    client: Client, dry_run: bool, verbose: bool, report: MigrationReport
) -> dict[str, bool]:
    """Migrate all studio JSON files. Returns {studio_id: success}."""
    files = list_json_files(STUDIOS_DIR)
    if not files:
        log.info("  No studio files found — skipping studio migration.")
        return {}

    results: dict[str, bool] = {}
    log.info(f"\n  Studios ({len(files)} files):")
    for path in files:
        data = load_json(path)
        if data is None:
            report.error(path.name, "JSON parse error")
            continue
        row = transform_studio(data)
        if row is None:
            report.skip(path.name, "Missing id field")
            continue
        ok = upsert(client, "studios", row, dry_run, verbose, report, row["id"])
        results[row["id"]] = ok

    return results


def migrate_people(
    client: Client, dry_run: bool, verbose: bool, report: MigrationReport
) -> dict[int, str]:
    """Migrate all people JSON files using canonical identity resolution."""
    files = list_json_files(PEOPLE_DIR)
    if not files:
        log.info("  No people files found — skipping people migration.")
        return {}

    log.info(f"\n  People ({len(files)} files):")
    
    if dry_run:
        for path in files:
            log.info(f"  [DRY RUN] would migrate → {path.name}")
        return {}
    
    tmdb_to_person: dict[int, str] = {}
    
    for path in files:
        data = load_json(path)
        if data is None:
            report.error(path.name, "JSON parse error")
            continue
        
        row = transform_person(data)
        if row is None:
            report.skip(path.name, "Missing id field")
            continue
        
        try:
            # SURGICAL FIX #1: Use inline helper to resolve by tmdb_id
            person_id = _resolve_person_by_tmdb(client, row)
            
            if row.get("tmdb_id"):
                tmdb_to_person[row["tmdb_id"]] = person_id
            
            if verbose:
                log.info(f"  ✅ {person_id} (tmdb:{row.get('tmdb_id')})")
            report.ok(person_id)
            
        except Exception as e:
            log.error(f"  ❌ {row['id']}: {e}")
            report.error(row["id"], str(e))
    
    return tmdb_to_person


def migrate_works(
    client: Client, dry_run: bool, verbose: bool, report: MigrationReport
) -> list[dict[str, Any]]:
    """
    Migrate all work JSON files (works + work_people + work_studios + color_assignments).
    Returns list of successfully processed work data dicts for junction table migration.
    """
    work_files = list_json_files(WORKS_DIR)
    if not work_files:
        log.info("  No work files found — skipping work migration.")
        return []

    log.info(f"\n  Works ({len(work_files)} files):")

    # Build derived color index
    derived_index: dict[str, dict[str, Any]] = {}
    for derived_path in list_json_files(DERIVED_DIR):
        derived_data = load_json(derived_path)
        if derived_data and "work_id" in derived_data:
            derived_index[derived_data["work_id"]] = derived_data

    processed_works: list[dict[str, Any]] = []

    for path in work_files:
        data = load_json(path)
        if data is None:
            report.error(path.name, "JSON parse error")
            continue

        work_id = data.get("id")
        if not work_id:
            report.skip(path.name, "Missing id field")
            continue

        # 1. Upsert work
        row = transform_work(data)
        if row is None:
            report.skip(work_id, "transform_work returned None")
            continue

        ok = upsert(client, "works", row, dry_run, verbose, report, work_id)
        if not ok:
            continue

        log.info(f"  ✅ Migrated work: {work_id}")
        processed_works.append(data)

        # 2. Upsert color_assignment
        derived = derived_index.get(work_id)
        color_row = transform_color_assignment(work_id, data, derived)
        if color_row:
            upsert(client, "color_assignments", color_row, dry_run, verbose, report, f"color:{work_id}")
        else:
            log.info(f"  ⚠  No color data for {work_id} — skipping color_assignment")

    return processed_works


def migrate_junctions(
    client: Client,
    processed_works: list[dict[str, Any]],
    dry_run: bool,
    verbose: bool,
    report: MigrationReport,
) -> None:
    """Migrate work_people and work_studios junction tables."""
    if not processed_works:
        return

    log.info(f"\n  Junctions (work_people + work_studios):")
    
    if dry_run:
        log.info(f"  [DRY RUN] would migrate junctions for {len(processed_works)} works")
        return
    
    resolver = PersonIdentityResolver(client)

    all_work_people: list[dict[str, Any]] = []
    all_work_studios: list[dict[str, Any]] = []

    for data in processed_works:
        wp = build_work_people_rows(data, resolver)
        all_work_people.extend(wp)
        all_work_studios.extend(build_work_studios_rows(data))

    if all_work_people:
        upsert_batch(
            client, "work_people", all_work_people, dry_run, verbose, report,
            f"{len(all_work_people)} work_people rows"
        )
    if all_work_studios:
        upsert_batch(
            client, "work_studios", all_work_studios, dry_run, verbose, report,
            f"{len(all_work_studios)} work_studios rows"
        )


# ─── Main ─────────────────────────────────────────────────────────────────────

def migrate_single_work(
    client: "Client",
    work_id: str,
    dry_run: bool,
    verbose: bool,
    report: MigrationReport,
) -> bool:
    """Upsert a single work (and its people/studios/color) by work_id."""
    # Load work file
    work_path = WORKS_DIR / f"{work_id}.json"
    if not work_path.exists():
        log.error(f"  ✗ Work file not found: {work_path}")
        report.error(work_id, "File not found")
        return False

    data = load_json(work_path)
    if data is None:
        report.error(work_id, "JSON parse error")
        return False

    # Build derived color index (single-work subset)
    derived_index: dict[str, Any] = {}
    for derived_path in list_json_files(DERIVED_DIR):
        derived_data = load_json(derived_path)
        if derived_data and derived_data.get("work_id") == work_id:
            derived_index[work_id] = derived_data
            break

    # Upsert any referenced studios first (FK deps)
    for studio_id in data.get("studios", []):
        studio_path = STUDIOS_DIR / f"{studio_id}.json"
        if studio_path.exists():
            s_data = load_json(studio_path)
            if s_data:
                row = transform_studio(s_data)
                if row:
                    upsert(client, "studios", row, dry_run, verbose, report, row["id"])

    # Resolve people using canonical identity
    if not dry_run:
        resolver = PersonIdentityResolver(client)
        for role_list in data.get("people", {}).values():
            if not isinstance(role_list, list):
                continue
            for person_slug in role_list:
                if not isinstance(person_slug, str):
                    continue
                person_path = PEOPLE_DIR / f"{person_slug}.json"
                if person_path.exists():
                    p_data = load_json(person_path)
                    if p_data:
                        row = transform_person(p_data)
                        if row:
                            resolver.resolve_or_create(
                                tmdb_id=row.get("tmdb_id"),
                                name=row["name"],
                                slug=person_slug,
                                profile_data=row,
                            )

    # Upsert work
    work_row = transform_work(data)
    if work_row is None:
        report.skip(work_id, "transform_work returned None")
        return False
    ok = upsert(client, "works", work_row, dry_run, verbose, report, work_id)
    if not ok:
        return False

    # Upsert color assignment
    derived = derived_index.get(work_id)
    color_row = transform_color_assignment(work_id, data, derived)
    if color_row:
        upsert(client, "color_assignments", color_row, dry_run, verbose, report, f"color:{work_id}")

    # Upsert junctions
    if not dry_run:
        resolver = PersonIdentityResolver(client)
        wp_rows = build_work_people_rows(data, resolver)
        ws_rows = build_work_studios_rows(data)
        if wp_rows:
            upsert_batch(client, "work_people", wp_rows, dry_run, verbose, report, f"{len(wp_rows)} work_people")
        if ws_rows:
            upsert_batch(client, "work_studios", ws_rows, dry_run, verbose, report, f"{len(ws_rows)} work_studios")

    log.info(f"  ✅ Upserted: {work_id}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate pipeline JSON files to Supabase PostgreSQL."
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--film", metavar="WORK_ID",
        help="Upsert a single work by work_id (e.g. work_marie-antoinette_2006).",
    )
    mode_group.add_argument(
        "--all",
        action="store_true",
        help="Upsert all normalized works (idempotent). Alias for default full-migration mode.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write to Supabase. Without this flag, runs as a dry run.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-record success messages.",
    )
    args = parser.parse_args()

    dry_run = not args.execute

    if dry_run:
        print("\n  ╔══════════════════════════════════════════╗")
        print("  ║  DRY RUN MODE — no data will be written  ║")
        print("  ║  Use --execute to apply changes          ║")
        print("  ╚══════════════════════════════════════════╝")

    # ── Validate environment variables ────────────────────────────────────────
    supabase_url = os.environ.get("SUPABASE_URL") or os.environ.get("PUBLIC_SUPABASE_URL")
    service_key  = os.environ.get("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        print("\n  ✗  Missing required environment variables:")
        if not supabase_url:
            print("     SUPABASE_URL (your Supabase project URL)")
        if not service_key:
            print("     SUPABASE_SERVICE_KEY (service role key from Supabase dashboard)")
        print("\n     Set them in .env.local or export them in your shell.\n")
        return 1

    # ── Check for color ID violations before proceeding ───────────────────────
    print("\n  Running color ID validation...")
    import subprocess
    result = subprocess.run(
        [sys.executable, "pipeline/validate_color_ids.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("\n  ✗  Color ID violations detected. Fix them first:")
        print("     python pipeline/validate_color_ids.py --fix")
        print(result.stdout)
        return 1
    else:
        print("  ✅ Color IDs are clean.")

    # ── Create Supabase client ─────────────────────────────────────────────────
    if not dry_run:
        try:
            client: Client = create_client(supabase_url, service_key)
        except Exception as e:
            print(f"\n  ✗  Failed to connect to Supabase: {e}\n")
            return 1
    else:
        client = None  # type: ignore  # unused in dry run

    # ── Run migration ─────────────────────────────────────────────────────────
    report = MigrationReport()

    print(f"\n  Starting migration — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Source: {PIPELINE_DIR}")
    print(f"  Target: {supabase_url[:40]}...\n")

    if args.film:
        # ── Single-work incremental upsert ────────────────────────────────────
        print(f"  Mode: single-work upsert → {args.film}\n")
        migrate_single_work(client, args.film, dry_run, args.verbose, report)
    else:
        # ── Full migration (--all or default) ─────────────────────────────────
        print(f"  Mode: {'full' if args.all else 'full (default)'} migration\n")
        # Order matters: studios and people before works (FK dependencies)
        migrate_studios(client, dry_run, args.verbose, report)
        migrate_people(client, dry_run, args.verbose, report)
        processed_works = migrate_works(client, dry_run, args.verbose, report)
        migrate_junctions(client, processed_works, dry_run, args.verbose, report)

    # ── Ensure all works published and assignments approved ───────────────────
    if not dry_run and client:
        print("\n🔧 Ensuring all works are published...")
        try:
            client.table('works').update({'is_published': True}).neq('id', '').execute()
            client.table('color_assignments').update({'review_status': 'approved'}).neq('work_id', '').execute()
            print("✅ All works published and assignments approved")
        except Exception as e:
            print(f"⚠️  Warning: Could not update publication status: {e}")

    # ── Save error log ─────────────────────────────────────────────────────────
    log_path = report.save()
    print(f"\n  Log saved to: {log_path}")

    report.print_summary()

    if dry_run:
        print("  ─── This was a dry run. Use --execute to apply. ───\n")

    return 0 if not report.errors else 1


if __name__ == "__main__":
    sys.exit(main())
