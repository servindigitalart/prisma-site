-- ═══════════════════════════════════════════════════════════════════════════════
-- PRISMA DATABASE DIAGNOSTIC AUDIT
-- READ-ONLY SQL queries for system health analysis
-- ═══════════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────────
-- PART 1: FILM COMPLETENESS DIAGNOSTIC
-- ───────────────────────────────────────────────────────────────────────────────

\echo '════════════════════════════════════════════════════════════════════════════════'
\echo 'PART 1: FILM COMPLETENESS DIAGNOSTIC'
\echo '════════════════════════════════════════════════════════════════════════════════'

-- Overall statistics
\echo '\n📊 OVERALL STATISTICS'
SELECT 
    COUNT(*) as total_works,
    COUNT(*) FILTER (WHERE synopsis IS NOT NULL) as has_synopsis,
    COUNT(*) FILTER (WHERE release_year IS NOT NULL) as has_year,
    COUNT(*) FILTER (WHERE runtime IS NOT NULL) as has_runtime,
    COUNT(*) FILTER (WHERE poster_url IS NOT NULL) as has_poster,
    COUNT(*) FILTER (WHERE backdrop_url IS NOT NULL) as has_backdrop,
    COUNT(*) FILTER (WHERE temperatura_emocional IS NOT NULL) as has_temperatura,
    COUNT(*) FILTER (WHERE ritmo_visual IS NOT NULL) as has_ritmo,
    COUNT(*) FILTER (WHERE abstraccion IS NOT NULL) as has_abstraccion
FROM works;

-- Completeness percentages
\echo '\n📉 COMPLETENESS BREAKDOWN (%)'
SELECT 
    ROUND(100.0 * COUNT(*) FILTER (WHERE synopsis IS NULL) / COUNT(*), 1) as "Missing Synopsis %",
    ROUND(100.0 * COUNT(*) FILTER (WHERE release_year IS NULL) / COUNT(*), 1) as "Missing Year %",
    ROUND(100.0 * COUNT(*) FILTER (WHERE runtime IS NULL) / COUNT(*), 1) as "Missing Runtime %",
    ROUND(100.0 * COUNT(*) FILTER (WHERE poster_url IS NULL) / COUNT(*), 1) as "Missing Poster %",
    ROUND(100.0 * COUNT(*) FILTER (WHERE backdrop_url IS NULL) / COUNT(*), 1) as "Missing Backdrop %",
    ROUND(100.0 * COUNT(*) FILTER (WHERE temperatura_emocional IS NULL) / COUNT(*), 1) as "Missing Temp %",
    ROUND(100.0 * COUNT(*) FILTER (WHERE ritmo_visual IS NULL) / COUNT(*), 1) as "Missing Ritmo %",
    ROUND(100.0 * COUNT(*) FILTER (WHERE abstraccion IS NULL) / COUNT(*), 1) as "Missing Abstrac %"
FROM works;

-- Works missing people relationships
\echo '\n👥 PEOPLE RELATIONSHIPS'
SELECT 
    COUNT(DISTINCT w.id) as total_works,
    COUNT(DISTINCT w.id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM work_people wp WHERE wp.work_id = w.id
        )
    ) as works_without_people,
    ROUND(100.0 * COUNT(DISTINCT w.id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM work_people wp WHERE wp.work_id = w.id
        )
    ) / COUNT(DISTINCT w.id), 1) as "Missing People %"
FROM works w;

-- Works missing studios
\echo '\n🏢 STUDIO RELATIONSHIPS'
SELECT 
    COUNT(DISTINCT w.id) as total_works,
    COUNT(DISTINCT w.id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM work_studios ws WHERE ws.work_id = w.id
        )
    ) as works_without_studios,
    ROUND(100.0 * COUNT(DISTINCT w.id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM work_studios ws WHERE ws.work_id = w.id
        )
    ) / COUNT(DISTINCT w.id), 1) as "Missing Studios %"
FROM works w;

-- Works missing color assignments
\echo '\n🎨 COLOR ASSIGNMENTS'
SELECT 
    COUNT(DISTINCT w.id) as total_works,
    COUNT(DISTINCT w.id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM color_assignments ca WHERE ca.work_id = w.id
        )
    ) as works_without_color,
    ROUND(100.0 * COUNT(DISTINCT w.id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM color_assignments ca WHERE ca.work_id = w.id
        )
    ) / COUNT(DISTINCT w.id), 1) as "Missing Color %"
