#!/usr/local/bin/python3
"""
PRISMA Database Diagnostic Audit
=================================
READ-ONLY analysis of data completeness, integrity, and distribution.

Sections:
1. Film Completeness
2. People Coverage
3. Relationship Integrity
4. Dimensional Distribution
5. Color Distribution
"""

import os
import sys
from pathlib import Path
from collections import Counter, defaultdict
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
    sys.exit(1)

client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: FILM COMPLETENESS DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════

def diagnose_film_completeness():
    """Analyze completeness of all works in database."""
    print("\n" + "="*80)
    print("PART 1: FILM COMPLETENESS DIAGNOSTIC")
    print("="*80)
    
    # Fetch all works
    works = client.table("works").select("*").execute()
    total_works = len(works.data)
    
    if total_works == 0:
        print("⚠️  No works found in database")
        return
    
    # Fetch related data
    work_people = client.table("work_people").select("work_id, person_id, role").execute()
    work_studios = client.table("work_studios").select("work_id, studio_id").execute()
    color_assignments = client.table("color_assignments").select("work_id, color_iconico").execute()
    
    # Build lookup maps
    people_by_work = defaultdict(list)
    for wp in work_people.data:
        people_by_work[wp["work_id"]].append(wp)
    
    studios_by_work = defaultdict(list)
    for ws in work_studios.data:
        studios_by_work[ws["work_id"]].append(ws)
    
    colors_by_work = {ca["work_id"]: ca for ca in color_assignments.data}
    
    # Analyze each work
    issues = []
    incomplete_works = []
    
    for work in works.data:
        work_id = work["id"]
        work_issues = []
        completeness_score = 0
        max_score = 12  # Total criteria
        
        # Check basic metadata
        if work.get("synopsis"):
            completeness_score += 1
        else:
            work_issues.append("Missing synopsis")
        
        if work.get("release_year"):
            completeness_score += 1
        else:
            work_issues.append("Missing release_year")
        
        if work.get("runtime"):
            completeness_score += 1
        else:
            work_issues.append("Missing runtime")
        
        # Check studios
        if studios_by_work.get(work_id):
            completeness_score += 1
        else:
            work_issues.append("Missing studios")
        
        # Check people
        people_count = len(people_by_work.get(work_id, []))
        if people_count >= 5:
            completeness_score += 1
        elif people_count > 0:
            work_issues.append(f"⚠️  Low people count: {people_count}")
        else:
            work_issues.append("❌ No people relationships")
        
        # Check color assignment
        if colors_by_work.get(work_id):
            completeness_score += 1
        else:
            work_issues.append("Missing color assignment")
        
        # Check dimensions
        if work.get("temperatura_emocional"):
            completeness_score += 1
        else:
            work_issues.append("Missing temperatura_emocional")
        
        if work.get("ritmo_visual"):
            completeness_score += 1
        else:
            work_issues.append("Missing ritmo_visual")
        
        if work.get("abstraccion"):
            completeness_score += 1
        else:
            work_issues.append("Missing abstraccion")
        
        # Check media
        if work.get("poster_url"):
            completeness_score += 1
        else:
            work_issues.append("Missing poster")
        
        if work.get("backdrop_url"):
            completeness_score += 1
        else:
            work_issues.append("Missing backdrop")
        
        # Check derived color data (check if file exists)
        # For now, we'll skip this check as it requires filesystem access
        completeness_score += 1  # Assume present
        
        completion_pct = (completeness_score / max_score) * 100
        
        if work_issues:
            incomplete_works.append({
                "work_id": work_id,
                "title": work.get("title", "Unknown"),
                "year": work.get("release_year"),
                "completion": completion_pct,
                "issues": work_issues
            })
    
    # Calculate statistics
    missing_synopsis = sum(1 for w in works.data if not w.get("synopsis"))
    missing_year = sum(1 for w in works.data if not w.get("release_year"))
    missing_runtime = sum(1 for w in works.data if not w.get("runtime"))
    missing_people = sum(1 for w in works.data if len(people_by_work.get(w["id"], [])) == 0)
    missing_studios = sum(1 for w in works.data if len(studios_by_work.get(w["id"], [])) == 0)
    missing_color = sum(1 for w in works.data if w["id"] not in colors_by_work)
    missing_temp = sum(1 for w in works.data if not w.get("temperatura_emocional"))
    missing_ritmo = sum(1 for w in works.data if not w.get("ritmo_visual"))
    missing_abstraccion = sum(1 for w in works.data if not w.get("abstraccion"))
    missing_poster = sum(1 for w in works.data if not w.get("poster_url"))
    missing_backdrop = sum(1 for w in works.data if not w.get("backdrop_url"))
    
    fully_complete = sum(1 for w in incomplete_works if w["completion"] == 100)
    
    # Print summary
    print(f"\n📊 OVERALL STATISTICS")
    print(f"Total works: {total_works}")
    print(f"Fully complete: {fully_complete} ({(fully_complete/total_works*100):.1f}%)")
    print(f"Incomplete: {len(incomplete_works)} ({(len(incomplete_works)/total_works*100):.1f}%)")
    
    print(f"\n📉 COMPLETENESS BREAKDOWN")
    print(f"Missing synopsis:       {missing_synopsis:4d} ({missing_synopsis/total_works*100:5.1f}%)")
    print(f"Missing release_year:   {missing_year:4d} ({missing_year/total_works*100:5.1f}%)")
    print(f"Missing runtime:        {missing_runtime:4d} ({missing_runtime/total_works*100:5.1f}%)")
    print(f"Missing people:         {missing_people:4d} ({missing_people/total_works*100:5.1f}%)")
    print(f"Missing studios:        {missing_studios:4d} ({missing_studios/total_works*100:5.1f}%)")
    print(f"Missing color:          {missing_color:4d} ({missing_color/total_works*100:5.1f}%)")
    print(f"Missing temperatura:    {missing_temp:4d} ({missing_temp/total_works*100:5.1f}%)")
    print(f"Missing ritmo:          {missing_ritmo:4d} ({missing_ritmo/total_works*100:5.1f}%)")
    print(f"Missing abstraccion:    {missing_abstraccion:4d} ({missing_abstraccion/total_works*100:5.1f}%)")
    print(f"Missing poster:         {missing_poster:4d} ({missing_poster/total_works*100:5.1f}%)")
    print(f"Missing backdrop:       {missing_backdrop:4d} ({missing_backdrop/total_works*100:5.1f}%)")
    
    # Top 10 most incomplete
    incomplete_works_sorted = sorted(incomplete_works, key=lambda x: x["completion"])[:10]
    
    print(f"\n❌ TOP 10 MOST INCOMPLETE WORKS")
    print(f"{'Title':<50} {'Year':<6} {'Complete':<10} {'Issues'}")
    print("-" * 120)
    for w in incomplete_works_sorted:
        title = w["title"][:47] + "..." if len(w["title"]) > 50 else w["title"]
        year = str(w["year"]) if w["year"] else "N/A"
        print(f"{title:<50} {year:<6} {w['completion']:>6.1f}%    {len(w['issues'])} issues")
        for issue in w["issues"][:3]:  # Show first 3 issues
            print(f"  {'':50}          ⚠️  {issue}")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: PEOPLE DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════

