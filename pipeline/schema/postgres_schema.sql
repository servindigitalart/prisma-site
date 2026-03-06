-- ============================================================
-- PRISMA — Supabase PostgreSQL Schema
-- Version: 1.0
-- Generated: 2026-02-25
-- Doctrine: Color v1.2 | Score v1.0 | Tier v1.0
--
-- Apply this schema in your Supabase project via:
--   Dashboard → SQL Editor → New Query → paste → Run
-- Or via Supabase CLI:
--   supabase db push (after saving to supabase/migrations/)
--
-- Tables (in dependency order):
--   Core:       works, people, studios
--   Junctions:  work_people, work_studios, work_collections
--   Color:      color_assignments
--   Awards:     awards, work_awards
--   Computed:   ranking_scores, person_color_profiles
--   User:       user_profiles, user_ratings, follows, review_likes, watchlists
--   Content:    film_collections, collection_works
--   Streaming:  film_submissions
--   pSEO:       generated_articles, news_items
-- ============================================================

-- ────────────────────────────────────────────────────────────────────────────
-- EXTENSIONS
-- ────────────────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- fuzzy title search

-- ────────────────────────────────────────────────────────────────────────────
-- HELPER: auto-update updated_at timestamp
-- ────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ────────────────────────────────────────────────────────────────────────────
-- ENUM TYPES
-- ────────────────────────────────────────────────────────────────────────────

-- Content types
CREATE TYPE work_type AS ENUM ('film', 'short', 'series', 'music_video');

-- Prisma color tier (from tier_doctrine.json v1.0)
CREATE TYPE color_tier AS ENUM ('canon', 'core', 'strong', 'peripheral', 'uncertain');

-- Color assignment source
CREATE TYPE assignment_source AS ENUM ('ai', 'editorial', 'hybrid');

-- Color mode
CREATE TYPE color_mode AS ENUM ('color', 'monochromatic');

-- Prisma palette v1.2 canonical IDs
-- 15 chromatic + 2 monochromatic modes = 17 total
CREATE TYPE prisma_color_id AS ENUM (
  -- Chromatic
  'rojo_pasional',
  'naranja_apocaliptico',
  'ambar_desertico',
  'amarillo_ludico',
  'verde_lima',
  'verde_esmeralda',
  'verde_distopico',
  'cian_melancolico',
  'azul_nocturno',
  'violeta_cinetico',
  'purpura_onirico',
  'magenta_pop',
  'blanco_polar',
  'negro_abismo',
  'titanio_mecanico',
  -- Monochromatic modes
  'claroscuro_dramatico',
  'monocromatico_intimo'
);

-- People roles in relation to works
CREATE TYPE person_role AS ENUM ('director', 'cinematography', 'actor', 'writer', 'editor', 'composer', 'production_design');

-- Award types
CREATE TYPE award_type AS ENUM ('festival', 'academy', 'guild', 'critics');

-- Award result
CREATE TYPE award_result AS ENUM ('win', 'nomination');

-- Streaming providers
CREATE TYPE streaming_provider AS ENUM ('bunny', 'mux', 'youtube_embed', 'vimeo');

-- Film submission status
CREATE TYPE submission_status AS ENUM ('pending', 'under_review', 'approved', 'rejected');

-- Ranking context
CREATE TYPE ranking_context AS ENUM (
  'global', 'director', 'actor', 'dp', 'writer',
  'country_ar', 'country_at', 'country_br', 'country_cn', 'country_de',
  'country_dk', 'country_es', 'country_fr', 'country_gb', 'country_hu',
  'country_in', 'country_ir', 'country_it', 'country_jp', 'country_kr',
  'country_mx', 'country_ng', 'country_pl', 'country_pt', 'country_ro',
  'country_ru', 'country_se', 'country_tw', 'country_us'
);

-- ────────────────────────────────────────────────────────────────────────────
-- CORE ENTITIES
-- ────────────────────────────────────────────────────────────────────────────

