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
    const { work_id } = body

    if (!work_id) {
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 400, headers: { 'Content-Type': 'application/json' }
      })
    }

    const supabase = createSupabaseServerClient(cookies, request)

    const { data: existing } = await supabase
      .from('user_watchlist')
      .select('work_id')
      .eq('user_id', user.id)
      .eq('work_id', work_id)
      .maybeSingle()

    if (existing) {
      const { error } = await supabase
        .from('user_watchlist')
        .delete()
        .eq('user_id', user.id)
        .eq('work_id', work_id)

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500, headers: { 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({ success: true, added: false }), {
        status: 200, headers: { 'Content-Type': 'application/json' }
      })
    } else {
      const { error } = await supabase
        .from('user_watchlist')
        .insert({ user_id: user.id, work_id, added_at: new Date().toISOString() })

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500, headers: { 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({ success: true, added: true }), {
        status: 200, headers: { 'Content-Type': 'application/json' }
      })
    }
  } catch (err) {
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    })
  }
}