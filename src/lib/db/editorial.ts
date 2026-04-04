import { createServiceClient, isSupabaseConfigured } from './client';

export interface EditorialArticle {
  id: string;
  slug: string;
  title: string;
  subtitle?: string;
  body_html: string;
  excerpt: string;
  category: 'editorial' | 'laboratory' | 'fastfood';
  film_slug?: string;
  film_title?: string;
  film_year?: number;
  director?: string;
  color_slug?: string;
  cover_image?: string;
  og_image?: string;
  tags: string[];
  reading_time?: number;
  published_at: string;
  featured: boolean;
  author: string;
  meta_title?: string;
  meta_desc?: string;
  schema_type: string;
  voice?: string;
}

export async function getPublishedArticles(options: {
  limit?: number;
  offset?: number;
  category?: string;
  featured?: boolean;
} = {}): Promise<EditorialArticle[]> {
  if (!isSupabaseConfigured()) return [];
  const supabase = createServiceClient();
  const { limit = 20, offset = 0, category, featured } = options;

  let query = supabase
    .from('editorial_articles')
    .select('*')
    .eq('published', true)
    .order('published_at', { ascending: false })
    .range(offset, offset + limit - 1);

  if (category) query = query.eq('category', category);
  if (featured !== undefined) query = query.eq('featured', featured);

  const { data, error } = await query;
  if (error) { console.error('[editorial] fetch error:', error); return []; }
  return (data ?? []) as EditorialArticle[];
}

export async function getArticleBySlug(
  slug: string
): Promise<EditorialArticle | null> {
  if (!isSupabaseConfigured()) return null;
  const supabase = createServiceClient();
  const { data, error } = await supabase
    .from('editorial_articles')
    .select('*')
    .eq('slug', slug)
    .eq('published', true)
    .single();
  if (error) return null;
  return data as EditorialArticle;
}

export async function getRelatedArticles(
  article: EditorialArticle,
  limit = 3
): Promise<EditorialArticle[]> {
  if (!isSupabaseConfigured()) return [];
  const supabase = createServiceClient();

  // Find articles with same film or same category, excluding current
  let query = supabase
    .from('editorial_articles')
    .select(
      'id, slug, title, subtitle, excerpt, category, film_title, ' +
      'film_year, director, color_slug, cover_image, og_image, ' +
      'tags, reading_time, published_at, featured, author, voice'
    )
    .eq('published', true)
    .neq('slug', article.slug)
    .limit(limit);

  if (article.film_slug) {
    query = query.eq('film_slug', article.film_slug);
  } else {
    query = query.eq('category', article.category);
  }

  const { data } = await query.order('published_at', { ascending: false });
  return (data ?? []) as EditorialArticle[];
}

export async function getFeaturedArticle(): Promise<EditorialArticle | null> {
  const articles = await getPublishedArticles({ featured: true, limit: 1 });
  return articles[0] ?? null;
}

export async function getArticleCount(category?: string): Promise<number> {
  if (!isSupabaseConfigured()) return 0;
  const supabase = createServiceClient();
  let query = supabase
    .from('editorial_articles')
    .select('id', { count: 'exact', head: true })
    .eq('published', true);
  if (category) query = query.eq('category', category);
  const { count } = await query;
  return count ?? 0;
}
