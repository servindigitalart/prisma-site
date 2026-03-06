# TMDB Queue System

## Overview
The TMDB Queue System provides an efficient workflow for discovering, queueing, and ingesting films from The Movie Database (TMDB). This eliminates the need to manually look up TMDB IDs before adding films to the pipeline.

## Components

### 1. `search_tmdb.py` - Film Discovery
Search for films by title and interactively queue them for ingestion.

**Basic Usage:**
```bash
# Search by title
python pipeline/search_tmdb.py "Portrait of a Lady on Fire"

# Search with year for disambiguation
python pipeline/search_tmdb.py "Dune" --year 2021

# Auto-queue first result
python pipeline/search_tmdb.py "Mustang" --year 2015 --top

# Queue without confirmation
python pipeline/search_tmdb.py "Cleo from 5 to 7" --year 1962 --queue
```

**Queue Management:**
```bash
# List current queue
python pipeline/search_tmdb.py --list

# Clear the queue
python pipeline/search_tmdb.py --clear
```

**Output Format:**
```
🔍 Searching TMDB for: "Portrait of a Lady on Fire" (2019)

Results:
  1. Portrait of a Lady on Fire (2019) — France — ID: 531428
     Director: Céline Sciamma — TMDB popularity: 6.8

Found 1 result.
✅ Queued: work_portrait-of-a-lady-on-fire_2019 (TMDB ID: 531428)
```

### 2. `queue_film.py` - Simple Queue Wrapper
Unified interface for queueing films by either TMDB ID or title.

**Usage:**
```bash
# Queue by TMDB ID (legacy workflow)
python pipeline/queue_film.py --id 601666

# Queue by title (new workflow)
python pipeline/queue_film.py --title "Portrait of a Lady on Fire" --year 2019

# Queue by title with auto-select
python pipeline/queue_film.py --title "Mustang" --year 2015 --top
```

### 3. `ingest_queue.py` - Batch Ingestion
Process all films in the queue and fetch their complete TMDB data.

**Usage:**
```bash
# Process entire queue
python pipeline/ingest_queue.py

# Process first 5 films only
python pipeline/ingest_queue.py --limit 5

# Process queue but keep it (don't clear)
python pipeline/ingest_queue.py --keep-queue
```

**Output:**
```
🎬 Processing 5 film(s) from queue...

  ✅ Portrait of a Lady on Fire (2019) → pipeline/raw/tmdb_531428.json
  ✅ Mustang (2015) → pipeline/raw/tmdb_336804.json
  ✅ Cléo from 5 to 7 (1962) → pipeline/raw/tmdb_499.json
  ✅ Three Colors: White (1994) → pipeline/raw/tmdb_109.json
  ✅ Chungking Express (1994) → pipeline/raw/tmdb_11104.json

✨ Completed: 5/5 films ingested successfully
🗑️  Queue cleared.
```

## Queue File Structure

The queue is stored in `pipeline/queue/films_to_ingest.json` as a simple JSON array:

```json
[
  531428,
  336804,
  499,
  109,
  11104
]
```

**Features:**
- Automatic deduplication (won't queue the same TMDB ID twice)
- Persistent across sessions
- Created automatically on first use

## Complete Workflow Example

### Scenario: Curating a French New Wave Collection

```bash
# 1. Search and queue films
python pipeline/search_tmdb.py "Cleo from 5 to 7" --year 1962 --top
python pipeline/search_tmdb.py "Breathless" --year 1960 --top
python pipeline/search_tmdb.py "The 400 Blows" --year 1959 --top
python pipeline/search_tmdb.py "Jules and Jim" --year 1962 --top

# 2. Review the queue
python pipeline/search_tmdb.py --list

# 3. Ingest all queued films
python pipeline/ingest_queue.py

# 4. Run the normalization pipeline
python pipeline/run_pipeline.py --normalize

# 5. Run the color resolution pipeline
python pipeline/run_pipeline.py --cultural-memory
python pipeline/run_pipeline.py --visual-resolution

# 6. Migrate to database
python pipeline/migrate_to_db.py
```

## Search Features

### Disambiguation
When multiple results are found, you can interactively select which film to queue:

```bash
python pipeline/search_tmdb.py "Blue" --year 1993
```

Output:
```
Results:
  1. Three Colors: Blue (1993) — France — ID: 110
  2. Blue (1993) — United Kingdom — ID: 35669

Enter result number to queue (1-2) or 'n' to cancel: 1
✅ Queued: work_three-colors:-blue_1993 (TMDB ID: 110)
```

### Automatic Selection
Use `--top` to automatically select the first (most popular) result:

```bash
python pipeline/search_tmdb.py "Amélie" --year 2001 --top
```

### Duplicate Detection
The system prevents duplicate entries:

```bash
python pipeline/search_tmdb.py "Mustang" --year 2015 --top
# Output: ℹ️  Already queued: TMDB ID 336804
```

## Integration with Existing Pipeline

The queue system integrates seamlessly with the existing Prisma pipeline:

```
TMDB Queue System          Existing Pipeline
─────────────────          ─────────────────

search_tmdb.py    →    queue/*.json
                              ↓
ingest_queue.py   →    raw/tmdb_*.json
                              ↓
                       normalize_tmdb_work.py
                              ↓
                       phase_2_cultural_memory/
                              ↓
                       phase_3_visual_resolution/
                              ↓
                       migrate_to_db.py
```

## API Requirements

**Environment Variables:**
- `TMDB_API_KEY` - Required (stored in `.env.local`)

**Python Dependencies:**
- `requests` - HTTP client
- `python-dotenv` - Environment variable loading

Install if needed:
```bash
pip install requests python-dotenv
```

## Test Results

### Validated Films (February 26, 2026)

| Film Title | Year | TMDB ID | Director | Status |
|------------|------|---------|----------|--------|
| Portrait of a Lady on Fire | 2019 | 531428 | Céline Sciamma | ✅ Queued |
| Mustang | 2015 | 336804 | Deniz Gamze Ergüven | ✅ Queued |
| Cléo from 5 to 7 | 1962 | 499 | Agnès Varda | ✅ Queued |
| Three Colors: White | 1994 | 109 | Krzysztof Kieślowski | ✅ Queued |
| Chungking Express | 1994 | 11104 | Wong Kar-Wai | ✅ Queued |

All films successfully queued with correct TMDB IDs and metadata.

## Notes

- Search results are limited to top 3 matches to keep output clean
- Director information is fetched from `/movie/{id}/credits` endpoint
- Country information comes from `production_countries` in movie details
- TMDB popularity scores help rank results for disambiguation
- The queue persists across sessions until explicitly cleared
