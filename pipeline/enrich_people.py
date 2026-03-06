"""
Scans all work JSON files, finds referenced people without JSON files,
fetches their data from TMDB API, and creates the missing person files.

Run: python pipeline/enrich_people.py
"""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/Users/servinemilio/Documents/REPOS/prisma-site/.env.local')

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE = 'https://api.themoviedb.org/3'
WORKS_DIR = Path('pipeline/normalized/works')
PEOPLE_DIR = Path('pipeline/normalized/people')
PEOPLE_DIR.mkdir(exist_ok=True)

headers = {'Authorization': f'Bearer {os.environ.get("TMDB_ACCESS_TOKEN", "")}'}
params_base = {'api_key': TMDB_API_KEY, 'language': 'en-US'}

def tmdb_get(endpoint, params={}):
    url = f'{TMDB_BASE}{endpoint}'
    all_params = {**params_base, **params}
    r = requests.get(url, params=all_params)
    r.raise_for_status()
    time.sleep(0.25)  # Rate limit: 4 req/sec
    return r.json()

def person_file_exists(person_id: str) -> bool:
    return (PEOPLE_DIR / f'{person_id}.json').exists()

def create_person_file(person_id: str, tmdb_id: int, role: str):
    """Fetch person data from TMDB and create their JSON file."""
    try:
        data = tmdb_get(f'/person/{tmdb_id}', {'append_to_response': 'external_ids'})
        
        person = {
            'id': person_id,
            'name': data.get('name', ''),
            'biography': data.get('biography', '') or None,
            'birth_year': int(data['birthday'][:4]) if data.get('birthday') else None,
            'death_year': int(data['deathday'][:4]) if data.get('deathday') else None,
            'nationality': [data.get('place_of_birth', '')] if data.get('place_of_birth') else [],
            'profile_path': data.get('profile_path'),
            'roles': [role],
            'works': [],  # Will be populated by migration script
            'ids': {
                'tmdb': tmdb_id,
                'imdb': data.get('external_ids', {}).get('imdb_id'),
            }
        }
        
        out_path = PEOPLE_DIR / f'{person_id}.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(person, f, ensure_ascii=False, indent=2)
        
        return person['name']
    except Exception as e:
        print(f'  ❌ Failed to fetch TMDB {tmdb_id}: {e}')
        return None

# --- Main: scan all work files ---
print('=' * 60)
print('PRISMA — Person Enrichment Script')
print('=' * 60)

all_work_files = list(WORKS_DIR.glob('work_*.json'))
print(f'\n📽️  Scanning {len(all_work_files)} work files...')

missing_people = {}  # person_id → {tmdb_id, role}
found = 0
missing = 0

for work_file in all_work_files:
    with open(work_file, encoding='utf-8') as f:
        work = json.load(f)
    
    # Get TMDB credits for this work
    tmdb_id = work.get('ids', {}).get('tmdb')
    if not tmdb_id:
        continue
    
    # Collect referenced people from the work
    people_refs = work.get('people', {})
    for role, person_ids in people_refs.items():
        for person_id in (person_ids or []):
            if person_file_exists(person_id):
                found += 1
            else:
                if person_id not in missing_people:
                    missing_people[person_id] = {
                        'role': role,
                        'work_tmdb_id': tmdb_id,
                        'work_title': work.get('title', '')
                    }
                    missing += 1

print(f'  ✅ Person files exist: {found}')
print(f'  ❌ Missing person files: {len(missing_people)} unique people')

if not missing_people:
    print('\n✅ All person files exist. Nothing to do.')
    exit(0)

# Fetch missing people from TMDB credits
print(f'\n🔍 Fetching missing people from TMDB...')

# Group by work to minimize API calls
work_people_cache = {}  # work_tmdb_id → credits data

created = 0
failed = 0

for person_id, info in list(missing_people.items())[:100]:  # Limit to 100 to avoid hitting rate limits
    work_tmdb_id = info['work_tmdb_id']
    role = info['role']
    
    print(f'\n  👤 Processing: {person_id}')
    print(f'     Work: {info["work_title"]} (TMDB {work_tmdb_id})')
    print(f'     Role: {role}')
    
    # Fetch credits for this work if not cached
    if work_tmdb_id not in work_people_cache:
        try:
            credits = tmdb_get(f'/movie/{work_tmdb_id}/credits')
            work_people_cache[work_tmdb_id] = credits
            print(f'     📥 Fetched credits: {len(credits.get("cast", []))} cast + {len(credits.get("crew", []))} crew')
        except Exception as e:
            print(f'     ❌ Failed credits for work {work_tmdb_id}: {e}')
            work_people_cache[work_tmdb_id] = {}
    
    credits = work_people_cache[work_tmdb_id]
    
    # Find this person in the credits
    all_credit_people = (
        credits.get('cast', []) + credits.get('crew', [])
    )
    
    # Match by slug similarity
    person_slug = person_id.replace('person_', '')
    matched_tmdb_id = None
    
    for credit in all_credit_people:
        credit_name = credit.get('name', '')
        credit_slug = credit_name.lower().replace(' ', '-').replace('.', '').replace("'", '').replace(',', '')
        person_slug_clean = person_slug.replace('-', '')
        credit_slug_clean = credit_slug.replace('-', '')
        
        if credit_slug == person_slug or credit_slug_clean == person_slug_clean:
            matched_tmdb_id = credit['id']
            print(f'     ✓ Matched: {credit_name} (TMDB {matched_tmdb_id})')
            break
    
    if matched_tmdb_id:
        name = create_person_file(person_id, matched_tmdb_id, role)
        if name:
            print(f'     ✅ Created: {person_id} ({name})')
            created += 1
        else:
            failed += 1
    else:
        # Create minimal file without TMDB match
        minimal = {
            'id': person_id,
            'name': person_id.replace('person_', '').replace('-', ' ').title(),
            'biography': None,
            'birth_year': None,
            'death_year': None,
            'nationality': [],
            'profile_path': None,
            'roles': [role],
            'works': [],
            'ids': {'tmdb': None, 'imdb': None}
        }
        out_path = PEOPLE_DIR / f'{person_id}.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(minimal, f, ensure_ascii=False, indent=2)
        print(f'     ⚠️  Minimal file (no TMDB match): {person_id}')
        created += 1

print(f'\n{"=" * 60}')
print(f'📊 Results:')
print(f'  ✅ Created: {created} person files')
print(f'  ❌ Failed: {failed}')
print(f'\n✅ Person enrichment complete!')
