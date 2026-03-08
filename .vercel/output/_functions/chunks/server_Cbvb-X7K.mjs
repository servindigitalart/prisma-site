import { createServerClient, parseCookieHeader } from '@supabase/ssr';

function createSupabaseServerClient(cookies, request) {
  return createServerClient(
    "https://porqyokkphflvqfclvkj.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvcnF5b2trcGhmbHZxZmNsdmtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNDE2MzEsImV4cCI6MjA4NzYxNzYzMX0.q_fDlajLrMQ1Cbg7o_gwDGPhX8Mt7BwhgXapMkY9jN4",
    {
      cookies: {
        getAll() {
          const raw = request?.headers?.get("cookie") ?? cookies._request?.headers?.get("cookie") ?? "";
          return parseCookieHeader(raw).map((c) => ({
            name: c.name,
            value: c.value ?? ""
          }));
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookies.set(name, value, {
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
}

export { createSupabaseServerClient as c };
