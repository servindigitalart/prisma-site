export const prerender = false

import type { APIRoute } from 'astro'
import { createSupabaseServerClient } from '../../../lib/supabase/server'
import { PRISMA_PALETTE } from '../../../lib/color/colorPalette'

export const GET: APIRoute = async ({ url, cookies }) => {
  const workId = url.searchParams.get('work_id')
  const userId = url.searchParams.get('user_id')

  if (!workId) {
    return new Response(JSON.stringify({ error: 'work_id required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  const supabase = createSupabaseServerClient(cookies)

  // Get work details with color
  const { data: work } = await supabase
    .from('works')
    .select(`
      title,
      year,
      color_assignments (
        color_id
      )
    `)
    .eq('id', workId)
    .single()

  if (!work) {
    return new Response(JSON.stringify({ error: 'Work not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  const colorId = (work as any).color_assignments?.[0]?.color_id
  const color = colorId ? PRISMA_PALETTE[colorId] : null
  
  let rating = null
  if (userId) {
    const { data: ratingData } = await supabase
      .from('user_ratings')
      .select('rating')
      .eq('user_id', userId)
      .eq('work_id', workId)
      .single()
    
    rating = ratingData?.rating || null
  }

  const slug = workId.replace(/^work_/, '')

  return new Response(JSON.stringify({
    url: `/share/${slug}${userId ? `?user=${userId}` : ''}`,
    title: work.title,
    year: (work as any).year,
    color: color?.name || 'Unknown',
    hex: color?.hex || '#4A4A4A',
    rating
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