FROM works w;

-- Top 10 most incomplete works
\echo '\n❌ TOP 10 MOST INCOMPLETE WORKS'
WITH work_completeness AS (
    SELECT 
        w.id,
        w.title,
        w.release_year,
        (
            CASE WHEN w.synopsis IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN w.release_year IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN w.runtime IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN EXISTS(SELECT 1 FROM work_studios ws WHERE ws.work_id = w.id) THEN 1 ELSE 0 END +
            CASE WHEN EXISTS(SELECT 1 FROM work_people wp WHERE wp.work_id = w.id) THEN 1 ELSE 0 END +
            CASE WHEN EXISTS(SELECT 1 FROM color_assignments ca WHERE ca.work_id = w.id) THEN 1 ELSE 0 END +
            CASE WHEN w.temperatura_emocional IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN w.ritmo_visual IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN w.abstraccion IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN w.poster_url IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN w.backdrop_url IS NOT NULL THEN 1 ELSE 0 END
        ) as completeness_score,
        ARRAY_REMOVE(ARRAY[
            CASE WHEN w.synopsis IS NULL THEN 'No synopsis' END,
            CASE WHEN w.release_year IS NULL THEN 'No year' END,
            CASE WHEN w.runtime IS NULL THEN 'No runtime' END,
            CASE WHEN NOT EXISTS(SELECT 1 FROM work_studios ws WHERE ws.work_id = w.id) THEN 'No studios' END,
            CASE WHEN NOT EXISTS(SELECT 1 FROM work_people wp WHERE wp.work_id = w.id) THEN 'No people' END,
            CASE WHEN NOT EXISTS(SELECT 1 FROM color_assignments ca WHERE ca.work_id = w.id) THEN 'No color' END,
            CASE WHEN w.temperatura_emocional IS NULL THEN 'No temperatura' END,
            CASE WHEN w.ritmo_visual IS NULL THEN 'No ritmo' END,
            CASE WHEN w.abstraccion IS NULL THEN 'No abstraccion' END,
            CASE WHEN w.poster_url IS NULL THEN 'No poster' END,
            CASE WHEN w.backdrop_url IS NULL THEN 'No backdrop' END
        ], NULL) as missing_fields
    FROM works w
)
SELECT 
    LEFT(title, 50) as title,
    release_year as year,
    ROUND(100.0 * completeness_score / 11, 1) as "Complete %",
    array_to_string(missing_fields, ', ') as issues
FROM work_completeness
ORDER BY completeness_score ASC, title
LIMIT 10;


-- ───────────────────────────────────────────────────────────────────────────────
-- PART 2: PEOPLE DIAGNOSTIC
-- ───────────────────────────────────────────────────────────────────────────────

\echo '\n════════════════════════════════════════════════════════════════════════════════'
\echo 'PART 2: PEOPLE COVERAGE DIAGNOSTIC'
\echo '════════════════════════════════════════════════════════════════════════════════'

-- People statistics
\echo '\n📊 PEOPLE STATISTICS'
SELECT 
    COUNT(*) as total_people,
    COUNT(*) FILTER (WHERE profile_url IS NULL) as missing_image,
    ROUND(100.0 * COUNT(*) FILTER (WHERE profile_url IS NULL) / COUNT(*), 1) as "Missing Image %",
    COUNT(*) FILTER (WHERE biography IS NULL OR biography = '') as missing_bio,
    ROUND(100.0 * COUNT(*) FILTER (WHERE biography IS NULL OR biography = '') / COUNT(*), 1) as "Missing Bio %",
    COUNT(*) FILTER (WHERE tmdb_id IS NULL) as missing_tmdb,
    ROUND(100.0 * COUNT(*) FILTER (WHERE tmdb_id IS NULL) / COUNT(*), 1) as "Missing TMDB %"
FROM people;

-- Orphaned people (no work relationships)
\echo '\n⚠️  ORPHANED PEOPLE (no work relationships)'
SELECT 
    COUNT(*) as orphaned_people,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM people), 1) as "Orphaned %"
