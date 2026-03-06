/**
 * src/lib/festivalUtils.ts
 * ─────────────────────────
 * Utilities for festival logo display and monogram generation.
 *
 * logo_path in DB can be:
 *   - A local asset path (e.g. /logos/festivals/cannes.png) — starts with '/logos/'
 *   - A full URL (Wikipedia/Wikimedia SVG thumbnail) — starts with 'http'
 *   - A TMDB-style path (e.g. /krQ8RCXPmQHmJ50gTEplxg3p588.png)
 *   - null → use CSS monogram fallback
 */

export function getFestivalLogoUrl(logoPath: string | null | undefined): string | null {
  if (!logoPath) return null;
  // Local asset (served from /public)
  if (logoPath.startsWith("/logos/")) return logoPath;
  // Full URL (Wikipedia SVG thumbnails)
  if (logoPath.startsWith("http")) return logoPath;
  // TMDB company logo path
  return `https://image.tmdb.org/t/p/w92${logoPath}`;
}

/** Returns true when the logo is a locally hosted file (needs invert filter). */
export function isFestivalLogoLocal(logoPath: string | null | undefined): boolean {
  return !!logoPath && logoPath.startsWith("/logos/");
}

// Words to exclude when generating monograms
const STOP_WORDS = new Set([
  "of", "the", "and", "de", "du", "di", "del", "la", "le", "les",
  "film", "festival", "awards", "award", "international", "prize",
  "cinema", "film", "a",
]);

/**
 * Generate a 1–3 character monogram from a festival name.
 * Examples:
 *   "Cannes Film Festival"              → "C"
 *   "Academy Awards"                    → "AA"
 *   "Golden Globe Awards"               → "GG"
 *   "San Sebastián International..."    → "SS"
 *   "BAFTA Film Awards"                 → "BA"
 *   "Bodil Awards"                      → "B"
 */
export function getFestivalMonogram(name: string): string {
  const words = name
    .split(/[\s\-]+/)
    .map((w) => w.replace(/[^A-Za-zÀ-ÿ]/g, ""))
    .filter((w) => w.length > 0 && !STOP_WORDS.has(w.toLowerCase()));

  if (words.length === 0) return name[0]?.toUpperCase() ?? "?";

  // If first word is all-caps acronym (e.g. "BAFTA", "FIPRESCI"), use first 2 chars
  if (words[0] === words[0].toUpperCase() && words[0].length >= 2) {
    return words[0].slice(0, 2).toUpperCase();
  }

  // Up to 2 significant words
  return words
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}
