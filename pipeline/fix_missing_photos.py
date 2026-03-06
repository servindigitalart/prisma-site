#!/usr/bin/env python3
"""
Fix missing profile photos for people in Supabase by fetching from TMDB.
Only updates people with NULL profile_path.
"""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.local')

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE = 'https://api.themoviedb.org/3'
headers = {'Authorization': f'Bearer {os.environ.get("TMDB_ACCESS_TOKEN", "")}'}
params_base = {'api_key': TMDB_API_KEY, 'language': 'en-US'}

db = create_client(
    os.environ['PUBLIC_SUPABASE_URL'],
    os.environ['SUPABASE_SERVICE_KEY']
)

def tmdb_get(endpoint, params={}):
    url = f'{TMDB_BASE}{endpoint}'
    all_params = {**params_base, **params}
    r = requests.get(url, params=all_params, headers=headers)
    r.raise_for_status()
    time.sleep(0.25)  # Rate limit
    return r.json()

def find_person_tmdb_id(name: str):
    """Search TMDB for person by name."""
    try:
        results = tmdb_get('/search/person', {'query': name})
        if results.get('results'):
            return results['results'][0].get('id')
    except:
        pass
    return None

def update_person_photo(person_id: str, name: str, tmdb_id: int | None):
    """Fetch profile photo from TMDB and update in Supabase."""
    if not tmdb_id:
        tmdb_id = find_person_tmdb_id(name)
    
    if not tmdb_id:
        print(f"  ⚠️  {name}: No TMDB match found")
        return False
    
    try:
        data = tmdb_get(f'/person/{tmdb_id}')
        profile_path = data.get('profile_path')
        
        if profile_path:
            db.table('people').update({
                'profile_path': profile_path,
                'tmdb_id': tmdb_id
            }).eq('id', person_id).execute()
            print(f"  ✅ {name}: Added photo")
            return True
        else:
            print(f"  ⚠️  {name}: No photo on TMDB")
            return False
    except Exception as e:
        print(f"  ❌ {name}: Error - {e}")
        return False

def main():
    print("🔍 Finding people without photos...")
    response = db.table('people').select('id, name, tmdb_id').is_('profile_path', 'null').order('name').execute()
    people = response.data
    
    print(f"\nFound {len(people)} people without photos\n")
    
    updated = 0
    for person in people:
        if update_person_photo(person['id'], person['name'], person.get('tmdb_id')):
            updated += 1
    
    print(f"\n✅ Updated {updated}/{len(people)} people with photos")

if __name__ == '__main__':
    main()
