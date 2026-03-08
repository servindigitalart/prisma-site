import os, json
from dotenv import load_dotenv
load_dotenv('.env.local')
from supabase import create_client
db = create_client(os.environ['PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

# Check imdb_id availability for sameAs
result = db.table('people').select('id, name, imdb_id, wikidata_id').not_.is_('imdb_id', 'null').limit(5).execute()
print('People with imdb_id:')
for r in result.data:
    print(f'  {r["name"]}: imdb={r["imdb_id"]} wikidata={r["wikidata_id"]}')

total = db.table('people').select('id', count='exact').not_.is_('imdb_id', 'null').execute()
print(f'Total people with imdb_id: {total.count}')

# Check works for imdb_id
works = db.table('works').select('id, title, imdb_id, year').not_.is_('imdb_id', 'null').limit(3).execute()
print('\nWorks with imdb_id:')
for w in works.data:
    print(f'  {w["title"]} ({w["year"]}): {w["imdb_id"]}')

# Check color palette data
colors = db.table('color_assignments').select('color_iconico').execute()
from collections import Counter
dist = Counter(r['color_iconico'] for r in colors.data)
print(f'\nColor distribution (top 5): {dict(list(dist.most_common(5)))}')

# Check works table for slug column
sample = db.table('works').select('id, title, year').limit(3).execute()
print('\nSample work IDs:')
for w in sample.data:
    print(f'  {w["id"]} -> slug would be: {w["id"].replace("work_", "")}')
