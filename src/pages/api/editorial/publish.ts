import type { APIRoute } from 'astro';
import { createServiceClient } from '../../../lib/db/client';
import { generateArticleSlug, estimateReadingTime } from '../../../lib/seo/editorial';

// Simple API key auth — content engine sends this header
const PRISMA_API_SECRET = import.meta.env.PRISMA_INTERNAL_SECRET || 'prisma-internal-2025';

export const POST: APIRoute = async ({ request }) => {
  // Auth check
  const authHeader = request.headers.get('X-Prisma-Secret');
  if (authHeader !== PRISMA_API_SECRET) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  let body: any;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const {
    title,
    subtitle,
    body_html,
    body_text,
    excerpt,
    category = 'editorial',
    film_slug,
    film_title,
    film_year,
    director,
    color_slug,
    cover_image,
    og_image,
    tags = [],
    author = 'PRISMA Editorial',
    schema_type = 'Article',
    source_url,
    gemini_score,
    voice = 'editorial',
    meta_title,
    meta_desc,
    focus_keyword,
    published = false,
    featured = false,
    slug: providedSlug,
  } = body;

  if (!title || !body_html || !excerpt) {
    return new Response(
      JSON.stringify({ error: 'Missing required fields: title, body_html, excerpt' }),
      { status: 422, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const slug = providedSlug || generateArticleSlug(title);
  const word_count = body_text ? body_text.split(/\s+/).length : 0;
  const reading_time = body_text ? estimateReadingTime(body_text) : 5;

  const supabase = createServiceClient();
  const { data, error } = await supabase
    .from('editorial_articles')
    .upsert(
      {
        slug,
        title,
        subtitle,
        body_html,
        body_text,
        excerpt,
        category,
        film_slug,
        film_title,
        film_year,
        director,
        color_slug,
        cover_image,
        og_image,
        tags,
        reading_time,
        word_count,
        author,
        schema_type,
        source_url,
        gemini_score,
        voice,
        meta_title: meta_title || title,
        meta_desc: meta_desc || excerpt,
        focus_keyword,
        published,
        featured,
        published_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      { onConflict: 'slug' }
    )
    .select('id, slug')
    .single();

  if (error) {
    console.error('[editorial/publish] Supabase error:', error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  return new Response(
    JSON.stringify({
      success: true,
      id: data.id,
      slug: data.slug,
      url: `https://prisma.film/editorial/${data.slug}`,
    }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  );
};
