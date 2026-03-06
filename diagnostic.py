#!/usr/bin/env python3
"""
Database diagnostic script - analyzes current state without making changes
"""
import os
from supabase import create_client
from dotenv import load_dotenv
from collections import Counter

load_dotenv(".env.local")

url = os.getenv("PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("ERROR: Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)

print("=" * 80)
print("PRISMA DATABASE DIAGNOSTIC REPORT")
print("=" * 80)
print()

# 1. Color assignments with dimensions
print("1. COLOR ASSIGNMENTS WITH DIMENSION DATA")
print("-" * 80)
response = supabase.table("color_assignments").select(
    "work_id, color_iconico, ritmo_visual, temperatura_emocional, grado_abstraccion, works(title, is_published)"
).eq("review_status", "approved").order("works(title)").limit(30).execute()

total_approved = len(response.data)
with_rhythm = sum(1 for r in response.data if r.get("ritmo_visual"))
with_temp = sum(1 for r in response.data if r.get("temperatura_emocional"))
with_abs = sum(1 for r in response.data if r.get("grado_abstraccion"))

print(f"Total approved color assignments: {total_approved}")
print(f"  - With ritmo_visual: {with_rhythm}")
print(f"  - With temperatura_emocional: {with_temp}")
print(f"  - With grado_abstraccion: {with_abs}")
print()
print("Sample (first 5):")
for item in response.data[:5]:
    work_title = item.get("works", {}).get("title", "Unknown") if item.get("works") else "Unknown"
    print(f"  {work_title}")
    print(f"    Color: {item.get('color_iconico')}")
    print(f"    Ritmo: {item.get('ritmo_visual')}")
    print(f"    Temperatura: {item.get('temperatura_emocional')}")
    print(f"    Abstracción: {item.get('grado_abstraccion')}")
print()

# 2. Dimension distribution
print("2. DIMENSION VALUE DISTRIBUTION")
print("-" * 80)

# Ritmo
rhythms = [r.get("ritmo_visual") for r in response.data if r.get("ritmo_visual")]
rhythm_counts = Counter(rhythms)
print(f"Ritmo Visual ({len(rhythms)} total):")
for value, count in sorted(rhythm_counts.items()):
    print(f"  {value}: {count}")
print()

# Temperatura
temps = [r.get("temperatura_emocional") for r in response.data if r.get("temperatura_emocional")]
temp_counts = Counter(temps)
print(f"Temperatura Emocional ({len(temps)} total):")
for value, count in sorted(temp_counts.items()):
    print(f"  {value}: {count}")
print()

# Abstracción
abs_vals = [r.get("grado_abstraccion") for r in response.data if r.get("grado_abstraccion")]
abs_counts = Counter(abs_vals)
print(f"Grado de Abstracción ({len(abs_vals)} total):")
for value, count in sorted(abs_counts.items()):
    print(f"  {value}: {count}")
print()

# 3. People without photos
print("3. PEOPLE WITHOUT PROFILE PHOTOS")
print("-" * 80)
people_response = supabase.table("people").select("id, name, profile_path").is_("profile_path", "null").order("name").limit(20).execute()
print(f"People without photos: {len(people_response.data)} (showing first 20)")
for person in people_response.data[:10]:
    print(f"  - {person['name']}")
print()

# 4. Top ranked works
print("4. TOP RANKED WORKS (SCORE-BASED)")
print("-" * 80)
try:
    ranking_response = supabase.table("ranking_scores").select(
        "rank, score, entity_id"
    ).eq("entity_type", "work").eq("context", "global").order("rank", desc=False).limit(10).execute()
    
    work_ids = [r["entity_id"] for r in ranking_response.data]
    works_response = supabase.table("works").select("id, title").in_("id", work_ids).execute()
    works_map = {w["id"]: w["title"] for w in works_response.data}
    
    print(f"Top 10 ranked films:")
    for item in ranking_response.data:
        entity_id = item.get("entity_id")
        title = works_map.get(entity_id, entity_id)
        rank = item.get("rank", "?")
        score = item.get("score", 0)
        print(f"  #{rank:2d}. {title:40s} (Score: {score:.1f})")
except Exception as e:
    print(f"Error fetching rankings: {e}")
print()

# 5. Color assignments by color_iconico
print("5. COLOR ASSIGNMENTS BY COLOR")
print("-" * 80)
color_response = supabase.table("color_assignments").select("color_iconico").eq("review_status", "approved").execute()
color_counts = Counter([r.get("color_iconico") for r in color_response.data if r.get("color_iconico")])
print(f"Total color assignments: {len(color_response.data)}")
print("Distribution by color:")
for color, count in sorted(color_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {color}: {count}")
print()

# 6. Works with vs without color assignments
print("6. WORKS PUBLICATION STATUS")
print("-" * 80)
works_response = supabase.table("works").select("id, is_published").execute()
total_works = len(works_response.data)
published_works = sum(1 for w in works_response.data if w.get("is_published"))
print(f"Total works: {total_works}")
print(f"Published works: {published_works}")
print(f"Unpublished works: {total_works - published_works}")
print()

print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
