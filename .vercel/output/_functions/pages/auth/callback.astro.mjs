/* empty css                                     */
import { e as createAstro, f as createComponent } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import 'clsx';
import { createServerClient, parseCookieHeader } from '@supabase/ssr';
export { renderers } from '../../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const prerender = false;
const $$Callback = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$Callback;
  const { request, cookies, redirect, url } = Astro2;
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
  const code = url.searchParams.get("code");
  if (code) {
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (error) {
      console.error("[callback] Code exchange error:", error);
      return redirect("/auth/error?message=Code+exchange+failed");
    }
  }
  return redirect("/");
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/auth/callback.astro", void 0);
const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/auth/callback.astro";
const $$url = "/auth/callback";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Callback,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
