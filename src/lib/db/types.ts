/**
 * src/lib/db/types.ts
 * ────────────────────
 * Shared TypeScript types for PRISMA database entities.
 *
 * These are manually maintained until Supabase CLI generates types.
 * Run: npx supabase gen types typescript --project-id YOUR_PROJECT_ID
 * Then delete this file and import from ./database.types instead.
 */

// ─── Prisma palette v1.2 ─────────────────────────────────────────────────────

export type ChromaticColorId =
  | "rojo_pasional"
  | "naranja_apocaliptico"
  | "ambar_desertico"
  | "amarillo_ludico"
  | "verde_lima"
  | "verde_esmeralda"
  | "verde_distopico"
  | "cian_melancolico"
  | "azul_nocturno"
  | "violeta_cinetico"
  | "purpura_onirico"
  | "magenta_pop"
  | "blanco_polar"
  | "negro_abismo"
  | "titanio_mecanico";

export type MonochromaticModeId = "claroscuro_dramatico" | "monocromatico_intimo";

export type PrismaColorId = ChromaticColorId | MonochromaticModeId;

// ─── Enums ────────────────────────────────────────────────────────────────────

export type WorkType = "film" | "short" | "series" | "music_video";
export type ColorTier = "canon" | "core" | "strong" | "peripheral" | "uncertain";
export type ColorMode = "color" | "monochromatic";
export type AssignmentSource = "ai" | "editorial" | "hybrid";
export type PersonRole =
  | "director"
  | "cinematography"
  | "actor"
  | "writer"
  | "editor"
  | "composer"
  | "production_design";

// ─── Core entity types ────────────────────────────────────────────────────────

export interface Work {
  id: string;
  type: WorkType;
  title: string;
  original_title: string | null;
  year: number | null;
  duration_min: number | null;
  countries: string[];
  languages: string[];
  genres: string[];
  synopsis: string | null;
  tagline: string | null;
  tmdb_id: number | null;
  imdb_id: string | null;
  wikidata_id: string | null;
  imdb_rating: number | null;
  imdb_votes: number | null;
  tmdb_popularity: number | null;
  criterion_title: boolean;
  mubi_title: boolean;
  is_sight_and_sound: boolean;
  tmdb_poster_path: string | null;
  trailer_key: string | null;
  where_to_watch: Record<string, boolean>;
  streaming_url: string | null;
  streaming_id: string | null;
  streaming_type: string | null;
  is_streamable: boolean;
  ingested_at: string;
  updated_at: string;
  is_published: boolean;
}

export interface Person {
  id: string;
  name: string;
  birth_year: number | null;
  death_year: number | null;
  bio: string | null;
  nationality: string[];
  tmdb_id: number | null;
  wikidata_id: string | null;
  profile_path: string | null;
  gender: number | null;
  updated_at: string;
}

export interface Studio {
  id: string;
  name: string;
  country: string | null;
  founded_year: number | null;
  tmdb_id: number | null;
  wikidata_id: string | null;
  logo_path: string | null;
  updated_at: string;
}

export interface ColorAssignment {
  work_id: string;
  mode: ColorMode;
  color_iconico: PrismaColorId;
  color_rank: number | null;
  colores_secundarios: PrismaColorId[];
  temperatura_emocional: string | null;
  ritmo_visual: string | null;
  grado_abstraccion: string | null;
  tier: ColorTier | null;
  tier_rank: number | null;
  numeric_score: number | null;
  cultural_weight: number | null;
  authorship_score: number | null;
  popularity_score: number | null;
  ai_confidence: number | null;
  source: AssignmentSource;
  pipeline_version: string | null;
  doctrine_version: string;
  assigned_at: string;
  reasoning: Record<string, unknown> | null;
  editorial_override: Record<string, unknown> | null;
  review_status: "pending_review" | "approved" | "rejected";
  updated_at: string;
}

export interface WorkPerson {
  work_id: string;
  person_id: string;
  role: PersonRole;
  billing_order: number | null;
}

export interface WorkStudio {
  work_id: string;
  studio_id: string;
}

export interface Festival {
  id: string;
  name: string;
  name_local: string | null;
  country: string | null;
  city: string | null;
  founded_year: number | null;
  tier: "A" | "B" | "C" | "D" | null;
  wikidata_id: string | null;
  logo_path: string | null;
  website: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
}

export interface FestivalEdition {
  id: string;
  festival_id: string;
  year: number;
  jury_president: string | null;
  jury_member_ids: string[];
  location: string | null;
  notes: string | null;
  created_at: string;
}

export interface Award {
  id: string;
  name: string;
  organization: string;
  type: string | null;
  tier: "A" | "B" | "C" | null;
  country: string | null;
  wikidata_id: string | null;
  scoring_points: number;
  festival_id: string | null;
  is_grand_prize: boolean;
  award_category_display: string | null;
}

export interface WorkAward {
  id: number;
  work_id: string;
  award_id: string;
  year: number | null;
  category: string | null;
  result: "win" | "nomination";
  person_id: string | null;
}

export interface PersonColorProfile {
  person_id: string;
  role_context: PersonRole;
  color_distribution: Partial<Record<PrismaColorId, number>>;
  dominant_color: PrismaColorId | null;
  film_count: number;
  updated_at: string;
}

// ─── Composed / joined types (query results) ─────────────────────────────────

export interface WorkPeopleJoined extends WorkPerson {
  people: Person;
}

export interface WorkStudiosJoined extends WorkStudio {
  studios: Studio;
}

export interface FestivalMini {
  id: string;
  name: string;
  country: string | null;
  tier: "A" | "B" | "C" | "D" | null;
  logo_path: string | null;
}

export interface WorkAwardJoined extends WorkAward {
  awards: Award & { festivals: FestivalMini | null };
  people: Pick<Person, "id" | "name"> | null;
}

/** Full work record with all relations, as returned by getWorkBySlug() */
export interface WorkFull extends Work {
  color_assignments: ColorAssignment | null;
  work_people: WorkPeopleJoined[];
  work_studios: WorkStudiosJoined[];
  work_awards: WorkAwardJoined[];
}

export interface PersonFull extends Person {
  color_profile: PersonColorProfile | null;
  filmography: Array<{
    work: Pick<Work, "id" | "title" | "year" | "tmdb_poster_path">;
    role: PersonRole;
    color: Pick<ColorAssignment, "color_iconico" | "tier"> | null;
  }>;
}

// ─── Ranking / discovery types ────────────────────────────────────────────────

export interface RankingScore {
  entity_type: "work" | "person" | "studio";
  entity_id: string;
  context: string;
  score: number;
  rank: number | null;
  updated_at: string;
}

export interface GeneratedArticle {
  id: number;
  slug: string;
  title: string;
  template_type: "color_decade" | "director_color_profile" | "country_visual_atlas" | "dp_signature" | "color_listicle";
  content_md: string;
  excerpt: string | null;
  word_count: number | null;
  related_works: string[];
  related_people: string[];
  related_colors: string[];
  related_decades: string[];
  related_countries: string[];
  meta_title: string | null;
  meta_description: string | null;
  canonical_url: string | null;
  is_published: boolean;
  generated_at: string;
  reviewed_at: string | null;
  published_at: string | null;
}

/** Lightweight work card for listing pages */
export interface WorkCard {
  id: string;
  title: string;
  year: number | null;
  countries: string[];
  tmdb_poster_path: string | null;
  criterion_title: boolean;
  color_iconico: PrismaColorId | null;
  tier: ColorTier | null;
  tier_rank: number | null;
  numeric_score: number | null;
  prestige_score: number | null;
  global_rank: number | null;
}
