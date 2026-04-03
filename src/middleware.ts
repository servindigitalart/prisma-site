import { defineMiddleware } from 'astro:middleware'
import { createServerClient, parseCookieHeader } from '@supabase/ssr'

export const onRequest = defineMiddleware(async (context, next) => {
  // Skip auth check for prerendered (static) pages — no request headers available
  if (context.isPrerendered) {
    context.locals.user = null
    return next()
  }

  const supabase = createServerClient(
    import.meta.env.PUBLIC_SUPABASE_URL,
    import.meta.env.PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          const raw = context.request.headers.get('Cookie') ?? ''
          const cookies = parseCookieHeader(raw)
          return cookies.map(cookie => ({
            name: cookie.name,
            value: cookie.value ?? ''
          }))
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            context.cookies.set(name, value, {
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

  const { data: { user } } = await supabase.auth.getUser()
  context.locals.user = user ?? null

  return next()
})
