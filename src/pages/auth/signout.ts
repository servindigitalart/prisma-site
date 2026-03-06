import type { APIRoute } from 'astro'
import { createSupabaseServerClient } from '../../lib/supabase/server'

export const prerender = false

export const POST: APIRoute = async ({ cookies, redirect }) => {
  const supabase = createSupabaseServerClient(cookies)
  await supabase.auth.signOut()
  return redirect('/', 302)
}
