/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_CKaj1kxH.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { g as getPaletteEntry } from '../../chunks/colorPalette_MBD9-pHi.mjs';
import { s as slugToIso, i as isoToName, a as isoToFlag } from '../../chunks/countries_xwzpexnz.mjs';
import { l as loadAllWorks } from '../../chunks/loadWork_B0uYB5uV.mjs';
/* empty css                                     */
export { renderers } from '../../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$slug;
  const { slug } = Astro2.params;
  if (!slug) return Astro2.redirect("/404");
  const iso2 = slugToIso(slug);
  const countryName = isoToName(iso2);
  const countryFlag = isoToFlag(iso2);
  let films = [];
  if (isSupabaseConfigured()) {
    const db = createServiceClient();
    const { data, error } = await db.from("works").select(`
      id,
      title,
      year,
      tmdb_poster_path,
      color_assignments(color_iconico, numeric_score)
    `).contains("countries", [iso2]).eq("is_published", true).order("year", { ascending: false }).limit(500);
    if (error) console.error("[countries/slug] Error:", error);
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
    films = works.filter((w) => (w.countries ?? []).includes(iso2)).map((w) => ({
      id: w.id,
      title: w.title,
      year: w.year ?? null,
      tmdb_poster_path: w.media?.poster_path ?? null,
      color_iconico: w.prisma_palette?.primary ?? null,
      numeric_score: null
    }));
  }
  if (films.length === 0) return Astro2.redirect("/404");
  const TMDB_IMG = "https://image.tmdb.org/t/p/w342";
  const top5 = films.filter((f) => f.tmdb_poster_path).sort((a, b) => (b.numeric_score ?? 0) - (a.numeric_score ?? 0)).slice(0, 5);
  const sorted = [...films].sort((a, b) => {
    if (a.numeric_score != null && b.numeric_score != null) return b.numeric_score - a.numeric_score;
    if (a.numeric_score != null) return -1;
    if (b.numeric_score != null) return 1;
    return (b.year ?? 0) - (a.year ?? 0);
  });
  const topFilmNames = films.slice(0, 3).map((f) => f.title);
  const topFilmList = topFilmNames.length ? ` Incluye ${topFilmNames.join(", ")} y m\xE1s.` : "";
  const pageTitle = `Cine de ${countryName} ${countryFlag} \u2014 PRISMA`;
  const pageDescription = `Las mejores pel\xEDculas de ${countryName} seg\xFAn PRISMA. Cine de autor, festivales y directores de ${countryName}.${topFilmList}`.slice(0, 160);
  const countryOgImage = films.find((f) => f.tmdb_poster_path)?.tmdb_poster_path ? `https://image.tmdb.org/t/p/w780${films.find((f) => f.tmdb_poster_path).tmdb_poster_path}` : void 0;
  const SITE = "https://prisma.film";
  const countryJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: pageTitle,
    description: pageDescription,
    url: `${SITE}/countries/${slug}`,
    numberOfItems: films.length,
    itemListElement: films.slice(0, 10).map((film, i) => ({
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
  const countryBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Pa\xEDses", url: `${SITE}/countries` },
    { name: countryName, url: `${SITE}/countries/${slug}` }
  ];
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "ogImage": countryOgImage, "jsonLd": countryJsonLd, "breadcrumbs": countryBreadcrumbs, "data-astro-cid-gsg47nhg": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="country-page page-enter" data-astro-cid-gsg47nhg> <!-- Header --> <section class="country-header" data-astro-cid-gsg47nhg> <div class="site-container" data-astro-cid-gsg47nhg> <div class="country-header__inner" data-astro-cid-gsg47nhg> <div class="country-header__flag" aria-hidden="true" data-astro-cid-gsg47nhg>${countryFlag}</div> <div class="country-header__info" data-astro-cid-gsg47nhg> <div class="country-header__overline" data-astro-cid-gsg47nhg>Cine Nacional</div> <h1 class="country-header__name" data-astro-cid-gsg47nhg>${countryName}</h1> <p class="country-header__count" data-astro-cid-gsg47nhg>${films.length} ${films.length === 1 ? "pel\xEDcula" : "pel\xEDculas"} en el catálogo</p> </div> </div> </div> </section> <!-- Top 5 poster row --> ${top5.length > 0 && renderTemplate`<section class="country-posters" data-astro-cid-gsg47nhg> <div class="site-container" data-astro-cid-gsg47nhg> <div class="country-posters__label" data-astro-cid-gsg47nhg>Películas Destacadas</div> <div class="poster-row" data-astro-cid-gsg47nhg> ${top5.map((film, i) => {
    const filmSlug = film.id.replace(/^work_/, "");
    const palette = film.color_iconico ? getPaletteEntry(film.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="poster-card" data-astro-cid-gsg47nhg> <img${addAttribute(`${TMDB_IMG}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} class="poster-card__img" loading="lazy" decoding="async" data-astro-cid-gsg47nhg> <span class="poster-card__num" data-astro-cid-gsg47nhg>#${i + 1}</span> <div class="poster-card__overlay" data-astro-cid-gsg47nhg> <span class="poster-card__overlay-title" data-astro-cid-gsg47nhg>${film.title}</span> ${film.year && renderTemplate`<span class="poster-card__overlay-year" data-astro-cid-gsg47nhg>${film.year}</span>`} ${palette && renderTemplate`<span class="poster-card__overlay-color"${addAttribute(`color: ${palette.hex}`, "style")} data-astro-cid-gsg47nhg> ${palette.name} </span>`} </div> </a>`;
  })} </div> </div> </section>`} <!-- Film list --> <section class="country-films" data-astro-cid-gsg47nhg> <div class="site-container" data-astro-cid-gsg47nhg> <h2 class="country-films__heading" data-astro-cid-gsg47nhg>Filmography</h2> <div class="country-films__list" data-astro-cid-gsg47nhg> ${sorted.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    const palette = film.color_iconico ? getPaletteEntry(film.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="country-film-row" data-astro-cid-gsg47nhg> <div class="country-film-row__strip"${addAttribute(palette ? `background: ${palette.hex}` : "background: var(--surface-border)", "style")} data-astro-cid-gsg47nhg></div> <div class="country-film-row__year" data-astro-cid-gsg47nhg> ${film.year ?? "\u2014"} </div> <div class="country-film-row__info" data-astro-cid-gsg47nhg> <span class="country-film-row__title" data-astro-cid-gsg47nhg>${film.title}</span> ${palette && renderTemplate`<span class="country-film-row__color" data-astro-cid-gsg47nhg>${palette.name}</span>`} </div> ${film.numeric_score != null && renderTemplate`<div class="country-film-row__score" data-astro-cid-gsg47nhg> ${film.numeric_score.toFixed(1)} </div>`} </a>`;
  })} </div> </div> </section> </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/countries/[slug].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/countries/[slug].astro";
const $$url = "/countries/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
