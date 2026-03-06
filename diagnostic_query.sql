-- Color assignments with dimension data
SELECT 
  ca.work_id,
  ca.color_iconico,
  ca.ritmo_visual,
  ca.temperatura_emocional,
  ca.grado_abstraccion,
  w.title,
  w.is_published
FROM color_assignments ca
JOIN works w ON ca.work_id = w.id
WHERE ca.review_status = 'approved'
ORDER BY w.title
LIMIT 30;

-- Dimension distribution
SELECT 
  'ritmo_visual' as dimension,
  ritmo_visual as value,
  COUNT(*) as count
FROM color_assignments
WHERE review_status = 'approved'
  AND ritmo_visual IS NOT NULL
GROUP BY ritmo_visual
UNION ALL
SELECT 
  'temperatura_emocional' as dimension,
  temperatura_emocional as value,
  COUNT(*) as count
FROM color_assignments
WHERE review_status = 'approved'
  AND temperatura_emocional IS NOT NULL
GROUP BY temperatura_emocional
UNION ALL
SELECT 
  'grado_abstraccion' as dimension,
  grado_abstraccion as value,
  COUNT(*) as count
FROM color_assignments
WHERE review_status = 'approved'
  AND grado_abstraccion IS NOT NULL
GROUP BY grado_abstraccion
ORDER BY dimension, value;

-- People without profile photos
SELECT id, name, profile_path
FROM people
WHERE profile_path IS NULL
ORDER BY name
LIMIT 20;

-- Top ranked works with scores
SELECT 
  rs.rank,
  rs.score,
  w.id,
  w.title,
  ca.color_iconico
FROM ranking_scores rs
JOIN works w ON rs.entity_id = w.id
LEFT JOIN color_assignments ca ON w.id = ca.work_id AND ca.review_status = 'approved'
WHERE rs.entity_type = 'work'
  AND rs.context = 'global'
ORDER BY rs.rank
LIMIT 10;
