/**
 * src/lib/seo/festivalSeo.ts
 * ──────────────────────────
 * SEO utilities for festival pages.
 */

const SITE_URL = 'https://prisma.film';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface FestivalSeoInput {
  id: string;
  name: string;
  description: string | null;
  city: string | null;
  country: string | null;
  founded_year: number | null;
  tier: string | null;
  logo_path: string | null;
  website: string | null;
}

export interface FestivalSeoData {
  title: string;
  description: string;
  ogImage: string;
  ogType: string;
  jsonLd: Record<string, unknown>;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildDescription(input: FestivalSeoInput): string {
  if (input.description) {
    return input.description.length > 155
      ? input.description.slice(0, 152) + '…'
      : input.description;
  }
  const loc = [input.city, input.country].filter(Boolean).join(', ');
  return `${input.name}${loc ? ` — ${loc}` : ''} — Historial de ganadores y nominados en el catálogo PRISMA.`;
}

// ─── JSON-LD builder ──────────────────────────────────────────────────────────

function buildJsonLd(input: FestivalSeoInput, description: string): Record<string, unknown> {
  const festSlug = input.id.replace(/^festival_/, '');
  const festUrl = `${SITE_URL}/festivals/${festSlug}`;

  const schema: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Event',
    name: input.name,
    url: festUrl,
    description,
    eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
  };

  if (input.city || input.country) {
    schema.location = {
      '@type': 'Place',
      name: input.city ?? input.country,
      address: {
        '@type': 'PostalAddress',
        ...(input.city ? { addressLocality: input.city } : {}),
        ...(input.country ? { addressCountry: input.country } : {}),
      },
    };
  }

  if (input.founded_year) {
    schema.startDate = String(input.founded_year);
  }

  if (input.website) {
    schema.sameAs = input.website;
  }

  return schema;
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function buildFestivalSeo(input: FestivalSeoInput): FestivalSeoData {
  const description = buildDescription(input);

  // Use festival logo if local, otherwise fallback
  const ogImage = input.logo_path?.startsWith('http')
    ? input.logo_path
    : `${SITE_URL}/og-default.jpg`;

  return {
    title: `${input.name} — PRISMA`,
    description,
    ogImage,
    ogType: 'website',
    jsonLd: buildJsonLd(input, description),
  };
}
