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
    const { work_id, watched_at } = body

    if (!work_id) {
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 400, headers: { 'Content-Type': 'application/json' }
      })
    }

    const watchedDate = watched_at || new Date().toISOString().slice(0, 10)
    const supabase = createSupabaseServerClient(cookies, request)

    // Check if already marked as seen
    const { data: existing, error: selectError } = await supabase
      .from('user_watches')
      .select('work_id')
      .eq('user_id', user.id)
      .eq('work_id', work_id)
      .limit(1)

    if (selectError) {
      console.error('[seen] select error:', selectError.message)
    }

    if (existing && existing.length > 0) {
      // Toggle off — remove all watch entries for this work
      const { error } = await supabase
        .from('user_watches')
        .delete()
        .eq('user_id', user.id)
        .eq('work_id', work_id)

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500, headers: { 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({ success: true, seen: false }), {
        status: 200, headers: { 'Content-Type': 'application/json' }
      })
    } else {
      // Mark as seen
      const { data: insertData, error } = await supabase
        .from('user_watches')
        .insert({ user_id: user.id, work_id, watched_at: watchedDate })
        .select()

      console.log('[seen] insert result:', JSON.stringify({ insertData, error: error?.message, work_id, watchedDate }))

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500, headers: { 'Content-Type': 'application/json' }
        })
      }

      // Auto-remove from watchlist
      await supabase.from('user_watchlist').delete()
        .eq('user_id', user.id).eq('work_id', work_id)

      return new Response(JSON.stringify({ success: true, seen: true }), {
        status: 200, headers: { 'Content-Type': 'application/json' }
      })
    }
  } catch (err) {
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    })
  }
}