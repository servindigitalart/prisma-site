#!/usr/bin/env python3
"""
catalog_diagnostic.py
─────────────────────
Production-level READ-ONLY diagnostic for PRISMA database.

USAGE:
    python3 pipeline/catalog_diagnostic.py

REQUIRES:
    SUPABASE_URL and SUPABASE_SERVICE_KEY in environment
"""

import os
import sys
from collections import Counter

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
except ImportError:
    pass

def _require(package):
    try:
        __import__(package)
    except ImportError:
        print(f"✗ Missing package: {package}")
        print(f"  Install: pip install {package}\n")
        sys.exit(1)

_require("supabase")
from supabase import create_client

# ─── Setup ────────────────────────────────────────────────────────────────────

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
    sys.exit(1)

client = create_client(url, key)

def fetch_all(table: str, columns: str = "*", filters: dict | None = None) -> list:
    """Fetch all rows from a Supabase table, bypassing the default 1000-row limit."""
    PAGE = 1000
    offset = 0
    rows: list = []
    while True:
        q = client.table(table).select(columns)
        if filters:
            for col, val in filters.items():
                q = q.eq(col, val)
        resp = q.range(offset, offset + PAGE - 1).execute()
        if not resp.data:
            break
        rows.extend(resp.data)
        if len(resp.data) < PAGE:
            break
        offset += PAGE
    return rows

print("=" * 70)
print("PRISMA CATALOG DIAGNOSTIC")
print("=" * 70)
print()

# ─── WORK COMPLETENESS ────────────────────────────────────────────────────────

print("=" * 70)
print("📊 WORK COMPLETENESS")
print("=" * 70)
print()

works_data = fetch_all("works", "id,title,synopsis,duration_min")
total_works = len(works_data)

color_assigns_data = fetch_all("color_assignments", "work_id")
works_with_colors = {ca["work_id"] for ca in color_assigns_data}

work_people_data = fetch_all("work_people", "work_id")
works_with_people = {wp["work_id"] for wp in work_people_data}

work_studios_data = fetch_all("work_studios", "work_id")
works_with_studios = {ws["work_id"] for ws in work_studios_data}

missing_colors = [w for w in works_data if w["id"] not in works_with_colors]
missing_people = [w for w in works_data if w["id"] not in works_with_people]
missing_studios = [w for w in works_data if w["id"] not in works_with_studios]
missing_synopsis = [w for w in works_data if not w.get("synopsis")]
missing_duration = [w for w in works_data if not w.get("duration_min")]

print(f"Total works: {total_works}")
print()
print(f"{'❌' if missing_colors else '✅'} Without color_assignments: {len(missing_colors)}")
print(f"{'❌' if missing_people else '✅'} Without people: {len(missing_people)}")
print(f"{'❌' if missing_studios else '✅'} Without studios: {len(missing_studios)}")
print(f"{'⚠️ ' if missing_synopsis else '✅'} Missing synopsis: {len(missing_synopsis)}")
print(f"{'⚠️ ' if missing_duration else '✅'} Missing duration_min: {len(missing_duration)}")
print()

# Calculate completeness score
work_scores = []
for w in works_data:
    score = 0
    if w["id"] in works_with_colors:
        score += 1
    if w["id"] in works_with_people:
        score += 1
    if w["id"] in works_with_studios:
        score += 1
    if w.get("synopsis"):
        score += 1
    if w.get("duration_min"):
        score += 1
    work_scores.append((w["id"], w.get("title", "Unknown"), score))

work_scores.sort(key=lambda x: x[2])

if work_scores:
    print("Top 10 least complete works:")
    for work_id, title, score in work_scores[:10]:
        pct = (score / 5) * 100
        print(f"  {score}/5 ({pct:3.0f}%) - {title[:50]}")
print()

# ─── PEOPLE COVERAGE ──────────────────────────────────────────────────────────

print("=" * 70)
print("👥 PEOPLE COVERAGE")
print("=" * 70)
print()

people_data = fetch_all("people", "id,profile_path,bio")
total_people = len(people_data)

no_image = [p for p in people_data if not p.get("profile_path")]
no_bio = [p for p in people_data if not p.get("bio")]

pct_no_image = (len(no_image) / total_people * 100) if total_people > 0 else 0
pct_no_bio = (len(no_bio) / total_people * 100) if total_people > 0 else 0

