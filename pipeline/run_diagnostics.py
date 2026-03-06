#!/usr/bin/env python3
"""
PRISMA DATABASE DIAGNOSTICS - Simplified Live Audit
====================================================
Connects to Supabase and runs diagnostic queries on actual schema.

USAGE:
    python3 pipeline/run_diagnostics.py

REQUIRES:
    SUPABASE_URL and SUPABASE_SERVICE_KEY in environment
"""

import os
import sys

# Check for required packages
def _require(package):
    try:
        __import__(package)
    except ImportError:
        pkg = "python-dotenv" if package == "dotenv" else package
        print(f"\n  ✗  Required package not installed: {package}")
        print(f"     Install with: pip install {pkg}\n")
        sys.exit(1)

_require("supabase")

from supabase import create_client

print("=" * 70)
print("PRISMA DATABASE LIVE DIAGNOSTICS")
print("=" * 70)
print()

# Load environment
print("🔌 Loading credentials...")
supabase_url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not supabase_url or not service_key:
    print("❌ ERROR: Missing credentials")
    print("   Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
    sys.exit(1)

print(f"   URL: {supabase_url[:40]}...")
print("   Key: [REDACTED]")
print()

# Connect
print("🔌 Connecting to database...")
try:
    client = create_client(supabase_url, service_key)
    print("✅ Connected\n")
except Exception as e:
    print(f"❌ Connection failed: {e}\n")
    sys.exit(1)

# ─── DIAGNOSTIC 1: Table Counts ───────────────────────────────────────────────

print("=" * 70)
print("📊 DIAGNOSTIC 1: TABLE RECORD COUNTS")
print("=" * 70)
print()

tables = [
    'works', 'people', 'studios', 'colors', 'dimensions', 'media_types',
    'work_colors', 'work_dimensions', 'work_people', 'work_studios'
]

table_counts = {}
for table in tables:
    try:
        result = client.table(table).select('*', count='exact').limit(0).execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        table_counts[table] = count
        flag = '⚠️ ' if count == 0 else '✅'
        print(f"{flag} {table:20s}: {count:6,d} records")
    except Exception as e:
        print(f"❌ {table:20s}: ERROR - {str(e)[:40]}")
        table_counts[table] = -1

print()

# ─── DIAGNOSTIC 2: Duplicate tmdb_id in People ────────────────────────────────

print("=" * 70)
print("👥 DIAGNOSTIC 2: PEOPLE IDENTITY CONFLICTS")
print("=" * 70)
print()

print("Checking for duplicate tmdb_id values...")
try:
    # Get all people records
    people = client.table('people').select('id,tmdb_id,name').execute()
    
    # Group by tmdb_id
    tmdb_map = {}
    no_tmdb_count = 0
    
    for person in people.data:
        tmdb_id = person.get('tmdb_id')
        if tmdb_id is None:
            no_tmdb_count += 1
            continue
        
        if tmdb_id not in tmdb_map:
            tmdb_map[tmdb_id] = []
        tmdb_map[tmdb_id].append({
            'id': person['id'],
            'name': person.get('name', 'Unknown')
        })
    
    # Find duplicates
    duplicates = {tid: records for tid, records in tmdb_map.items() if len(records) > 1}
    
    print(f"   Total people: {len(people.data):,d}")
    print(f"   Without tmdb_id: {no_tmdb_count:,d}")
    print(f"   With tmdb_id: {len(tmdb_map):,d}")
    print()
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate tmdb_id values!\n")
        print("   Sample duplicates (showing first 10):")
        for tmdb_id, records in list(duplicates.items())[:10]:
            print(f"\n   tmdb_id={tmdb_id} ({len(records)} records):")
            for rec in records[:5]:
                print(f"      • {rec['id']:50s} - {rec['name'][:40]}")
    else:
        print("✅ No duplicate tmdb_id values found")
    
except Exception as e:
    print(f"❌ Error checking duplicates: {e}")

print()

# ─── DIAGNOSTIC 3: Orphaned Records ───────────────────────────────────────────

print("=" * 70)
print("🔗 DIAGNOSTIC 3: ORPHANED RECORDS IN JUNCTION TABLES")
print("=" * 70)
print()

# Check work_colors
print("Checking work_colors...")
try:
    work_colors = client.table('work_colors').select('work_id,color_id').execute()
    works_result = client.table('works').select('id').execute()
    colors_result = client.table('colors').select('id').execute()
    
    valid_work_ids = {w['id'] for w in works_result.data}
    valid_color_ids = {c['id'] for c in colors_result.data}
    
    orphaned_works = [wc for wc in work_colors.data if wc['work_id'] not in valid_work_ids]
    orphaned_colors = [wc for wc in work_colors.data if wc['color_id'] not in valid_color_ids]
    
    print(f"   Total work_colors: {len(work_colors.data):,d}")
    
    if orphaned_works:
        print(f"   ❌ Orphaned work_id: {len(orphaned_works)} (work not in works table)")
        for ow in orphaned_works[:3]:
            print(f"      • work_id={ow['work_id']}")
    else:
        print(f"   ✅ Orphaned work_id: 0")
    
    if orphaned_colors:
        print(f"   ❌ Orphaned color_id: {len(orphaned_colors)} (color not in colors table)")
        for oc in orphaned_colors[:3]:
            print(f"      • color_id={oc['color_id']}")
    else:
        print(f"   ✅ Orphaned color_id: 0")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Check work_people
print("Checking work_people...")
try:
    work_people = client.table('work_people').select('work_id,person_id').execute()
    works_result = client.table('works').select('id').execute()
    people_result = client.table('people').select('id').execute()
    
    valid_work_ids = {w['id'] for w in works_result.data}
    valid_person_ids = {p['id'] for p in people_result.data}
    
    orphaned_works = [wp for wp in work_people.data if wp['work_id'] not in valid_work_ids]
    orphaned_people = [wp for wp in work_people.data if wp['person_id'] not in valid_person_ids]
    
    print(f"   Total work_people: {len(work_people.data):,d}")
    
    if orphaned_works:
        print(f"   ❌ Orphaned work_id: {len(orphaned_works)}")
    else:
        print(f"   ✅ Orphaned work_id: 0")
    
    if orphaned_people:
        print(f"   ❌ Orphaned person_id: {len(orphaned_people)}")
    else:
        print(f"   ✅ Orphaned person_id: 0")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# ─── DIAGNOSTIC 4: Color Distribution ─────────────────────────────────────────

print("=" * 70)
print("🎨 DIAGNOSTIC 4: COLOR USAGE DISTRIBUTION")
print("=" * 70)
print()

try:
    work_colors = client.table('work_colors').select('color_id').execute()
    colors = client.table('colors').select('id,name').execute()
    
    # Build color name map
    color_names = {c['id']: c.get('name', c['id']) for c in colors.data}
    
    # Count usage
    color_counts = {}
    for wc in work_colors.data:
        cid = wc['color_id']
        color_counts[cid] = color_counts.get(cid, 0) + 1
    
    # Sort by usage
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    total = sum(color_counts.values())
    
    print(f"   Total assignments: {total:,d}")
    print(f"   Unique colors used: {len(color_counts)}/{len(colors.data)}")
    print()
    print("   Top 15 colors by usage:")
    
    for color_id, count in sorted_colors[:15]:
        pct = (count / total * 100) if total > 0 else 0
        bar = '█' * min(int(pct / 2), 40)
        name = color_names.get(color_id, color_id)[:25]
        flag = '⚠️ ' if pct > 20 else '   '
        print(f"{flag}{name:25s}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Flag overused
    overused = [(c, n) for c, n in sorted_colors if n / total > 0.2]
    if overused:
        print(f"\n   ⚠️  Overused colors (>20% of total):")
        for cid, count in overused:
            pct = count / total * 100
            print(f"      • {color_names.get(cid, cid)}: {pct:.1f}%")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# ─── DIAGNOSTIC 5: Film Completeness ──────────────────────────────────────────

print("=" * 70)
print("🎬 DIAGNOSTIC 5: FILM COMPLETENESS")
print("=" * 70)
print()

try:
    works = client.table('works').select('id,title,release_date').execute()
    
    print("Checking first 20 films for completeness...")
    print()
    
    incomplete_count = 0
    
    for work in works.data[:20]:
        wid = work['id']
        title = work.get('title', 'Unknown')[:40]
        issues = []
        
        # Check colors
        wc = client.table('work_colors').select('color_id', count='exact').eq('work_id', wid).limit(0).execute()
        colors_count = wc.count if hasattr(wc, 'count') else len(wc.data)
        if colors_count == 0:
            issues.append('no_colors')
        
        # Check people
        wp = client.table('work_people').select('person_id', count='exact').eq('work_id', wid).limit(0).execute()
        people_count = wp.count if hasattr(wp, 'count') else len(wp.data)
        if people_count == 0:
            issues.append('no_people')
        
        # Check dimensions
        wd = client.table('work_dimensions').select('dimension_id', count='exact').eq('work_id', wid).limit(0).execute()
        dims_count = wd.count if hasattr(wd, 'count') else len(wd.data)
        if dims_count == 0:
            issues.append('no_dimensions')
        
        if issues:
            incomplete_count += 1
            flag = '⚠️ '
            issues_str = ', '.join(issues)
            print(f"{flag}{title:40s} | {issues_str}")
        else:
            print(f"✅ {title:40s}")
    
    print()
    print(f"   Incomplete films (in sample of 20): {incomplete_count}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# ─── SUMMARY ──────────────────────────────────────────────────────────────────

print("=" * 70)
print("📋 DIAGNOSTIC COMPLETE")
print("=" * 70)
print()

critical_issues = []
warnings = []

# Check table counts
if table_counts.get('works', 0) == 0:
    critical_issues.append("No works in database")
if table_counts.get('people', 0) == 0:
    critical_issues.append("No people in database")

# Check for duplicate tmdb_ids
if duplicates:
    critical_issues.append(f"{len(duplicates)} duplicate tmdb_id values in people table")

if critical_issues:
    print("❌ CRITICAL ISSUES FOUND:")
    for issue in critical_issues:
        print(f"   • {issue}")
    print()

if warnings:
    print("⚠️  WARNINGS:")
    for warning in warnings:
        print(f"   • {warning}")
    print()

if not critical_issues and not warnings:
    print("✅ No critical issues found")
    print()

print("Review the detailed output above for complete analysis.")
print()
