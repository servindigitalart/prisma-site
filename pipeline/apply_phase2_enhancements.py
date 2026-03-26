#!/usr/local/bin/python3
"""
apply_phase2_enhancements.py
────────────────────────────
Apply Phase 2 database enhancements:
1. Add canon_tier and arthouse_dist fields
2. Create ranking_scores table and functions
3. Add pSEO review workflow constraints
4. Generate initial rankings

Usage:
    python pipeline/apply_phase2_enhancements.py
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('SUPABASE_URL') or os.getenv('PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment")
    sys.exit(1)

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n🔧 Phase 2 Database Enhancements")
print("=" * 60)

# For Supabase, we need to apply schema changes via their dashboard or SQL editor
# For now, let's apply what we can via the API and document what needs manual setup

# Step 1: Update existing color_assignments to set canon_tier from works data
print("\n1. Setting canon_tier values from works data...")
try:
    # Fetch works with Criterion/MUBI flags
    works_result = client.table('works').select('id, criterion_title, mubi_title').execute()
    
    updated_count = 0
    for work in works_result.data:
        canon_tier = 'none'
        if work.get('criterion_title'):
            canon_tier = 'criterion'
        elif work.get('mubi_title'):
            canon_tier = 'mubi_permanent'
        
        # Update color_assignment
        try:
            client.table('color_assignments').update({
                'canon_tier': canon_tier
            }).eq('work_id', work['id']).execute()
            updated_count += 1
        except Exception as e:
            pass  # Color assignment might not exist
    
    print(f"   ✅ Updated {updated_count} color assignments with canon_tier")
except Exception as e:
    print(f"   ⚠️  Note: canon_tier column needs to be added via Supabase dashboard")
    print(f"      SQL: ALTER TABLE color_assignments ADD COLUMN canon_tier TEXT;")

# Step 2: Document ranking system setup
print("\n2. Ranking System Setup:")
print("   📝 The following SQL needs to be executed in Supabase SQL Editor:")
print("      File: pipeline/phase2_enhancements.sql")
print("      Contains:")
print("        - ranking_scores table creation")
print("        - Scoring functions (canon_tier_multiplier, arthouse_score)")
print("        - refresh_work_rankings() function")
print("        - Status workflow triggers for pSEO review gate")

# Step 3: Show current data state
print("\n3. Current Database State:")
print("   " + "-" * 56)
try:
    works = client.table('works').select('*', count='exact').execute()
    people = client.table('people').select('*', count='exact').execute()
    studios = client.table('studios').select('*', count='exact').execute()
    colors = client.table('color_assignments').select('*', count='exact').execute()
    
    print(f"   works               : {works.count:3d} rows")
    print(f"   people              : {people.count:3d} rows")
    print(f"   studios             : {studios.count:3d} rows")
    print(f"   color_assignments   : {colors.count:3d} rows")
    
    # Check for ranking_scores table
    try:
        rankings = client.table('ranking_scores').select('*', count='exact').execute()
        print(f"   ranking_scores      : {rankings.count:3d} rows")
    except:
        print(f"   ranking_scores      : NOT CREATED YET")
    
except Exception as e:
    print(f"   ❌ Error querying tables: {e}")

print("   " + "-" * 56)

# Step 4: Show what canon_tier values exist
print("\n4. Canon Tier Distribution:")
try:
    works_data = client.table('works').select('id, title, criterion_title, mubi_title').execute()
    criterion_count = sum(1 for w in works_data.data if w.get('criterion_title'))
    mubi_count = sum(1 for w in works_data.data if w.get('mubi_title'))
    none_count = len(works_data.data) - criterion_count - mubi_count
    
    print(f"   criterion         : {criterion_count} works")
    print(f"   mubi_permanent    : {mubi_count} works")
    print(f"   none              : {none_count} works")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("📋 NEXT STEPS:")
print("=" * 60)
print("1. Open Supabase Dashboard → SQL Editor")
print("2. Paste contents of: pipeline/phase2_enhancements.sql")
print("3. Execute the SQL script")
print("4. Run: SELECT refresh_work_rankings();")
print("5. Verify with: SELECT * FROM ranking_scores;")
print("=" * 60)
print()
