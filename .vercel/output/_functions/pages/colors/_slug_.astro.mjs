/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_BW8MRUf7.mjs';
import { g as getColorProfile } from '../../chunks/colors_QF5cQfB_.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { i as isLightColor } from '../../chunks/colorPalette_MBD9-pHi.mjs';
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
  const TMDB_SM = "https://image.tmdb.org/t/p/w342";
  const colorDisplayName = doctrine.name;
  const colorMood = doctrine.cultural_context ?? "";
  const topFilmNames = allFilms.slice(0, 3).map((f) => f.title);
  const topFilmList = topFilmNames.length ? ` Incluye ${topFilmNames.join(", ")} y m\xE1s.` : "";
  const pageTitle = `${colorDisplayName} \u2014 Paleta PRISMA | Cine de Autor`;
  const pageDescription = `Las mejores pel\xEDculas de cine de autor clasificadas como ${colorDisplayName} en PRISMA. ${colorMood}${topFilmList}`.slice(0, 160);
  const colorOgImage = allFilms.find((f) => f.tmdb_poster_path)?.tmdb_poster_path ? `https://image.tmdb.org/t/p/w780${allFilms.find((f) => f.tmdb_poster_path).tmdb_poster_path}` : void 0;
  const SITE = "https://prisma.film";
  const colorJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: pageTitle,
    description: pageDescription,
    url: `${SITE}/colors/${slug}`,
    numberOfItems: allFilms.length,
    itemListElement: allFilms.slice(0, 10).map((film, i) => ({
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
  const colorBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Colores", url: `${SITE}/colors` },
    { name: colorDisplayName, url: `${SITE}/colors/${slug}` }
  ];
  const CINEMATOGRAPHER_SLUG = {
    "Agnes Godard": "agnes-godard",
    "Bruno Delbonnel": "bruno-delbonnel",
    "Christopher Doyle": "christopher-doyle",
    "Ed Lachman": "edward-lachman",
    "Edward Lachman": "edward-lachman",
    "Emmanuel Lubezki": "emmanuel-lubezki",
    "Gordon Willis": "gordon-willis",
    "Gregg Toland": "gregg-toland",
    "Harris Savides": "harris-savides",
    "Raoul Coutard": "raoul-coutard",
    "Robert Richardson": "robert-richardson",
    "Robert Yeoman": "robert-d-yeoman",
    "Rodrigo Prieto": "rodrigo-prieto",
    "Roger Deakins": "roger-deakins",
    "Sven Nykvist": "sven-nykvist",
    "Vittorio Storaro": "vittorio-storaro"
  };
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "ogImage": colorOgImage, "jsonLd": colorJsonLd, "breadcrumbs": colorBreadcrumbs, "data-astro-cid-ggvco4jb": true }, { "default": async ($$result2) => renderTemplate`  ${maybeRenderHead()}<section class="color-hero"${addAttribute(`--c-hex: ${doctrine.hex}; --c-text: ${heroTextColor}; --c-sub: ${heroSubColor};`, "style")} data-astro-cid-ggvco4jb> <div class="color-hero__wash" data-astro-cid-ggvco4jb></div> <!-- Vertical accent bar — ColorsxStudios color identity edge --> <div class="color-hero__edge"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb></div> <div class="color-hero__inner site-container" data-astro-cid-ggvco4jb> <div class="color-hero__overline" data-astro-cid-ggvco4jb>Paleta Prisma</div> <h1 class="color-hero__name" data-astro-cid-ggvco4jb>${doctrine.name}</h1> <div class="color-hero__hex" data-astro-cid-ggvco4jb>${doctrine.hex}</div> <p class="color-hero__context" data-astro-cid-ggvco4jb>${doctrine.cultural_context}</p> <div class="color-hero__moods" data-astro-cid-ggvco4jb> ${doctrine.moods.map((mood) => renderTemplate`<span class="color-hero__mood" data-astro-cid-ggvco4jb>${mood}</span>`)} </div> </div> </section>  <section class="color-notes" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="color-notes__inner" data-astro-cid-ggvco4jb> <p class="color-notes__text reveal" data-astro-cid-ggvco4jb>${doctrine.cinematographic_notes}</p> ${doctrine.cinematographer_signatures.length > 0 && renderTemplate`<div class="color-notes__sigs reveal" data-delay="100" data-astro-cid-ggvco4jb> <span class="color-notes__sigs-label" data-astro-cid-ggvco4jb>Cinefotógrafos asociados</span> <span class="color-notes__sigs-names" data-astro-cid-ggvco4jb> ${doctrine.cinematographer_signatures.map((name, i) => {
    const personSlug = CINEMATOGRAPHER_SLUG[name];
    return renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-ggvco4jb": true }, { "default": async ($$result3) => renderTemplate`${i > 0 && renderTemplate`<span class="color-notes__sigs-sep" data-astro-cid-ggvco4jb> · </span>`}${personSlug ? renderTemplate`<a${addAttribute(`/people/${personSlug}`, "href")} class="color-notes__sigs-link" data-astro-cid-ggvco4jb>${name}</a>` : renderTemplate`<span data-astro-cid-ggvco4jb>${name}</span>`}` })}`;
  })} </span> </div>`} </div> </div> </section>  ${top10.length > 0 && renderTemplate`<section class="poster-ranking" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="section-label poster-ranking__label reveal" data-astro-cid-ggvco4jb>Ranking</div> <div class="poster-row" data-astro-cid-ggvco4jb> ${posterRow1.map((film, i) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="pcard reveal"${addAttribute(String(i * 60), "data-delay")} data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_IMG}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="pcard__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <span class="pcard__num" data-astro-cid-ggvco4jb>#${i + 1}</span> <div class="pcard__overlay" data-astro-cid-ggvco4jb> <span class="pcard__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="pcard__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> ${posterRow2.length > 0 && renderTemplate`<div class="poster-row poster-row--secondary" data-astro-cid-ggvco4jb> ${posterRow2.map((film, i) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="pcard reveal"${addAttribute(String(i * 50), "data-delay")} data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_IMG}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="pcard__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <span class="pcard__num" data-astro-cid-ggvco4jb>#${i + 6}</span> <div class="pcard__overlay" data-astro-cid-ggvco4jb> <span class="pcard__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="pcard__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div>`} </div> </section>`} ${allFilms.length > 0 ? renderTemplate`<section class="color-films" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="color-films__header reveal" data-astro-cid-ggvco4jb> <h2 class="color-films__heading" data-astro-cid-ggvco4jb>Películas en este color</h2> <span class="color-films__count" data-astro-cid-ggvco4jb>${allFilms.length} obras</span> </div> ${films.canon.length > 0 && renderTemplate`<div class="color-films__tier reveal" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--canon" data-astro-cid-ggvco4jb>Canon</span> </div> <div class="color-poster-grid" data-astro-cid-ggvco4jb> ${films.canon.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="pcard" data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_SM}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="pcard__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <div class="pcard__overlay" data-astro-cid-ggvco4jb> <span class="pcard__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="pcard__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> </div>`} ${films.core.length > 0 && renderTemplate`<div class="color-films__tier reveal" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--core" data-astro-cid-ggvco4jb>Core</span> </div> <div class="color-poster-grid" data-astro-cid-ggvco4jb> ${films.core.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="pcard" data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_SM}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="pcard__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <div class="pcard__overlay" data-astro-cid-ggvco4jb> <span class="pcard__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="pcard__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> </div>`} ${films.strong.length > 0 && renderTemplate`<div class="color-films__tier reveal" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--strong" data-astro-cid-ggvco4jb>Strong</span> </div> <div class="color-poster-grid" data-astro-cid-ggvco4jb> ${films.strong.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="pcard" data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_SM}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="pcard__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <div class="pcard__overlay" data-astro-cid-ggvco4jb> <span class="pcard__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="pcard__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> </div>`} ${films.peripheral.length > 0 && renderTemplate`<div class="color-films__tier reveal" data-astro-cid-ggvco4jb> <div class="color-films__tier-label" data-astro-cid-ggvco4jb> <span class="tier-badge tier-badge--peripheral" data-astro-cid-ggvco4jb>Peripheral</span> </div> <div class="color-poster-grid" data-astro-cid-ggvco4jb> ${films.peripheral.map((film) => {
    const filmSlug = film.id.replace(/^work_/, "");
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="pcard" data-astro-cid-ggvco4jb> ${film.tmdb_poster_path ? renderTemplate`<img${addAttribute(`${TMDB_SM}${film.tmdb_poster_path}`, "src")}${addAttribute(film.title, "alt")} loading="lazy" decoding="async" data-astro-cid-ggvco4jb>` : renderTemplate`<div class="pcard__fallback"${addAttribute(`background: ${doctrine.hex}`, "style")} data-astro-cid-ggvco4jb> <span data-astro-cid-ggvco4jb>${film.title}</span> </div>`} <div class="pcard__overlay" data-astro-cid-ggvco4jb> <span class="pcard__overlay-title" data-astro-cid-ggvco4jb>${film.title}</span> ${film.year && renderTemplate`<span class="pcard__overlay-year" data-astro-cid-ggvco4jb>${film.year}</span>`} </div> </a>`;
  })} </div> </div>`} </div> </section>` : renderTemplate`<section class="color-films" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <p class="color-films__empty" data-astro-cid-ggvco4jb>Aún no hay películas asignadas a este color.</p> </div> </section>`} ${doctrine.reference_examples.length > 0 && renderTemplate`<section class="color-refs" data-astro-cid-ggvco4jb> <div class="site-container" data-astro-cid-ggvco4jb> <div class="color-refs__inner" data-astro-cid-ggvco4jb> <div class="section-label color-refs__label reveal" data-astro-cid-ggvco4jb>Ejemplos de referencia</div> <p class="color-refs__note reveal" data-delay="60" data-astro-cid-ggvco4jb>Ilustrativos únicamente — no son asignaciones canónicas.</p> <ul class="color-refs__list" data-astro-cid-ggvco4jb> ${doctrine.reference_examples.map((ex, i) => renderTemplate`<li class="color-refs__item reveal"${addAttribute(String(i * 40), "data-delay")} data-astro-cid-ggvco4jb>${ex}</li>`)} </ul> </div> </div> </section>`}` })} `;
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
