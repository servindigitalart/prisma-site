-- Migration: Admin + Ficha Técnica support
-- Run in Supabase SQL Editor

-- 1. Add is_admin column to user_profiles
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Extend submission_status enum with new values
ALTER TYPE submission_status ADD VALUE IF NOT EXISTS 'awaiting_ficha';
ALTER TYPE submission_status ADD VALUE IF NOT EXISTS 'ficha_received';

-- 3. Add ficha columns to film_submissions
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_token TEXT UNIQUE;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_token_expires_at TIMESTAMPTZ;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_submitted_at TIMESTAMPTZ;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_credits JSONB;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_bio_full TEXT;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_countries TEXT[];
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_languages TEXT[];
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_genres TEXT[];
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_filmmaker_photo TEXT;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_filmmaker_website TEXT;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_filmmaker_instagram TEXT;
ALTER TABLE film_submissions ADD COLUMN IF NOT EXISTS ficha_synopsis_full TEXT;

CREATE INDEX IF NOT EXISTS idx_fs_ficha_token ON film_submissions(ficha_token) WHERE ficha_token IS NOT NULL;

-- 4. Set yourself as admin (replace with your user id)
-- UPDATE user_profiles SET is_admin = true WHERE id = 'YOUR-USER-ID-HERE';