-- Works: films, shorts, series, music videos
-- Primary content entity. Slug-based ID from normalization pipeline.
CREATE TABLE works (
  -- Identity
  id                  TEXT PRIMARY KEY,           -- "work_marie-antoinette_2006"
  type                work_type NOT NULL,
  title               TEXT NOT NULL,
  original_title      TEXT,
  year                INT CHECK (year BETWEEN 1888 AND 2100),
  duration_min        INT CHECK (duration_min > 0),

  -- Classification
  countries           TEXT[] NOT NULL DEFAULT '{}', -- ISO 3166-1 alpha-2 codes
  languages           TEXT[] NOT NULL DEFAULT '{}', -- BCP-47 language codes
  genres              TEXT[] NOT NULL DEFAULT '{}',

  -- Narrative
  synopsis            TEXT,
  tagline             TEXT,

  -- External IDs
  tmdb_id             INT UNIQUE,
  imdb_id             TEXT UNIQUE,
  wikidata_id         TEXT,

  -- Ratings (cached from external sources, refreshed nightly)
  imdb_rating         NUMERIC(3,1) CHECK (imdb_rating BETWEEN 0 AND 10),
  imdb_votes          INT,
  tmdb_popularity     NUMERIC(10,2),

  -- Arthouse / curatorial status (boost factors in ranking formula)
  criterion_title     BOOLEAN NOT NULL DEFAULT FALSE,   -- Criterion Collection release
  mubi_title          BOOLEAN NOT NULL DEFAULT FALSE,   -- On MUBI
  is_sight_and_sound  BOOLEAN NOT NULL DEFAULT FALSE,   -- In S&S top 250

  -- Media
  tmdb_poster_path    TEXT,                         -- relative path, prefix with TMDB base URL
  trailer_key         TEXT,                         -- YouTube video ID from TMDB

  -- Streaming
  where_to_watch      JSONB DEFAULT '{}',           -- {"netflix": true, "mubi": false, ...}
  streaming_url       TEXT,                         -- Bunny/Mux HLS .m3u8 URL
  streaming_id        TEXT,                         -- Bunny/Mux video ID
  streaming_type      streaming_provider,
  is_streamable       BOOLEAN NOT NULL DEFAULT FALSE,

  -- Pipeline metadata
  ingested_at         TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW(),
  is_published        BOOLEAN NOT NULL DEFAULT FALSE,   -- Gates public visibility

  -- Full-text search (auto-updated by trigger)
  search_vector       TSVECTOR
);

-- Indexes
CREATE INDEX idx_works_type        ON works(type);
CREATE INDEX idx_works_year        ON works(year);
CREATE INDEX idx_works_published   ON works(is_published) WHERE is_published = TRUE;
CREATE INDEX idx_works_search      ON works USING GIN(search_vector);
CREATE INDEX idx_works_countries   ON works USING GIN(countries);
CREATE INDEX idx_works_genres      ON works USING GIN(genres);
CREATE INDEX idx_works_tmdb_pop    ON works(tmdb_popularity DESC NULLS LAST);
CREATE INDEX idx_works_title_trgm  ON works USING GIN(title gin_trgm_ops);
CREATE INDEX idx_works_criterion   ON works(criterion_title) WHERE criterion_title = TRUE;
CREATE INDEX idx_works_mubi        ON works(mubi_title) WHERE mubi_title = TRUE;

-- Auto-update updated_at
CREATE TRIGGER works_set_updated_at
  BEFORE UPDATE ON works
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- Auto-update search_vector from title, original_title, synopsis
CREATE OR REPLACE FUNCTION works_update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector =
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.original_title, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.synopsis, '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER works_search_vector_update
  BEFORE INSERT OR UPDATE OF title, original_title, synopsis ON works
  FOR EACH ROW EXECUTE FUNCTION works_update_search_vector();

COMMENT ON TABLE works IS 'Primary content entity: films, short films, series, and music videos.';
COMMENT ON COLUMN works.id IS 'Slug-based primary key matching pipeline normalized file name (work_{slug}).';
COMMENT ON COLUMN works.criterion_title IS 'True if released by Criterion Collection. Boosts ranking_scores cultural weight.';
COMMENT ON COLUMN works.mubi_title IS 'True if available on MUBI library. Minor arthouse boost.';
COMMENT ON COLUMN works.is_published IS 'Gates public visibility. Set to TRUE after editorial color approval.';
COMMENT ON COLUMN works.search_vector IS 'Auto-updated tsvector for full-text search. Do not edit manually.';


-- ────────────────────────────────────────────────────────────────────────────
-- PEOPLE
-- ────────────────────────────────────────────────────────────────────────────

-- Directors, actors, cinematographers, writers, etc.
CREATE TABLE people (
  id              TEXT PRIMARY KEY,           -- "person_sofia-coppola"
  name            TEXT NOT NULL,
  birth_year      INT,
  death_year      INT,
  bio             TEXT,
  nationality     TEXT[] DEFAULT '{}',        -- ISO 3166-1 alpha-2 codes
  tmdb_id         INT UNIQUE,
  wikidata_id     TEXT,
  profile_path    TEXT,                       -- relative TMDB profile image path
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  search_vector   TSVECTOR
);

CREATE INDEX idx_people_name_trgm ON people USING GIN(name gin_trgm_ops);
CREATE INDEX idx_people_search    ON people USING GIN(search_vector);
CREATE INDEX idx_people_tmdb      ON people(tmdb_id);

