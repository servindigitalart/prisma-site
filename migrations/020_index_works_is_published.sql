-- Migration: add indexes to fix slow queries in ingest_agent.py
-- Run this in the Supabase SQL editor or via psql.

-- 1. Partial index for fast draft-works fetch (--retry-drafts)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_works_drafts
  ON public.works (id, tmdb_id)
  WHERE is_published = FALSE;

-- 2. Plain boolean index for general is_published filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_works_is_published
  ON public.works (is_published);

-- 3. Index on ranking_scores(entity_id) — currently causes 5s+ timeouts
--    in run_verification() and recompute_film_scores.py
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ranking_scores_entity_id
  ON public.ranking_scores (entity_id);
