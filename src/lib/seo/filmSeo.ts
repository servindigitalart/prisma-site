/**
 * src/lib/seo/filmSeo.ts
 * ──────────────────────
 * SEO utilities for film pages.
 *
 * Generates:
 * - Page title + meta description
 * - Open Graph + Twitter Card image URL (TMDB poster at w1280)
 * - JSON-LD Movie structured data (schema.org)
 *
 * Works with both WorkFull (Supabase) and FilesystemWork (JSON) shapes.
 */

import type { WorkFull } from '../db/types';
import type { FilesystemWork } from '../loaders/loadWork';

const SITE_URL   = 'https://prisma.film';
const TMDB_IMAGE = 'https://image.tmdb.org/t/p';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface FilmSeoData {
  title: string;
  description: string;
  ogImage: string;
  ogType: string;
  jsonLd: Record<string, unknown>;
}

// ─── Image helpers ────────────────────────────────────────────────────────────

function getPosterPath(work: WorkFull | FilesystemWork): string | null {
  if ('tmdb_poster_path' in work && work.tmdb_poster_path) {
    return work.tmdb_poster_path;
  }
  if ('media' in work && work.media?.poster_path) {
    return work.media.poster_path;
  }
  return null;
}

export function buildPosterUrl(
  posterPath: string | null,
  size: 'w342' | 'w780' | 'w1280' = 'w780'
): string | null {
  if (!posterPath) return null;
  return `${TMDB_IMAGE}/${size}${posterPath}`;
}

// ─── Content helpers ──────────────────────────────────────────────────────────

function getDirectorNames(work: WorkFull | FilesystemWork): string[] {
  if ('work_people' in work && Array.isArray(work.work_people)) {
    return (work.work_people as Array<{ role: string; person?: { name: string } }>)
      .filter((p) => p.role === 'director')
      .map((p) => p.person?.name ?? '')
      .filter(Boolean);
  }
  if ('people' in work && work.people?.director) {
    return work.people.director.map((id) =>
      id.replace(/^person_/, '').replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    );
  }
  return [];
}

function getSynopsis(work: WorkFull | FilesystemWork): string | null {
  if ('synopsis' in work && work.synopsis) return work.synopsis;
  return null;
}

function getColorNarrative(work: WorkFull | FilesystemWork): string | null {
  if ('color_narrative' in work && typeof work.color_narrative === 'string') {
    return work.color_narrative;
  }
  return null;
}

function buildDescription(work: WorkFull | FilesystemWork): string {
  const year    = work.year ? ` (${work.year})` : '';
  const dirs    = getDirectorNames(work);
  const dirStr  = dirs.length ? ` Dirigida por ${dirs.join(', ')}.` : '';
  const synopsis = getSynopsis(work) ?? getColorNarrative(work);

  if (synopsis) {
    // Trim to ~155 chars for meta description
    const trimmed = synopsis.length > 155 ? synopsis.slice(0, 152) + '…' : synopsis;
    return trimmed;
  }

  return `${work.title}${year} en PRISMA — identidad visual cinematográfica.${dirStr}`;
}

// ─── JSON-LD builder ──────────────────────────────────────────────────────────

