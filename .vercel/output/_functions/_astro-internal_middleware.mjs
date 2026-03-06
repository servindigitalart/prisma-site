import { d as defineMiddleware, s as sequence } from './chunks/index_6CbnbTQl.mjs';
import { createServerClient, parseCookieHeader } from '@supabase/ssr';
import 'es-module-lexer';
import './chunks/astro-designed-error-pages_CCSgb7cW.mjs';
import 'piccolore';
import './chunks/astro/server_DZETslqp.mjs';
import 'clsx';

const onRequest$1 = defineMiddleware(async (context, next) => {
  const supabase = createServerClient(
    "https://porqyokkphflvqfclvkj.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvcnF5b2trcGhmbHZxZmNsdmtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNDE2MzEsImV4cCI6MjA4NzYxNzYzMX0.q_fDlajLrMQ1Cbg7o_gwDGPhX8Mt7BwhgXapMkY9jN4",
    {
      cookies: {
        getAll() {
          const cookies = parseCookieHeader(context.request.headers.get("Cookie") ?? "");
          return cookies.map((cookie) => ({
            name: cookie.name,
            value: cookie.value ?? ""
          }));
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            context.cookies.set(name, value, {
              ...options,
              path: "/",
              sameSite: "lax",
              httpOnly: true,
              secure: true
            });
          });
        }
      }
    }
  );
  const { data: { user } } = await supabase.auth.getUser();
  context.locals.user = user ?? null;
  return next();
});

const onRequest = sequence(
	
	onRequest$1
	
);

export { onRequest };
