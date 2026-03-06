import { defineMiddleware } from 'astro:middleware'
import { createServerClient, parseCookieHeader } from '@supabase/ssr'

export const onRequest = defineMiddleware(async (context, next) => {
  const supabase = createServerClient(
    import.meta.env.PUBLIC_SUPABASE_URL,
    import.meta.env.PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          const cookies = parseCookieHeader(context.request.headers.get('Cookie') ?? '')
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
