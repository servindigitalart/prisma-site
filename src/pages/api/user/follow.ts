export const prerender = false

import type { APIRoute } from 'astro'
import { createSupabaseServerClient } from '../../../lib/supabase/server'

export const POST: APIRoute = async ({ request, cookies, locals }) => {
  const user = locals.user
  if (!user) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  const body = await request.clone().json()
  const { following_id } = body

  if (!following_id) {
    return new Response(JSON.stringify({ error: 'Invalid request' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  // Can't follow yourself
  if (following_id === user.id) {
    return new Response(JSON.stringify({ error: 'Cannot follow yourself' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  const supabase = createSupabaseServerClient(cookies, request)
  
  // Check if already following
  const { data: existing } = await supabase
    .from('follows')
    .select('*')
    .eq('follower_id', user.id)
    .eq('following_id', following_id)
    .maybeSingle()

  let following = false

  if (existing) {
    // Unfollow
    const { error } = await supabase
      .from('follows')
      .delete()
      .eq('follower_id', user.id)
      .eq('following_id', following_id)

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
    }
  } else {
    // Follow
    const { error } = await supabase
      .from('follows')
      .insert({
        follower_id: user.id,
        following_id,
        created_at: new Date().toISOString()
      })

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
    }

    following = true
  }

  return new Response(JSON.stringify({ success: true, following }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
