export const prerender = false

import type { APIRoute } from 'astro'
import { createSupabaseServerClient } from '../../../lib/supabase/server'

export const POST: APIRoute = async ({ request, cookies, locals }) => {
  try {
    const user = locals.user
    if (!user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401, headers: { 'Content-Type': 'application/json' }
      })
    }

    const body = await request.clone().json()
    const { work_id, rating } = body

    if (!work_id || !rating || rating < 1 || rating > 10) {
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 400, headers: { 'Content-Type': 'application/json' }
      })
    }

    const supabase = createSupabaseServerClient(cookies, request)

    const { data, error } = await supabase
      .from('user_ratings')
      .upsert(
        { user_id: user.id, work_id, rating: Number(rating), updated_at: new Date().toISOString() },
        { onConflict: 'user_id,work_id' }
      )
      .select()
      .single()

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500, headers: { 'Content-Type': 'application/json' }
      })
    }

    // Auto-remove from watchlist after rating
    await supabase.from('user_watchlist').delete()
      .eq('user_id', user.id).eq('work_id', work_id)

    return new Response(JSON.stringify({ success: true, data }), {
      status: 200, headers: { 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    })
  }
}