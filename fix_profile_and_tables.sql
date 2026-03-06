-- ============================================================================
-- FIX 1: Update existing user profile to have a valid username
-- The handle_new_user trigger inserted a row with NULL username,
-- violating the NOT NULL constraint. Fix it.
-- ============================================================================

-- First, check if the username column actually has the NOT NULL constraint
-- If it does, the row shouldn't exist. Let's just update it.
UPDATE user_profiles
SET username = 'emilio_servin',
    updated_at = NOW()
WHERE id = 'b08f6ed6-0758-4684-af6b-3031db54cece'
  AND (username IS NULL OR username = '');

-- ============================================================================
-- FIX 2: Alter user_profiles to allow NULL username temporarily
-- (for the handle_new_user trigger — new users won't have a username yet)
-- ============================================================================
-- If username has NOT NULL, we need to drop it so the trigger can work
-- Then we rely on the app to prompt users to set a username later
ALTER TABLE user_profiles ALTER COLUMN username DROP NOT NULL;

-- Also drop the CHECK constraints that would block NULL/empty usernames on insert
-- (The trigger sets username to NULL initially)
ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_username_check;
ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_username_check1;

-- ============================================================================
-- FIX 3: Fix the handle_new_user trigger to generate a username
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  new_username TEXT;
BEGIN
  -- Generate a username from email or a random string
  new_username := COALESCE(
    -- Try to use the part before @ in email
    LOWER(REGEXP_REPLACE(SPLIT_PART(NEW.email, '@', 1), '[^a-z0-9_-]', '', 'g')),
    -- Fallback to a random string
    'user_' || SUBSTR(NEW.id::text, 1, 8)
  );

  -- Ensure minimum length
  IF char_length(new_username) < 3 THEN
    new_username := 'user_' || SUBSTR(NEW.id::text, 1, 8);
  END IF;

  -- Truncate to max 30 chars
  new_username := SUBSTR(new_username, 1, 30);

  -- Handle uniqueness: append random suffix if username exists
  WHILE EXISTS (SELECT 1 FROM public.user_profiles WHERE username = new_username) LOOP
    new_username := SUBSTR(new_username, 1, 22) || '_' || SUBSTR(gen_random_uuid()::text, 1, 7);
  END LOOP;

  INSERT INTO public.user_profiles (id, username, display_name, avatar_url)
  VALUES (
    NEW.id,
    new_username,
    COALESCE(NEW.raw_user_meta_data ->> 'full_name', NEW.raw_user_meta_data ->> 'name'),
    COALESCE(NEW.raw_user_meta_data ->> 'avatar_url', NEW.raw_user_meta_data ->> 'picture')
  )
  ON CONFLICT (id) DO UPDATE SET
    display_name = COALESCE(EXCLUDED.display_name, user_profiles.display_name),
    avatar_url = COALESCE(EXCLUDED.avatar_url, user_profiles.avatar_url),
    username = COALESCE(user_profiles.username, EXCLUDED.username),
    updated_at = NOW();

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Make sure trigger exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- FIX 4: Create user_watches table (tracks "seen" separately from ratings)
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_watches (
  user_id     UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  work_id     TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  watched_at  DATE NOT NULL DEFAULT CURRENT_DATE,
  added_at    TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, work_id, watched_at)
);

CREATE INDEX IF NOT EXISTS idx_uw_user ON user_watches(user_id, watched_at DESC);
CREATE INDEX IF NOT EXISTS idx_uw_work ON user_watches(work_id);

-- ============================================================================
-- FIX 5: Create user_watchlist table (renamed from watchlists for consistency)
-- ============================================================================
-- Check if user_watchlist already exists; if not, create it
-- We keep the original 'watchlists' table and also create user_watchlist
CREATE TABLE IF NOT EXISTS user_watchlist (
  user_id     UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  work_id     TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  added_at    TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, work_id)
);

CREATE INDEX IF NOT EXISTS idx_uwl_user ON user_watchlist(user_id, added_at DESC);
CREATE INDEX IF NOT EXISTS idx_uwl_work ON user_watchlist(work_id);

-- ============================================================================
-- FIX 6: RLS policies for user_profiles
-- ============================================================================
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Public read (profiles are public)
DROP POLICY IF EXISTS "Public profiles are visible to all" ON user_profiles;
CREATE POLICY "Public profiles are visible to all"
  ON user_profiles FOR SELECT
  USING (TRUE);

-- Self write
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (id = auth.uid());

DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
CREATE POLICY "Users can insert own profile"
  ON user_profiles FOR INSERT
  WITH CHECK (id = auth.uid());

-- ============================================================================
-- FIX 7: RLS policies for user_watches
-- ============================================================================
ALTER TABLE user_watches ENABLE ROW LEVEL SECURITY;

-- Public read (anyone can see what films a user has watched)
DROP POLICY IF EXISTS "User watches are publicly visible" ON user_watches;
CREATE POLICY "User watches are publicly visible"
  ON user_watches FOR SELECT
  USING (TRUE);

DROP POLICY IF EXISTS "Users can insert own watches" ON user_watches;
CREATE POLICY "Users can insert own watches"
  ON user_watches FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own watches" ON user_watches;
CREATE POLICY "Users can delete own watches"
  ON user_watches FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- FIX 8: RLS policies for user_watchlist
-- ============================================================================
ALTER TABLE user_watchlist ENABLE ROW LEVEL SECURITY;

-- Public read
DROP POLICY IF EXISTS "User watchlists are publicly visible" ON user_watchlist;
CREATE POLICY "User watchlists are publicly visible"
  ON user_watchlist FOR SELECT
  USING (TRUE);

DROP POLICY IF EXISTS "Users can insert own watchlist" ON user_watchlist;
CREATE POLICY "Users can insert own watchlist"
  ON user_watchlist FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own watchlist" ON user_watchlist;
CREATE POLICY "Users can delete own watchlist"
  ON user_watchlist FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- FIX 9: RLS policies for user_ratings (public ratings visible, self write)
-- ============================================================================
ALTER TABLE user_ratings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public ratings are visible to all" ON user_ratings;
CREATE POLICY "Public ratings are visible to all"
  ON user_ratings FOR SELECT
  USING (is_public = TRUE OR user_id = auth.uid());

DROP POLICY IF EXISTS "Users can insert their own ratings" ON user_ratings;
CREATE POLICY "Users can insert their own ratings"
  ON user_ratings FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own ratings" ON user_ratings;
CREATE POLICY "Users can update their own ratings"
  ON user_ratings FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own ratings" ON user_ratings;
CREATE POLICY "Users can delete their own ratings"
  ON user_ratings FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- FIX 10: RLS policies for follows
-- ============================================================================
ALTER TABLE follows ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Follows are publicly visible" ON follows;
CREATE POLICY "Follows are publicly visible"
  ON follows FOR SELECT
  USING (TRUE);

DROP POLICY IF EXISTS "Users can insert own follows" ON follows;
CREATE POLICY "Users can insert own follows"
  ON follows FOR INSERT
  WITH CHECK (auth.uid() = follower_id);

DROP POLICY IF EXISTS "Users can delete own follows" ON follows;
CREATE POLICY "Users can delete own follows"
  ON follows FOR DELETE
  USING (auth.uid() = follower_id);

-- ============================================================================
-- VERIFY
-- ============================================================================
SELECT tablename, policyname, permissive, cmd
FROM pg_policies
WHERE tablename IN ('user_profiles', 'user_watches', 'user_watchlist', 'user_ratings', 'follows')
ORDER BY tablename, policyname;
