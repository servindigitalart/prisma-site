/**
 * src/lib/db/works.ts
 * ────────────────────
 * Supabase query functions for works (films, shorts, series, music videos).
 * All functions use the SERVICE CLIENT for server-side / build-time queries.
 *
 * Used by:
 *   - Astro getStaticPaths() for static path generation
 *   - Astro page components for data loading
 *   - SSR API routes (server-rendered, per-request)
 */

import { createServiceClient } from "./client";
import type {
  WorkFull,
  WorkCard,
  PrismaColorId,
  ColorTier,
  PersonRole,
} from "./types";

// ─── Static path generation ───────────────────────────────────────────────────

/**
 * Returns all published work slugs for Astro getStaticPaths().
 * Strips the "work_" prefix to produce URL slugs.
 */
export async function getAllWorkSlugs(): Promise<string[]> {
  const db = createServiceClient();
  const { data, error } = await db
    .from("works")
    .select("id")
    .eq("is_published", true);

  if (error) {
    console.error("[works] getAllWorkSlugs error:", error.message);
    return [];
  }

  return (data ?? []).map((row) =>
    (row as { id: string }).id.replace(/^work_/, "")
  );
}

// ─── Single work queries ──────────────────────────────────────────────────────

/**
 * Fetches a full work record with all joined relations:
 * - color_assignments
 * - work_people (with nested people)
 * - work_studios (with nested studios)
 * - work_awards (with nested awards and people)
 *
 * Returns null if not found or not published.
 */
export async function getWorkBySlug(slug: string): Promise<WorkFull | null> {
  const db = createServiceClient();
  const workId = `work_${slug}`;

  const { data, error } = await db
    .from("works")
    .select(
      `
      *,
      color_assignments(*),
      work_people(role, billing_order, people(*)),
      work_studios(studios(*)),
      work_awards(*, awards(*), people(id, name))
    `
    )
    .eq("id", workId)
    .eq("is_published", true)
    .single();

  if (error) {
    if (error.code !== "PGRST116") {
      // PGRST116 = row not found, expected; other errors are unexpected
      console.error(`[works] getWorkBySlug(${slug}) error:`, error.message);
    }
    return null;
  }

  return data as unknown as WorkFull;
}

// ─── Collection queries ───────────────────────────────────────────────────────

/**
 * Fetches works by Prisma color ID, returning lightweight WorkCards.
 * Used by color pages (/colors/[slug]).
 *
 * @param colorId   Canonical Prisma palette v1.2 color ID
 * @param limit     Max results (default 100)
 * @param offset    Pagination offset (default 0)
 */