FROM people p
WHERE NOT EXISTS (
    SELECT 1 FROM work_people wp WHERE wp.person_id = p.id
);

-- Duplicate tmdb_id check
\echo '\n🔍 DUPLICATE tmdb_id CHECK'
SELECT 
    tmdb_id,
    COUNT(*) as duplicate_count,
    array_agg(id) as person_ids
FROM people
WHERE tmdb_id IS NOT NULL
GROUP BY tmdb_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;

-- Works with director missing image
\echo '\n⚠️  WORKS WHERE DIRECTOR HAS NO IMAGE'
SELECT 
    w.title,
    w.release_year,
    p.name as director_name
FROM works w
JOIN work_people wp ON w.id = wp.work_id AND wp.role = 'director'
JOIN people p ON wp.person_id = p.id
WHERE p.profile_url IS NULL
ORDER BY w.release_year DESC
LIMIT 10;

-- Works with main actor missing image
\echo '\n⚠️  WORKS WHERE LEAD ACTOR HAS NO IMAGE'
WITH ranked_actors AS (
    SELECT 
        wp.work_id,
        wp.person_id,
        ROW_NUMBER() OVER (PARTITION BY wp.work_id ORDER BY wp.billing_order NULLS LAST) as rn
    FROM work_people wp
    WHERE wp.role = 'actor'
)
SELECT 
    w.title,
    w.release_year,
    p.name as actor_name
FROM works w
JOIN ranked_actors ra ON w.id = ra.work_id AND ra.rn = 1
JOIN people p ON ra.person_id = p.id
WHERE p.profile_url IS NULL
ORDER BY w.release_year DESC
LIMIT 10;


-- ───────────────────────────────────────────────────────────────────────────────
-- PART 3: RELATIONSHIP INTEGRITY
-- ───────────────────────────────────────────────────────────────────────────────

\echo '\n════════════════════════════════════════════════════════════════════════════════'
\echo 'PART 3: RELATIONSHIP INTEGRITY DIAGNOSTIC'
\echo '════════════════════════════════════════════════════════════════════════════════'

-- work_people → works integrity
\echo '\n🔗 work_people → works INTEGRITY'
SELECT 
    COUNT(*) as total_work_people_rows,
    COUNT(*) FILTER (
        WHERE NOT EXISTS (SELECT 1 FROM works w WHERE w.id = work_people.work_id)
    ) as orphaned_work_refs
FROM work_people;

-- work_people → people integrity
\echo '\n🔗 work_people → people INTEGRITY'
SELECT 
    COUNT(*) as total_work_people_rows,
    COUNT(*) FILTER (
        WHERE NOT EXISTS (SELECT 1 FROM people p WHERE p.id = work_people.person_id)
    ) as orphaned_person_refs
FROM work_people;

-- work_studios → works integrity
\echo '\n🔗 work_studios → works INTEGRITY'
SELECT 
    COUNT(*) as total_work_studios_rows,
    COUNT(*) FILTER (
        WHERE NOT EXISTS (SELECT 1 FROM works w WHERE w.id = work_studios.work_id)
    ) as orphaned_work_refs
FROM work_studios;

-- work_studios → studios integrity
\echo '\n🔗 work_studios → studios INTEGRITY'
SELECT 
    COUNT(*) as total_work_studios_rows,
    COUNT(*) FILTER (
        WHERE NOT EXISTS (SELECT 1 FROM studios s WHERE s.id = work_studios.studio_id)
    ) as orphaned_studio_refs
FROM work_studios;

-- color_assignments → works integrity
\echo '\n🔗 color_assignments → works INTEGRITY'
SELECT 
    COUNT(*) as total_color_assignments,
    COUNT(*) FILTER (
        WHERE NOT EXISTS (SELECT 1 FROM works w WHERE w.id = color_assignments.work_id)
    ) as orphaned_work_refs
FROM color_assignments;


-- ───────────────────────────────────────────────────────────────────────────────
-- PART 4: DIMENSIONAL DISTRIBUTION
-- ───────────────────────────────────────────────────────────────────────────────

\echo '\n════════════════════════════════════════════════════════════════════════════════'
\echo 'PART 4: DIMENSIONAL DISTRIBUTION DIAGNOSTIC'
\echo '════════════════════════════════════════════════════════════════════════════════'

