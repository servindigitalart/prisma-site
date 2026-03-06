"""
pipeline/fix_photos_targeted.py
────────────────────────────────
Fetches missing profile photos (and bios) for all people in Supabase
that have a tmdb_id but no profile_path.

Calls TMDB /person/{tmdb_id} directly — no search, uses stored ID.
Also populates bio if TMDB returns one and bio is currently null.

Usage:
    python3 pipeline/fix_photos_targeted.py
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')
from supabase import create_client

db = create_client(os.environ['PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
TMDB_KEY = os.environ['TMDB_API_KEY']
TMDB_BASE = 'https://api.themoviedb.org/3'
HEADERS = {'User-Agent': 'PRISMA-film-db/1.0'}


def fetch_tmdb_person(tmdb_id: int) -> dict:
    try:
        r = requests.get(
            f'{TMDB_BASE}/person/{tmdb_id}',
            params={'api_key': TMDB_KEY, 'language': 'en-US'},
            headers=HEADERS,
            timeout=10,
        )
        if r.status_code == 404:
            return {}
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f'  ⚠ TMDB error for {tmdb_id}: {e}')
        return {}


def main():
    # ── 1. Paginated fetch of all people without profile_path ─────────────────
    print('Fetching all people without profile_path (paginated)...')
    all_missing: list[dict] = []
    offset = 0
    while True:
        batch = (
            db.table('people')
            .select('id, name, tmdb_id, bio')
            .is_('profile_path', 'null')
            .not_.is_('tmdb_id', 'null')
            .range(offset, offset + 999)
            .execute()
        )
        all_missing.extend(batch.data)
        if len(batch.data) < 1000:
            break
        offset += 1000

    print(f'People without photo but with TMDB ID: {len(all_missing)}')
    if not all_missing:
        print('Nothing to do.')
        return

    # ── 2. Fetch from TMDB and update ─────────────────────────────────────────
    photos_added = 0
    bios_added = 0
    not_found = 0

    for i, person in enumerate(all_missing):
        data = fetch_tmdb_person(person['tmdb_id'])

        update: dict = {}
        if data.get('profile_path'):
            update['profile_path'] = data['profile_path']
            photos_added += 1
        if data.get('biography') and not person.get('bio'):
            update['bio'] = data['biography'][:2000]
            bios_added += 1
        if not data:
            not_found += 1

        if update:
            db.table('people').update(update).eq('id', person['id']).execute()

        if i % 100 == 0:
            print(f'  [{i}/{len(all_missing)}] photos_added={photos_added}  bios_added={bios_added}  not_found={not_found}')

        time.sleep(0.2)

    print(f'\nDone.')
    print(f'  Photos added : {photos_added}')
    print(f'  Bios added   : {bios_added}')
    print(f'  Not found    : {not_found}')
    print(f'  No profile   : {len(all_missing) - photos_added - not_found}')


if __name__ == '__main__':
    main()