export async function getWorksByColor(
  colorId: PrismaColorId,
  limit = 100,
  offset = 0
): Promise<WorkCard[]> {
  const db = createServiceClient();

  const { data, error } = await db
    .from("works_with_color")
    .select(
      "id, title, year, countries, tmdb_poster_path, criterion_title, color_iconico, tier, tier_rank, numeric_score, prestige_score, global_rank"
    )
    .eq("color_iconico", colorId)
    .order("tier", { ascending: true }) // canon < core < strong < peripheral
    .order("tier_rank", { ascending: true, nullsFirst: false })
    .order("numeric_score", { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) {
    console.error(`[works] getWorksByColor(${colorId}) error:`, error.message);
    return [];
  }

  return (data ?? []) as unknown as WorkCard[];
}

/**
 * Fetches works by Prisma color ID, grouped by tier.
 * Used by color pages to display canon/core/strong/peripheral sections.
 */
export async function getWorksByColorTiered(colorId: PrismaColorId): Promise<{
  canon: WorkCard[];
  core: WorkCard[];
  strong: WorkCard[];
  peripheral: WorkCard[];
}> {
  const all = await getWorksByColor(colorId, 300, 0);

  const grouped: Record<ColorTier, WorkCard[]> = {
    canon: [],
    core: [],
    strong: [],
    peripheral: [],
    uncertain: [],
  };

  for (const work of all) {
    const tier = (work.tier ?? "uncertain") as ColorTier;
    if (tier in grouped) {
      grouped[tier].push(work);
    }
  }

  return grouped;
}

/**
 * Fetches all published works by a specific person in a given role.
 * Used by person pages (/people/[slug]).
 *
 * @param personId  Canonical person ID (e.g. "person_sofia-coppola")
 * @param role      Role to filter by (director, cinematography, actor, etc.)
 */
export async function getWorksByPerson(
  personId: string,
  role?: PersonRole
): Promise<WorkCard[]> {
  const db = createServiceClient();

  let query = db
    .from("work_people")
    .select(
      `
      role,
      works!inner(
        id, title, year, countries, tmdb_poster_path, criterion_title, is_published,
        color_assignments(color_iconico, tier, tier_rank, numeric_score)
      )
    `
    )
    .eq("person_id", personId)
    .eq("works.is_published", true);

  if (role) {
    query = query.eq("role", role);
  }

  const { data, error } = await query;

  if (error) {
    console.error(`[works] getWorksByPerson(${personId}) error:`, error.message);
    return [];
  }

  return ((data ?? []) as unknown[]).map((row: unknown) => {
    const r = row as {
      role: PersonRole;
      works: {
        id: string;
        title: string;
        year: number | null;
        countries: string[];
        tmdb_poster_path: string | null;
        criterion_title: boolean;
        color_assignments: Array<{
          color_iconico: PrismaColorId | null;
          tier: ColorTier | null;
          tier_rank: number | null;
          numeric_score: number | null;
        }> | null;
      };
    };
    const ca = r.works.color_assignments?.[0] ?? null;
    return {
      id: r.works.id,
      title: r.works.title,
      year: r.works.year,
      countries: r.works.countries,
      tmdb_poster_path: r.works.tmdb_poster_path,
      criterion_title: r.works.criterion_title,
      color_iconico: ca?.color_iconico ?? null,
      tier: ca?.tier ?? null,
      tier_rank: ca?.tier_rank ?? null,
      numeric_score: ca?.numeric_score ?? null,
      prestige_score: null,
      global_rank: null,
    } as WorkCard;
  });
}

/**
 * Fetches all published works by a studio.
 * Used by studio pages (/studios/[slug]).
 */
export async function getWorksByStudio(studioId: string): Promise<WorkCard[]> {
  const db = createServiceClient();

  const { data, error } = await db
    .from("work_studios")
    .select(
      `
      works!inner(
        id, title, year, countries, tmdb_poster_path, criterion_title, is_published,
        color_assignments(color_iconico, tier, tier_rank, numeric_score)
      )
    `
    )
    .eq("studio_id", studioId)
    .eq("works.is_published", true);

  if (error) {
    console.error(`[works] getWorksByStudio(${studioId}) error:`, error.message);
    return [];
  }

  return ((data ?? []) as unknown[]).map((row: unknown) => {
    const r = row as {
      works: {
        id: string;
        title: string;
        year: number | null;
        countries: string[];
        tmdb_poster_path: string | null;
        criterion_title: boolean;
        color_assignments: Array<{
          color_iconico: PrismaColorId | null;
          tier: ColorTier | null;
          tier_rank: number | null;
          numeric_score: number | null;
        }> | null;
      };
    };
    const ca = r.works.color_assignments?.[0] ?? null;
    return {
      id: r.works.id,
      title: r.works.title,
      year: r.works.year,
      countries: r.works.countries,
      tmdb_poster_path: r.works.tmdb_poster_path,
      criterion_title: r.works.criterion_title,
      color_iconico: ca?.color_iconico ?? null,
      tier: ca?.tier ?? null,
      tier_rank: ca?.tier_rank ?? null,
      numeric_score: ca?.numeric_score ?? null,
      prestige_score: null,
      global_rank: null,
    } as WorkCard;
  });
}

/**
 * Fetches published works from a specific country.
 * Used by country pages (/countries/[iso]).
 *
 * @param isoCode  ISO 3166-1 alpha-2 code (e.g. "FR", "JP")
 */
export async function getWorksByCountry(
  isoCode: string,
  limit = 100,
  offset = 0
): Promise<WorkCard[]> {
  const db = createServiceClient();

  const { data, error } = await db
    .from("works_with_color")
    .select(
      "id, title, year, countries, tmdb_poster_path, criterion_title, color_iconico, tier, tier_rank, numeric_score, prestige_score, global_rank"
    )
    .contains("countries", [isoCode.toUpperCase()])
    .order("prestige_score", { ascending: false, nullsFirst: false })
    .range(offset, offset + limit - 1);

  if (error) {
    console.error(`[works] getWorksByCountry(${isoCode}) error:`, error.message);
    return [];
  }

  return (data ?? []) as unknown as WorkCard[];
}

/**
 * Fetches published works from a given decade.
 * Used by decade pages (/decades/[decade]).
 *
 * @param decade  Decade start year (e.g. 1970 for the 1970s)
 */
export async function getWorksByDecade(
  decade: number,
  limit = 100,
  offset = 0
): Promise<WorkCard[]> {
  const db = createServiceClient();
  const yearStart = decade;
  const yearEnd = decade + 9;

  const { data, error } = await db
    .from("works_with_color")
    .select(
      "id, title, year, countries, tmdb_poster_path, criterion_title, color_iconico, tier, tier_rank, numeric_score, prestige_score, global_rank"
    )
    .gte("year", yearStart)
    .lte("year", yearEnd)
    .order("prestige_score", { ascending: false, nullsFirst: false })
    .range(offset, offset + limit - 1);

  if (error) {
    console.error(
      `[works] getWorksByDecade(${decade}s) error:`,
      error.message
    );
    return [];
  }

  return (data ?? []) as unknown as WorkCard[];
}

/**
 * Fetches top-ranked works for ranking pages (/rankings/films).
 *
 * @param limit    Max results (default 100)
 * @param context  Ranking context: 'global' or 'country_{iso}' (default 'global')
 */
export async function getTopRankedWorks(
  limit = 100,
  context = "global"
): Promise<WorkCard[]> {
  const db = createServiceClient();

  const { data, error } = await db
    .from("ranking_scores")
    .select(
      `
      score, rank,
      works!inner(
        id, title, year, countries, tmdb_poster_path, criterion_title, is_published,
        color_assignments(color_iconico, tier, tier_rank, numeric_score)
      )
    `
    )
    .eq("entity_type", "work")
    .eq("context", context)
    .eq("works.is_published", true)
    .order("score", { ascending: false })
    .limit(limit);

  if (error) {
    console.error(`[works] getTopRankedWorks(${context}) error:`, error.message);
    return [];
  }

  return ((data ?? []) as unknown[]).map((row: unknown) => {
    const r = row as {
      score: number;
      rank: number | null;
      works: {
        id: string;
        title: string;
        year: number | null;
        countries: string[];
        tmdb_poster_path: string | null;
        criterion_title: boolean;
        color_assignments: Array<{
          color_iconico: PrismaColorId | null;
          tier: ColorTier | null;
          tier_rank: number | null;
          numeric_score: number | null;
        }> | null;
      };
    };
    const ca = r.works.color_assignments?.[0] ?? null;
    return {
      id: r.works.id,
      title: r.works.title,
      year: r.works.year,
      countries: r.works.countries,
      tmdb_poster_path: r.works.tmdb_poster_path,
      criterion_title: r.works.criterion_title,
      color_iconico: ca?.color_iconico ?? null,
      tier: ca?.tier ?? null,
      tier_rank: ca?.tier_rank ?? null,
      numeric_score: ca?.numeric_score ?? null,
      prestige_score: r.score,
      global_rank: r.rank,
    } as WorkCard;
  });
}

// ─── Dimension category queries ───────────────────────────────────────────────

/**
 * Get all films with a specific visual rhythm.
 * Used by /ritmo/[slug] category pages.
 */
export async function getWorksByRhythm(
  rhythm: string,
  limit = 100,
  offset = 0
): Promise<WorkCard[]> {
  const db = createServiceClient()
  
  // Development mode: show all films (published or unpublished) if in dev environment
  const isDev = import.meta.env.DEV || process.env.NODE_ENV === 'development'
  
  let query = db
    .from('color_assignments')
    .select(`
      work_id,
      ritmo_visual,
      color_iconico,
      tier,
      tier_rank,
      numeric_score,
      works!inner(id, title, year, countries, tmdb_poster_path, criterion_title, is_published)
    `)
    .eq('ritmo_visual', rhythm)
    .eq('review_status', 'approved')
    .order('numeric_score', { ascending: false, nullsFirst: false })
    .range(offset, offset + limit - 1)
  
  // Only filter by is_published in production
  if (!isDev) {
    query = query.eq('works.is_published', true)
  }
  
  const { data, error } = await query
  
  if (error) {
    console.error(`[works] getWorksByRhythm(${rhythm}) error:`, error.message)
    return []
  }
  
  // Fallback: if no approved results, try without review_status filter
  let finalData = data ?? []
  if (finalData.length === 0) {
    const fallbackQuery = db
      .from('color_assignments')
      .select(`
        work_id,
        ritmo_visual,
        color_iconico,
        tier,
        tier_rank,
        numeric_score,
        works!inner(id, title, year, countries, tmdb_poster_path, criterion_title, is_published)
      `)
      .eq('ritmo_visual', rhythm)
      .order('numeric_score', { ascending: false, nullsFirst: false })
      .range(offset, offset + limit - 1)
    
    if (!isDev) {
      fallbackQuery.eq('works.is_published', true)
    }
    
    const fallback = await fallbackQuery
    if (!fallback.error) {
      finalData = fallback.data ?? []
    }
  }
  
  return (finalData as unknown[]).map((row: unknown) => {
    const r = row as {
      work_id: string
      color_iconico: PrismaColorId
      tier: ColorTier | null
      tier_rank: number | null
      numeric_score: number | null
      works: {
        id: string
        title: string
        year: number | null
        countries: string[]
        tmdb_poster_path: string | null
        criterion_title: boolean
      }
    }
    return {
      id: r.works.id,
      title: r.works.title,
      year: r.works.year,
      countries: r.works.countries,
      tmdb_poster_path: r.works.tmdb_poster_path,
      criterion_title: r.works.criterion_title,
      color_iconico: r.color_iconico,
      tier: r.tier,
      tier_rank: r.tier_rank,
      numeric_score: r.numeric_score,
      prestige_score: null,
      global_rank: null,
    } as WorkCard
  })
}

/**
 * Get all films with a specific emotional temperature.
 * Used by /temperatura/[slug] category pages.
 */
export async function getWorksByTemperature(
  temperature: string,
  limit = 100,
  offset = 0
): Promise<WorkCard[]> {
  const db = createServiceClient()
  
  const isDev = import.meta.env.DEV || process.env.NODE_ENV === 'development'
  
  let query = db
    .from('color_assignments')
    .select(`
      work_id,
      temperatura_emocional,
      color_iconico,
      tier,
      tier_rank,
      numeric_score,
      works!inner(id, title, year, countries, tmdb_poster_path, criterion_title, is_published)
    `)
    .eq('temperatura_emocional', temperature)
    .eq('review_status', 'approved')
    .order('numeric_score', { ascending: false, nullsFirst: false })
    .range(offset, offset + limit - 1)
  
  if (!isDev) {
    query = query.eq('works.is_published', true)
  }
  
  const { data, error } = await query
  
  if (error) {
    console.error(`[works] getWorksByTemperature(${temperature}) error:`, error.message)
    return []
  }
  
  // Fallback: if no approved results, try without review_status filter
  let finalData = data ?? []
  if (finalData.length === 0) {
    const fallbackQuery = db
      .from('color_assignments')
      .select(`
        work_id,
        temperatura_emocional,
        color_iconico,
        tier,
        tier_rank,
        numeric_score,
        works!inner(id, title, year, countries, tmdb_poster_path, criterion_title, is_published)
      `)
      .eq('temperatura_emocional', temperature)
      .order('numeric_score', { ascending: false, nullsFirst: false })
      .range(offset, offset + limit - 1)
    
    if (!isDev) {
      fallbackQuery.eq('works.is_published', true)
    }
    
    const fallback = await fallbackQuery
    if (!fallback.error) {
      finalData = fallback.data ?? []
    }
  }
  
  return (finalData as unknown[]).map((row: unknown) => {
    const r = row as {
      work_id: string
      color_iconico: PrismaColorId
      tier: ColorTier | null
      tier_rank: number | null
      numeric_score: number | null
      works: {
        id: string
        title: string
        year: number | null
        countries: string[]
        tmdb_poster_path: string | null
        criterion_title: boolean
      }
    }
    return {
      id: r.works.id,
      title: r.works.title,
      year: r.works.year,
      countries: r.works.countries,
      tmdb_poster_path: r.works.tmdb_poster_path,
      criterion_title: r.works.criterion_title,
      color_iconico: r.color_iconico,
      tier: r.tier,
      tier_rank: r.tier_rank,
      numeric_score: r.numeric_score,
      prestige_score: null,
      global_rank: null,
    } as WorkCard
  })
}

/**
 * Get all films with a specific abstraction level.
 * Used by /abstraccion/[slug] category pages.
 */
export async function getWorksByAbstraction(
  abstraction: string,
  limit = 100,
  offset = 0
): Promise<WorkCard[]> {
  const db = createServiceClient()
  
  const isDev = import.meta.env.DEV || process.env.NODE_ENV === 'development'
  
  let query = db
    .from('color_assignments')
    .select(`
      work_id,
      grado_abstraccion,
      color_iconico,
      tier,
      tier_rank,
      numeric_score,
      works!inner(id, title, year, countries, tmdb_poster_path, criterion_title, is_published)
    `)
    .eq('grado_abstraccion', abstraction)
    .eq('review_status', 'approved')
    .order('numeric_score', { ascending: false, nullsFirst: false })
    .range(offset, offset + limit - 1)
  
  if (!isDev) {
    query = query.eq('works.is_published', true)
  }
  
  const { data, error } = await query
  
  if (error) {
    console.error(`[works] getWorksByAbstraction(${abstraction}) error:`, error.message)
    return []
  }
  
  // Fallback: if no approved results, try without review_status filter
  let finalData = data ?? []
  if (finalData.length === 0) {
    const fallbackQuery = db
      .from('color_assignments')
      .select(`
        work_id,
        grado_abstraccion,
        color_iconico,
        tier,
        tier_rank,
        numeric_score,
        works!inner(id, title, year, countries, tmdb_poster_path, criterion_title, is_published)
      `)
      .eq('grado_abstraccion', abstraction)
      .order('numeric_score', { ascending: false, nullsFirst: false })
      .range(offset, offset + limit - 1)
    
    if (!isDev) {
      fallbackQuery.eq('works.is_published', true)
    }
    
    const fallback = await fallbackQuery
    if (!fallback.error) {
      finalData = fallback.data ?? []
    }
  }
  
  return (finalData as unknown[]).map((row: unknown) => {
    const r = row as {
      work_id: string
      color_iconico: PrismaColorId
      tier: ColorTier | null
      tier_rank: number | null
      numeric_score: number | null
      works: {
        id: string
        title: string
        year: number | null
        countries: string[]
        tmdb_poster_path: string | null
        criterion_title: boolean
      }
    }
    return {
      id: r.works.id,
      title: r.works.title,
      year: r.works.year,
      countries: r.works.countries,
      tmdb_poster_path: r.works.tmdb_poster_path,
      criterion_title: r.works.criterion_title,
      color_iconico: r.color_iconico,
      tier: r.tier,
      tier_rank: r.tier_rank,
      numeric_score: r.numeric_score,
      prestige_score: null,
      global_rank: null,
    } as WorkCard
  })
}
