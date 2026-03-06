-- ══════════════════════════════════════════════════════════════════════════════
-- PRISMA DIMENSION PAGES DIAGNOSTIC SQL
-- ══════════════════════════════════════════════════════════════════════════════
-- Purpose: Diagnose why dimension category pages (ritmo, temperatura, abstraccion)
--          show 0 films even though Barbie has dimension data.
--
-- Run these queries in Supabase SQL Editor to identify the issue.
-- ══════════════════════════════════════════════════════════════════════════════

-- ─── 1. Check works table ─────────────────────────────────────────────────────
-- Verify which works exist and their publication status
SELECT 
  id, 
  title, 
  year,
  is_published 
FROM works 
ORDER BY id
LIMIT 20;

-- Expected: Should see work_barbie_2023, work_marie-antoinette_2006, etc.
-- Check: is_published should be TRUE for films to appear

-- ─── 2. Check color_assignments table ─────────────────────────────────────────
-- Verify dimension data exists and review_status
SELECT 
  work_id,
  color_iconico,
  ritmo_visual,
  temperatura_emocional,
  grado_abstraccion,
  review_status,
  tier
FROM color_assignments 
ORDER BY work_id
LIMIT 20;

-- Expected: Should see Barbie with:
--   - ritmo_visual = 'moderado_balanceado'
--   - temperatura_emocional = 'calido_apasionado'  
--   - grado_abstraccion = 'estilizado'
--   - review_status = 'approved'

-- ─── 3. Check if works_with_color view includes dimension columns ─────────────
-- This view is used by some queries - check what columns it has
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_name = 'works_with_color'
ORDER BY ordinal_position;

-- Expected issue: works_with_color may NOT have:
--   - ritmo_visual
--   - temperatura_emocional
--   - grado_abstraccion
-- If missing, queries using this view will return 0 results

-- ─── 4. Test actual dimension query ───────────────────────────────────────────
-- Simulate the query used by getWorksByRhythm()
SELECT 
  ca.work_id,
  ca.ritmo_visual,
  ca.color_iconico,
  ca.tier,
  ca.numeric_score,
  w.id,
  w.title,
  w.year,
  w.is_published
FROM color_assignments ca
INNER JOIN works w ON w.id = ca.work_id
WHERE ca.ritmo_visual = 'moderado_balanceado'
  AND w.is_published = true
  AND ca.review_status = 'approved'
ORDER BY ca.numeric_score DESC
LIMIT 10;

-- Expected: Should return Barbie if data exists and is_published = true
-- If 0 results, check:
--   a) is_published = false (Barbie not published yet)
--   b) ritmo_visual is NULL or different value
--   c) review_status != 'approved'

-- ─── 5. Test without is_published filter ──────────────────────────────────────
-- Development fallback query (shows all films, published or not)
SELECT 
  ca.work_id,
  ca.ritmo_visual,
  w.title,
  w.year,
  w.is_published,
  ca.review_status
FROM color_assignments ca
INNER JOIN works w ON w.id = ca.work_id
WHERE ca.ritmo_visual = 'moderado_balanceado'
ORDER BY ca.numeric_score DESC
LIMIT 10;

-- This should show Barbie even if is_published = false

-- ─── 6. Check all unique dimension values ─────────────────────────────────────
-- See what dimension values actually exist in the database
SELECT DISTINCT ritmo_visual, COUNT(*) as count
FROM color_assignments
WHERE ritmo_visual IS NOT NULL
GROUP BY ritmo_visual
ORDER BY count DESC;

SELECT DISTINCT temperatura_emocional, COUNT(*) as count
FROM color_assignments
WHERE temperatura_emocional IS NOT NULL
GROUP BY temperatura_emocional
ORDER BY count DESC;

SELECT DISTINCT grado_abstraccion, COUNT(*) as count
FROM color_assignments
WHERE grado_abstraccion IS NOT NULL
GROUP BY grado_abstraccion
ORDER BY count DESC;

-- Expected: Should see the values from Barbie's data
-- If 0 rows, dimension columns are empty

-- ══════════════════════════════════════════════════════════════════════════════
-- DIAGNOSIS SUMMARY
-- ══════════════════════════════════════════════════════════════════════════════
--
-- Most likely cause: is_published = FALSE for Barbie
--   → Fix: Update works SET is_published = TRUE WHERE id = 'work_barbie_2023'
--   → OR: Modify getWorksByRhythm() to accept both published and unpublished
--
-- Secondary cause: works_with_color view doesn't include dimension columns
--   → Fix: Recreate the view with dimension columns (see postgres_schema.sql)
--
-- Verify fix worked:
--   Run query #4 again - should return Barbie
--   Visit /ritmo/moderado-balanceado - should show 1 película
-- ══════════════════════════════════════════════════════════════════════════════
