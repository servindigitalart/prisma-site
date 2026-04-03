/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, al as renderSlot, m as maybeRenderHead, o as Fragment, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_BW8MRUf7.mjs';
import { g as getPaletteEntry } from '../../chunks/colorPalette_MBD9-pHi.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { l as loadAllWorks } from '../../chunks/loadWork_B0uYB5uV.mjs';
/* empty css                                    */
export { renderers } from '../../renderers.mjs';

const $$Astro$1 = createAstro("https://prisma.film");
const $$Layout = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$1, $$props, $$slots);
  Astro2.self = $$Layout;
  const { title = "PRISMA", description, ogImage, ogType, jsonLd, breadcrumbs } = Astro2.props;
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description, "ogImage": ogImage, "ogType": ogType, "jsonLd": jsonLd, "breadcrumbs": breadcrumbs }, { "default": ($$result2) => renderTemplate` ${renderSlot($$result2, $$slots["default"])} ` })}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/layouts/Layout.astro", void 0);

const $$Astro = createAstro("https://prisma.film");
const $$Films = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$Films;
  const PER_PAGE = 50;
  const pageParam = Astro2.url.searchParams.get("page");
  const currentPage = Math.max(1, parseInt(pageParam ?? "1", 10));
  let allRankedWorks = [];
  if (isSupabaseConfigured()) {
    const db = createServiceClient();
    const { data: rankings } = await db.from("ranking_scores").select("entity_id, score, rank").eq("entity_type", "work").eq("context", "global").order("rank", { ascending: true }).limit(1e3);
    const { data: allWorks, error } = await db.from("works").select("id, title, year, color_assignments(color_iconico, tier, numeric_score)").eq("is_published", true).limit(1e3);
    if (error) console.error("[rankings/films] Error fetching works:", error);
    const rankMap = new Map(
      (rankings ?? []).map((r) => [r.entity_id, r])
    );
    const fsColorMap = new Map(
      loadAllWorks().map((w) => [w.id, w.prisma_palette?.primary ?? null])
    );
    const merged = (allWorks ?? []).map((work) => {
      const ranking = rankMap.get(work.id);
      const colorId = work.color_assignments?.[0]?.color_iconico ?? fsColorMap.get(work.id) ?? null;
      const p = colorId ? getPaletteEntry(colorId) : null;
      return {
        slug: work.id.replace("work_", ""),
        title: work.title,
        year: work.year,
        _hasRank: ranking != null,
        _rawRank: ranking?.rank ?? null,
        score: ranking?.score ?? null,
        colorId,
        colorHex: p?.hex ?? "#1B2A41",
        colorName: p?.name ?? "",
        tier: work.color_assignments?.[0]?.tier ?? null
      };
    });
    merged.sort((a, b) => {
      if (a._hasRank && b._hasRank) return (a._rawRank ?? 9999) - (b._rawRank ?? 9999);
      if (a._hasRank) return -1;
      if (b._hasRank) return 1;
      return (b.year ?? 0) - (a.year ?? 0);
    });
    allRankedWorks = merged.map((w, i) => ({
      slug: w.slug,
      title: w.title,
      year: w.year,
      rank: i + 1,
      score: w.score,
      colorId: w.colorId,
      colorHex: w.colorHex,
      colorName: w.colorName,
      tier: w.tier
    }));
  } else {
    const works = loadAllWorks();
    allRankedWorks = works.map((w, i) => {
      const colorId = w.prisma_palette?.primary ?? null;
      const p = colorId ? getPaletteEntry(colorId) : null;
      return {
        slug: w.slug,
        title: w.title,
        year: w.year ?? null,
        rank: i + 1,
        score: null,
        colorId,
        colorHex: p?.hex ?? "#1B2A41",
        colorName: p?.name ?? "",
        tier: null
      };
    });
  }
  const totalFilms = allRankedWorks.length;
  const totalPages = Math.max(1, Math.ceil(totalFilms / PER_PAGE));
  const safePage = Math.min(currentPage, totalPages);
  const offset = (safePage - 1) * PER_PAGE;
  const pageWorks = allRankedWorks.slice(offset, offset + PER_PAGE);
  const SITE = "https://prisma.film";
  const rankingsTitle = "Rankings de Pel\xEDculas \u2014 PRISMA | Mejores Pel\xEDculas de Autor";
  const rankingsDescription = "El ranking PRISMA de las mejores pel\xEDculas de cine de autor, ordenadas por peso cultural, premios internacionales y calificaci\xF3n editorial. Descubre las joyas del cine mundial.";
  const rankingsBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Rankings", url: `${SITE}/rankings/films` }
  ];
  const rankingsJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: rankingsTitle,
    description: rankingsDescription,
    url: `${SITE}/rankings/films`,
    numberOfItems: totalFilms,
    itemListElement: pageWorks.slice(0, 20).map((film, i) => ({
      "@type": "ListItem",
      position: offset + i + 1,
      item: {
        "@type": "Movie",
        name: film.title,
        dateCreated: film.year?.toString(),
        url: `${SITE}/films/${film.slug}`
      }
    }))
  };
  function pageUrl(p) {
    return `/rankings/films${p === 1 ? "" : `?page=${p}`}`;
  }
  function pageWindow(current, total) {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages = [1];
    if (current > 3) pages.push("\u2026");
    for (let p = Math.max(2, current - 1); p <= Math.min(total - 1, current + 1); p++) pages.push(p);
    if (current < total - 2) pages.push("\u2026");
    pages.push(total);
    return pages;
  }
  return renderTemplate`${renderComponent($$result, "Layout", $$Layout, { "title": rankingsTitle, "description": rankingsDescription, "jsonLd": rankingsJsonLd, "breadcrumbs": rankingsBreadcrumbs, "data-astro-cid-4e4smigm": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="rankings-page page-enter" data-astro-cid-4e4smigm> <div class="rankings-header site-container" data-astro-cid-4e4smigm> <h1 class="rankings-header__title" data-astro-cid-4e4smigm>Rankings de Películas</h1> <p class="rankings-header__desc" data-astro-cid-4e4smigm>
Clasificadas por puntaje de prestigio: canon (40%), reconocimiento en festivales (30%),
        engagement (20%), distribución arthouse (10%).
</p> <p class="rankings-header__count" data-astro-cid-4e4smigm> ${totalFilms} películas &middot; página ${safePage} de ${totalPages} </p> </div> <div class="site-container" data-astro-cid-4e4smigm> ${pageWorks.length === 0 ? renderTemplate`<div class="rankings-empty" data-astro-cid-4e4smigm> <p data-astro-cid-4e4smigm>Aún no hay rankings disponibles. Los rankings se calculan a partir de las obras ingresadas.</p> </div>` : renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-4e4smigm": true }, { "default": async ($$result3) => renderTemplate` <div class="rankings-list" data-astro-cid-4e4smigm> ${pageWorks.map((item) => renderTemplate`<a${addAttribute(`/films/${item.slug}`, "href")} class="ranking-row" data-astro-cid-4e4smigm> <div class="ranking-row__num" data-astro-cid-4e4smigm>#${item.rank}</div> <div class="ranking-row__color-strip"${addAttribute(`background: ${item.colorHex}`, "style")}${addAttribute(item.colorName, "title")} data-astro-cid-4e4smigm></div> <div class="ranking-row__info" data-astro-cid-4e4smigm> <span class="ranking-row__title" data-astro-cid-4e4smigm>${item.title}</span> ${item.year && renderTemplate`<span class="ranking-row__year" data-astro-cid-4e4smigm>${item.year}</span>`} </div> <div class="ranking-row__meta" data-astro-cid-4e4smigm> ${item.colorName && renderTemplate`<span class="ranking-row__color" data-astro-cid-4e4smigm>${item.colorName}</span>`} ${item.tier && renderTemplate`<span${addAttribute(`tier-badge tier-badge--${item.tier}`, "class")} data-astro-cid-4e4smigm>${item.tier}</span>`} ${item.score && renderTemplate`<span class="ranking-row__score" data-astro-cid-4e4smigm>${item.score.toFixed(1)}</span>`} </div> </a>`)} </div> ${totalPages > 1 && renderTemplate`<nav class="pagination" aria-label="Rankings pages" data-astro-cid-4e4smigm> <a${addAttribute(pageUrl(safePage - 1), "href")}${addAttribute(`pagination__btn${safePage === 1 ? " pagination__btn--disabled" : ""}`, "class")}${addAttribute(safePage === 1, "aria-disabled")} data-astro-cid-4e4smigm>
← Anterior
</a> <div class="pagination__pages" data-astro-cid-4e4smigm> ${pageWindow(safePage, totalPages).map(
    (p) => p === "\u2026" ? renderTemplate`<span class="pagination__ellipsis" data-astro-cid-4e4smigm>…</span>` : renderTemplate`<a${addAttribute(pageUrl(p), "href")}${addAttribute(`pagination__page${p === safePage ? " pagination__page--active" : ""}`, "class")}${addAttribute(p === safePage ? "page" : void 0, "aria-current")} data-astro-cid-4e4smigm> ${p} </a>`
  )} </div> <a${addAttribute(pageUrl(safePage + 1), "href")}${addAttribute(`pagination__btn${safePage === totalPages ? " pagination__btn--disabled" : ""}`, "class")}${addAttribute(safePage === totalPages, "aria-disabled")} data-astro-cid-4e4smigm>
Siguiente →
</a> </nav>`}` })}`} </div> </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/rankings/films.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/rankings/films.astro";
const $$url = "/rankings/films";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Films,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
