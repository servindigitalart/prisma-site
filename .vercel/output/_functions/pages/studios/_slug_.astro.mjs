/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_BW8MRUf7.mjs';
import { g as getPaletteEntry } from '../../chunks/colorPalette_MBD9-pHi.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { a as isoToFlag, i as isoToName } from '../../chunks/countries_xwzpexnz.mjs';
import fs from 'node:fs';
import path from 'node:path';
/* empty css                                     */
export { renderers } from '../../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$slug;
  const { slug } = Astro2.params;
  if (!slug) return Astro2.redirect("/404");
  const studioId = `studio_${slug}`;
  let studio = null;
  let films = [];
  if (isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const { data: studioData } = await db.from("studios").select("id, name, country, founded_year, tmdb_id, logo_path").eq("id", studioId).maybeSingle();
      if (studioData) {
        studio = studioData;
        const { data: filmData } = await db.from("work_studios").select(`
          works!inner(
            id, title, year, is_published, tmdb_poster_path,
            color_assignments(color_iconico, tier, numeric_score)
          )
        `).eq("studio_id", studioId).eq("works.is_published", true);
        films = (filmData ?? []).map((row) => {
          const r = row;
          const ca = r.works.color_assignments?.[0] ?? null;
          return {
            id: r.works.id,
            title: r.works.title,
            year: r.works.year,
            color_iconico: ca?.color_iconico ?? null,
            tier: ca?.tier ?? null,
            tmdb_poster_path: r.works.tmdb_poster_path ?? null,
            numeric_score: ca?.numeric_score ?? null
          };
        });
      }
    } catch {
    }
  }
  if (!studio) {
    const studioPath = path.resolve(`pipeline/normalized/studios/${studioId}.json`);
    if (fs.existsSync(studioPath)) {
      try {
        const raw = JSON.parse(fs.readFileSync(studioPath, "utf-8"));
        studio = { id: raw.id, name: raw.name, country: raw.country, founded_year: raw.founded_year };
      } catch {
      }
    }
  }
  if (studio && films.length === 0) {
    const worksDir = path.resolve("pipeline/normalized/works");
    if (fs.existsSync(worksDir)) {
      for (const file of fs.readdirSync(worksDir).filter((f) => f.endsWith(".json"))) {
        try {
          const work = JSON.parse(fs.readFileSync(path.join(worksDir, file), "utf-8"));
          const studios = work.studios ?? [];
          if (studios.includes(studioId)) {
            const palette = work.prisma_palette;
            films.push({
              id: work.id,
              title: work.title,
              year: work.year ?? null,
              color_iconico: palette?.primary ?? null,
              tier: null,
              tmdb_poster_path: null,
              numeric_score: null
            });
          }
        } catch {
        }
      }
    }
  }
  if (!studio) return Astro2.redirect("/404");
  const topFilms = [...films].filter((f) => f.tmdb_poster_path).sort((a, b) => (b.numeric_score ?? 0) - (a.numeric_score ?? 0)).slice(0, 5);
  films.sort((a, b) => (b.year ?? 0) - (a.year ?? 0));
  const TMDB_IMG = "https://image.tmdb.org/t/p";
  const logoUrl = studio.logo_path ? `${TMDB_IMG}/w300${studio.logo_path}` : null;
  function getStudioMonogram(name) {
    return name.split(/\s+/).slice(0, 3).map((w) => w[0]?.toUpperCase() ?? "").join("");
  }
  const monogram = getStudioMonogram(studio.name);
  const flag = studio.country ? isoToFlag(studio.country) : null;
  const countryName = studio.country ? isoToName(studio.country) : null;
  const pageTitle = `${studio.name} \u2014 PRISMA`;
  const pageDescription = `${studio.name}${countryName ? ` (${countryName})` : ""}${studio.founded_year ? `, fundado en ${studio.founded_year}` : ""} \u2014 ${films.length} pel\xEDcula${films.length !== 1 ? "s" : ""} en el cat\xE1logo PRISMA.`;
  const SITE = "https://prisma.film";
  const studioBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Estudios", url: SITE },
    { name: studio.name, url: `${SITE}/studios/${slug}` }
  ];
  const studioJsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: studio.name,
    url: `${SITE}/studios/${slug}`,
    ...logoUrl ? { logo: logoUrl } : {},
    ...countryName ? { location: { "@type": "Place", name: countryName } } : {},
    ...studio.founded_year ? { foundingDate: String(studio.founded_year) } : {}
  };
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "ogImage": logoUrl ?? void 0, "jsonLd": studioJsonLd, "breadcrumbs": studioBreadcrumbs, "data-astro-cid-anxbl64p": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="studio-page page-enter" data-astro-cid-anxbl64p> <!-- ── Header ── --> <section class="studio-header" data-astro-cid-anxbl64p> <div class="site-container" data-astro-cid-anxbl64p> <div class="studio-header__inner" data-astro-cid-anxbl64p> <!-- Logo or monogram --> <div class="studio-header__logo-wrap" data-astro-cid-anxbl64p> ${logoUrl ? renderTemplate`<img${addAttribute(logoUrl, "src")} alt="" class="studio-header__logo" loading="eager" data-astro-cid-anxbl64p>` : renderTemplate`<div class="studio-header__monogram" aria-hidden="true" data-astro-cid-anxbl64p>${monogram}</div>`} ${flag && renderTemplate`<span class="studio-header__flag" aria-hidden="true" data-astro-cid-anxbl64p>${flag}</span>`} </div> <div class="studio-header__info" data-astro-cid-anxbl64p> <p class="studio-header__overline" data-astro-cid-anxbl64p>Production Studio</p> <h1 class="studio-header__name" data-astro-cid-anxbl64p>${studio.name}</h1> <div class="studio-header__meta" data-astro-cid-anxbl64p> ${countryName && renderTemplate`<span class="studio-header__meta-item" data-astro-cid-anxbl64p>${countryName}</span>`} ${studio.founded_year && renderTemplate`<span class="studio-header__meta-item" data-astro-cid-anxbl64p>Fund. ${studio.founded_year}</span>`} ${films.length > 0 && renderTemplate`<span class="studio-header__meta-item" data-astro-cid-anxbl64p> ${films.length} ${films.length === 1 ? "pel\xEDcula" : "pel\xEDculas"} en catálogo
</span>`} </div> </div> </div> </div> </section> ${films.length === 0 ? renderTemplate`<section class="studio-empty" data-astro-cid-anxbl64p> <div class="site-container" data-astro-cid-anxbl64p> <p class="studio-empty__text" data-astro-cid-anxbl64p>Aún no hay películas de este estudio en el catálogo.</p> </div> </section>` : renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-anxbl64p": true }, { "default": async ($$result3) => renderTemplate`  ${topFilms.length > 0 && renderTemplate`<section class="studio-posters" data-astro-cid-anxbl64p> <div class="site-container" data-astro-cid-anxbl64p> <div class="sect-label" data-astro-cid-anxbl64p>Películas Destacadas</div> <div class="poster-row" data-astro-cid-anxbl64p> ${topFilms.map((film, i) => {
    const filmSlug = film.id.replace(/^work_/, "");
    const palette = film.color_iconico ? getPaletteEntry(film.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="poster-card" data-astro-cid-anxbl64p> <img${addAttribute(`${TMDB_IMG}/w342${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} class="poster-card__img" loading="lazy" decoding="async" data-astro-cid-anxbl64p> <span class="poster-card__num" data-astro-cid-anxbl64p>#${i + 1}</span> <div class="poster-card__overlay" data-astro-cid-anxbl64p> <span class="poster-card__overlay-title" data-astro-cid-anxbl64p>${film.title}</span> ${film.year && renderTemplate`<span class="poster-card__overlay-year" data-astro-cid-anxbl64p>${film.year}</span>`} ${palette && renderTemplate`<span class="poster-card__overlay-color"${addAttribute(`color: ${palette.hex}`, "style")} data-astro-cid-anxbl64p> ${palette.name} </span>`} </div> </a>`;
  })} </div> </div> </section>`} <section class="studio-films" data-astro-cid-anxbl64p> <div class="site-container" data-astro-cid-anxbl64p> <div class="studio-films__list" data-astro-cid-anxbl64p> ${films.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    const palette = film.color_iconico ? getPaletteEntry(film.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="studio-film-item" data-astro-cid-anxbl64p> <div class="studio-film-item__color-strip"${addAttribute(palette ? `background: ${palette.hex}` : "background: var(--surface-border)", "style")} data-astro-cid-anxbl64p></div> <span class="studio-film-item__year" data-astro-cid-anxbl64p>${film.year ?? "\u2014"}</span> <span class="studio-film-item__title" data-astro-cid-anxbl64p>${film.title}</span> ${palette && renderTemplate`<span class="studio-film-item__color" data-astro-cid-anxbl64p>${palette.name}</span>`} </a>`;
  })} </div> </div> </section> ` })}`} </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/studios/[slug].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/studios/[slug].astro";
const $$url = "/studios/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
