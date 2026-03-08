/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_CKaj1kxH.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { g as getPaletteEntry } from '../../chunks/colorPalette_MBD9-pHi.mjs';
import { l as loadAllWorks } from '../../chunks/loadWork_B0uYB5uV.mjs';
/* empty css                                       */
export { renderers } from '../../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
async function getStaticPaths() {
  const decades = ["1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"];
  return decades.map((decade) => ({ params: { decade } }));
}
const $$decade = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$decade;
  const { decade } = Astro2.params;
  if (!decade) return Astro2.redirect("/404");
  const startYear = parseInt(decade);
  const endYear = startYear + 9;
  let films = [];
  if (isSupabaseConfigured()) {
    const db = createServiceClient();
    const { data, error } = await db.from("works").select(`
      id,
      title,
      year,
      tmdb_poster_path,
      color_assignments(color_iconico, numeric_score)
    `).eq("is_published", true).gte("year", startYear).lte("year", endYear).order("year", { ascending: false }).limit(500);
    if (error) console.error("[decades] Error:", error);
    for (const row of data ?? []) {
      const ca = Array.isArray(row.color_assignments) ? row.color_assignments[0] : row.color_assignments;
      films.push({
        id: row.id,
        title: row.title,
        year: row.year,
        tmdb_poster_path: row.tmdb_poster_path,
        color_iconico: ca?.color_iconico ?? null,
        numeric_score: ca?.numeric_score ?? null
      });
    }
  } else {
    const works = loadAllWorks();
    films = works.filter((w) => w.year && w.year >= startYear && w.year <= endYear).map((w) => ({
      id: w.id,
      title: w.title,
      year: w.year ?? null,
      tmdb_poster_path: w.media?.poster_path ?? null,
      color_iconico: w.prisma_palette?.primary ?? null,
      numeric_score: null
    }));
  }
  const sorted = [...films].sort((a, b) => {
    if (a.numeric_score != null && b.numeric_score != null) return b.numeric_score - a.numeric_score;
    if (a.numeric_score != null) return -1;
    if (b.numeric_score != null) return 1;
    return (b.year ?? 0) - (a.year ?? 0);
  });
  const TMDB_IMG = "https://image.tmdb.org/t/p/w342";
  const top5 = sorted.filter((f) => f.tmdb_poster_path).slice(0, 5);
  const decadeLabel = `los ${decade}`;
  const topFilmNames = sorted.slice(0, 3).map((f) => f.title);
  const topFilmList = topFilmNames.length ? ` Incluye ${topFilmNames.join(", ")} y m\xE1s.` : "";
  const SITE = "https://prisma.film";
  const pageTitle = `Las Mejores Pel\xEDculas de ${decadeLabel} \u2014 PRISMA`;
  const pageDescription = `El mejor cine de autor de la d\xE9cada de ${decadeLabel} seg\xFAn PRISMA. Ranking editorial con ${films.length} pel\xEDculas seleccionadas por color, premios y peso cultural.${topFilmList}`.slice(0, 160);
  const decadeOgImage = sorted.find((f) => f.tmdb_poster_path)?.tmdb_poster_path ? `https://image.tmdb.org/t/p/w780${sorted.find((f) => f.tmdb_poster_path).tmdb_poster_path}` : void 0;
  const decadeJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: pageTitle,
    description: pageDescription,
    url: `${SITE}/decades/${decade}`,
    numberOfItems: films.length,
    itemListElement: sorted.slice(0, 10).map((film, i) => ({
      "@type": "ListItem",
      position: i + 1,
      item: {
        "@type": "Movie",
        name: film.title,
        dateCreated: film.year?.toString(),
        url: `${SITE}/films/${film.id.replace(/^work_/, "")}`
      }
    }))
  };
  const decadeBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Rankings", url: `${SITE}/rankings/films` },
    { name: `D\xE9cada de ${decadeLabel}`, url: `${SITE}/decades/${decade}` }
  ];
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "ogImage": decadeOgImage, "jsonLd": decadeJsonLd, "breadcrumbs": decadeBreadcrumbs, "data-astro-cid-wsuawy6a": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="decade-page page-enter" data-astro-cid-wsuawy6a> <!-- Header --> <section class="decade-header" data-astro-cid-wsuawy6a> <div class="site-container" data-astro-cid-wsuawy6a> <div class="decade-header__inner" data-astro-cid-wsuawy6a> <div class="decade-header__badge" aria-hidden="true" data-astro-cid-wsuawy6a>${decade}</div> <div class="decade-header__info" data-astro-cid-wsuawy6a> <div class="decade-header__overline" data-astro-cid-wsuawy6a>Cine de Autor por Década</div> <h1 class="decade-header__name" data-astro-cid-wsuawy6a>Década de ${decadeLabel}</h1> <p class="decade-header__count" data-astro-cid-wsuawy6a> ${films.length} ${films.length === 1 ? "pel\xEDcula" : "pel\xEDculas"} en el catálogo
</p> </div> </div> </div> </section> <!-- Top 5 poster row --> ${top5.length > 0 && renderTemplate`<section class="decade-posters" data-astro-cid-wsuawy6a> <div class="site-container" data-astro-cid-wsuawy6a> <div class="decade-posters__label" data-astro-cid-wsuawy6a>Películas Destacadas</div> <div class="poster-row" data-astro-cid-wsuawy6a> ${top5.map((film, i) => {
    const filmSlug = film.id.replace(/^work_/, "");
    const palette = film.color_iconico ? getPaletteEntry(film.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="poster-card" data-astro-cid-wsuawy6a> <img${addAttribute(`${TMDB_IMG}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} class="poster-card__img" loading="lazy" decoding="async" data-astro-cid-wsuawy6a> <span class="poster-card__num" data-astro-cid-wsuawy6a>#${i + 1}</span> <div class="poster-card__overlay" data-astro-cid-wsuawy6a> <span class="poster-card__overlay-title" data-astro-cid-wsuawy6a>${film.title}</span> ${film.year && renderTemplate`<span class="poster-card__overlay-year" data-astro-cid-wsuawy6a>${film.year}</span>`} ${palette && renderTemplate`<span class="poster-card__overlay-color"${addAttribute(`color: ${palette.hex}`, "style")} data-astro-cid-wsuawy6a> ${palette.name} </span>`} </div> </a>`;
  })} </div> </div> </section>`} <!-- Film list --> <section class="decade-films" data-astro-cid-wsuawy6a> <div class="site-container" data-astro-cid-wsuawy6a> <div class="decade-films__list" data-astro-cid-wsuawy6a> ${sorted.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    const palette = film.color_iconico ? getPaletteEntry(film.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="decade-film-row" data-astro-cid-wsuawy6a> <div class="decade-film-row__strip"${addAttribute(palette ? `background: ${palette.hex}` : "background: var(--surface-border)", "style")} data-astro-cid-wsuawy6a></div> <div class="decade-film-row__year" data-astro-cid-wsuawy6a> ${film.year ?? "\u2014"} </div> <div class="decade-film-row__info" data-astro-cid-wsuawy6a> <span class="decade-film-row__title" data-astro-cid-wsuawy6a>${film.title}</span> ${palette && renderTemplate`<span class="decade-film-row__color" data-astro-cid-wsuawy6a>${palette.name}</span>`} </div> </a>`;
  })} </div> </div> </section> ${films.length === 0 && renderTemplate`<div class="decade-empty site-container" data-astro-cid-wsuawy6a> <p data-astro-cid-wsuawy6a>Aún no hay películas de esta década en el catálogo.</p> </div>`} </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/decades/[decade].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/decades/[decade].astro";
const $$url = "/decades/[decade]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$decade,
  file: $$file,
  getStaticPaths,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
