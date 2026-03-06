/* empty css                                     */
import { e as createAstro, f as createComponent, p as renderHead, r as renderTemplate } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import 'clsx';
export { renderers } from '../../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const prerender = false;
const $$Error = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$Error;
  const message = Astro2.url.searchParams.get("message") ?? "Authentication failed. Please try again.";
  return renderTemplate`<html lang="en"> <head><meta charset="UTF-8"><title>Auth Error — PRISMA</title>${renderHead()}</head> <body style="background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;gap:1rem;"> <h1 style="font-size:1.2rem;color:#f87171;">Authentication error</h1> <p style="color:#888;font-size:0.9rem;">${message}</p> <a href="/" style="color:#fff;border:1px solid #333;padding:0.5rem 1rem;border-radius:4px;text-decoration:none;">Back to PRISMA</a> </body></html>`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/auth/error.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/auth/error.astro";
const $$url = "/auth/error";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Error,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
