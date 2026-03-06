/**
 * src/lib/db/colors.ts
 * ─────────────────────
 * Functions for color-related data.
 *
 * Color doctrine (the 17 canonical colors) is read from the static JSON file
 * at build time — not from Supabase — since it's a versioned editorial asset.
 *
 * Color-to-film assignments are fetched from Supabase via works.ts.
 */

import { readFileSync } from "fs";
import { resolve } from "path";
import type { PrismaColorId, WorkCard } from "./types";
import { getWorksByColorTiered } from "./works";

// ─── Doctrine types ───────────────────────────────────────────────────────────

export interface ColorDoctrineEntry {
  id: PrismaColorId;
  hex: string;
  name: string;
  moods: string[];
  genre_associations: string[];
  cinematographer_signatures: string[];
  reference_examples: string[];
  cultural_context: string;
  cinematographic_notes: string;
}

export interface ColorDoctrine {
  version: string;
  last_updated: string;
  principles: Record<string, string>;
  colors: ColorDoctrineEntry[];
}

// ─── Load color doctrine (static, build-time) ────────────────────────────────

let _doctrinCache: ColorDoctrine | null = null;

/**
 * Loads the color doctrine JSON from the filesystem.
 * Cached after first load (build-time singleton).
 * Falls back gracefully if the file cannot be read.
 */
export function loadColorDoctrine(): ColorDoctrine | null {
  if (_doctrinCache) return _doctrinCache;

  const doctrinePaths = [
    // Try current symlink first
    "pipeline/doctrine/current/color_doctrine.json",
    // Fallback to versioned file
    "pipeline/doctrine/v1.1/color_doctrine.json",
  ];

  for (const relativePath of doctrinePaths) {
    try {
      const fullPath = resolve(process.cwd(), relativePath);
      const raw = readFileSync(fullPath, "utf-8");
      _doctrinCache = JSON.parse(raw) as ColorDoctrine;
      return _doctrinCache;
    } catch {
      // Try next path
    }
  }

  console.error("[colors] Could not load color doctrine from any known path.");
  return null;
}

/**
 * Returns the doctrine entry for a specific color ID.
 * Returns null if the color ID is not found in the doctrine.
 */
export function getColorProfile(
  colorId: string
): ColorDoctrineEntry | null {
  const doctrine = loadColorDoctrine();
  if (!doctrine) return null;

  return doctrine.colors.find((c) => c.id === colorId) ?? null;
}

/**
 * Returns all color doctrine entries.
 * Used by /colors/[slug] static paths and color index pages.
 */
export function getAllColorProfiles(): ColorDoctrineEntry[] {
  const doctrine = loadColorDoctrine();
  return doctrine?.colors ?? [];
}

/**
 * Returns all valid color IDs from the doctrine.
 * Includes monochromatic modes.
 */
export function getAllColorIds(): PrismaColorId[] {
  const chromatic = (getAllColorProfiles().map((c) => c.id) as PrismaColorId[]);
  const monochromatic: PrismaColorId[] = [
    "claroscuro_dramatico",
    "monocromatico_intimo",
  ];
  return [...chromatic, ...monochromatic];
}

// ─── Color page data (doctrine + tiered films) ───────────────────────────────

export interface ColorPageData {
  doctrine: ColorDoctrineEntry;
  films: {
    canon: WorkCard[];
    core: WorkCard[];
    strong: WorkCard[];
    peripheral: WorkCard[];
  };
}

/**
 * Aggregates everything needed to render a color page:
 * - Doctrine entry (hex, name, moods, etc.)
 * - Films grouped by tier (from Supabase)
 *
 * Returns null if the color ID is not found in doctrine.
 */
export async function getColorPageData(
  colorId: string
): Promise<ColorPageData | null> {
  const doctrine = getColorProfile(colorId);
  if (!doctrine) return null;

  const films = await getWorksByColorTiered(colorId as PrismaColorId);

  return { doctrine, films };
}
