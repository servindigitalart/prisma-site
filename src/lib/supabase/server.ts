import { createServerClient, parseCookieHeader } from '@supabase/ssr'
import type { AstroCookies } from 'astro'

export function createSupabaseServerClient(cookies: AstroCookies, request?: Request) {
  return createServerClient(
    import.meta.env.PUBLIC_SUPABASE_URL,
    import.meta.env.PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          const raw = request?.headers?.get('cookie') ??
                      (cookies as any)._request?.headers?.get('cookie') ?? ''
          return parseCookieHeader(raw).map(c => ({
            name: c.name,
            value: c.value ?? '',
          }))
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
}