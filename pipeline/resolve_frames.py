#!/usr/local/bin/python3
from pathlib import Path

FRAMES_ROOT = Path.home() / "prisma_automator/data/frames"

def resolve_frames(work_ids):
    """
    work_ids: dict con posibles ids:
      { "tmdb": 1887, "imdb": "tt0422720" }
    return: (frames_path, source) o (None, None)
    """

    tmdb_id = work_ids.get("tmdb")
    imdb_id = work_ids.get("imdb")

    # 1. TMDB frames
    if tmdb_id:
        p = FRAMES_ROOT / "tmdb" / str(tmdb_id)
        if p.exists() and any(p.glob("*.jpg")):
            return p, "tmdb"

    # 2. Fanart frames
    if imdb_id:
        p = FRAMES_ROOT / "fanart" / imdb_id
        if p.exists() and any(p.glob("*.jpg")):
            return p, "fanart"

    return None, None
