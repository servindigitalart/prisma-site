-- ─────────────────────────────────────────────────────────────────────────────
-- PRISMA — Festivals & Awards Schema Extension
-- Run this in: https://supabase.com/dashboard/project/porqyokkphflvqfclvkj/sql
-- Then run: python3 pipeline/insert_festivals_awards.py
-- ─────────────────────────────────────────────────────────────────────────────

-- Festivals table
CREATE TABLE IF NOT EXISTS festivals (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  name_local TEXT,
  country TEXT,
  city TEXT,
  founded_year INTEGER,
  tier TEXT CHECK (tier IN ('A', 'B', 'C', 'D')),
  wikidata_id TEXT,
  logo_path TEXT,
  website TEXT,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Festival editions (one per year)
CREATE TABLE IF NOT EXISTS festival_editions (
  id TEXT PRIMARY KEY,
  festival_id TEXT REFERENCES festivals(id),
  year INTEGER NOT NULL,
  jury_president TEXT,
  jury_member_ids TEXT[],
  location TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Extend existing awards table
ALTER TABLE awards ADD COLUMN IF NOT EXISTS festival_id TEXT REFERENCES festivals(id);
ALTER TABLE awards ADD COLUMN IF NOT EXISTS is_grand_prize BOOLEAN DEFAULT false;
ALTER TABLE awards ADD COLUMN IF NOT EXISTS award_category_display TEXT;

-- Enable RLS (read-only public access)
ALTER TABLE festivals ENABLE ROW LEVEL SECURITY;
ALTER TABLE festival_editions ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "festivals_public_read"
  ON festivals FOR SELECT USING (true);

CREATE POLICY IF NOT EXISTS "festival_editions_public_read"
  ON festival_editions FOR SELECT USING (true);
