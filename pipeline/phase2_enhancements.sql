-- Phase 2 Database Enhancements
-- 1. Ranking system with weighted signals
-- 2. pSEO review gate check constraint

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. RANKING SYSTEM IMPLEMENTATION
-- ═══════════════════════════════════════════════════════════════════════════

-- Add canon_tier field to color_assignments if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'color_assignments' AND column_name = 'canon_tier'
    ) THEN
        ALTER TABLE color_assignments 
        ADD COLUMN canon_tier TEXT CHECK (canon_tier IN ('criterion', 'mubi_permanent', 'none', NULL));
    END IF;
END $$;

-- Add arthouse_dist field to works if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'works' AND column_name = 'arthouse_dist'
    ) THEN
        ALTER TABLE works 
        ADD COLUMN arthouse_dist TEXT;
    END IF;
END $$;

-- Create ranking_scores table if not exists (matches postgres_schema.sql)
CREATE TABLE IF NOT EXISTS ranking_scores (
    entity_type TEXT NOT NULL CHECK (entity_type IN ('work', 'person', 'studio')),
    entity_id TEXT NOT NULL,
    context TEXT NOT NULL DEFAULT 'global',
    score NUMERIC(10,4) NOT NULL,
    rank INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (entity_type, entity_id, context)
);

CREATE INDEX IF NOT EXISTS idx_rs_score ON ranking_scores(entity_type, context, score DESC);

-- Function to calculate canon tier multiplier
CREATE OR REPLACE FUNCTION get_canon_tier_multiplier(tier TEXT)
RETURNS NUMERIC AS $$
BEGIN
    RETURN CASE 
        WHEN tier = 'criterion' THEN 3.0
        WHEN tier = 'mubi_permanent' THEN 2.5
        ELSE 1.0
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to calculate arthouse distribution score
CREATE OR REPLACE FUNCTION get_arthouse_score(
    criterion_title BOOLEAN,
    mubi_title BOOLEAN,
    arthouse_dist TEXT
)
RETURNS NUMERIC AS $$
DECLARE
    score NUMERIC := 0;
BEGIN
    IF criterion_title THEN score := score + 15; END IF;
    IF mubi_title THEN score := score + 10; END IF;
    
    -- Add points based on arthouse_dist field
    IF arthouse_dist IS NOT NULL THEN
        IF arthouse_dist ILIKE '%criterion%' THEN score := score + 5; END IF;
        IF arthouse_dist ILIKE '%mubi%' THEN score := score + 3; END IF;
        IF arthouse_dist ILIKE '%janus%' THEN score := score + 8; END IF;
    END IF;
    
    RETURN LEAST(score, 25);  -- Cap at 25 points
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to refresh ranking scores for works
CREATE OR REPLACE FUNCTION refresh_work_rankings()
RETURNS void AS $$
BEGIN
    -- Delete existing work rankings
    DELETE FROM ranking_scores WHERE entity_type = 'work';
    
    -- Insert new rankings with weighted scoring
    -- Calculate all components inline and produce final score
    INSERT INTO ranking_scores (
        entity_type,
        entity_id,
        context,
        score
    )
    SELECT 
        'work' AS entity_type,
        w.id AS entity_id,
        'global' AS context,
        
        -- Final weighted score (calculated inline)
        -- Formula: canon_tier (40%) + festival (30%) + engagement (20%) + arthouse (10%)
        (
            -- Canon tier score (40% weight) - HIGHEST PRIORITY
            -- criterion: 3.0 × 40 = 120 pts max
            -- mubi_permanent: 2.5 × 40 = 100 pts max
            -- none: 1.0 × 40 = 40 pts max
            COALESCE(get_canon_tier_multiplier(ca.canon_tier) * 40, 0)
            
            -- Festival awards score (30% weight) - placeholder until work_awards populated
            -- A-list festivals: 30 pts each (Cannes, Berlinale, Venice, TIFF, Sundance)
            + 0
            
            -- Engagement metrics (20% weight) - IMDB ratings scaled 5-10 → 0-20 pts
            + COALESCE((w.imdb_rating - 5.0) * 4, 0)
            
            -- Arthouse distribution (10% weight) - max 2.5 pts (25 × 0.1)
            -- Criterion: 15, MUBI: 10, Janus: 8, capped at 25 then scaled to 10%
            + COALESCE(get_arthouse_score(w.criterion_title, w.mubi_title, w.arthouse_dist) * 0.1, 0)
        ) AS score
        
    FROM works w
    LEFT JOIN color_assignments ca ON ca.work_id = w.id
    WHERE w.is_published = TRUE;
    
    -- Update ranks based on score
    UPDATE ranking_scores rs
    SET rank = subq.rank
    FROM (
        SELECT 
            entity_id,
            ROW_NUMBER() OVER (
                PARTITION BY entity_type, context 
                ORDER BY score DESC
            ) AS rank
        FROM ranking_scores
        WHERE entity_type = 'work'
    ) subq
    WHERE rs.entity_id = subq.entity_id 
      AND rs.entity_type = 'work'
      AND rs.context = 'global';
      
