/**
 * src/pages/auth/signin.ts
 * ────────────────────────
 * Server-side Google OAuth with PKCE flow.
 * Creates a Supabase server client that can write cookies (code_verifier),
 * then redirects the user to Google's consent screen.
 */
import type { APIRoute } from 'astro'
import { createServerClient, parseCookieHeader } from '@supabase/ssr'

export const prerender = false

export const GET: APIRoute = async (context) => {
  const { url, request, cookies, redirect } = context

  const supabase = createServerClient(
    import.meta.env.PUBLIC_SUPABASE_URL,
    import.meta.env.PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          const parsed = parseCookieHeader(request.headers.get('Cookie') ?? '')
          return parsed.map(c => ({ name: c.name, value: c.value ?? '' }))
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookies.set(name, value, {
              ...options,
              path: '/',
              sameSite: 'lax',
              httpOnly: true,
              secure: import.meta.env.PROD,
            })
          })
        },
      },
    }
  )

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${url.origin}/auth/callback`,
    },
  })

  if (error || !data.url) {
    console.error('[signin] OAuth error:', error)
    return redirect('/auth/error?message=Could+not+start+sign+in', 302)
  }

  return redirect(data.url, 302)
}