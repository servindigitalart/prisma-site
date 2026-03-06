-- ══════════════════════════════════════════════════════════════════════════════
-- PRISMA JUNCTION TABLES DIAGNOSTIC SQL
-- ══════════════════════════════════════════════════════════════════════════════
-- Purpose: Diagnose why studio and people pages show no films.
--          Junction tables (work_studios, work_people) may be empty.
--
-- Run these queries in Supabase SQL Editor to identify the issue.
-- ══════════════════════════════════════════════════════════════════════════════

-- ─── 1. Check junction table row counts ───────────────────────────────────────
SELECT 'works' as table_name, COUNT(*) as row_count FROM works
UNION ALL
SELECT 'color_assignments', COUNT(*) FROM color_assignments
UNION ALL
SELECT 'work_studios', COUNT(*) FROM work_studios
UNION ALL
SELECT 'work_people', COUNT(*) FROM work_people
UNION ALL
SELECT 'studios', COUNT(*) FROM studios
UNION ALL
SELECT 'people', COUNT(*) FROM people;

-- Expected issue: work_studios and work_people will show 0 rows

-- ─── 2. Check studio existence ────────────────────────────────────────────────
SELECT id, name, country 
FROM studios 
WHERE id IN (
  'studio_pricel',
  'studio_columbia-pictures', 
  'studio_american-zoetrope',
  'studio_tfc'
);

-- ─── 3. Sample query after population ─────────────────────────────────────────
SELECT 
  ws.studio_id,
  w.id,
  w.title,
  w.year
FROM work_studios ws
INNER JOIN works w ON w.id = ws.work_id
WHERE ws.studio_id = 'studio_columbia-pictures';

-- ROOT CAUSE: Junction tables empty - needs migrate_to_db.py --execute
