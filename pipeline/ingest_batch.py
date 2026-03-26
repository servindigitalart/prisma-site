#!/usr/local/bin/python3
"""
ingest_batch.py
───────────────
Batch-ingest multiple films from TMDB.

Reads a plain-text file of TMDB IDs (one per line, # comments ignored),
runs ingest_tmdb.py + normalize_tmdb_work.py for each, then reports results.

Usage:
    python pipeline/ingest_batch.py --list films.txt
    python pipeline/ingest_batch.py --list films.txt --dry-run
    python pipeline/ingest_batch.py --list films.txt --skip-existing
    python pipeline/ingest_batch.py --list films.txt --normalize-only

films.txt format:
    # Sofia Coppola
    11801       # Lost in Translation (2003)
    289         # Marie Antoinette (2006)

    # Kubrick
    424         # Schindler's List  <-- comment after ID
    213         # Full Metal Jacket

Environment variables:
    TMDB_API_KEY   Required for TMDB fetches
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

BASE_DIR     = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
RAW_DIR      = PIPELINE_DIR / "raw"
WORKS_DIR    = PIPELINE_DIR / "normalized" / "works"


# ─── List parsing ─────────────────────────────────────────────────────────────

def parse_id_list(list_file: Path) -> list[int]:
    """
    Parse a text file into a list of integer TMDB IDs.
    Strips comments (# ...) and blank lines.
    """
    ids: list[int] = []
    with open(list_file) as f:
        for lineno, line in enumerate(f, 1):
            line = line.split("#")[0].strip()
            if not line:
                continue
            try:
                ids.append(int(line))
            except ValueError:
                print(f"  ⚠  Line {lineno}: '{line}' is not a valid TMDB ID — skipping")
    return ids


# ─── Single-film helpers ──────────────────────────────────────────────────────

def raw_exists(tmdb_id: int) -> bool:
    return (RAW_DIR / f"tmdb_{tmdb_id}.json").exists()


def normalized_exists(tmdb_id: int) -> bool:
    """Check if any normalized work file references this TMDB ID."""
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


def run_ingest(tmdb_id: int) -> bool:
    """Fetch raw TMDB data for one film. Returns True on success."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "pipeline/ingest_tmdb.py", str(tmdb_id)],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    if result.returncode != 0:
        print(f"    ✗ ingest failed: {result.stderr.strip() or result.stdout.strip()}")
        return False
    print(f"    ✓ raw fetched → pipeline/raw/tmdb_{tmdb_id}.json")
    return True


def run_normalize(tmdb_id: int) -> str | None:
    """
    Normalize raw TMDB data for one film.
    Returns the work_id string on success, None on failure.
    """
    import subprocess
    result = subprocess.run(
        [sys.executable, "pipeline/normalize_tmdb_work.py", str(tmdb_id)],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    if result.returncode != 0:
        print(f"    ✗ normalize failed: {result.stderr.strip() or result.stdout.strip()}")
        return None
    # Extract work_id from output line: "NORMALIZED work → pipeline/normalized/works/work_xxx.json"
    for line in result.stdout.splitlines():
        if "NORMALIZED work →" in line:
            path_str = line.split("→")[-1].strip()
            work_id = Path(path_str).stem
            print(f"    ✓ normalized → {work_id}")
            return work_id
    return None


# ─── Batch runner ─────────────────────────────────────────────────────────────

def run_batch(
    tmdb_ids: list[int],
    dry_run: bool,
    skip_existing: bool,
    normalize_only: bool,
    delay: float,
) -> tuple[list[str], list[int]]:
    """
    Process each TMDB ID. Returns (succeeded_work_ids, failed_tmdb_ids).
    """
    succeeded: list[str] = []
    failed: list[int] = []
    total = len(tmdb_ids)

    for i, tmdb_id in enumerate(tmdb_ids, 1):
        print(f"\n  [{i}/{total}] TMDB {tmdb_id}")

        if dry_run:
            print(f"    [DRY RUN] would ingest + normalize tmdb_{tmdb_id}")
            succeeded.append(f"work_dryrun_{tmdb_id}")
            continue

        # ── Ingest ────────────────────────────────────────────────────────────
        if not normalize_only:
            if skip_existing and raw_exists(tmdb_id):
                print(f"    ↷ raw already exists — skipping ingest")
            else:
                ok = run_ingest(tmdb_id)
                if not ok:
                    failed.append(tmdb_id)
                    continue
                # Brief pause to respect TMDB rate limits (40 req/10s)
                if delay > 0:
                    time.sleep(delay)

        # ── Normalize ─────────────────────────────────────────────────────────
        if skip_existing and normalized_exists(tmdb_id):
            print(f"    ↷ normalized work already exists — skipping normalize")
            succeeded.append(f"tmdb_{tmdb_id}_cached")
            continue

        work_id = run_normalize(tmdb_id)
        if work_id:
            succeeded.append(work_id)
        else:
            failed.append(tmdb_id)

    return succeeded, failed


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-ingest multiple films from TMDB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--list", "-l", required=True, metavar="FILE",
        help="Path to text file with TMDB IDs (one per line, # comments ok).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be ingested without making any API calls or writing files.",
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip films whose raw JSON already exists in pipeline/raw/.",
    )
    parser.add_argument(
        "--normalize-only", action="store_true",
        help="Skip TMDB fetch and only re-normalize already-downloaded raw files.",
    )
    parser.add_argument(
        "--delay", type=float, default=0.3, metavar="SECONDS",
        help="Delay between TMDB API calls (default: 0.3s). Set 0 to disable.",
    )
    args = parser.parse_args()

    list_file = Path(args.list)
    if not list_file.exists():
        print(f"\n  ✗ List file not found: {list_file}\n")
        return 1

    # Check TMDB API key unless dry run or normalize-only
    if not args.dry_run and not args.normalize_only:
        if not os.environ.get("TMDB_API_KEY"):
            print("\n  ✗ TMDB_API_KEY is not set.")
            print("    Add it to .env.local or export it in your shell.\n")
            return 1

    tmdb_ids = parse_id_list(list_file)
    if not tmdb_ids:
        print(f"\n  ✗ No valid TMDB IDs found in {list_file}\n")
        return 1

    print(f"\n  PRISMA Batch Ingest")
    print(f"  ─────────────────────────────────────────")
    print(f"  List:          {list_file} ({len(tmdb_ids)} films)")
    print(f"  Dry run:       {'yes' if args.dry_run else 'no'}")
    print(f"  Skip existing: {'yes' if args.skip_existing else 'no'}")
    print(f"  Normalize only:{'yes' if args.normalize_only else 'no'}")
    print(f"  Delay:         {args.delay}s between calls")
    print(f"  ─────────────────────────────────────────")

    succeeded, failed = run_batch(
        tmdb_ids,
        dry_run=args.dry_run,
        skip_existing=args.skip_existing,
        normalize_only=args.normalize_only,
        delay=args.delay,
    )

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n  ─────────────────────────────────────────")
    print(f"  Done.")
    print(f"  Succeeded: {len(succeeded)}")
    print(f"  Failed:    {len(failed)}")

    if succeeded and not args.dry_run:
        print(f"\n  Normalized work IDs:")
        for wid in succeeded:
            print(f"    • {wid}")

    if failed:
        print(f"\n  Failed TMDB IDs (retry manually):")
        for fid in failed:
            print(f"    • {fid}")
        print(f"\n  To retry a specific film:")
        print(f"    python pipeline/ingest_tmdb.py <tmdb_id>")
        print(f"    python pipeline/normalize_tmdb_work.py <tmdb_id>")

    if succeeded and not args.dry_run:
        print(f"\n  Next step: run the AI pipeline for each work:")
        print(f"    python pipeline/run_pipeline.py <work_id>")
        print(f"  Or process all at once:")
        print(f"    python pipeline/run_pipeline.py --all")

    print()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
