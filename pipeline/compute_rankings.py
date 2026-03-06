"""
Compute ranking scores for all works in Supabase.
Formula: imdb_rating * 10 + (criterion_title * 5) + (mubi_title * 3)
Run this whenever new films are added.
"""
import os
from dotenv import load_dotenv
load_dotenv('/Users/servinemilio/Documents/REPOS/prisma-site/.env.local')
from supabase import create_client

db = create_client(os.environ['PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

works = db.table('works').select('id, title, imdb_rating, criterion_title, mubi_title').execute()

scores = []
for w in works.data:
    score = 0
    score += (w.get('imdb_rating') or 0) * 10
    score += 5 if w.get('criterion_title') else 0
    score += 3 if w.get('mubi_title') else 0
    scores.append({
        'entity_id': w['id'],
        'entity_type': 'work',
        'context': 'global',
        'score': round(score, 2),
        'rank': 0  # will update after sorting
    })

scores.sort(key=lambda x: x['score'], reverse=True)
for i, s in enumerate(scores):
    s['rank'] = i + 1

result = db.table('ranking_scores').upsert(scores).execute()
print(f"✅ Computed rankings for {len(scores)} films")
for s in scores[:10]:
    print(f"  #{s['rank']} — score {s['score']} — {s['entity_id']}")
