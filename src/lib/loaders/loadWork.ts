/**
 * src/lib/loaders/loadWork.ts
 * ────────────────────────────
 * Work data loader with dual-mode support:
 *
 *   1. SUPABASE MODE (preferred): when PUBLIC_SUPABASE_URL is set.
 *      Queries Supabase for published works. Used in production.
 *
 *   2. FILESYSTEM MODE (fallback): when Supabase is not configured.
 *      Reads JSON files from pipeline/normalized/works/.
 *      Used during local development before Supabase is set up.
 *
 * Existing pages (films/[slug].astro, etc.) continue to work unchanged —
 * the exported function signatures are preserved.
 */

import fs from "fs";
import path from "path";
import { isSupabaseConfigured, createServiceClient } from "../db/client";
import type { WorkFull } from "../db/types";

const WORKS_DIR = path.resolve("pipeline/normalized/works");

// ─── Type for filesystem JSON work (legacy) ──────────────────────────────────
// Matches the shape of pipeline/normalized/works/work_*.json files.
// This is the pre-Supabase format; kept for backward compatibility.

export interface FilesystemWork {
  id: string;
  type: string;
  title: string;
  original_title?: string;
  year?: number;
  duration_min?: number;
  countries?: string[];
  languages?: string[];
  genres?: string[];
  studios?: string[];
  people?: {
    director?: string[];
    cinematography?: string[];
    writer?: string[];
    cast?: string[];
  };
  ids?: {
    tmdb?: number;
    imdb?: string;
    wikidata?: string;
  };
  prisma_palette?: {
    primary: string;
    rank?: number;
    secondary?: string[];
    mode?: string;
    source?: string;
  };
  media?: {
    poster_path?: string | null;
    backdrop_path?: string | null;
    trailer_key?: string | null;
  };
  synopsis?: string | null;
  tagline?: string | null;
  tmdb_popularity?: number | null;
  where_to_watch?: Record<string, unknown>;
  color_summary?: Record<string, unknown>;
  color_narrative?: string;
  slug: string; // Injected by loadAllWorks()
}

// ─── Filesystem loaders (legacy / fallback) ───────────────────────────────────

function loadAllWorksFromFilesystem(): FilesystemWork[] {
  if (!fs.existsSync(WORKS_DIR)) {
    console.warn(`[loadWork] Works directory not found: ${WORKS_DIR}`);
    return [];
  }
  return fs
    .readdirSync(WORKS_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((file) => {
      const raw = fs.readFileSync(path.join(WORKS_DIR, file), "utf-8");
      const data = JSON.parse(raw) as Omit<FilesystemWork, "slug">;
      return {
        ...data,
        slug: file.replace("work_", "").replace(".json", ""),
      } as FilesystemWork;
    });
}

function loadWorkBySlugFromFilesystem(slug: string): FilesystemWork | null {
  const file = `work_${slug}.json`;
  const fullPath = path.join(WORKS_DIR, file);
  if (!fs.existsSync(fullPath)) return null;
  const data = JSON.parse(
    fs.readFileSync(fullPath, "utf-8")
  ) as Omit<FilesystemWork, "slug">;
  return { ...data, slug } as FilesystemWork;
}

// ─── Supabase loaders ─────────────────────────────────────────────────────────

async function loadAllWorksFromSupabase(): Promise<FilesystemWork[]> {
  try {
    const db = createServiceClient();
    const { data, error } = await db
      .from("works")
      .select("id, type, title, original_title, year")
      .eq("is_published", true);

    if (error) {
      console.error("[loadWork] Supabase loadAllWorks error:", error.message);
      return [];
    }

    return ((data ?? []) as Array<{
      id: string;
      type: string;
      title: string;
      original_title: string | null;
      year: number | null;
    }>).map((row) => ({
      id: row.id,
      type: row.type,
      title: row.title,
      original_title: row.original_title ?? undefined,
      year: row.year ?? undefined,
      slug: row.id.replace(/^work_/, ""),
    }));
  } catch (err) {
    console.error("[loadWork] Supabase connection failed:", err);
    return [];
  }
}

async function loadWorkBySlugFromSupabase(
  slug: string
): Promise<WorkFull | null> {
  try {
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
        work_awards(*, awards(*, festivals(id, name, country, tier, logo_path)), people(id, name))
      `
      )
      .eq("id", workId)
      .eq("is_published", true)
      .single();

    if (error) {
      if (error.code !== "PGRST116") {
        console.error(
          `[loadWork] Supabase getWorkBySlug(${slug}) error:`,
          error.message
        );
      }
      return null;
    }

    return data as unknown as WorkFull;
  } catch (err) {
    console.error("[loadWork] Supabase connection failed:", err);
    return null;
  }
}

// ─── Public API ───────────────────────────────────────────────────────────────
// These functions preserve the exact signature of the original loader so
// existing pages (films/[slug].astro etc.) continue to work unchanged.

/**
 * Returns all works for use in getStaticPaths().
 *
 * In SUPABASE MODE: queries published works from DB (returns lightweight objects with slug).
 * In FILESYSTEM MODE: reads all JSON files from pipeline/normalized/works/.
 *
 * Both modes return objects with at minimum: { slug, id, type, title, year }
 */
export function loadAllWorks(): FilesystemWork[] {
  // Note: getStaticPaths() in Astro supports top-level await only in .astro files.
  // This synchronous version is kept for backward compatibility with existing pages.
  // For new pages, prefer the async Supabase functions in src/lib/db/works.ts.
  return loadAllWorksFromFilesystem();
}

/**
 * Loads a single work by its URL slug.
 *
 * FILESYSTEM MODE only (synchronous, for backward compatibility).
 * For Supabase-backed pages, use getWorkBySlug() from src/lib/db/works.ts instead.
 *
 * Returns null if the work is not found.
 */
export function loadWorkBySlug(slug: string): FilesystemWork | null {
  return loadWorkBySlugFromFilesystem(slug);
}

/**
 * Async version of loadWorkBySlug that uses Supabase when configured,
 * falling back to the filesystem otherwise.
 *
 * Use this in SSR pages or Astro page components where async is supported.
 */
export async function loadWorkBySlugAsync(
  slug: string
): Promise<WorkFull | FilesystemWork | null> {
  if (isSupabaseConfigured()) {
    const supabaseResult = await loadWorkBySlugFromSupabase(slug);
    // Fall back to filesystem if Supabase doesn't have the work yet
    // (e.g. not yet published, or migration not run)
    if (supabaseResult) return supabaseResult;
  }
  return loadWorkBySlugFromFilesystem(slug);
}

/**
 * Async version of loadAllWorks that uses Supabase when configured.
 *
 * Use this in Astro .astro files with top-level await or in SSR contexts.
 */
export async function loadAllWorksAsync(): Promise<FilesystemWork[]> {
  if (isSupabaseConfigured()) {
    return loadAllWorksFromSupabase();
  }
  return loadAllWorksFromFilesystem();
}