CREATE TRIGGER people_set_updated_at
  BEFORE UPDATE ON people
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE OR REPLACE FUNCTION people_update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector =
    setweight(to_tsvector('english', coalesce(NEW.name, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.bio, '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER people_search_vector_update
  BEFORE INSERT OR UPDATE OF name, bio ON people
  FOR EACH ROW EXECUTE FUNCTION people_update_search_vector();

COMMENT ON TABLE people IS 'All persons associated with works: directors, DPs, actors, writers, etc.';
COMMENT ON COLUMN people.id IS 'Slug-based primary key (person_{slug}). Must be unique per person, not per role.';


-- ────────────────────────────────────────────────────────────────────────────
-- STUDIOS
-- ────────────────────────────────────────────────────────────────────────────

-- Production companies and distributors
CREATE TABLE studios (
  id              TEXT PRIMARY KEY,           -- "studio_american-zoetrope"
  name            TEXT NOT NULL,
  country         TEXT,                       -- ISO 3166-1 alpha-2
  founded_year    INT,
  tmdb_id         INT UNIQUE,
  wikidata_id     TEXT,
  logo_path       TEXT,
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER studios_set_updated_at
  BEFORE UPDATE ON studios
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE studios IS 'Production companies and distributors associated with works.';


-- ────────────────────────────────────────────────────────────────────────────
-- JUNCTION: works ↔ people
-- ────────────────────────────────────────────────────────────────────────────

-- Connects works to people with role context.
-- A person can have multiple rows for the same work (e.g., director + writer).
CREATE TABLE work_people (
  work_id         TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  person_id       TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  role            person_role NOT NULL,
  billing_order   INT,                        -- Cast position (1 = lead); NULL for crew
  PRIMARY KEY (work_id, person_id, role)
);

CREATE INDEX idx_wp_person ON work_people(person_id);
CREATE INDEX idx_wp_work   ON work_people(work_id);
CREATE INDEX idx_wp_role   ON work_people(role);
CREATE INDEX idx_wp_person_role ON work_people(person_id, role);

COMMENT ON TABLE work_people IS 'Junction: works ↔ people. A person can have multiple roles per work.';
COMMENT ON COLUMN work_people.billing_order IS 'Cast billing order (1 = lead role). NULL for crew roles.';


-- ────────────────────────────────────────────────────────────────────────────
-- JUNCTION: works ↔ studios
-- ────────────────────────────────────────────────────────────────────────────

CREATE TABLE work_studios (
  work_id         TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  studio_id       TEXT NOT NULL REFERENCES studios(id) ON DELETE CASCADE,
  PRIMARY KEY (work_id, studio_id)
);

CREATE INDEX idx_ws_studio ON work_studios(studio_id);
CREATE INDEX idx_ws_work   ON work_studios(work_id);

COMMENT ON TABLE work_studios IS 'Junction: works ↔ studios (production companies).';


-- ────────────────────────────────────────────────────────────────────────────
-- FILM COLLECTIONS (e.g., Kieślowski Three Colors Trilogy)
-- ────────────────────────────────────────────────────────────────────────────

-- Named collections / series of related films
CREATE TABLE film_collections (
  id              TEXT PRIMARY KEY,           -- "collection_three-colors-trilogy"
  name            TEXT NOT NULL,
  description     TEXT,
  director_id     TEXT REFERENCES people(id) ON DELETE SET NULL,
  tmdb_id         INT UNIQUE,                 -- TMDB collection ID
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE film_collections IS 'Curated film collections (trilogies, series, themed groups).';

-- Junction: collections ↔ works
CREATE TABLE collection_works (
  collection_id   TEXT NOT NULL REFERENCES film_collections(id) ON DELETE CASCADE,
  work_id         TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  position        INT,                        -- Order within collection (1-indexed)
  PRIMARY KEY (collection_id, work_id)
);

CREATE INDEX idx_cw_work ON collection_works(work_id);

COMMENT ON TABLE collection_works IS 'Junction: film_collections ↔ works. Position orders films within a collection.';


-- ────────────────────────────────────────────────────────────────────────────
-- COLOR ASSIGNMENTS
-- ────────────────────────────────────────────────────────────────────────────

-- The definitive color identity for each work (one row per work).
-- This is the UX contract from Phase 3 of the pipeline.
CREATE TABLE color_assignments (
  work_id              TEXT PRIMARY KEY REFERENCES works(id) ON DELETE CASCADE,

  -- Core color identity
  mode                 color_mode NOT NULL,
  color_iconico        prisma_color_id NOT NULL,  -- Primary canonical color ID
  color_rank           NUMERIC(4,3) CHECK (color_rank BETWEEN 0 AND 1), -- Confidence 0-1
  colores_secundarios  prisma_color_id[] DEFAULT '{}', -- Max 3 secondary IDs
  temperatura_emocional TEXT,                     -- Emotional temperature descriptor
  ritmo_visual         TEXT,                      -- Visual rhythm descriptor
  grado_abstraccion    TEXT,                      -- Abstraction level descriptor

  -- Tier and scoring
  tier                 color_tier,
  tier_rank            INT CHECK (tier_rank BETWEEN 1 AND 30), -- Canon rank only (1-30)
  numeric_score        NUMERIC(5,2) CHECK (numeric_score BETWEEN 0 AND 100),
  cultural_weight      NUMERIC(5,2) CHECK (cultural_weight BETWEEN 0 AND 100),
  authorship_score     NUMERIC(5,2) CHECK (authorship_score BETWEEN 0 AND 100),
  popularity_score     NUMERIC(5,2) CHECK (popularity_score BETWEEN 0 AND 100),
  ai_confidence        NUMERIC(4,3) CHECK (ai_confidence BETWEEN 0 AND 1),

  -- Provenance
  source               assignment_source NOT NULL DEFAULT 'ai',
  pipeline_version     TEXT,                      -- e.g. "phase3_v1.0"
  doctrine_version     TEXT DEFAULT '1.2',        -- Prisma color doctrine version used
  assigned_at          TIMESTAMPTZ DEFAULT NOW(),

  -- AI reasoning (full JSON blob from Phase 2A/2D output)
  reasoning            JSONB,

  -- Editorial override (present only if an editor overrode the AI)
  editorial_override   JSONB,

  -- Review status
  review_status        TEXT NOT NULL DEFAULT 'pending_review'
                         CHECK (review_status IN ('pending_review', 'approved', 'rejected')),

  updated_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ca_color        ON color_assignments(color_iconico);
CREATE INDEX idx_ca_tier         ON color_assignments(tier, tier_rank, numeric_score DESC);
CREATE INDEX idx_ca_score        ON color_assignments(numeric_score DESC NULLS LAST);
CREATE INDEX idx_ca_review       ON color_assignments(review_status);
CREATE INDEX idx_ca_doctrine     ON color_assignments(doctrine_version);

-- GIN index for secondary colors array queries
CREATE INDEX idx_ca_secondary    ON color_assignments USING GIN(colores_secundarios);

CREATE TRIGGER ca_set_updated_at
  BEFORE UPDATE ON color_assignments
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE color_assignments IS 'Definitive color identity for each work. One row per work. Phase 3 pipeline output.';
COMMENT ON COLUMN color_assignments.color_iconico IS 'Primary Prisma palette v1.2 canonical ID.';
COMMENT ON COLUMN color_assignments.colores_secundarios IS 'Up to 3 supporting chromatic color IDs.';
COMMENT ON COLUMN color_assignments.tier_rank IS 'Manual rank 1-30 within canon tier. NULL for all other tiers.';
COMMENT ON COLUMN color_assignments.doctrine_version IS 'Enables targeted re-runs when doctrine is updated. Pin to "1.2".';
COMMENT ON COLUMN color_assignments.review_status IS 'Editorial gate: pending_review → approved → visible on site.';


-- ────────────────────────────────────────────────────────────────────────────
-- AWARDS
-- ────────────────────────────────────────────────────────────────────────────

-- Award definitions (Cannes Palme d'Or, Oscar for Best Picture, etc.)
CREATE TABLE awards (
  id              TEXT PRIMARY KEY,           -- "award_palme_dor"
  name            TEXT NOT NULL,
  organization    TEXT NOT NULL,              -- "Cannes Film Festival"
  type            award_type,
  tier            TEXT CHECK (tier IN ('A', 'B', 'C')), -- Prestige tier
  country         TEXT,                       -- ISO 3166-1 alpha-2
  wikidata_id     TEXT,
  scoring_points  INT NOT NULL DEFAULT 0     -- Points contributed to film_prestige_score
);

COMMENT ON TABLE awards IS 'Award definitions. Scoring points feed into ranking_scores formula.';
COMMENT ON COLUMN awards.scoring_points IS 'Points added to prestige score when a work wins this award.';

-- Award instances (a specific film won/was nominated for a specific award)
CREATE TABLE work_awards (
  id              BIGSERIAL PRIMARY KEY,
  work_id         TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  award_id        TEXT NOT NULL REFERENCES awards(id),
  year            INT,
  category        TEXT,                       -- "Best Film", "Best Cinematography", etc.
  result          award_result NOT NULL DEFAULT 'win',
  person_id       TEXT REFERENCES people(id) ON DELETE SET NULL -- If awarded to a person
);

CREATE INDEX idx_wa_work   ON work_awards(work_id);
CREATE INDEX idx_wa_award  ON work_awards(award_id);
CREATE INDEX idx_wa_person ON work_awards(person_id) WHERE person_id IS NOT NULL;

COMMENT ON TABLE work_awards IS 'Award instances: which work won/was nominated for which award in which year.';


-- ────────────────────────────────────────────────────────────────────────────
-- RANKING SCORES (pre-computed, refreshed nightly)
-- ────────────────────────────────────────────────────────────────────────────

-- Cached prestige scores for works, people, and studios.
-- Refreshed nightly by pipeline/compute_rankings.py.
-- Formula: film_prestige_score = festival_points×0.35 + critical_canon×0.25 +
--           cinematography×0.15 + imdb_score×0.10 + arthouse_dist×0.10 + language_bonus×0.05
CREATE TABLE ranking_scores (
  entity_type     TEXT NOT NULL CHECK (entity_type IN ('work', 'person', 'studio')),
  entity_id       TEXT NOT NULL,
  context         TEXT NOT NULL DEFAULT 'global', -- 'global' | 'director' | 'actor' | 'dp' | 'country_{iso}'
  score           NUMERIC(10,4) NOT NULL,
  rank            INT,                        -- Rank within (entity_type, context) at last refresh
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (entity_type, entity_id, context)
);

CREATE INDEX idx_rs_score ON ranking_scores(entity_type, context, score DESC);

COMMENT ON TABLE ranking_scores IS 'Pre-computed prestige scores. Refreshed nightly. Do not edit manually.';


-- ────────────────────────────────────────────────────────────────────────────
-- PERSON COLOR PROFILES (pre-computed, refreshed nightly)
-- ────────────────────────────────────────────────────────────────────────────

-- Visual color fingerprint for directors and DPs.
-- Computed from the color_assignments of all their films.
CREATE TABLE person_color_profiles (
  person_id          TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  role_context       person_role NOT NULL DEFAULT 'director', -- 'director' or 'cinematography'
  color_distribution JSONB NOT NULL DEFAULT '{}', -- {"rojo_pasional": 0.35, "azul_nocturno": 0.25, ...}
  dominant_color     prisma_color_id,
  film_count         INT NOT NULL DEFAULT 0,
  updated_at         TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (person_id, role_context)
);

COMMENT ON TABLE person_color_profiles IS 'Color fingerprint per person×role. Distribution sums to 1.0. Refreshed nightly.';
COMMENT ON COLUMN person_color_profiles.color_distribution IS 'Map of prisma_color_id → weight (0.0-1.0). Normalized to sum=1.0.';


-- ────────────────────────────────────────────────────────────────────────────
-- USER SYSTEM
-- ────────────────────────────────────────────────────────────────────────────

-- User profiles extending Supabase auth.users
-- Supabase Auth manages authentication; this table adds profile data.
CREATE TABLE user_profiles (
  id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username        TEXT UNIQUE NOT NULL
                    CHECK (char_length(username) BETWEEN 3 AND 30)
                    CHECK (username ~ '^[a-z0-9_-]+$'),
  display_name    TEXT CHECK (char_length(display_name) <= 50),
  avatar_url      TEXT,
  bio             TEXT CHECK (char_length(bio) <= 500),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_up_username ON user_profiles(username);

CREATE TRIGGER up_set_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE user_profiles IS 'Public user profile data. Extends Supabase auth.users (private auth data stays in auth schema).';

-- User ratings (1-10) and optional reviews
-- Rating a film automatically marks it as "watched" — no separate diary needed.
CREATE TABLE user_ratings (
  id              BIGSERIAL PRIMARY KEY,
  user_id         UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  work_id         TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 10),
  review          TEXT CHECK (char_length(review) <= 2000),
  is_public       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, work_id)
);

CREATE INDEX idx_ur_work   ON user_ratings(work_id);
CREATE INDEX idx_ur_user   ON user_ratings(user_id);
CREATE INDEX idx_ur_public ON user_ratings(work_id, rating) WHERE is_public = TRUE;

CREATE TRIGGER ur_set_updated_at
  BEFORE UPDATE ON user_ratings
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE user_ratings IS 'User film ratings (1-10). Submitting a rating = marking film as watched.';
COMMENT ON COLUMN user_ratings.review IS 'Optional short review (max 2,000 chars). Editable anytime.';

-- Watchlist ("want to watch")
-- Separate from ratings — for films the user hasn't seen yet.
CREATE TABLE watchlists (
  user_id         UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  work_id         TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  added_at        TIMESTAMPTZ DEFAULT NOW(),
  note            TEXT CHECK (char_length(note) <= 280), -- Optional short note
  PRIMARY KEY (user_id, work_id)
);

CREATE INDEX idx_wl_user ON watchlists(user_id, added_at DESC);
CREATE INDEX idx_wl_work ON watchlists(work_id);

COMMENT ON TABLE watchlists IS 'User "want to watch" list. Separate from ratings (which track watched films).';

-- Social follows
CREATE TABLE follows (
  follower_id     UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  following_id    UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (follower_id, following_id),
  CHECK (follower_id != following_id)       -- Cannot follow yourself
);

CREATE INDEX idx_follows_following ON follows(following_id);

COMMENT ON TABLE follows IS 'Social follow graph between users.';

-- Review likes
CREATE TABLE review_likes (
  user_id         UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  rating_id       BIGINT NOT NULL REFERENCES user_ratings(id) ON DELETE CASCADE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, rating_id)
);

CREATE INDEX idx_rl_rating ON review_likes(rating_id);

COMMENT ON TABLE review_likes IS 'Users liking public reviews. Denormalized like count should be cached.';


-- ────────────────────────────────────────────────────────────────────────────
-- STREAMING: FILM SUBMISSIONS
-- ────────────────────────────────────────────────────────────────────────────

-- Independent filmmaker short film submission workflow
CREATE TABLE film_submissions (
  id                  BIGSERIAL PRIMARY KEY,
  filmmaker_name      TEXT NOT NULL,
  filmmaker_email     TEXT NOT NULL,
  filmmaker_bio       TEXT,
  filmmaker_website   TEXT,                   -- Used for identity verification
  title               TEXT NOT NULL,
  year                INT,
  runtime_min         INT,
  synopsis            TEXT,
  countries           TEXT[] DEFAULT '{}',
  languages           TEXT[] DEFAULT '{}',
  genres              TEXT[] DEFAULT '{}',
  storage_path        TEXT,                   -- Supabase Storage path (pre-approval, private bucket)
  status              submission_status NOT NULL DEFAULT 'pending',
  rejection_reason    TEXT,
  reviewer_notes      TEXT,
  submitted_at        TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at         TIMESTAMPTZ,
  published_at        TIMESTAMPTZ,
  work_id             TEXT REFERENCES works(id) ON DELETE SET NULL, -- Set when approved
  copyright_attested  BOOLEAN NOT NULL DEFAULT FALSE, -- Filmmaker confirmed they own rights
  submitter_user_id   UUID REFERENCES user_profiles(id) ON DELETE SET NULL
);

CREATE INDEX idx_fs_status    ON film_submissions(status);
CREATE INDEX idx_fs_submitted ON film_submissions(submitted_at DESC);

COMMENT ON TABLE film_submissions IS 'Filmmaker short film submission workflow. storage_path is in a private Supabase Storage bucket.';
COMMENT ON COLUMN film_submissions.copyright_attested IS 'TRUE only if filmmaker checked the copyright attestation box during submission.';


-- ────────────────────────────────────────────────────────────────────────────
-- pSEO: GENERATED ARTICLES
-- ─────────────────────────────────��──────────────────────────────────────────

-- Auto-generated pSEO blog articles (generated nightly, human-gated before publish)
CREATE TABLE generated_articles (
  id                  BIGSERIAL PRIMARY KEY,
  slug                TEXT UNIQUE NOT NULL,
  title               TEXT NOT NULL,
  template_type       TEXT NOT NULL CHECK (template_type IN (
                        'color_decade',
                        'director_color_profile',
                        'country_visual_atlas',
                        'dp_signature',
                        'color_listicle'
                      )),
  content_md          TEXT NOT NULL,
  excerpt             TEXT CHECK (char_length(excerpt) <= 300),
  word_count          INT,

  -- Related entities for internal linking
  related_works       TEXT[] DEFAULT '{}',    -- work_ids referenced
  related_people      TEXT[] DEFAULT '{}',    -- person_ids referenced
  related_colors      TEXT[] DEFAULT '{}',    -- prisma color IDs referenced
  related_decades     TEXT[] DEFAULT '{}',    -- e.g. ["1970s", "1980s"]
  related_countries   TEXT[] DEFAULT '{}',    -- ISO codes

  -- SEO metadata
  meta_title          TEXT CHECK (char_length(meta_title) <= 60),
  meta_description    TEXT CHECK (char_length(meta_description) <= 160),
  canonical_url       TEXT,

  -- Status
  is_published        BOOLEAN NOT NULL DEFAULT FALSE,
  no_index            BOOLEAN NOT NULL DEFAULT FALSE, -- TRUE for thin content (<800 words)

  generated_at        TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at         TIMESTAMPTZ,
  published_at        TIMESTAMPTZ,
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ga_template   ON generated_articles(template_type, is_published);
CREATE INDEX idx_ga_published  ON generated_articles(published_at DESC) WHERE is_published = TRUE;
CREATE INDEX idx_ga_slug       ON generated_articles(slug);

CREATE TRIGGER ga_set_updated_at
  BEFORE UPDATE ON generated_articles
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE generated_articles IS 'AI-generated pSEO articles. All require human editorial approval before is_published=TRUE.';
COMMENT ON COLUMN generated_articles.no_index IS 'Set TRUE automatically for articles under 800 words to prevent thin-content penalty.';

-- ────────────────────────────────────────────────────────────────────────────
-- pSEO: NEWS ITEMS
-- ────────────────────────────────────────────────────────────────────────────

-- Ingested from RSS feeds, matched to catalog films, AI-summarized
CREATE TABLE news_items (
  id              BIGSERIAL PRIMARY KEY,
  source_name     TEXT NOT NULL,              -- "Variety", "IndieWire"
  source_url      TEXT UNIQUE NOT NULL,
  title           TEXT NOT NULL,
  summary         TEXT CHECK (char_length(summary) <= 500), -- AI-generated, 2-3 sentences
  related_works   TEXT[] DEFAULT '{}',        -- work_ids mentioned
  published_at    TIMESTAMPTZ,
  ingested_at     TIMESTAMPTZ DEFAULT NOW(),
  is_published    BOOLEAN NOT NULL DEFAULT FALSE -- noindex always; for engagement only
);

CREATE INDEX idx_ni_published ON news_items(published_at DESC) WHERE is_published = TRUE;
CREATE INDEX idx_ni_works     ON news_items USING GIN(related_works);

COMMENT ON TABLE news_items IS 'RSS-ingested news items about films in catalog. Always noindex — for user engagement, not SEO.';


-- ────────────────────────────────────────────────────────────────────────────
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ────────────────────────────────────────────────────────────────────────────
-- Enable RLS on all user-data tables. Public content tables are read-only.

ALTER TABLE user_profiles        ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ratings         ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists           ENABLE ROW LEVEL SECURITY;
ALTER TABLE follows              ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_likes         ENABLE ROW LEVEL SECURITY;

-- user_profiles: public read, self write
CREATE POLICY "Public profiles are visible to all"
  ON user_profiles FOR SELECT
  USING (TRUE);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (id = auth.uid());

CREATE POLICY "Users can insert own profile"
  ON user_profiles FOR INSERT
  WITH CHECK (id = auth.uid());

-- user_ratings: public ratings visible to all, private only to owner
CREATE POLICY "Public ratings are visible to all"
  ON user_ratings FOR SELECT
  USING (is_public = TRUE OR user_id = auth.uid());

CREATE POLICY "Users can insert own ratings"
  ON user_ratings FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own ratings"
  ON user_ratings FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "Users can delete own ratings"
  ON user_ratings FOR DELETE
  USING (user_id = auth.uid());

-- watchlists: only visible to owner
CREATE POLICY "Users see own watchlist"
  ON watchlists FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Users can manage own watchlist"
  ON watchlists FOR ALL
  USING (user_id = auth.uid());

-- follows: public read, self write
CREATE POLICY "Follows are publicly visible"
  ON follows FOR SELECT
  USING (TRUE);

CREATE POLICY "Users can follow/unfollow"
  ON follows FOR ALL
  USING (follower_id = auth.uid());

-- review_likes: public read, self write
CREATE POLICY "Review likes are publicly visible"
  ON review_likes FOR SELECT
  USING (TRUE);

CREATE POLICY "Users can like/unlike reviews"
  ON review_likes FOR ALL
  USING (user_id = auth.uid());


-- ────────────────────────────────────────────────────────────────────────────
-- HELPFUL VIEWS
-- ────────────────────────────────────────────────────────────────────────────

-- Works with their color assignment and global rank in a single query
CREATE OR REPLACE VIEW works_with_color AS
SELECT
  w.id,
  w.type,
  w.title,
  w.year,
  w.countries,
  w.genres,
  w.tmdb_poster_path,
  w.criterion_title,
  w.mubi_title,
  w.is_published,
  ca.color_iconico,
  ca.colores_secundarios,
  ca.tier,
  ca.tier_rank,
  ca.numeric_score,
  ca.mode AS color_mode,
  rs.score AS prestige_score,
  rs.rank  AS global_rank
FROM works w
LEFT JOIN color_assignments ca ON ca.work_id = w.id AND ca.review_status = 'approved'
LEFT JOIN ranking_scores rs    ON rs.entity_id = w.id
                               AND rs.entity_type = 'work'
                               AND rs.context = 'global'
WHERE w.is_published = TRUE;

COMMENT ON VIEW works_with_color IS 'Published works joined with approved color assignment and global prestige rank.';

-- Canon and Core films per color — used by color pages
CREATE OR REPLACE VIEW color_page_films AS
SELECT
  ca.color_iconico,
  ca.tier,
  ca.tier_rank,
  ca.numeric_score,
  ca.colores_secundarios,
  w.id AS work_id,
  w.title,
  w.year,
  w.countries,
  w.tmdb_poster_path,
  w.criterion_title
FROM color_assignments ca
JOIN works w ON w.id = ca.work_id
WHERE ca.review_status = 'approved'
  AND ca.tier IN ('canon', 'core', 'strong', 'peripheral')
  AND w.is_published = TRUE
ORDER BY ca.color_iconico, ca.tier, ca.tier_rank NULLS LAST, ca.numeric_score DESC;

COMMENT ON VIEW color_page_films IS 'All published films with approved color assignments, ordered for color page display.';


-- ────────────────────────────────────────────────────────────────────────────
-- SEED: AWARD DEFINITIONS
-- ────────────────────────────────────────────────────────────────────────────
-- Tier A festivals (30 scoring points each for wins)

INSERT INTO awards (id, name, organization, type, tier, country, scoring_points) VALUES
  ('award_palme_dor',             'Palme d''Or',              'Cannes Film Festival',              'festival', 'A', 'FR', 30),
  ('award_golden_lion',           'Golden Lion',              'Venice Film Festival',              'festival', 'A', 'IT', 30),
  ('award_golden_bear',           'Golden Bear',              'Berlin International Film Festival','festival', 'A', 'DE', 30),
  ('award_cannes_grand_prix',     'Grand Prix',               'Cannes Film Festival',              'festival', 'A', 'FR', 20),
  ('award_cannes_best_director',  'Best Director',            'Cannes Film Festival',              'festival', 'A', 'FR', 20),
  ('award_venice_silver_lion',    'Silver Lion (Grand Jury)', 'Venice Film Festival',              'festival', 'A', 'IT', 20),
  ('award_berlin_silver_bear',    'Silver Bear',              'Berlin International Film Festival','festival', 'A', 'DE', 20),
  ('award_sundance_grand_jury',   'Grand Jury Prize',         'Sundance Film Festival',            'festival', 'B', 'US', 20),
  ('award_tiff_platform',         'Platform Prize',           'Toronto International Film Festival','festival','B', 'CA', 10),
  ('award_oscar_picture',         'Best Picture',             'Academy of Motion Picture Arts',   'academy',  'A', 'US', 25),
  ('award_oscar_director',        'Best Director',            'Academy of Motion Picture Arts',   'academy',  'A', 'US', 25),
  ('award_oscar_cinematography',  'Best Cinematography',      'Academy of Motion Picture Arts',   'academy',  'A', 'US', 25),
  ('award_oscar_cin_nom',         'Best Cinematography (nom)','Academy of Motion Picture Arts',   'academy',  'A', 'US', 15),
  ('award_bafta_film',            'Best Film',                'BAFTA',                            'academy',  'A', 'GB', 20),
  ('award_bafta_cinematography',  'Best Cinematography',      'BAFTA',                            'academy',  'A', 'GB', 20),
  ('award_asc_award',             'ASC Award',                'American Society of Cinematographers','guild',  'B', 'US', 20)
ON CONFLICT (id) DO NOTHING;


-- ────────────────────────────────────────────────────────────────────────────
-- NOTES FOR DEVELOPERS
-- ────────────────────────────────────────────────────────────────────────────
--
-- 1. After applying this schema, run from project root:
--    python pipeline/validate_color_ids.py --fix  (ensure clean IDs first)
--    python pipeline/migrate_to_db.py              (import JSON data into Supabase)
--
-- 2. Generate TypeScript types from this schema:
--    npx supabase gen types typescript --project-id YOUR_PROJECT_ID > src/lib/db/database.types.ts
--
-- 3. Supabase Storage buckets to create (via Dashboard or CLI):
--    - "submissions" (private): for filmmaker video uploads pre-approval
--    - "assets"      (public):  for processed poster/still images if self-hosting
--
-- 4. Enable realtime (if needed for future features) on:
--    - user_ratings (for live feed of friends' activity)
--    - film_submissions (for admin notification of new submissions)
--
-- 5. The works.is_published flag is the editorial gate.
--    color_assignments.review_status = 'approved' is the color gate.
--    Both must be true for a film to appear on the public site.
-- ────────────────────────────────────────────────────────────────────────────
