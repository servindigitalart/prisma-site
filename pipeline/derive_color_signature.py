#!/usr/bin/env python3
import sys, json
from pathlib import Path
from slugify import slugify

# --- AÑADIR RAÍCES AL PYTHONPATH ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRISMA_AUTOMATOR = Path.home() / "prisma_automator"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PRISMA_AUTOMATOR))

from pipeline.resolve_frames import resolve_frames
from prisma.color.analyze_folder import analyze_folder
from pipeline.resolve_frames import resolve_frames

OUT_DIR = Path("pipeline/derived/color")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def derive(work_title, year, ids):
    work_id = f"work_{slugify(work_title)}_{year}"

    frames_dir, source = resolve_frames(ids)
    if not frames_dir:
        raise RuntimeError("No frames available for this work")

    metrics = analyze_folder(frames_dir)

    payload = {
        "work_id": work_id,
        "frames_source": source,
        "frames_path": str(frames_dir),
        "oklab_metrics": metrics
    }

    out_file = OUT_DIR / f"{work_id}.json"
    out_file.write_text(json.dumps(payload, indent=2))

    print(f"COLOR derived → {out_file}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: derive_color_signature.py <title> <year> <tmdb_id|-> <imdb_id|->")
        sys.exit(1)

    title = sys.argv[1]
    year = sys.argv[2]
    tmdb_id = None if sys.argv[3] == "-" else int(sys.argv[3])
    imdb_id = None if sys.argv[4] == "-" else sys.argv[4]

    derive(title, year, {"tmdb": tmdb_id, "imdb": imdb_id})