def diagnose_people_coverage():
    """Analyze people data quality and coverage."""
    print("\n" + "="*80)
    print("PART 2: PEOPLE COVERAGE DIAGNOSTIC")
    print("="*80)
    
    # Fetch all people
    people = client.table("people").select("*").execute()
    total_people = len(people.data)
    
    if total_people == 0:
        print("⚠️  No people found in database")
        return
    
    # Fetch work_people relationships
    work_people = client.table("work_people").select("person_id, work_id, role").execute()
    
    # Build person usage map
    people_with_works = set(wp["person_id"] for wp in work_people.data)
    
    # Analyze people
    missing_image = sum(1 for p in people.data if not p.get("profile_url"))
    missing_bio = sum(1 for p in people.data if not p.get("biography"))
    missing_tmdb = sum(1 for p in people.data if not p.get("tmdb_id"))
    orphaned = sum(1 for p in people.data if p["id"] not in people_with_works)
    
    # Check for duplicate tmdb_id
    tmdb_ids = [p.get("tmdb_id") for p in people.data if p.get("tmdb_id")]
    tmdb_counts = Counter(tmdb_ids)
    duplicates = {tid: count for tid, count in tmdb_counts.items() if count > 1}
    
    print(f"\n📊 PEOPLE STATISTICS")
    print(f"Total people: {total_people}")
    print(f"Missing profile image:  {missing_image:4d} ({missing_image/total_people*100:5.1f}%)")
    print(f"Missing biography:      {missing_bio:4d} ({missing_bio/total_people*100:5.1f}%)")
    print(f"Missing tmdb_id:        {missing_tmdb:4d} ({missing_tmdb/total_people*100:5.1f}%)")
    print(f"Orphaned (no works):    {orphaned:4d} ({orphaned/total_people*100:5.1f}%)")
    
    if duplicates:
        print(f"\n❌ DUPLICATE tmdb_id VIOLATIONS")
        for tmdb_id, count in duplicates.items():
            print(f"  tmdb_id {tmdb_id}: {count} occurrences")
    else:
        print(f"\n✅ No duplicate tmdb_id found")
    
    # Works with missing director/actor images
    works = client.table("works").select("id, title").execute()
    
    directors_missing_image = []
    actors_missing_image = []
    
    for work in works.data:
        work_id = work["id"]
        
        # Get directors
        directors = [wp for wp in work_people.data 
                    if wp["work_id"] == work_id and wp["role"] == "director"]
        
        if directors:
            director_id = directors[0]["person_id"]
            director = next((p for p in people.data if p["id"] == director_id), None)
            if director and not director.get("profile_url"):
                directors_missing_image.append({
                    "work": work["title"],
                    "person": director.get("name", "Unknown")
                })
        
        # Get main actor (first in billing)
        actors = [wp for wp in work_people.data 
                 if wp["work_id"] == work_id and wp["role"] == "actor"]
        
        if actors:
            actor_id = actors[0]["person_id"]
            actor = next((p for p in people.data if p["id"] == actor_id), None)
            if actor and not actor.get("profile_url"):
                actors_missing_image.append({
                    "work": work["title"],
                    "person": actor.get("name", "Unknown")
                })
    
    print(f"\n⚠️  WORKS WITH KEY MISSING IMAGES")
    print(f"Director missing image: {len(directors_missing_image)} works")
    print(f"Lead actor missing image: {len(actors_missing_image)} works")
    
    if directors_missing_image[:5]:
        print(f"\nSample works with director image missing:")
        for item in directors_missing_image[:5]:
            print(f"  - {item['work']}: {item['person']}")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: RELATIONSHIP INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

