/**
 * src/lib/loaders/loadPerson.ts
 * ─────────────────────────────
 * Dual-mode person loader: Supabase primary → filesystem fallback.
 *
 * The filesystem shape is intentionally lean (pipeline/normalized/people/*.json
 * only has name, roles, works, ids). We reconstruct filmography by scanning
 * the normalized works directory.
 */

import fs from 'node:fs';
import path from 'node:path';
import { isSupabaseConfigured } from '../db/client';

// ─── Filesystem types ─────────────────────────────────────────────────────────

export interface FilesystemFilmographyEntry {
  work: {
    id: string;
    title: string;
    year: number | null;
    tmdb_poster_path: string | null;
  };
  role: string;
  color: { color_iconico: string; tier: string | null } | null;
}

export interface FilesystemPerson {
  _source: 'filesystem';
  id: string;
  name: string;
  birth_year: number | null;
  death_year: number | null;
  bio: string | null;
  nationality: string[];
  profile_path: string | null;
  filmography: FilesystemFilmographyEntry[];
  color_profile: null; // not computed at filesystem level
}

// ─── Path helpers ─────────────────────────────────────────────────────────────

const PEOPLE_DIR = path.resolve('pipeline/normalized/people');
const WORKS_DIR  = path.resolve('pipeline/normalized/works');

function readJson(filePath: string): Record<string, unknown> | null {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

// ─── Filesystem loader ────────────────────────────────────────────────────────

export function loadPersonFromFilesystem(slug: string): FilesystemPerson | null {
  const personId = `person_${slug}`;
  const personPath = path.join(PEOPLE_DIR, `${personId}.json`);

  const raw = readJson(personPath);
  if (!raw) return null;

  // Build filmography by scanning works that reference this person
  const filmography: FilesystemFilmographyEntry[] = [];
  const personName = (raw.name as string) ?? slug;

  if (fs.existsSync(WORKS_DIR)) {
    const workFiles = fs.readdirSync(WORKS_DIR).filter((f) => f.endsWith('.json'));

    for (const file of workFiles) {
      const work = readJson(path.join(WORKS_DIR, file));
      if (!work) continue;

      const people = (work.people ?? {}) as Record<string, string[]>;
      const roleMap: Record<string, string> = {
        director:       'director',
        cinematography: 'cinematography',
        writer:         'writer',
        editor:         'editor',
        composer:       'composer',
        cast:           'actor',
      };

      for (const [sourceRole, dbRole] of Object.entries(roleMap)) {
        const ids = (people[sourceRole] ?? []) as string[];
        // Match by ID first, then by name (case-insensitive) as fallback
        const matchesId = ids.includes(personId);
        const matchesName = ids.some(id => {
          const idName = id.replace(/^person_/, '').split('-').join(' ').toLowerCase();
          return idName === personName.toLowerCase();
        });
        
        if (matchesId || matchesName) {
          const palette = work.prisma_palette as { primary?: string } | null;
          filmography.push({
            work: {
              id: work.id as string,
              title: work.title as string,
              year: (work.year as number | null) ?? null,
              tmdb_poster_path: ((work.media as Record<string, unknown> | null)?.poster_path as string | null) ?? null,
            },
            role: dbRole,
            color: palette?.primary
              ? { color_iconico: palette.primary, tier: null }
              : null,
          });
          break; // one entry per work, first matching role wins
        }
      }
    }
  }

  // Sort filmography by year descending
  filmography.sort((a, b) => (b.work.year ?? 0) - (a.work.year ?? 0));

  return {
    _source: 'filesystem',
    id: personId,
    name: personName,
    birth_year: (raw.birth_year as number | null) ?? null,
    death_year: (raw.death_year as number | null) ?? null,
    bio: (raw.bio as string | null) ?? null,
    nationality: (raw.nationality as string[]) ?? [],
    profile_path: (raw.profile_path as string | null) ?? null,
    filmography,
    color_profile: null,
  };
}

// ─── Public async loader (mirrors loadWorkBySlugAsync pattern) ────────────────

export async function loadPersonBySlugAsync(
  slug: string
): Promise<import('../db/types').PersonFull | FilesystemPerson | null> {
  // Try Supabase first
  if (isSupabaseConfigured()) {
    try {
      const { getPersonBySlug } = await import('../db/people');
      const result = await getPersonBySlug(slug);
      if (result) return result;
    } catch {
      // Fall through to filesystem
    }
  }

  // Filesystem fallback
  return loadPersonFromFilesystem(slug);
}