print(f"Total people: {total_people}")
print(f"{'⚠️ ' if pct_no_image > 20 else '📊'} Without profile image: {len(no_image)} ({pct_no_image:.1f}%)")
print(f"{'⚠️ ' if pct_no_bio > 20 else '📊'} Without biography: {len(no_bio)} ({pct_no_bio:.1f}%)")
print()

# Directors without images
directors_wp_data = fetch_all("work_people", "work_id,person_id", {"role": "director"})
director_ids = {wp["person_id"] for wp in directors_wp_data}
people_map = {p["id"]: p for p in people_data}

directors_no_image = []
for dir_id in director_ids:
    if dir_id in people_map and not people_map[dir_id].get("profile_path"):
        for wp in directors_wp_data:
            if wp["person_id"] == dir_id:
                directors_no_image.append(wp["work_id"])
                break

unique_works_no_dir_image = len(set(directors_no_image))
print(f"{'⚠️ ' if unique_works_no_dir_image > 0 else '✅'} Works where director has no image: {unique_works_no_dir_image}")

# Works with <5 people
people_count_per_work = Counter(wp["work_id"] for wp in work_people_data)
works_few_people = [wid for wid, count in people_count_per_work.items() if count < 5]
print(f"{'⚠️ ' if works_few_people else '✅'} Works with <5 people: {len(works_few_people)}")
print()

# ─── DIMENSION DISTRIBUTION ───────────────────────────────────────────────────

print("=" * 70)
print("📐 DIMENSION DISTRIBUTION")
print("=" * 70)
print()

ca_data = fetch_all("color_assignments", "color_iconico,temperatura_emocional,ritmo_visual,grado_abstraccion")
total_ca = len(ca_data)

temp_counts = Counter(c.get("temperatura_emocional") for c in ca_data if c.get("temperatura_emocional"))
ritmo_counts = Counter(c.get("ritmo_visual") for c in ca_data if c.get("ritmo_visual"))
abstraccion_counts = Counter(c.get("grado_abstraccion") for c in ca_data if c.get("grado_abstraccion"))

def print_dimension(name, counts, total):
    print(f"{name}:")
    if not counts:
        print("  ❌ No data")
        return
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for val, count in sorted_counts:
        pct = (count / total * 100) if total > 0 else 0
        flag = "⚠️ " if pct > 35 or pct < 5 else "📊"
        print(f"  {flag} {val:25s}: {count:4d} ({pct:5.1f}%)")
    print()

print_dimension("temperatura_emocional", temp_counts, total_ca)
print_dimension("ritmo_visual", ritmo_counts, total_ca)
print_dimension("grado_abstraccion", abstraccion_counts, total_ca)

# ─── COLOR DISTRIBUTION ───────────────────────────────────────────────────────

print("=" * 70)
print("🎨 COLOR DISTRIBUTION")
print("=" * 70)
print()

color_counts = Counter(c.get("color_iconico") for c in ca_data if c.get("color_iconico"))
total_colors = sum(color_counts.values())

print(f"color_iconico:")
if not color_counts:
    print("  ❌ No color data")
else:
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    for color, count in sorted_colors:
        pct = (count / total_colors * 100) if total_colors > 0 else 0
        if pct > 25:
            flag = "⚠️ "
        elif pct < 2:
            flag = "⚠️ "
        else:
            flag = "📊"
        print(f"  {flag} {color:25s}: {count:4d} ({pct:5.1f}%)")
print()

# ─── CROSS-DIMENSION COMBINATIONS ─────────────────────────────────────────────

print("=" * 70)
print("🔀 CROSS-DIMENSION COMBINATIONS")
print("=" * 70)
print()

combos = Counter()
for c in ca_data:
    temp = c.get("temperatura_emocional", "unknown")
    ritmo = c.get("ritmo_visual", "unknown")
    abstr = c.get("grado_abstraccion", "unknown")
    if temp != "unknown" and ritmo != "unknown" and abstr != "unknown":
        combos[(temp, ritmo, abstr)] += 1

print("Top 10 most frequent (temperatura + ritmo + abstraccion):")
if not combos:
    print("  ❌ No complete dimension data")
else:
    for (temp, ritmo, abstr), count in combos.most_common(10):
        pct = (count / total_ca * 100) if total_ca > 0 else 0
        print(f"  📊 {count:3d} ({pct:4.1f}%) - {temp} × {ritmo} × {abstr}")
print()

print("=" * 70)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 70)