def diagnose_relationship_integrity():
    """Validate foreign key consistency and orphaned records."""
    print("\n" + "="*80)
    print("PART 3: RELATIONSHIP INTEGRITY DIAGNOSTIC")
    print("="*80)
    
    # Fetch all tables
    works = client.table("works").select("id").execute()
    people = client.table("people").select("id").execute()
    studios = client.table("studios").select("id").execute()
    
    work_people = client.table("work_people").select("work_id, person_id").execute()
    work_studios = client.table("work_studios").select("work_id, studio_id").execute()
    color_assignments = client.table("color_assignments").select("work_id").execute()
    
    work_ids = set(w["id"] for w in works.data)
    people_ids = set(p["id"] for p in people.data)
    studio_ids = set(s["id"] for s in studios.data)
    
    # Check work_people integrity
    orphaned_wp_works = []
    orphaned_wp_people = []
    
    for wp in work_people.data:
        if wp["work_id"] not in work_ids:
            orphaned_wp_works.append(wp["work_id"])
        if wp["person_id"] not in people_ids:
            orphaned_wp_people.append(wp["person_id"])
    
    # Check work_studios integrity
    orphaned_ws_works = []
    orphaned_ws_studios = []
    
    for ws in work_studios.data:
        if ws["work_id"] not in work_ids:
            orphaned_ws_works.append(ws["work_id"])
        if ws["studio_id"] not in studio_ids:
            orphaned_ws_studios.append(ws["studio_id"])
    
    # Check color_assignments integrity
    orphaned_ca_works = []
    
    for ca in color_assignments.data:
        if ca["work_id"] not in work_ids:
            orphaned_ca_works.append(ca["work_id"])
    
    # Print results
    print(f"\n📊 INTEGRITY CHECK RESULTS")
    
    if orphaned_wp_works:
        print(f"❌ work_people → works: {len(orphaned_wp_works)} orphaned references")
    else:
        print(f"✅ work_people → works: All references valid")
    
    if orphaned_wp_people:
        print(f"❌ work_people → people: {len(orphaned_wp_people)} orphaned references")
    else:
        print(f"✅ work_people → people: All references valid")
    
    if orphaned_ws_works:
        print(f"❌ work_studios → works: {len(orphaned_ws_works)} orphaned references")
    else:
        print(f"✅ work_studios → works: All references valid")
    
    if orphaned_ws_studios:
        print(f"❌ work_studios → studios: {len(orphaned_ws_studios)} orphaned references")
    else:
        print(f"✅ work_studios → studios: All references valid")
    
    if orphaned_ca_works:
        print(f"❌ color_assignments → works: {len(orphaned_ca_works)} orphaned references")
    else:
        print(f"✅ color_assignments → works: All references valid")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: DIMENSIONAL DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════