-- Temperatura Emocional distribution
\echo '\n🌡️  TEMPERATURA EMOCIONAL DISTRIBUTION'
SELECT 
    temperatura_emocional,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage,
    CASE 
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) > 35 THEN '⚠️  DOMINATES'
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) < 5 THEN '📊 RARE'
        ELSE ''
    END as status
FROM works
WHERE temperatura_emocional IS NOT NULL
GROUP BY temperatura_emocional
ORDER BY count DESC;

-- Ritmo Visual distribution
\echo '\n⚡ RITMO VISUAL DISTRIBUTION'
SELECT 
    ritmo_visual,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage,
    CASE 
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) > 35 THEN '⚠️  DOMINATES'
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) < 5 THEN '📊 RARE'
        ELSE ''
    END as status
FROM works
WHERE ritmo_visual IS NOT NULL
GROUP BY ritmo_visual
ORDER BY count DESC;

-- Abstracción distribution
\echo '\n🎨 ABSTRACCIÓN DISTRIBUTION'
SELECT 
    abstraccion,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage,
    CASE 
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) > 35 THEN '⚠️  DOMINATES'
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) < 5 THEN '📊 RARE'
        ELSE ''
    END as status
FROM works
WHERE abstraccion IS NOT NULL
GROUP BY abstraccion
ORDER BY count DESC;

-- Cross-dimension combinations (top 15)
\echo '\n🔀 CROSS-DIMENSION COMBINATIONS (Top 15)'
SELECT 
    temperatura_emocional || ' + ' || ritmo_visual || ' + ' || abstraccion as combination,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage,
    CASE 
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) > 10 THEN '⚠️  OVERREPRESENTED'
        ELSE ''
    END as status
FROM works
WHERE temperatura_emocional IS NOT NULL 
  AND ritmo_visual IS NOT NULL 
  AND abstraccion IS NOT NULL
GROUP BY temperatura_emocional, ritmo_visual, abstraccion
ORDER BY count DESC
LIMIT 15;

-- Rarest combinations
\echo '\n📊 RAREST COMBINATIONS (Bottom 10)'
SELECT 
    temperatura_emocional || ' + ' || ritmo_visual || ' + ' || abstraccion as combination,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage
FROM works
WHERE temperatura_emocional IS NOT NULL 
  AND ritmo_visual IS NOT NULL 
  AND abstraccion IS NOT NULL
GROUP BY temperatura_emocional, ritmo_visual, abstraccion
ORDER BY count ASC
LIMIT 10;


-- ───────────────────────────────────────────────────────────────────────────────
-- PART 5: COLOR DISTRIBUTION
-- ───────────────────────────────────────────────────────────────────────────────

\echo '\n════════════════════════════════════════════════════════════════════════════════'
\echo 'PART 5: COLOR DISTRIBUTION DIAGNOSTIC'
\echo '════════════════════════════════════════════════════════════════════════════════'

-- Color iconico distribution
\echo '\n🎨 COLOR_ICONICO DISTRIBUTION'
SELECT 
    color_iconico,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage,
    CASE 
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) > 25 THEN '⚠️  OVERUSED'
        WHEN ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) < 2 THEN '📊 RARE'
        ELSE ''
    END as status
FROM color_assignments
GROUP BY color_iconico
ORDER BY count DESC;


-- ───────────────────────────────────────────────────────────────────────────────
-- SUMMARY
-- ───────────────────────────────────────────────────────────────────────────────

\echo '\n════════════════════════════════════════════════════════════════════════════════'
\echo 'DIAGNOSTIC AUDIT COMPLETE'
\echo '════════════════════════════════════════════════════════════════════════════════'
\echo ''
\echo '📋 RECOMMENDATIONS SUMMARY'
\echo '1. Prioritize enriching works with missing people relationships'
\echo '2. Fill missing dimensional attributes for complete works'
\echo '3. Resolve any orphaned records found in integrity checks'
\echo '4. Balance dimensional distribution if severe skew detected'
\echo '5. Investigate duplicate tmdb_id violations if found'
\echo ''
\echo '✅ Audit complete - no database modifications made'
\echo ''
