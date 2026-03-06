"""
Diagnostic + fix script for Supabase publishing status.
Checks current state of works and color_assignments tables,
then marks everything as published/approved for development.
"""
import os
from dotenv import load_dotenv

load_dotenv('/Users/servinemilio/Documents/REPOS/prisma-site/.env.local')

from supabase import create_client

url = os.environ.get('PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env.local")
    exit(1)

db = create_client(url, key)

print("=" * 60)
print("PRISMA — Supabase Diagnostic Report")
print("=" * 60)

# --- Check works table ---
print("\n📽️  WORKS TABLE:")
works = db.table('works').select('id, title, is_published').execute()
if works.data:
    for w in works.data:
        status = "✅ published" if w['is_published'] else "⚠️  unpublished"
        print(f"  {status} — {w['title']} ({w['id']})")
else:
    print("  ❌ No works found in database")

# --- Check color_assignments table ---
print("\n🎨  COLOR ASSIGNMENTS:")
assignments = db.table('color_assignments').select(
    'work_id, color_iconico, ritmo_visual, temperatura_emocional, review_status'
).execute()
if assignments.data:
    for a in assignments.data:
        print(f"  {a['work_id']}")
        print(f"    color: {a['color_iconico']} | ritmo: {a['ritmo_visual']} | temp: {a['temperatura_emocional']}")
        print(f"    review_status: {a['review_status']}")
else:
    print("  ❌ No color assignments found in database")

# --- Check junction tables ---
print("\n🔗  JUNCTION TABLES:")
wp = db.table('work_people').select('work_id, role', count='exact').execute()
print(f"  work_people: {wp.count or 0} rows")

ws = db.table('work_studios').select('work_id', count='exact').execute()
print(f"  work_studios: {ws.count or 0} rows")

wa = db.table('work_awards').select('work_id', count='exact').execute()
print(f"  work_awards: {wa.count or 0} rows")

# --- Fix: publish everything ---
print("\n🔧  APPLYING FIXES:")

result_works = db.table('works').update({'is_published': True}).neq('id', '').execute()
print(f"  ✅ Marked all works as is_published = true")

result_assignments = db.table('color_assignments').update(
    {'review_status': 'approved'}
).neq('work_id', '').execute()
print(f"  ✅ Marked all color_assignments as review_status = approved")

# --- Verify fixes ---
print("\n✅  VERIFICATION:")
works_after = db.table('works').select('id, title, is_published').execute()
for w in works_after.data or []:
    status = "✅" if w['is_published'] else "❌"
    print(f"  {status} {w['title']}")

assignments_after = db.table('color_assignments').select(
    'work_id, review_status'
).execute()
for a in assignments_after.data or []:
    print(f"  ✅ {a['work_id']} → {a['review_status']}")

print("\n" + "=" * 60)
print("NEXT STEP: Run the full migration to populate junction tables:")
print("  python pipeline/migrate_to_db.py --execute")
print("=" * 60)
