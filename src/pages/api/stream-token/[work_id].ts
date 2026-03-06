export const prerender = false

import type { APIRoute } from 'astro'
import { createServiceClient } from '../../../lib/db/client'
import { getBunnyEmbedUrlSigned } from '../../../lib/bunny'

/**
 * GET /api/stream-token/:work_id
 * Returns a fresh signed embed URL for a streamable work.
 * Token expires in 4 hours.
 */
export const GET: APIRoute = async ({ params }) => {
  const workId = params.work_id
  if (!workId) {
    return json({ error: 'Missing work_id' }, 400)
  }

  const db = createServiceClient()

  const { data: work } = await db
    .from('works')
    .select('id, streaming_id, streaming_type, is_streamable')
    .eq('id', workId)
    .maybeSingle()

  if (!work) {
    return json({ error: 'Work not found' }, 404)
  }

  if (!work.is_streamable || !work.streaming_id) {
    return json({ error: 'This work is not available for streaming' }, 404)
  }

  if (work.streaming_type !== 'bunny') {
    return json({ error: `Unsupported streaming provider: ${work.streaming_type}` }, 400)
  }

  const embedUrl = getBunnyEmbedUrlSigned(work.streaming_id)
  const expires = Math.floor(Date.now() / 1000) + 14400

  return json({ embedUrl, expires })
}

function json(data: Record<string, any>, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}