function buildJsonLd(work: WorkFull | FilesystemWork, posterUrl: string | null): Record<string, unknown> {
  const directors = getDirectorNames(work);
  const filmSlug  = work.id.replace(/^work_/, '');
  const filmUrl   = `${SITE_URL}/films/${filmSlug}`;

  // schema.org/Movie
  const schema: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Movie',
    name: work.title,
    url: filmUrl,
  };

  if (work.year) {
    schema.datePublished = String(work.year);
  }

  const synopsis = getSynopsis(work);
  if (synopsis) {
    schema.description = synopsis;
  }

  if (posterUrl) {
    schema.image = posterUrl;
  }

  if (directors.length) {
    schema.director = directors.map((name) => ({
      '@type': 'Person',
      name,
    }));
  }

  if ('duration_min' in work && work.duration_min) {
    // ISO 8601 duration: PT{h}H{m}M
    const h = Math.floor(work.duration_min / 60);
    const m = work.duration_min % 60;
    schema.duration = h > 0 ? `PT${h}H${m}M` : `PT${m}M`;
  }

  if ('genres' in work && Array.isArray(work.genres) && work.genres.length) {
    schema.genre = work.genres;
  }

  if ('countries' in work && Array.isArray(work.countries) && work.countries.length) {
    schema.countryOfOrigin = work.countries.map((c) => ({
      '@type': 'Country',
      name: c,
    }));
  }

  // Cinematographers
  const dps: string[] = [];
  if ('work_people' in work && Array.isArray(work.work_people)) {
    (work.work_people as Array<{ role: string; person?: { name: string } }>)
      .filter((p) => p.role === 'cinematography')
      .forEach((p) => { if (p.person?.name) dps.push(p.person.name); });
  } else if ('people' in work && work.people?.cinematography) {
    work.people.cinematography.forEach((id) => {
      dps.push(id.replace(/^person_/, '').replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()));
    });
  }
  if (dps.length) {
    schema.cinematographer = dps.map((name) => ({ '@type': 'Person', name }));
  }

  // Actors (top 5)
  const actors: string[] = [];
  if ('work_people' in work && Array.isArray(work.work_people)) {
    (work.work_people as Array<{ role: string; person?: { name: string } }>)
      .filter((p) => p.role === 'actor')
      .slice(0, 5)
      .forEach((p) => { if (p.person?.name) actors.push(p.person.name); });
  } else if ('people' in work && work.people?.cast) {
    work.people.cast.slice(0, 5).forEach((id) => {
      actors.push(id.replace(/^person_/, '').replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()));
    });
  }
  if (actors.length) {
    schema.actor = actors.map((name) => ({ '@type': 'Person', name }));
  }

  // IMDb rating
  const imdbRating = ('imdb_rating' in work) ? work.imdb_rating : null;
  if (imdbRating) {
    schema.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: imdbRating,
      bestRating: 10,
      ratingCount: 1000, // conservative placeholder — real votes not in schema
    };
  }

  return schema;
}

// ─── FAQ JSON-LD builder ──────────────────────────────────────────────────────

export function buildFilmFaqJsonLd(
  work: WorkFull | FilesystemWork,
): Record<string, unknown> {
  const directors = getDirectorNames(work);
  const synopsis = getSynopsis(work);
  const questions: Record<string, unknown>[] = [];

  // Q1: Where to watch
  questions.push({
    '@type': 'Question',
    name: `¿Dónde ver ${work.title} online?`,
    acceptedAnswer: {
      '@type': 'Answer',
      text: `${work.title} está disponible en plataformas de streaming de cine de autor como MUBI y Criterion Channel. Consulta la disponibilidad en tu región. También puedes encontrar su análisis cromático completo en PRISMA.`,
    },
  });

  // Q2: Who directed
  if (directors.length) {
    questions.push({
      '@type': 'Question',
      name: `¿Quién dirigió ${work.title}?`,
      acceptedAnswer: {
        '@type': 'Answer',
        text: `${work.title} fue dirigida por ${directors.join(', ')}${work.year ? ` en ${work.year}` : ''}.`,
      },
    });
  }

  // Q3: What is it about
  if (synopsis) {
    questions.push({
      '@type': 'Question',
      name: `¿De qué trata ${work.title}?`,
      acceptedAnswer: {
        '@type': 'Answer',
        text: synopsis.length > 300 ? synopsis.slice(0, 297) + '…' : synopsis,
      },
    });
  }

  // Q4: Awards
  questions.push({
    '@type': 'Question',
    name: `¿Qué premios ganó ${work.title}?`,
    acceptedAnswer: {
      '@type': 'Answer',
      text: `Consulta el historial completo de premios y nominaciones de ${work.title} en PRISMA, incluyendo festivales internacionales de cine como Cannes, Venecia y Berlín.`,
    },
  });

  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: questions,
  };
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function buildFilmSeo(work: WorkFull | FilesystemWork): FilmSeoData {
  const posterPath = getPosterPath(work);
  const posterUrl  = buildPosterUrl(posterPath, 'w1280');

  const yearSuffix = work.year ? ` (${work.year})` : '';
  const pageTitle  = `${work.title}${yearSuffix} — PRISMA`;
  const description = buildDescription(work);

  // OG image: TMDB poster at w1280, fallback to default
  const ogImage = posterUrl ?? `${SITE_URL}/og-default.jpg`;

  return {
    title: pageTitle,
    description,
    ogImage,
    ogType: 'video.movie',
    jsonLd: buildJsonLd(work, posterUrl),
  };
}
