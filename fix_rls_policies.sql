-- Fix RLS policies for user tables
-- These policies allow authenticated users to manage their own data

-- ============================================================================
-- user_ratings table
-- ============================================================================

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view their own ratings" ON user_ratings;
DROP POLICY IF EXISTS "Users can insert their own ratings" ON user_ratings;
DROP POLICY IF EXISTS "Users can update their own ratings" ON user_ratings;
DROP POLICY IF EXISTS "Users can delete their own ratings" ON user_ratings;

-- Enable RLS
ALTER TABLE user_ratings ENABLE ROW LEVEL SECURITY;

-- Allow users to view their own ratings
CREATE POLICY "Users can view their own ratings"
ON user_ratings FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Allow users to insert their own ratings
CREATE POLICY "Users can insert their own ratings"
ON user_ratings FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own ratings
CREATE POLICY "Users can update their own ratings"
ON user_ratings FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own ratings
CREATE POLICY "Users can delete their own ratings"
ON user_ratings FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- ============================================================================
-- user_watches table
-- ============================================================================

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view their own watches" ON user_watches;
DROP POLICY IF EXISTS "Users can insert their own watches" ON user_watches;
DROP POLICY IF EXISTS "Users can update their own watches" ON user_watches;
DROP POLICY IF EXISTS "Users can delete their own watches" ON user_watches;

-- Enable RLS
ALTER TABLE user_watches ENABLE ROW LEVEL SECURITY;

-- Allow users to view their own watches
CREATE POLICY "Users can view their own watches"
ON user_watches FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Allow users to insert their own watches
CREATE POLICY "Users can insert their own watches"
ON user_watches FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own watches
CREATE POLICY "Users can update their own watches"
ON user_watches FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own watches
CREATE POLICY "Users can delete their own watches"
ON user_watches FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- ============================================================================
-- user_watchlist table
-- ============================================================================

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view their own watchlist" ON user_watchlist;
DROP POLICY IF EXISTS "Users can insert to their own watchlist" ON user_watchlist;
DROP POLICY IF EXISTS "Users can update their own watchlist" ON user_watchlist;
DROP POLICY IF EXISTS "Users can delete from their own watchlist" ON user_watchlist;

-- Enable RLS
ALTER TABLE user_watchlist ENABLE ROW LEVEL SECURITY;

-- Allow users to view their own watchlist
CREATE POLICY "Users can view their own watchlist"
ON user_watchlist FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Allow users to insert to their own watchlist
CREATE POLICY "Users can insert to their own watchlist"
ON user_watchlist FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own watchlist
CREATE POLICY "Users can update their own watchlist"
ON user_watchlist FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Allow users to delete from their own watchlist
CREATE POLICY "Users can delete from their own watchlist"
ON user_watchlist FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- ============================================================================
-- Verification
-- ============================================================================

-- Check that policies are created
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE tablename IN ('user_ratings', 'user_watches', 'user_watchlist')
ORDER BY tablename, policyname;