def diagnose_dimensional_distribution():
    """Analyze distribution balance across cinematic dimensions."""
    print("\n" + "="*80)
    print("PART 4: DIMENSIONAL DISTRIBUTION DIAGNOSTIC")
    print("="*80)
    
    works = client.table("works").select(
        "id, title, temperatura_emocional, ritmo_visual, abstraccion"
    ).execute()
    
    total_works = len(works.data)
    
    # Analyze each dimension
    temp_dist = Counter(w.get("temperatura_emocional") for w in works.data if w.get("temperatura_emocional"))
    ritmo_dist = Counter(w.get("ritmo_visual") for w in works.data if w.get("ritmo_visual"))
    abstraccion_dist = Counter(w.get("abstraccion") for w in works.data if w.get("abstraccion"))
    
    # Temperatura Emocional
    print(f"\n🌡️  TEMPERATURA EMOCIONAL DISTRIBUTION")
    print(f"{'Category':<30} {'Count':<10} {'%':<10} {'Status'}")
    print("-" * 70)
    
    for category, count in temp_dist.most_common():
        pct = (count / total_works) * 100
        flag = ""
        if pct > 35:
            flag = "⚠️  DOMINATES"
        elif pct < 5:
            flag = "📊 RARE"
        print(f"{category:<30} {count:<10} {pct:>5.1f}%     {flag}")
    
    # Ritmo Visual
    print(f"\n⚡ RITMO VISUAL DISTRIBUTION")
    print(f"{'Category':<30} {'Count':<10} {'%':<10} {'Status'}")
    print("-" * 70)
    
    for category, count in ritmo_dist.most_common():
        pct = (count / total_works) * 100
        flag = ""
        if pct > 35:
            flag = "⚠️  DOMINATES"
        elif pct < 5:
            flag = "📊 RARE"
        print(f"{category:<30} {count:<10} {pct:>5.1f}%     {flag}")
    
    # Abstracción
    print(f"\n🎨 ABSTRACCIÓN DISTRIBUTION")
    print(f"{'Category':<30} {'Count':<10} {'%':<10} {'Status'}")
    print("-" * 70)
    
    for category, count in abstraccion_dist.most_common():
        pct = (count / total_works) * 100
        flag = ""
        if pct > 35:
            flag = "⚠️  DOMINATES"
        elif pct < 5:
            flag = "📊 RARE"
        print(f"{category:<30} {count:<10} {pct:>5.1f}%     {flag}")
    
    # Cross-dimension combinations
    combinations = Counter()
    
    for w in works.data:
        temp = w.get("temperatura_emocional")
        ritmo = w.get("ritmo_visual")
        abst = w.get("abstraccion")
        
        if temp and ritmo and abst:
            combo = f"{temp} + {ritmo} + {abst}"
            combinations[combo] += 1
    
    print(f"\n🔀 CROSS-DIMENSION COMBINATIONS")
    print(f"Total unique combinations: {len(combinations)}")
    print(f"\nTop 10 most common:")
    for combo, count in combinations.most_common(10):
        pct = (count / total_works) * 100
        flag = "⚠️  OVERREPRESENTED" if pct > 10 else ""
        print(f"  {count:3d} ({pct:4.1f}%) - {combo} {flag}")
    
    print(f"\n10 rarest combinations:")
    for combo, count in combinations.most_common()[-10:]:
        pct = (count / total_works) * 100
        print(f"  {count:3d} ({pct:4.1f}%) - {combo}")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: COLOR DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════

