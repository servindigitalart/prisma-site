"""
Updates Supabase works table with enriched data from JSON files.
Run after enrich_works.py to sync data to database.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/Users/servinemilio/Documents/REPOS/prisma-site/.env.local')

from supabase import create_client

db = create_client(
    os.environ['PUBLIC_SUPABASE_URL'],
    os.environ['SUPABASE_SERVICE_KEY']
)

WORKS_DIR = Path('pipeline/normalized/works')

print('=' * 60)
print('PRISMA — Supabase Works Update')
print('=' * 60)

work_files = list(WORKS_DIR.glob('work_*.json'))
print(f'\n📽️  Updating {len(work_files)} works in Supabase...\n')

updated = 0
failed = 0

for work_file in work_files:
    with open(work_file, encoding='utf-8') as f:
        work = json.load(f)
    
    work_id = work.get('id', work_file.stem)
    if not work_id.startswith('work_'):
        work_id = f'work_{work_id}'
    
    title = work.get('title', work_id)
    
    update_data = {}
    if work.get('tmdb_rating'):
        update_data['imdb_rating'] = work['tmdb_rating']
    
    poster_path = work.get('media', {}).get('poster_path')
    if poster_path:
        update_data['tmdb_poster_path'] = poster_path
    
    if update_data:
        try:
            db.table('works').update(update_data).eq('id', work_id).execute()
            updated += 1
            print(f'  ✅ {title}: rating={update_data.get("imdb_rating", "—")}, poster={bool(poster_path)}')
        except Exception as e:
            print(f'  ❌ {title}: {e}')
            failed += 1

print(f'\n{"=" * 60}')
print(f'📊 Results:')
print(f'  ✅ Updated: {updated} works')
print(f'  ❌ Failed: {failed}')
print(f'\n✅ Supabase update complete!')
