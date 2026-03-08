import os, json
from dotenv import load_dotenv
load_dotenv('.env.local')
from supabase import create_client

db = create_client(os.environ['PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

# Sample film data
result = db.table('works').select('id,title,year,synopsis,tmdb_poster_path,countries,languages,duration_min,genres,imdb_rating').eq('id', 'work_parasite_2019').execute()
print("=== FILM DATA ===")
print(json.dumps(result.data[0] if result.data else {}, indent=2, default=str))

# Sample work_people for that film
wp = db.table('work_people').select('role, person_id, people(id, name)').eq('work_id', 'work_parasite_2019').execute()
print("\n=== WORK_PEOPLE ===")
for row in (wp.data or []):
    print(f"  {row['role']}: {row.get('people', {}).get('name', '?')}")

# Check works table columns (slug? or id-based?)
cols = db.table('works').select('id').limit(3).execute()
print("\n=== SAMPLE WORK IDS ===")
for r in (cols.data or []):
    print(f"  {r['id']}")

# Check people table columns
pcols = db.table('people').select('id, name, bio, profile_path, nationality').limit(2).execute()
print("\n=== SAMPLE PEOPLE ===")
for r in (pcols.data or []):
    print(json.dumps(r, indent=2, default=str))

# Check festivals table
fcols = db.table('festivals').select('id, name, description, city, country').limit(2).execute()
print("\n=== SAMPLE FESTIVALS ===")
for r in (fcols.data or []):
    print(json.dumps(r, indent=2, default=str))
