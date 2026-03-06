export const prerender = false

import type { APIRoute } from 'astro'
import { requireAdmin } from '../../../lib/admin'
import { createServiceClient } from '../../../lib/db/client'
import { createBunnyVideo, getBunnyUploadUrl } from '../../../lib/bunny'

/**
 * POST /api/admin/bunny-upload
 * Creates a Bunny Stream video slot and links it to the work record.
 *
 * Body: { submission_id: number, title: string }
 * Returns: { videoId, uploadUrl, libraryId }
 */
export const POST: APIRoute = async ({ request, locals }) => {
  const isAdmin = await requireAdmin(locals)
  if (!isAdmin) {
    return json({ error: 'Forbidden' }, 403)
  }

  let body: any
  try {
    body = await request.json()
  } catch {
    return json({ error: 'Invalid JSON body' }, 400)
  }

  const { submission_id, title } = body

  if (!submission_id || !title) {
    return json({ error: 'Missing submission_id or title' }, 400)
  }

  const db = createServiceClient()

  // Fetch submission to get work_id
  const { data: sub } = await db
    .from('film_submissions')
    .select('id, work_id, status')
    .eq('id', Number(submission_id))
    .maybeSingle()

  if (!sub) {
    return json({ error: 'Submission not found' }, 404)
  }

  if (!sub.work_id) {
    return json({ error: 'Work has not been published yet. Publish first, then upload video.' }, 400)
  }

  // Check if work already has a streaming_id
  const { data: work } = await db
    .from('works')
    .select('id, streaming_id, streaming_type')
    .eq('id', sub.work_id)
    .maybeSingle()

  if (work?.streaming_id) {
    return json({
      error: 'Work already has a video linked.',
      videoId: work.streaming_id,
      uploadUrl: getBunnyUploadUrl(work.streaming_id),
      libraryId: import.meta.env.BUNNY_LIBRARY_ID,
    }, 409)
  }

  try {
    // Create video in Bunny Stream
    const videoId = await createBunnyVideo(title)
    const uploadUrl = getBunnyUploadUrl(videoId)

    console.log(`[bunny-upload] Created video ${videoId} for work ${sub.work_id}`)

    // Update work with Bunny video reference
    const { error: updateErr } = await db
      .from('works')
      .update({
        streaming_id: videoId,
        streaming_type: 'bunny',
        streaming_url: `https://iframe.mediadelivery.net/embed/${import.meta.env.BUNNY_LIBRARY_ID}/${videoId}`,
        is_streamable: false, // Will be set to true after upload + encoding completes
      } as any)
      .eq('id', sub.work_id)

    if (updateErr) {
      console.error('[bunny-upload] DB update error:', updateErr.message)
      return json({ error: `Video created in Bunny (${videoId}) but DB update failed: ${updateErr.message}` }, 500)
    }

    return json({
      success: true,
      videoId,
      uploadUrl,
      libraryId: import.meta.env.BUNNY_LIBRARY_ID,
    })

  } catch (err: any) {
    console.error('[bunny-upload] Bunny API error:', err.message)
    return json({ error: err.message || 'Failed to create Bunny video' }, 500)
  }
}

function json(data: Record<string, any>, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}