END;
$$ LANGUAGE plpgsql;

-- Comment explaining the ranking formula
COMMENT ON FUNCTION refresh_work_rankings() IS 
'Calculates weighted ranking scores for works using:
 - canon_tier (40%): criterion=3.0x, mubi_permanent=2.5x, none=1.0x
 - festival_score (30%): A-list festival wins (Cannes, Berlinale, Venice, TIFF, Sundance)
 - engagement_score (20%): IMDB ratings scaled 5-10 → 0-20 points
 - arthouse_score (10%): Criterion, MUBI, Janus distribution with arthouse_dist field';

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. pSEO REVIEW GATE CHECK CONSTRAINT
-- ═══════════════════════════════════════════════════════════════════════════

-- Add status column to generated_articles if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'generated_articles' AND column_name = 'status'
    ) THEN
        ALTER TABLE generated_articles 
        ADD COLUMN status TEXT DEFAULT 'draft' 
        CHECK (status IN ('draft', 'pending_review', 'published', 'archived'));
    END IF;
END $$;

-- Create function to enforce status workflow
CREATE OR REPLACE FUNCTION enforce_article_status_workflow()
RETURNS TRIGGER AS $$
BEGIN
    -- Cannot go from draft directly to published
    IF OLD.status = 'draft' AND NEW.status = 'published' THEN
        RAISE EXCEPTION 'Cannot publish article directly from draft. Must pass through pending_review status.';
    END IF;
    
    -- Cannot go from archived to published without review
    IF OLD.status = 'archived' AND NEW.status = 'published' THEN
        RAISE EXCEPTION 'Cannot publish archived article. Must pass through pending_review status.';
    END IF;
    
    -- Set reviewed_at timestamp when moving to pending_review
    IF OLD.status != 'pending_review' AND NEW.status = 'pending_review' THEN
        NEW.reviewed_at := NOW();
    END IF;
    
    -- Set published_at timestamp when publishing
    IF OLD.status != 'published' AND NEW.status = 'published' THEN
        NEW.published_at := NOW();
        NEW.is_published := TRUE;
    END IF;
    
    -- Clear is_published flag when unpublishing
    IF OLD.status = 'published' AND NEW.status != 'published' THEN
        NEW.is_published := FALSE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for status workflow enforcement
DROP TRIGGER IF EXISTS trg_enforce_article_status_workflow ON generated_articles;
CREATE TRIGGER trg_enforce_article_status_workflow
    BEFORE UPDATE OF status ON generated_articles
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION enforce_article_status_workflow();

-- Comment explaining the workflow
COMMENT ON FUNCTION enforce_article_status_workflow() IS 
'Enforces pSEO review gate: articles must pass through pending_review before publishing.
Valid transitions:
  draft → pending_review → published
  draft → archived
  pending_review → published
  pending_review → draft
  published → archived
  published → pending_review (for re-review)
Blocked transitions:
  draft → published (must review first)
  archived → published (must review first)';

-- Add similar workflow to color_assignments for editorial approval
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'color_assignments' AND column_name = 'review_status'
    ) THEN
        ALTER TABLE color_assignments 
        ADD COLUMN review_status TEXT DEFAULT 'pending_review' 
        CHECK (review_status IN ('pending_review', 'approved', 'rejected'));
    END IF;
END $$;

-- Create indexes for review queues
CREATE INDEX IF NOT EXISTS idx_articles_status ON generated_articles(status) WHERE status = 'pending_review';
CREATE INDEX IF NOT EXISTS idx_color_assignments_review ON color_assignments(review_status) WHERE review_status = 'pending_review';

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. INITIAL DATA POPULATION
-- ═══════════════════════════════════════════════════════════════════════════

-- Run initial ranking calculation
SELECT refresh_work_rankings();

-- Report results
DO $$
DECLARE
    work_count INTEGER;
    ranked_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO work_count FROM works;
    SELECT COUNT(*) INTO ranked_count FROM ranking_scores WHERE entity_type = 'work';
    
    RAISE NOTICE '══════════════════════════════════════════════════════';
    RAISE NOTICE 'Phase 2 Enhancements Applied Successfully';
    RAISE NOTICE '══════════════════════════════════════════════════════';
    RAISE NOTICE 'Total works: %', work_count;
    RAISE NOTICE 'Ranked works: %', ranked_count;
    RAISE NOTICE 'Status workflow: ENFORCED';
    RAISE NOTICE '══════════════════════════════════════════════════════';
END $$;
