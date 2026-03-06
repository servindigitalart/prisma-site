#!/usr/bin/env python3
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env.local")
supabase = create_client(os.getenv("PUBLIC_SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# Check all color_assignments (not just approved)
response = supabase.table("color_assignments").select("*").limit(50).execute()
print(f"Total color_assignments: {len(response.data)}")
print(f"Review statuses:")
for status in set(r.get("review_status") for r in response.data):
    count = sum(1 for r in response.data if r.get("review_status") == status)
    print(f"  {status}: {count}")

print("\nDimension data check:")
with_dims = [r for r in response.data if r.get("ritmo_visual") or r.get("temperatura_emocional") or r.get("grado_abstraccion")]
print(f"Assignments with ANY dimension data: {len(with_dims)}")

if with_dims:
    print("\nSample with dimensions:")
    for r in with_dims[:3]:
        print(f"  Work: {r['work_id']}")
        print(f"    Status: {r.get('review_status')}")
        print(f"    Ritmo: {r.get('ritmo_visual')}")
        print(f"    Temp: {r.get('temperatura_emocional')}")
        print(f"    Abs: {r.get('grado_abstraccion')}")
