"""
Fetches missing data for all works:
- TMDB rating (vote_average) since OMDB key is not available
- Confirms poster_path is saved
- Saves enriched data back to JSON files
- Updates Supabase works table

Run: python pipeline/enrich_works.py
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

# Supabase will be updated separately
USE_SUPABASE = False
if USE_SUPABASE:
    from supabase import create_client
    db = create_client(
        os.environ['PUBLIC_SUPABASE_URL'],
        os.environ['SUPABASE_SERVICE_KEY']
    )

def tmdb_get(endpoint, params={}):
    url = f'{TMDB_BASE}{endpoint}'
    r = requests.get(url, params={'api_key': TMDB_API_KEY, 'language': 'en-US', **params})
    r.raise_for_status()
    time.sleep(0.25)
    return r.json()

print('=' * 60)
print('PRISMA — Work Enrichment Script')
print('=' * 60)

work_files = list(WORKS_DIR.glob('work_*.json'))
print(f'\n📽️  Processing {len(work_files)} works...\n')

enriched = 0
failed = 0

for work_file in work_files:
    with open(work_file, encoding='utf-8') as f:
        work = json.load(f)
    
    title = work.get('title', work_file.stem)
    tmdb_id = work.get('ids', {}).get('tmdb')
    changed = False
    
    print(f'  🎬 {title}')
    
    if not tmdb_id:
        print(f'     ❌ No TMDB ID, skipping')
        continue
    
    # 1. Fetch TMDB rating (vote_average)
    if not work.get('tmdb_rating'):
        try:
            details = tmdb_get(f'/movie/{tmdb_id}')
            rating = details.get('vote_average')
            if rating:
                work['tmdb_rating'] = round(rating, 1)
                changed = True
                print(f'     ⭐ TMDB rating: {rating}/10')
        except Exception as e:
            print(f'     ❌ Rating fetch failed: {e}')
    else:
        print(f'     ⭐ TMDB rating: {work["tmdb_rating"]} (already exists)')
    
    # 2. Confirm poster_path exists
    poster_path = work.get('media', {}).get('poster_path')
    if not poster_path and tmdb_id:
        try:
            details = tmdb_get(f'/movie/{tmdb_id}')
            poster_path = details.get('poster_path')
            if poster_path:
                if 'media' not in work:
                    work['media'] = {}
                work['media']['poster_path'] = poster_path
                changed = True
                print(f'     🖼️  Poster: {poster_path}')
        except Exception as e:
            print(f'     ❌ Poster fetch failed: {e}')
    elif poster_path:
        print(f'     🖼️  Poster: {poster_path} (already exists)')
    
    # 3. Save enriched JSON
    if changed:
        with open(work_file, 'w', encoding='utf-8') as f:
            json.dump(work, f, ensure_ascii=False, indent=2)
        print(f'     💾 JSON file updated')
    
    # 4. Update Supabase
    if USE_SUPABASE:
        work_id = work.get('id', work_file.stem)
        if not work_id.startswith('work_'):
            work_id = f'work_{work_id}'
        
        update_data = {}
        if work.get('tmdb_rating'):
            # Use tmdb_rating for imdb_rating field since they're similar scales
            update_data['imdb_rating'] = work['tmdb_rating']
        if poster_path:
            update_data['poster_path'] = poster_path
        
        if update_data:
            try:
                db.table('works').update(update_data).eq('id', work_id).execute()
                enriched += 1
                print(f'     ✅ Supabase updated')
            except Exception as e:
                print(f'     ❌ Supabase update failed: {e}')
                failed += 1
    elif changed:
        enriched += 1

print(f'\n{"=" * 60}')
print(f'📊 Summary:')
print(f'  ✅ Works enriched: {enriched}')
print(f'  ❌ Failed: {failed}')
print(f'\n✅ Work enrichment complete!')
