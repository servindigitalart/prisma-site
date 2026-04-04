import type { EditorialArticle } from '../db/editorial';

const SITE_URL = 'https://prisma.film';

export function buildArticleJsonLd(article: EditorialArticle): object {
  const schemaType = article.schema_type || 'Article';
  const url = `${SITE_URL}/editorial/${article.slug}`;
  const image = article.og_image || article.cover_image
    || `${SITE_URL}/og-default.jpg`;

  const base = {
    '@context': 'https://schema.org',
    '@type': schemaType,
    headline: article.meta_title || article.title,
    description: article.meta_desc || article.excerpt,
    image: [image],
    datePublished: article.published_at,
    dateModified: article.published_at,
    author: {
      '@type': 'Organization',
      name: article.author || 'PRISMA Editorial',
      url: SITE_URL,
    },
    publisher: {
      '@type': 'Organization',
      name: 'PRISMA',
      url: SITE_URL,
      logo: {
        '@type': 'ImageObject',
        url: `${SITE_URL}/brand/isotipo.png`,
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': url,
    },
    url,
    inLanguage: 'es-MX',
    keywords: article.tags?.join(', '),
  };

  // Add Review schema fields if it's a review
  if (schemaType === 'Review' && article.film_title) {
    return {
      ...base,
      '@type': 'Review',
      itemReviewed: {
        '@type': 'Movie',
        name: article.film_title,
        dateCreated: article.film_year?.toString(),
        director: article.director
          ? { '@type': 'Person', name: article.director }
          : undefined,
      },
    };
  }

  return base;
}

export function buildArticleBreadcrumbs(article: EditorialArticle) {
  const crumbs = [
    { name: 'PRISMA', url: SITE_URL },
    { name: 'Editorial', url: `${SITE_URL}/editorial` },
  ];
  if (article.category !== 'editorial') {
    crumbs.push({
      name: article.category === 'laboratory' ? 'Laboratorio' : 'Radar',
      url: `${SITE_URL}/editorial/${article.category}`,
    });
  }
  crumbs.push({ name: article.title, url: `${SITE_URL}/editorial/${article.slug}` });
  return crumbs;
}

export function estimateReadingTime(text: string): number {
  const words = text.split(/\s+/).length;
  return Math.ceil(words / 200); // 200 wpm average
}

export function generateArticleSlug(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 80);
}
