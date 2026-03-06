import type { APIRoute } from 'astro'

export const prerender = false

export const GET: APIRoute = async ({ redirect, url }) => {
  const supabaseUrl = 'https://porqyokkphflvqfclvkj.supabase.co'
  const redirectTo = encodeURIComponent(`${url.origin}/auth/callback`)
  
  return redirect(
    `${supabaseUrl}/auth/v1/authorize?provider=google&redirect_to=${redirectTo}`,
    302
  )
}