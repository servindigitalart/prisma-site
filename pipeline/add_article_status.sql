-- filepath: pipeline/add_article_status.sql
-- Add status column to generated_articles table for review workflow

ALTER TABLE generated_articles 
ADD COLUMN IF NOT EXISTS status TEXT 
CHECK (status IN ('draft', 'pending_review', 'published', 'rejected')) 
DEFAULT 'draft';

-- Update existing rows to set status based on is_published
UPDATE generated_articles 
SET status = CASE 
  WHEN is_published = TRUE THEN 'published'
  ELSE 'draft'
END
WHERE status IS NULL;

-- Add index for efficient filtering by status
CREATE INDEX IF NOT EXISTS idx_ga_status ON generated_articles(status, generated_at DESC);

COMMENT ON COLUMN generated_articles.status IS 'Workflow status: draft → pending_review → published (or rejected → draft)';
