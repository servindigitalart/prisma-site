/* empty css                                  */
import { f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_CKaj1kxH.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../chunks/client_DzNyPYKT.mjs';
import { a as isoToFlag, i as isoToName } from '../chunks/countries_xwzpexnz.mjs';
import { g as getFestivalLogoUrl, i as isFestivalLogoLocal } from '../chunks/festivalUtils_CMVWB9Ye.mjs';
/* empty css                                 */
export { renderers } from '../renderers.mjs';

const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  let festivals = [];
  if (isSupabaseConfigured()) {
    const db = createServiceClient();
    const [{ data: festData }, { data: waData }] = await Promise.all([
      db.from("festivals").select("id, name, city, country, founded_year, tier, logo_path").order("tier").order("name"),
      db.from("work_awards").select("result, work_id, awards!inner(festival_id)").limit(5e3)
    ]);
    const countMap = /* @__PURE__ */ new Map();
    for (const row of waData ?? []) {
      const fid = row.awards?.festival_id;
      if (!fid) continue;
      if (!countMap.has(fid)) countMap.set(fid, { films: /* @__PURE__ */ new Set(), wins: 0 });
      countMap.get(fid).films.add(row.work_id);
      if (row.result === "win") countMap.get(fid).wins++;
    }
    festivals = (festData ?? []).map((f) => ({
      id: f.id,
      name: f.name,
      city: f.city,
      country: f.country,
      founded_year: f.founded_year,
      tier: f.tier,
      logo_path: f.logo_path ?? null,
      filmCount: countMap.get(f.id)?.films.size ?? 0,
      winCount: countMap.get(f.id)?.wins ?? 0
    }));
  }
  function festSlug(id) {
    return id.replace(/^festival_/, "");
  }
  const TIER_GROUPS = [
    { key: "A", label: "Grandes Festivales Internacionales" },
    { key: "B", label: "Festivales y Premios Importantes" },
    { key: "C", label: "Premios Regionales y Especializados" }
  ];
  const byTier = (tier) => festivals.filter((f) => f.tier === tier);
  const SITE = "https://prisma.film";
  const festivalsBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Festivales", url: `${SITE}/festivals` }
  ];
  const festivalsJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "Festivales y Premios de Cine \u2014 PRISMA",
    description: `Los ${festivals.length} festivales y premios de cine m\xE1s prestigiosos del mundo. De Cannes a los Premios de la Academia.`,
    url: `${SITE}/festivals`,
    numberOfItems: festivals.length,
    itemListElement: festivals.slice(0, 30).map((f, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: f.name,
      url: `${SITE}/festivals/${festSlug(f.id)}`
    }))
  };
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Festivales y Premios \u2014 PRISMA", "description": "Los festivales y premios m\xE1s prestigiosos del cine, de Cannes a los Premios de la Academia.", "jsonLd": festivalsJsonLd, "breadcrumbs": festivalsBreadcrumbs, "data-astro-cid-vnfb5qxt": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="festivals-page page-enter" data-astro-cid-vnfb5qxt> <!-- Header --> <div class="festivals-header site-container" data-astro-cid-vnfb5qxt> <h1 class="festivals-header__title" data-astro-cid-vnfb5qxt>Festivales y Premios</h1> <p class="festivals-header__desc" data-astro-cid-vnfb5qxt> ${festivals.length} festivales curados · Los reconocimientos más prestigiosos del cine
</p> </div> <!-- Tier groups --> <div class="site-container festivals-body" data-astro-cid-vnfb5qxt> ${TIER_GROUPS.map(({ key, label }) => {
    const group = byTier(key);
    if (!group.length) return null;
    return renderTemplate`<section class="tier-section" data-astro-cid-vnfb5qxt> <div class="tier-section__header" data-astro-cid-vnfb5qxt> <span class="tier-badge"${addAttribute(key, "data-tier")} data-astro-cid-vnfb5qxt>[${key}]</span> <h2 class="tier-section__label" data-astro-cid-vnfb5qxt>${label}</h2> </div> <div class="festival-grid" data-astro-cid-vnfb5qxt> ${group.map((f) => renderTemplate`<a${addAttribute(`/festivals/${festSlug(f.id)}`, "href")} class="festival-card" data-astro-cid-vnfb5qxt> <div class="festival-card__top" data-astro-cid-vnfb5qxt> <div class="festival-card__identity" data-astro-cid-vnfb5qxt> ${(() => {
      const logoUrl = getFestivalLogoUrl(f.logo_path);
      const isLocal = isFestivalLogoLocal(f.logo_path);
      return renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-vnfb5qxt": true }, { "default": async ($$result3) => renderTemplate`${logoUrl && renderTemplate`<img${addAttribute(logoUrl, "src")} alt=""${addAttribute(`festival-card__logo${isLocal ? " festival-logo--local" : ""}`, "class")} loading="lazy" data-astro-cid-vnfb5qxt>`}<span class="festival-card__flag" aria-hidden="true" data-astro-cid-vnfb5qxt>${f.country ? isoToFlag(f.country) : "\u{1F3AC}"}</span> ` })}`;
    })()} </div> <span class="festival-card__tier"${addAttribute(f.tier, "data-tier")} data-astro-cid-vnfb5qxt>[${f.tier}]</span> </div> <div class="festival-card__name" data-astro-cid-vnfb5qxt>${f.name}</div> <div class="festival-card__meta" data-astro-cid-vnfb5qxt> ${f.city && f.country && renderTemplate`<span data-astro-cid-vnfb5qxt>${f.city}, ${isoToName(f.country)}</span>`} ${f.founded_year && renderTemplate`<span class="festival-card__year" data-astro-cid-vnfb5qxt>est. ${f.founded_year}</span>`} </div> ${f.filmCount > 0 && renderTemplate`<div class="festival-card__stats" data-astro-cid-vnfb5qxt> <span class="festival-card__stat" data-astro-cid-vnfb5qxt> ${f.winCount}W / ${f.filmCount - f.winCount}N
</span> <span class="festival-card__stat festival-card__stat--films" data-astro-cid-vnfb5qxt> ${f.filmCount} ${f.filmCount === 1 ? "film" : "films"} </span> </div>`} </a>`)} </div> </section>`;
  })} </div> </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/festivals/index.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/festivals/index.astro";
const $$url = "/festivals";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
