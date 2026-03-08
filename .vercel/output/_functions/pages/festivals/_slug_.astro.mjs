/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_CKaj1kxH.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { a as isoToFlag, i as isoToName } from '../../chunks/countries_xwzpexnz.mjs';
import { g as getPaletteEntry } from '../../chunks/colorPalette_MBD9-pHi.mjs';
import { g as getFestivalLogoUrl, i as isFestivalLogoLocal, a as getFestivalMonogram } from '../../chunks/festivalUtils_CMVWB9Ye.mjs';
/* empty css                                     */
export { renderers } from '../../renderers.mjs';

const SITE_URL = "https://prisma.film";
function buildDescription(input) {
  if (input.description) {
    return input.description.length > 155 ? input.description.slice(0, 152) + "…" : input.description;
  }
  const loc = [input.city, input.country].filter(Boolean).join(", ");
  return `${input.name}${loc ? ` — ${loc}` : ""} — Historial de ganadores y nominados en el catálogo PRISMA.`;
}
function buildJsonLd(input, description) {
  const festSlug = input.id.replace(/^festival_/, "");
  const festUrl = `${SITE_URL}/festivals/${festSlug}`;
  const schema = {
    "@context": "https://schema.org",
    "@type": "Event",
    name: input.name,
    url: festUrl,
    description,
    eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode"
  };
  if (input.city || input.country) {
    schema.location = {
      "@type": "Place",
      name: input.city ?? input.country,
      address: {
        "@type": "PostalAddress",
        ...input.city ? { addressLocality: input.city } : {},
        ...input.country ? { addressCountry: input.country } : {}
      }
    };
  }
  if (input.founded_year) {
    schema.startDate = String(input.founded_year);
  }
  if (input.website) {
    schema.sameAs = input.website;
  }
  return schema;
}
function buildFestivalSeo(input) {
  const description = buildDescription(input);
  const ogImage = input.logo_path?.startsWith("http") ? input.logo_path : `${SITE_URL}/og-default.jpg`;
  return {
    title: `${input.name} — PRISMA`,
    description,
    ogImage,
    ogType: "website",
    jsonLd: buildJsonLd(input, description)
  };
}

