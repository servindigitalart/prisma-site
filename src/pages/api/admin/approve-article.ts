// filepath: src/pages/api/admin/approve-article.ts
import type { APIRoute } from 'astro';
import { createServiceClient } from '../../../lib/db/client';

export const POST: APIRoute = async ({ request, redirect }) => {
  const db = createServiceClient();
  const formData = await request.formData();
  const articleId = formData.get('article_id');

  if (!articleId) {
    return new Response('Missing article_id', { status: 400 });
  }

  const id = parseInt(articleId.toString(), 10);
  if (isNaN(id)) {
    return new Response('Invalid article_id', { status: 400 });
  }

  try {
    const { error } = await db
      .from('generated_articles')
      .update({
        is_published: true,
        published_at: new Date().toISOString(),
        reviewed_at: new Date().toISOString()
      })
      .eq('id', id);

    if (error) {
      console.error('[approve-article] Error:', error);
      return new Response(`Error: ${error.message}`, { status: 500 });
    }

    return redirect('/admin/review', 303);
  } catch (err) {
    console.error('[approve-article] Exception:', err);
    return new Response('Internal server error', { status: 500 });
  }
};
