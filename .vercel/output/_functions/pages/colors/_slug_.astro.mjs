/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_QHw3iGXw.mjs';
import { g as getColorProfile } from '../../chunks/colors_QF5cQfB_.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { i as isLightColor } from '../../chunks/colorPalette_CcE_HP33.mjs';
/* empty css                                     */
export { renderers } from '../../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$slug;
  const { slug } = Astro2.params;
  if (!slug) return Astro2.redirect("/404");
  const colorId = slug.replace(/-/g, "_");
  const doctrine = getColorProfile(colorId);
  if (!doctrine) return Astro2.redirect("/404");
  const lightBg = isLightColor(colorId);
  const heroTextColor = lightBg ? "#0A0A0F" : "#F0EEE8";
  const heroSubColor = lightBg ? "rgba(10,10,15,0.55)" : "rgba(240,238,232,0.45)";
  let films = { canon: [], core: [], strong: [], peripheral: [] };
  if (isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const { data, error } = await db.from("color_assignments").select(`
        color_iconico,
        tier,
        tier_rank,
        numeric_score,
        works!inner(
          id,
          title,
          year,
          countries,
          tmdb_poster_path,
          criterion_title,
          is_published
        )
      `).eq("color_iconico", colorId).eq("review_status", "approved").order("tier", { ascending: true }).order("tier_rank", { ascending: true, nullsFirst: false }).limit(200);
      if (!error && data) {
        for (const row of data) {
          const work = row.works;
          if (!work) continue;
          const workCard = {
            id: work.id,
            title: work.title,
            year: work.year,
            countries: work.countries,
            tmdb_poster_path: work.tmdb_poster_path,
            criterion_title: work.criterion_title,
            color_iconico: row.color_iconico,
            tier: row.tier,
            tier_rank: row.tier_rank,
            numeric_score: row.numeric_score,
            prestige_score: null,
            global_rank: null
          };
          const t = row.tier ?? "uncertain";
          if (t === "canon") films.canon.push(workCard);
          else if (t === "core") films.core.push(workCard);
          else if (t === "strong") films.strong.push(workCard);
          else if (t === "peripheral") films.peripheral.push(workCard);
          else films.peripheral.push(workCard);
        }
      }
    } catch (err) {
      console.error("[colors/slug] Error fetching films:", err);
    }
  }
  const allFilms = [...films.canon, ...films.core, ...films.strong, ...films.peripheral];
  const top10 = allFilms.filter((f) => f.tmdb_poster_path).sort((a, b) => (b.numeric_score ?? 0) - (a.numeric_score ?? 0)).slice(0, 10);
  const posterRow1 = top10.slice(0, 5);
  const posterRow2 = top10.slice(5, 10);
  const TMDB_IMG = "https://image.tmdb.org/t/p/w342";
  const pageTitle = `${doctrine.name} \u2014 Prisma Color`;
  const pageDescription = doctrine.cultural_context;
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "data-astro-cid-ggvco4jb": true }, { "default": async ($$result2) => renderTemplate`  ${maybeRenderHead()}<section class="color-hero"${addAttribute(`--c-hex: ${doctrine.hex}; --c-text: ${heroTextColor}; --c-sub: ${heroSubColor};`, "style")} data-astro-cid-ggvco4jb> <div class="color-hero__wash" data-astro-cid-ggvco4jb></div> <div class="color-hero__inner site-container" data-astro-cid-ggvco4jb> <div class="color-hero__overline" data-astro-cid-ggvco4jb>Prisma Palette</div> <h1 class="color-hero__name" data-astro-cid-ggvco4jb>${doctrine.name}</h1> <div class="color-hero__hex" data-astro-cid-ggvco4jb>${doctrine.hex}</div> <p class="color-hero__context" data-astro-cid-ggvco4jb>${doctrine.cultural_context}</p> <div class="color-hero__moods" data-astro-cid-ggvco4jb> ${doctrine.moods.map((mood) => renderTemplate`<span class="color-hero__mood" data-astro-cid-ggvco4jb>${mood}</span>`)} </div> </div> <div class="color-hero__bar"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb></div> </section>  <section class="color-notes" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="color-notes__inner" data-astro-cid-ggvco4jb> <p class="color-notes__text" data-astro-cid-ggvco4jb>${doctrine.cinematographic_notes}</p> ${doctrine.cinematographer_signatures.length > 0 && renderTemplate`<div class="color-notes__sigs" data-astro-cid-ggvco4jb> <span class="color-notes__sigs-label" data-astro-cid-ggvco4jb>Associated cinematographers</span> <span class="color-notes__sigs-names" data-astro-cid-ggvco4jb>${doctrine.cinematographer_signatures.join(" \xB7 ")}</span> </div>`} </div> </div> </section>  ${top10.length > 0 && renderTemplate`<section class="poster-ranking" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="poster-ranking__label" data-astro-cid-ggvco4jb>Ranking</div> <div class="poster-row" data-astro-cid-ggvco4jb> ${posterRow1.map((film, i) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="poster-card" data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_IMG}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} class="poster-card__img" loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="poster-card__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span class="poster-card__fallback-title" data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <span class="poster-card__num" data-astro-cid-ggvco4jb>#${i + 1}</span> <div class="poster-card__overlay" data-astro-cid-ggvco4jb> <span class="poster-card__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="poster-card__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> ${posterRow2.length > 0 && renderTemplate`<div class="poster-row poster-row--secondary" data-astro-cid-ggvco4jb> ${posterRow2.map((film, i) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="poster-card" data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_IMG}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} class="poster-card__img" loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="poster-card__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span class="poster-card__fallback-title" data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <span class="poster-card__num" data-astro-cid-ggvco4jb>#${i + 6}</span> <div class="poster-card__overlay" data-astro-cid-ggvco4jb> <span class="poster-card__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="poster-card__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div>`} </div> </section>`} ${allFilms.length > 0 ? renderTemplate`<section class="color-films" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="color-films__header" data-astro-cid-ggvco4jb> <h2 class="color-films__heading" data-astro-cid-ggvco4jb>Films in this color</h2> <span class="color-films__count" data-astro-cid-ggvco4jb>${allFilms.length} works</span> </div> ${films.canon.length > 0 && renderTemplate`<div class="color-films__tier" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--canon" data-astro-cid-ggvco4jb>Canon</span> </div> <div class="color-films__grid" data-astro-cid-ggvco4jb> ${films.canon.map((film) => {
    const slug2 = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${slug2}`, "href")} class="film-card" data-astro-cid-ggvco4jb> <div class="film-card__rank" data-astro-cid-ggvco4jb> ${film.tier_rank ? `#${film.tier_rank}` : ""} </div> <div class="film-card__info" data-astro-cid-ggvco4jb> <span class="film-card__title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="film-card__year" data-astro-cid-ggvco4jb>${film.year}</span>`} ${film.criterion_title && renderTemplate`<span class="film-card__criterion" data-astro-cid-ggvco4jb>C</span>`} </div> </a>`;
  })} </div> </div>`} ${films.core.length > 0 && renderTemplate`<div class="color-films__tier" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--core" data-astro-cid-ggvco4jb>Core</span> </div> <div class="color-films__grid" data-astro-cid-ggvco4jb> ${films.core.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="film-card" data-astro-cid-ggvco4jb> <div class="film-card__info" data-astro-cid-ggvco4jb> <span class="film-card__title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="film-card__year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> </div>`} ${films.strong.length > 0 && renderTemplate`<div class="color-films__tier" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--strong" data-astro-cid-ggvco4jb>Strong</span> </div> <div class="color-films__grid" data-astro-cid-ggvco4jb> ${films.strong.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="film-card" data-astro-cid-ggvco4jb> <div class="film-card__info" data-astro-cid-ggvco4jb> <span class="film-card__title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="film-card__year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> </div>`} ${films.peripheral.length > 0 && renderTemplate`<div class="color-films__tier" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--peripheral" data-astro-cid-ggvco4jb>Peripheral</span> </div> <div class="color-films__grid" data-astro-cid-ggvco4jb> ${films.peripheral.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="film-card" data-astro-cid-ggvco4jb> <div class="film-card__info" data-astro-cid-ggvco4jb> <span class="film-card__title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="film-card__year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> </div>`} </div> </section>` : renderTemplate`<section class="color-films" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <p class="color-films__empty" data-astro-cid-ggvco4jb>No films assigned to this color yet.</p> </div> </section>`} ${doctrine.reference_examples.length > 0 && renderTemplate`<section class="color-refs" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="color-refs__inner" data-astro-cid-ggvco4jb> <h3 class="color-refs__heading" data-astro-cid-ggvco4jb>Reference examples</h3> <p class="color-refs__note" data-astro-cid-ggvco4jb>Illustrative only — not canonical assignments.</p> <ul class="color-refs__list" data-astro-cid-ggvco4jb> ${doctrine.reference_examples.map((ex) => renderTemplate`<li class="color-refs__item" data-astro-cid-ggvco4jb>${ex}</li>`)} </ul> </div> </div> </section>`}` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/colors/[slug].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/colors/[slug].astro";
const $$url = "/colors/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
