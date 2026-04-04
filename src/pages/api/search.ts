export const prerender = false

import type { APIRoute } from 'astro'
import { createServiceClient } from '../../lib/db/client'

const TMDB_IMG = 'https://image.tmdb.org/t/p/w185'

export const GET: APIRoute = async ({ url }) => {
  const q = (url.searchParams.get('q') ?? '').trim()

  if (q.length < 2) {
    return new Response(JSON.stringify({ films: [], people: [] }), {
      headers: { 'Content-Type': 'application/json' },
    })
  }

  const db = createServiceClient()

  const [filmsRes, peopleRes] = await Promise.all([
    db
      .from('works')
      .select('id, title, year, tmdb_poster_path')
      .ilike('title', `%${q}%`)
      .eq('is_published', true)
      .order('year', { ascending: false })
      .limit(8),
    db
      .from('people')
      .select('id, name, profile_path')
      .ilike('name', `%${q}%`)
      .limit(5),
  ])

  const films = (filmsRes.data ?? []).map((w: any) => ({
    id:     w.id,
    title:  w.title,
    year:   w.year,
    poster: w.tmdb_poster_path ? `${TMDB_IMG}${w.tmdb_poster_path}` : null,
    slug:   w.id.replace(/^work_/, ''),
  }))

  const people = (peopleRes.data ?? []).map((p: any) => ({
    id:    p.id,
    name:  p.name,
    photo: p.profile_path ? `${TMDB_IMG}${p.profile_path}` : null,
    slug:  p.id.replace(/^person_/, ''),
    role:  null,
  }))

  return new Response(JSON.stringify({ films, people }), {
    headers: { 'Content-Type': 'application/json' },
  })
}
