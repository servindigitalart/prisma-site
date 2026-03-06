/**
 * src/lib/db/people.ts
 * ─────────────────────
 * Supabase query functions for people (directors, DPs, actors, writers).
 * All functions use the SERVICE CLIENT for server-side / build-time queries.
 */

import { createServiceClient } from "./client";
import type { PersonFull, PersonRole } from "./types";

// ─── Static path generation ───────────────────────────────────────────────────

/**
 * Returns all person slugs for Astro getStaticPaths().
 * Strips the "person_" prefix to produce URL slugs.
 */
export async function getAllPeopleSlugs(): Promise<string[]> {
  const db = createServiceClient();
  const { data, error } = await db.from("people").select("id");

  if (error) {
    console.error("[people] getAllPeopleSlugs error:", error.message);
    return [];
  }

  return (data ?? []).map((row) =>
    (row as { id: string }).id.replace(/^person_/, "")
  );
}

// ─── Single person queries ────────────────────────────────────────────────────

/**
 * Fetches a full person record with:
 * - Filmography (published works they appear in + their role + color assignment)
 * - Color profile (precomputed distribution from person_color_profiles)
 *
 * Returns null if not found.
 */
export async function getPersonBySlug(slug: string): Promise<PersonFull | null> {
  const db = createServiceClient();
  const personId = `person_${slug}`;

  // Fetch person base data
  const { data: personData, error: personError } = await db
    .from("people")
    .select("*")
    .eq("id", personId)
    .single();

  if (personError) {
    if (personError.code !== "PGRST116") {
      console.error(`[people] getPersonBySlug(${slug}) error:`, personError.message);
    }
    return null;
  }

  // Fetch color profile (all role contexts)
  const { data: profileData } = await db
    .from("person_color_profiles")
    .select("*")
    .eq("person_id", personId);

  // Fetch filmography: published works + their color assignments
  const { data: filmographyData, error: filmError } = await db
    .from("work_people")
    .select(
      `
      role,
      works!inner(
        id, title, year, tmdb_poster_path, is_published,
        color_assignments(color_iconico, tier)
      )
    `
    )
    .eq("person_id", personId)
    .eq("works.is_published", true);

  if (filmError) {
    console.error(`[people] filmography query error for ${slug}:`, filmError.message);
  }

  // Pick the most relevant color profile (prefer 'director', fall back to first)
  const profiles = profileData ?? [];
  const directorProfile =
    profiles.find((p) => (p as { role_context: string }).role_context === "director") ||
    profiles.find((p) => (p as { role_context: string }).role_context === "cinematography") ||
    profiles[0] ||
    null;

  const filmography = ((filmographyData ?? []) as unknown[]).map((row: unknown) => {
    const r = row as {
      role: PersonRole;
      works: {
        id: string;
        title: string;
        year: number | null;
        tmdb_poster_path: string | null;
        color_assignments: Array<{
          color_iconico: string | null;
          tier: string | null;
        }> | null;
      };
    };
    const ca = r.works.color_assignments?.[0] ?? null;
    return {
      work: {
        id: r.works.id,
        title: r.works.title,
        year: r.works.year,
        tmdb_poster_path: r.works.tmdb_poster_path,
      },
      role: r.role,
      color: ca ? { color_iconico: ca.color_iconico, tier: ca.tier } : null,
    };
  });

  return {
    ...(personData as object),
    color_profile: directorProfile,
    filmography,
  } as unknown as PersonFull;
}

// ─── Collection queries ───────────────────────────────────────────────────────

/**
 * Returns all people with basic info for the people index page.
 */
export async function getAllPeople(): Promise<Array<{
  id: string;
  slug: string;
  name: string;
  birth_year: number | null;
  death_year: number | null;
  nationality: string[] | null;
  bio: string | null;
}>> {
  const db = createServiceClient();
  const { data, error } = await db
    .from("people")
    .select("id, name, birth_year, death_year, nationality, bio")
    .order("name");

  if (error) {
    console.error("[people] getAllPeople error:", error.message);
    return [];
  }

  return (data ?? []).map((row) => ({
    id: row.id,
    slug: row.id.replace(/^person_/, ""),
    name: row.name,
    birth_year: row.birth_year,
    death_year: row.death_year,
    nationality: row.nationality,
    bio: row.bio,
  }));
}

/**
 * Returns top-ranked people by role for ranking pages.
 *
 * @param role   PersonRole to filter by ('director', 'cinematography', 'actor', etc.)
 * @param limit  Max results (default 100)
 */
export async function getTopRankedPeople(
  role: PersonRole,
  limit = 100
): Promise<Array<{ person_id: string; score: number; rank: number | null }>> {
  const db = createServiceClient();

  const contextMap: Partial<Record<PersonRole, string>> = {
    director: "director",
    cinematography: "dp",
    actor: "actor",
    writer: "writer",
  };

  const context = contextMap[role] ?? role;

  const { data, error } = await db
    .from("ranking_scores")
    .select("entity_id, score, rank")
    .eq("entity_type", "person")
    .eq("context", context)
    .order("score", { ascending: false })
    .limit(limit);

  if (error) {
    console.error(`[people] getTopRankedPeople(${role}) error:`, error.message);
    return [];
  }

  return ((data ?? []) as unknown[]).map((row: unknown) => {
    const r = row as { entity_id: string; score: number; rank: number | null };
    return { person_id: r.entity_id, score: r.score, rank: r.rank };
  });
}
