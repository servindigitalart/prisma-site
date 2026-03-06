"""
pipeline/enrich_bios.py
────────────────────────
Fetches TMDB biographies for all people who have a tmdb_id and
profile_path but no bio yet.

Run after fix_photos_targeted.py.

Usage:
    python3 pipeline/enrich_bios.py
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


def fetch_biography(tmdb_id: int) -> str | None:
    try:
        r = requests.get(
            f'{TMDB_BASE}/person/{tmdb_id}',
            params={'api_key': TMDB_KEY, 'language': 'en-US'},
            headers=HEADERS,
            timeout=10,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        bio = r.json().get('biography', '')
        return bio[:2000] if bio else None
    except Exception as e:
        print(f'  ⚠ TMDB error for {tmdb_id}: {e}')
        return None


def main():
    # ── 1. Fetch all people with tmdb_id + profile_path but no bio ────────────
    print('Fetching people with photo but no bio (paginated)...')
    targets: list[dict] = []
    offset = 0
    while True:
        batch = (
            db.table('people')
            .select('id, name, tmdb_id')
            .not_.is_('tmdb_id', 'null')
            .not_.is_('profile_path', 'null')
            .is_('bio', 'null')
            .range(offset, offset + 999)
            .execute()
        )
        targets.extend(batch.data)
        if len(batch.data) < 1000:
            break
        offset += 1000

    print(f'People with photo but no bio: {len(targets)}')
    if not targets:
        print('Nothing to do.')
        return

    # ── 2. Fetch bio and update ───────────────────────────────────────────────
    bios_added = 0
    empty = 0

    for i, person in enumerate(targets):
        bio = fetch_biography(person['tmdb_id'])

        if bio:
            db.table('people').update({'bio': bio}).eq('id', person['id']).execute()
            bios_added += 1
        else:
            empty += 1

        if i % 100 == 0:
            print(f'  [{i}/{len(targets)}] bios_added={bios_added}  no_bio_on_tmdb={empty}')

        time.sleep(0.2)

    print(f'\nDone.')
    print(f'  Bios added       : {bios_added}')
    print(f'  No bio on TMDB   : {empty}')


if __name__ == '__main__':
    main()
