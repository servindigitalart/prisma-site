/**
 * src/lib/seo/personSeo.ts
 * ────────────────────────
 * SEO utilities for person (filmmaker) pages.
 */

import type { PersonRole } from '../db/types';

const SITE_URL = 'https://prisma.film';
const TMDB_IMAGE = 'https://image.tmdb.org/t/p';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface PersonSeoInput {
  name: string;
  id: string;
  bio: string | null;
  nationality: string[] | null | undefined;
  birth_year: number | null;
  death_year: number | null;
  profile_path: string | null;
  imdb_id?: string | null;
  wikidata_id?: string | null;
  filmography: Array<{ role: string; work: { id: string; title: string; year: number | null } }>;
}

export interface PersonSeoData {
  title: string;
  description: string;
  ogImage: string;
  ogType: string;
  jsonLd: Record<string, unknown>;
}

// ─── Role label (Spanish) ─────────────────────────────────────────────────────

const ROLE_LABELS: Record<PersonRole, string> = {
  director: 'director/a',
  cinematography: 'director/a de fotografía',
  actor: 'actor/actriz',
  writer: 'guionista',
  editor: 'editor/a',
  composer: 'compositor/a',
  production_design: 'director/a de arte',
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildProfileUrl(profilePath: string | null): string | null {
  if (!profilePath) return null;
  return `${TMDB_IMAGE}/w500${profilePath}`;
}

function buildDescription(input: PersonSeoInput, primaryRole?: string): string {
  if (input.bio) {
    return input.bio.length > 155 ? input.bio.slice(0, 152) + '…' : input.bio;
  }

  const roleLabel = primaryRole ? (ROLE_LABELS[primaryRole as PersonRole] ?? 'cineasta') : 'cineasta';
  const filmCount = input.filmography.length;
  const nat = input.nationality?.length ? ` (${input.nationality.join(', ')})` : '';

  return `${input.name}${nat}, ${roleLabel} con ${filmCount} película${filmCount !== 1 ? 's' : ''} en el catálogo PRISMA.`;
}

// ─── JSON-LD builder ──────────────────────────────────────────────────────────

function buildJsonLd(input: PersonSeoInput, description: string, profileUrl: string | null): Record<string, unknown> {
  const personSlug = input.id.replace(/^person_/, '');
  const personUrl = `${SITE_URL}/people/${personSlug}`;

  const schema: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: input.name,
    url: personUrl,
    description,
  };

  if (profileUrl) {
    schema.image = profileUrl;
  }

  if (input.nationality?.length) {
    schema.nationality = input.nationality.map((n) => ({
      '@type': 'Country',
      name: n,
    }));
  }

  if (input.birth_year) {
    schema.birthDate = String(input.birth_year);
  }
  if (input.death_year) {
    schema.deathDate = String(input.death_year);
  }

  // sameAs — external profile links
  const sameAs: string[] = [];
  if (input.imdb_id) {
    sameAs.push(`https://www.imdb.com/name/${input.imdb_id}/`);
  }
  if (input.wikidata_id) {
    sameAs.push(`https://www.wikidata.org/wiki/${input.wikidata_id}`);
  }
  if (sameAs.length) {
    schema.sameAs = sameAs;
  }

  // Top 5 known-for works
  const topWorks = input.filmography
    .filter((e) => e.role === 'director')
    .slice(0, 5);

  if (topWorks.length === 0) {
    // Fall back to any role
    topWorks.push(...input.filmography.slice(0, 5));
  }

  if (topWorks.length) {
    schema.knowsAbout = topWorks.map((e) => ({
      '@type': 'Movie',
      name: e.work.title,
      dateCreated: e.work.year ? String(e.work.year) : undefined,
    }));
  }

  return schema;
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function buildPersonSeo(input: PersonSeoInput, primaryRole?: string): PersonSeoData {
  const profileUrl = buildProfileUrl(input.profile_path);
  const description = buildDescription(input, primaryRole);
  const ogImage = profileUrl ?? `${SITE_URL}/og-default.jpg`;

  return {
    title: `${input.name} — PRISMA`,
    description,
    ogImage,
    ogType: 'profile',
    jsonLd: buildJsonLd(input, description, profileUrl),
  };
}
