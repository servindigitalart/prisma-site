import { createServerClient, parseCookieHeader } from '@supabase/ssr';
export { renderers } from '../../renderers.mjs';

const prerender = false;
const GET = async (context) => {
  const { url, request, cookies, redirect } = context;
  const supabase = createServerClient(
    "https://porqyokkphflvqfclvkj.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvcnF5b2trcGhmbHZxZmNsdmtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNDE2MzEsImV4cCI6MjA4NzYxNzYzMX0.q_fDlajLrMQ1Cbg7o_gwDGPhX8Mt7BwhgXapMkY9jN4",
    {
      cookies: {
        getAll() {
          const parsed = parseCookieHeader(request.headers.get("Cookie") ?? "");
          return parsed.map((c) => ({ name: c.name, value: c.value ?? "" }));
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
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: `${url.origin}/auth/callback`
    }
  });
  if (error || !data.url) {
    console.error("[signin] OAuth error:", error);
    return redirect("/auth/error?message=Could+not+start+sign+in", 302);
  }
  return redirect(data.url, 302);
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