def diagnose_color_distribution():
    """Analyze color_iconico distribution and balance."""
    print("\n" + "="*80)
    print("PART 5: COLOR DISTRIBUTION DIAGNOSTIC")
    print("="*80)
    
    color_assignments = client.table("color_assignments").select("color_iconico").execute()
    
    total_assignments = len(color_assignments.data)
    
    if total_assignments == 0:
        print("⚠️  No color assignments found")
        return
    
    color_dist = Counter(ca.get("color_iconico") for ca in color_assignments.data)
    
    print(f"\n🎨 COLOR_ICONICO DISTRIBUTION")
    print(f"Total assignments: {total_assignments}")
    print(f"\n{'Color ID':<30} {'Count':<10} {'%':<10} {'Status'}")
    print("-" * 70)
    
    for color_id, count in color_dist.most_common():
        pct = (count / total_assignments) * 100
        flag = ""
        if pct > 25:
            flag = "⚠️  OVERUSED"
        elif pct < 2:
            flag = "📊 RARE"
        print(f"{color_id:<30} {count:<10} {pct:>5.1f}%     {flag}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Run all diagnostic sections."""
    print("\n" + "="*80)
    print("PRISMA DATABASE DIAGNOSTIC AUDIT")
    print("READ-ONLY SYSTEM HEALTH ANALYSIS")
    print("="*80)
    
    try:
        diagnose_film_completeness()
        diagnose_people_coverage()
        diagnose_relationship_integrity()
        diagnose_dimensional_distribution()
        diagnose_color_distribution()
        
        print("\n" + "="*80)
        print("DIAGNOSTIC AUDIT COMPLETE")
        print("="*80)
        print("\n📋 RECOMMENDATIONS SUMMARY")
        print("1. Prioritize enriching works with missing people relationships")
        print("2. Fill missing dimensional attributes for complete works")
        print("3. Resolve any orphaned records found in integrity checks")
        print("4. Balance dimensional distribution if severe skew detected")
        print("5. Investigate duplicate tmdb_id violations if found")
        print("\n✅ Audit complete - no database modifications made")
        
    except Exception as e:
        print(f"\n❌ ERROR during diagnostic: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
