/* empty css                                  */
import { f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_QHw3iGXw.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../chunks/client_DzNyPYKT.mjs';
import { c as countryToSlug, a as isoToFlag, i as isoToName } from '../chunks/countries_xwzpexnz.mjs';
import { l as loadAllWorks } from '../chunks/loadWork_B0uYB5uV.mjs';
/* empty css                                 */
export { renderers } from '../renderers.mjs';

const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const countMap = /* @__PURE__ */ new Map();
  if (isSupabaseConfigured()) {
    const db = createServiceClient();
    const { data } = await db.from("works").select("countries").eq("is_published", true).limit(2e3);
    for (const row of data ?? []) {
      for (const iso2 of row.countries ?? []) {
        countMap.set(iso2, (countMap.get(iso2) ?? 0) + 1);
      }
    }
  } else {
    const works = loadAllWorks();
    for (const w of works) {
      for (const iso2 of w.countries ?? []) {
        countMap.set(iso2, (countMap.get(iso2) ?? 0) + 1);
      }
    }
  }
  const countries = Array.from(countMap.entries()).map(([iso2, count]) => ({
    iso2,
    name: isoToName(iso2),
    flag: isoToFlag(iso2),
    slug: countryToSlug(iso2),
    count
  })).sort((a, b) => b.count - a.count);
  const totalFilms = Array.from(countMap.values()).reduce((s, c) => s + c, 0);
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Countries \u2014 PRISMA", "description": "Browse films by country of origin. Every national cinema has a visual identity.", "data-astro-cid-fipljrac": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="countries-page page-enter" data-astro-cid-fipljrac> <div class="countries-header site-container" data-astro-cid-fipljrac> <h1 class="countries-header__title" data-astro-cid-fipljrac>Countries</h1> <p class="countries-header__desc" data-astro-cid-fipljrac> ${countries.length} national cinemas · ${totalFilms} film entries
</p> </div> <div class="site-container" data-astro-cid-fipljrac> ${countries.length === 0 ? renderTemplate`<p class="countries-empty" data-astro-cid-fipljrac>No country data available yet.</p>` : renderTemplate`<div class="country-grid" data-astro-cid-fipljrac> ${countries.map((c) => renderTemplate`<a${addAttribute(`/countries/${c.slug}`, "href")} class="country-card" data-astro-cid-fipljrac> <span class="country-card__flag" aria-hidden="true" data-astro-cid-fipljrac>${c.flag}</span> <div class="country-card__info" data-astro-cid-fipljrac> <span class="country-card__name" data-astro-cid-fipljrac>${c.name}</span> <span class="country-card__count" data-astro-cid-fipljrac>${c.count} ${c.count === 1 ? "film" : "films"}</span> </div> </a>`)} </div>`} </div> </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/countries/index.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/countries/index.astro";
const $$url = "/countries";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
