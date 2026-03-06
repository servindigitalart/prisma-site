import { createServerClient } from '@supabase/ssr'
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
          if (!raw) return []
          return raw.split(';').map((c: string) => {
            const [name, ...rest] = c.trim().split('=')
            return { name: name.trim(), value: decodeURIComponent(rest.join('=').trim()) }
          })
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookies.set(name, value, {
              ...options,
              path: '/',
              sameSite: 'lax',
              httpOnly: false,
              secure: false,
            })
          })
        },
      },
    }
  )
}