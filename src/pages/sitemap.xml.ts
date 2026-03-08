/**
 * src/pages/sitemap.xml.ts
 * ────────────────────────
 * Dynamic XML sitemap generated from Supabase data.
 * Covers all works (films), people, festivals, countries, and static pages.
 */
export const prerender = false;

import type { APIRoute } from 'astro';
import { createServiceClient, isSupabaseConfigured } from '../lib/db/client';

const SITE = 'https://prisma.film';

export const GET: APIRoute = async () => {
  if (!isSupabaseConfigured()) {
    return new Response('<!-- Supabase not configured -->', {
      status: 503,
      headers: { 'Content-Type': 'application/xml' },
    });
  }

  const db = createServiceClient();

  // Fetch all entity slugs in parallel
  const [worksRes, peopleRes, festivalsRes] = await Promise.all([
    db.from('works').select('id, updated_at').order('updated_at', { ascending: false }),
    db.from('people').select('id, updated_at').order('updated_at', { ascending: false }),
    (db as any).from('festivals').select('id').order('name', { ascending: true }),
  ]);

  // Static pages
  const staticPages = [
    { loc: '/', priority: '1.0', changefreq: 'daily' },
    { loc: '/rankings/films', priority: '0.9', changefreq: 'daily' },
    { loc: '/colors', priority: '0.8', changefreq: 'weekly' },
    { loc: '/people', priority: '0.8', changefreq: 'weekly' },
    { loc: '/festivals', priority: '0.8', changefreq: 'weekly' },
    { loc: '/countries', priority: '0.7', changefreq: 'weekly' },
    { loc: '/submit', priority: '0.4', changefreq: 'monthly' },
  ];

  // Decade pages
  const decades = ['1920s','1930s','1940s','1950s','1960s','1970s','1980s','1990s','2000s','2010s','2020s'];

  // Build URL entries
  const urls: string[] = [];

  // Static pages
  for (const page of staticPages) {
    urls.push(
      `  <url>\n    <loc>${SITE}${page.loc}</loc>\n    <changefreq>${page.changefreq}</changefreq>\n    <priority>${page.priority}</priority>\n  </url>`
    );
  }

  // Decades
  for (const decade of decades) {
    urls.push(
      `  <url>\n    <loc>${SITE}/decades/${decade}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>`
    );
  }

  // Films
  for (const work of worksRes.data ?? []) {
    const slug = (work.id as string).replace(/^work_/, '');
    const lastmod = work.updated_at ? new Date(work.updated_at as string).toISOString().split('T')[0] : '';
    urls.push(
      `  <url>\n    <loc>${SITE}/films/${slug}</loc>${lastmod ? `\n    <lastmod>${lastmod}</lastmod>` : ''}\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>`
    );
  }

  // People
  for (const person of peopleRes.data ?? []) {
    const slug = (person.id as string).replace(/^person_/, '');
    const lastmod = person.updated_at ? new Date(person.updated_at as string).toISOString().split('T')[0] : '';
    urls.push(
      `  <url>\n    <loc>${SITE}/people/${slug}</loc>${lastmod ? `\n    <lastmod>${lastmod}</lastmod>` : ''}\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>`
    );
  }

  // Festivals
  for (const fest of (festivalsRes.data ?? []) as Array<{ id: string }>) {
    const slug = fest.id.replace(/^festival_/, '');
    urls.push(
      `  <url>\n    <loc>${SITE}/festivals/${slug}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>`
    );
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>`;

  return new Response(xml, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  });
};