const $$Astro = createAstro("https://prisma.film");
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$slug;
  const { slug } = Astro2.params;
  if (!slug) return Astro2.redirect("/404");
  const festivalId = `festival_${slug}`;
  if (!isSupabaseConfigured()) return Astro2.redirect("/festivals");
  const db = createServiceClient();
  const { data: festRow, error: festErr } = await db.from("festivals").select("id, name, name_local, country, city, founded_year, tier, description, website, is_active, logo_path").eq("id", festivalId).single();
  if (festErr || !festRow) return Astro2.redirect("/404");
  const festival = festRow;
  const { data: waData } = await db.from("work_awards").select(`
    id,
    result,
    year,
    work_id,
    award_id,
    awards!inner(id, name, scoring_points, is_grand_prize, festival_id),
    works(id, title, year, tmdb_poster_path, color_assignments(color_iconico))
  `).eq("awards.festival_id", festivalId).order("year", { ascending: false }).limit(1e3);
  const rows = waData ?? [];
  const wins = rows.filter((r) => r.result === "win");
  const noms = rows.filter((r) => r.result === "nomination");
  const uniqueFilms = new Set(rows.map((r) => r.work_id));
  const totalWins = wins.length;
  const totalNoms = noms.length;
  const TMDB_IMG = "https://image.tmdb.org/t/p/w342";
  const seenWinWorks = /* @__PURE__ */ new Set();
  const topWinners = [];
  for (const r of wins) {
    if (!r.works?.tmdb_poster_path) continue;
    if (seenWinWorks.has(r.work_id)) continue;
    seenWinWorks.add(r.work_id);
    topWinners.push(r);
    if (topWinners.length >= 5) break;
  }
  const awardGroupMap = /* @__PURE__ */ new Map();
  for (const r of rows) {
    const aid = r.award_id;
    if (!awardGroupMap.has(aid)) {
      awardGroupMap.set(aid, {
        awardId: aid,
        awardName: r.awards.name,
        isGrandPrize: r.awards.is_grand_prize,
        wins: [],
        noms: []
      });
    }
    if (r.result === "win") awardGroupMap.get(aid).wins.push(r);
    else awardGroupMap.get(aid).noms.push(r);
  }
  const awardGroups = [...awardGroupMap.values()].sort((a, b) => {
    if (a.isGrandPrize !== b.isGrandPrize) return a.isGrandPrize ? -1 : 1;
    return b.wins.length - a.wins.length;
  });
  function filmSlug(workId) {
    return workId.replace(/^work_/, "");
  }
  function getColor(work) {
    if (!work) return null;
    const ca = Array.isArray(work.color_assignments) ? work.color_assignments[0] : work.color_assignments;
    return ca?.color_iconico ?? null;
  }
  const flag = festival.country ? isoToFlag(festival.country) : "\u{1F3AC}";
  const countryName = festival.country ? isoToName(festival.country) : "";
  const festLogoUrl = getFestivalLogoUrl(festival.logo_path);
  const festLogoIsLocal = isFestivalLogoLocal(festival.logo_path);
  const festMonogram = getFestivalMonogram(festival.name);
  const festivalSeo = buildFestivalSeo({
    id: festival.id,
    name: festival.name,
    description: festival.description,
    city: festival.city,
    country: festival.country,
    founded_year: festival.founded_year,
    tier: festival.tier,
    logo_path: festival.logo_path,
    website: festival.website
  });
  const SITE = "https://prisma.film";
  const festBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Festivales", url: `${SITE}/festivals` },
    { name: festival.name, url: `${SITE}/festivals/${slug}` }
  ];
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": festivalSeo.title, "description": festivalSeo.description, "ogImage": festivalSeo.ogImage, "ogType": festivalSeo.ogType, "jsonLd": festivalSeo.jsonLd, "breadcrumbs": festBreadcrumbs, "data-astro-cid-7rwoky4j": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="festival-page page-enter" data-astro-cid-7rwoky4j> <!-- ── Header ── --> <section class="fest-header" data-astro-cid-7rwoky4j> <div class="site-container" data-astro-cid-7rwoky4j> <div class="fest-header__inner" data-astro-cid-7rwoky4j> <div class="fest-header__logo-wrap" data-astro-cid-7rwoky4j> ${festLogoUrl ? renderTemplate`<img${addAttribute(festLogoUrl, "src")} alt=""${addAttribute(`fest-header__logo${festLogoIsLocal ? " festival-logo--local" : ""}`, "class")} loading="eager" data-astro-cid-7rwoky4j>` : renderTemplate`<div class="fest-header__monogram" aria-hidden="true" data-astro-cid-7rwoky4j>${festMonogram}</div>`} <span class="fest-header__flag" aria-hidden="true" data-astro-cid-7rwoky4j>${flag}</span> </div> <div class="fest-header__info" data-astro-cid-7rwoky4j> <div class="fest-header__overline" data-astro-cid-7rwoky4j> ${festival.city && renderTemplate`<span data-astro-cid-7rwoky4j>${festival.city}</span>`} ${festival.city && countryName && renderTemplate`<span aria-hidden="true" data-astro-cid-7rwoky4j>·</span>`} ${countryName && renderTemplate`<span data-astro-cid-7rwoky4j>${countryName}</span>`} ${festival.founded_year && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-7rwoky4j": true }, { "default": async ($$result3) => renderTemplate` <span aria-hidden="true" data-astro-cid-7rwoky4j>·</span> <span data-astro-cid-7rwoky4j>fund. ${festival.founded_year}</span> ` })}`} ${festival.tier && renderTemplate`<span class="fest-tier-badge" data-astro-cid-7rwoky4j>[${festival.tier}]</span>`} </div> <h1 class="fest-header__title" data-astro-cid-7rwoky4j>${festival.name}</h1> ${festival.name_local && festival.name_local !== festival.name && renderTemplate`<p class="fest-header__local" data-astro-cid-7rwoky4j>${festival.name_local}</p>`} ${festival.description && renderTemplate`<p class="fest-header__desc" data-astro-cid-7rwoky4j>${festival.description}</p>`} <div class="fest-header__links" data-astro-cid-7rwoky4j> ${festival.website && renderTemplate`<a${addAttribute(festival.website, "href")} target="_blank" rel="noopener noreferrer" class="fest-website-link" data-astro-cid-7rwoky4j>
Sitio oficial ↗
</a>`} </div> </div> </div> <!-- Stats bar --> ${rows.length > 0 && renderTemplate`<div class="fest-stats" data-astro-cid-7rwoky4j> <span class="fest-stat" data-astro-cid-7rwoky4j><strong data-astro-cid-7rwoky4j>${totalWins}</strong> premios en catálogo</span> <span class="fest-stat-sep" aria-hidden="true" data-astro-cid-7rwoky4j>·</span> <span class="fest-stat" data-astro-cid-7rwoky4j><strong data-astro-cid-7rwoky4j>${totalNoms}</strong> nominaciones</span> <span class="fest-stat-sep" aria-hidden="true" data-astro-cid-7rwoky4j>·</span> <span class="fest-stat" data-astro-cid-7rwoky4j><strong data-astro-cid-7rwoky4j>${uniqueFilms.size}</strong> películas</span> </div>`} </div> </section> ${rows.length === 0 ? renderTemplate`<div class="site-container fest-empty" data-astro-cid-7rwoky4j> <p data-astro-cid-7rwoky4j>Aún no hay películas de este festival en el catálogo.</p> </div>` : renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-7rwoky4j": true }, { "default": async ($$result3) => renderTemplate`  ${topWinners.length > 0 && renderTemplate`<section class="fest-posters" data-astro-cid-7rwoky4j> <div class="site-container" data-astro-cid-7rwoky4j> <div class="sect-label" data-astro-cid-7rwoky4j>Ganadores en el Catálogo</div> <div class="poster-row" data-astro-cid-7rwoky4j> ${topWinners.map((r, i) => {
    const colorId = getColor(r.works);
    const palette = colorId ? getPaletteEntry(colorId) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug(r.work_id)}`, "href")} class="poster-card" data-astro-cid-7rwoky4j> <img${addAttribute(`${TMDB_IMG}${r.works.tmdb_poster_path}`, "src")}${addAttribute(r.works.title, "alt")} class="poster-card__img" loading="lazy" decoding="async" data-astro-cid-7rwoky4j> <span class="poster-card__num" data-astro-cid-7rwoky4j>#${i + 1}</span> <div class="poster-card__overlay" data-astro-cid-7rwoky4j> <span class="poster-card__overlay-title" data-astro-cid-7rwoky4j>${r.works.title}</span> ${r.works.year && renderTemplate`<span class="poster-card__overlay-year" data-astro-cid-7rwoky4j>${r.works.year}</span>`} <span class="poster-card__overlay-award" data-astro-cid-7rwoky4j>${r.awards.name}</span> ${palette && renderTemplate`<span class="poster-card__overlay-color"${addAttribute(`color: ${palette.hex}`, "style")} data-astro-cid-7rwoky4j> ${palette.name} </span>`} </div> </a>`;
  })} </div> </div> </section>`} <section class="fest-history" data-astro-cid-7rwoky4j> <div class="site-container" data-astro-cid-7rwoky4j> <h2 class="sect-label" data-astro-cid-7rwoky4j>Historial de Premios</h2> <div class="award-groups" data-astro-cid-7rwoky4j> ${awardGroups.map((group) => renderTemplate`<div class="award-group" data-astro-cid-7rwoky4j> <h3 class="award-group__name" data-astro-cid-7rwoky4j> ${group.isGrandPrize && renderTemplate`<span class="award-group__star" aria-hidden="true" data-astro-cid-7rwoky4j>★</span>`} ${group.awardName} <span class="award-group__counts" data-astro-cid-7rwoky4j> ${group.wins.length > 0 && renderTemplate`<span class="count-win" data-astro-cid-7rwoky4j>${group.wins.length}W</span>`} ${group.noms.length > 0 && renderTemplate`<span class="count-nom" data-astro-cid-7rwoky4j>${group.noms.length}N</span>`} </span> </h3> <ul class="award-rows" role="list" data-astro-cid-7rwoky4j>  ${[...group.wins].sort((a, b) => (b.year ?? 0) - (a.year ?? 0)).map((r) => renderTemplate`<li class="award-row award-row--win" data-astro-cid-7rwoky4j> <span class="award-row__year" data-astro-cid-7rwoky4j>${r.year ?? "\u2014"}</span> ${r.works ? renderTemplate`<a${addAttribute(`/films/${filmSlug(r.work_id)}`, "href")} class="award-row__title" data-astro-cid-7rwoky4j> ${r.works.title} </a>` : renderTemplate`<span class="award-row__title award-row__title--unknown" data-astro-cid-7rwoky4j>${r.work_id}</span>`} <span class="award-row__badge award-row__badge--win" data-astro-cid-7rwoky4j>WIN</span> </li>`)}  ${[...group.noms].sort((a, b) => (b.year ?? 0) - (a.year ?? 0)).map((r) => renderTemplate`<li class="award-row award-row--nom" data-astro-cid-7rwoky4j> <span class="award-row__year" data-astro-cid-7rwoky4j>${r.year ?? "\u2014"}</span> ${r.works ? renderTemplate`<a${addAttribute(`/films/${filmSlug(r.work_id)}`, "href")} class="award-row__title" data-astro-cid-7rwoky4j> ${r.works.title} </a>` : renderTemplate`<span class="award-row__title award-row__title--unknown" data-astro-cid-7rwoky4j>${r.work_id}</span>`} <span class="award-row__badge award-row__badge--nom" data-astro-cid-7rwoky4j>NOM</span> </li>`)} </ul> </div>`)} </div> </div> </section> ` })}`} </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/festivals/[slug].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/festivals/[slug].astro";
const $$url = "/festivals/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
