/* empty css                                  */
import { f as createComponent, r as renderTemplate, k as renderComponent, m as maybeRenderHead, h as addAttribute } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_CKaj1kxH.mjs';
import { a as getAllColorProfiles } from '../chunks/colors_QF5cQfB_.mjs';
import { g as getPaletteEntry, i as isLightColor } from '../chunks/colorPalette_MBD9-pHi.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../chunks/client_DzNyPYKT.mjs';
import { l as loadAllWorks } from '../chunks/loadWork_B0uYB5uV.mjs';
/* empty css                                 */
export { renderers } from '../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const COLOR_STRIP_ORDER = [
    "rojo_pasional",
    "naranja_apocaliptico",
    "ambar_desertico",
    "amarillo_ludico",
    "verde_lima",
    "verde_esmeralda",
    "verde_distopico",
    "cian_melancolico",
    "azul_nocturno",
    "violeta_cinetico",
    "purpura_onirico",
    "magenta_pop",
    "rosa_pastel",
    "blanco_polar",
    "titanio_mecanico",
    "monocromatico_intimo",
    "claroscuro_dramatico",
    "negro_abismo"
  ];
  const colorStrips = COLOR_STRIP_ORDER.map((id) => {
    const p = getPaletteEntry(id);
    return { id, hex: p.hex, name: p.name, posters: [] };
  });
  if (isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const { data } = await db.from("color_assignments").select(`color_iconico, works!inner(id, title, tmdb_poster_path, is_published)`).in("color_iconico", COLOR_STRIP_ORDER).eq("works.is_published", true).not("works.tmdb_poster_path", "is", null).order("color_rank", { ascending: false }).limit(500);
      const countPerColor = {};
      for (const row of data ?? []) {
        const colorId = row.color_iconico;
        const work = row.works;
        if (!work?.tmdb_poster_path) continue;
        countPerColor[colorId] = countPerColor[colorId] ?? 0;
        if (countPerColor[colorId] >= 3) continue;
        countPerColor[colorId]++;
        const strip = colorStrips.find((s) => s.id === colorId);
        if (strip) {
          strip.posters.push({ slug: work.id.replace(/^work_/, ""), title: work.title, path: work.tmdb_poster_path });
        }
      }
    } catch {
    }
  }
  let topFilms = [];
  if (isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const { data } = await db.from("ranking_scores").select(`rank, score, works!inner(id, title, year, is_published, color_assignments(color_iconico, tier))`).eq("entity_type", "work").eq("context", "global").order("score", { ascending: false }).limit(5);
      for (const row of data ?? []) {
        const r = row;
        const colorId = r.works.color_assignments?.[0]?.color_iconico ?? null;
        const p = colorId ? getPaletteEntry(colorId) : null;
        topFilms.push({
          id: r.works.id,
          title: r.works.title,
          year: r.works.year,
          slug: r.works.id.replace(/^work_/, ""),
          colorId,
          colorHex: p?.hex ?? "#1B2A41",
          colorName: p?.name ?? "",
          rank: r.rank,
          score: r.score
        });
      }
      topFilms.sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
    } catch {
    }
  }
  if (topFilms.length === 0) {
    const works = loadAllWorks();
    works.sort((a, b) => (b.tmdb_rating ?? 0) - (a.tmdb_rating ?? 0));
    topFilms = works.slice(0, 5).map((w) => {
      const colorId = w.prisma_palette?.primary ?? null;
      const p = colorId ? getPaletteEntry(colorId) : null;
      return {
        id: w.id,
        title: w.title,
        year: w.year ?? null,
        slug: w.slug,
        colorId,
        colorHex: p?.hex ?? "#1B2A41",
        colorName: p?.name ?? "",
        rank: null
      };
    });
  }
  const allColors = getAllColorProfiles();
  const FEATURED_COLOR_IDS = ["amarillo_ludico", "azul_nocturno", "rojo_pasional"];
  const featuredColors = FEATURED_COLOR_IDS.map((id) => allColors.find((c) => c.id === id)).filter(Boolean);
  const homepageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "PRISMA",
    alternateName: "PRISMA Film",
    url: "https://prisma.film",
    description: "Cada pel\xEDcula tiene un color. PRISMA traza el ADN visual del cine a trav\xE9s de una paleta emocional de 18 colores.",
    potentialAction: {
      "@type": "SearchAction",
      target: "https://prisma.film/rankings/films?q={search_term_string}",
      "query-input": "required name=search_term_string"
    }
  };
  return renderTemplate(_a || (_a = __template(["", "  <script>\n(function () {\n  var TMDB = 'https://image.tmdb.org/t/p/w185';\n\n  function hexToRgba(hex, alpha) {\n    var r = parseInt(hex.slice(1, 3), 16);\n    var g = parseInt(hex.slice(3, 5), 16);\n    var b = parseInt(hex.slice(5, 7), 16);\n    return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';\n  }\n\n  // Skip on mobile\n  if (window.matchMedia('(max-width: 640px)').matches) return;\n\n  var strips = document.querySelectorAll('.prism-strip');\n\n  strips.forEach(function (strip) {\n    var posters = [];\n    try { posters = JSON.parse(strip.dataset.posters || '[]'); } catch (_) {}\n    var hex = strip.dataset.hex || '#888';\n    var injected = [];\n    var leaveTimer = null;\n\n    strip.addEventListener('mouseenter', function () {\n      if (leaveTimer) { clearTimeout(leaveTimer); leaveTimer = null; }\n      if (injected.length > 0 || posters.length === 0) return;\n\n      var n = posters.length;\n      var positions = n === 1 ? ['bottom'] : n === 2 ? ['30%', '70%'] : ['18%', '50%', '82%'];\n\n      posters.forEach(function (poster, i) {\n        var a = document.createElement('a');\n        a.href = '/films/' + poster.slug;\n        a.className = 'prism-poster';\n        a.style.left = positions[i];\n        a.style.transform = 'translateX(-50%) translateY(8px)';\n\n        var img = document.createElement('img');\n        img.src = TMDB + poster.path;\n        img.alt = poster.title;\n        img.loading = 'lazy';\n        img.decoding = 'async';\n\n        var label = document.createElement('span');\n        label.className = 'prism-poster__label';\n        label.textContent = poster.title;\n        label.style.background = hexToRgba(hex, 0.85);\n\n        a.appendChild(img);\n        a.appendChild(label);\n        strip.appendChild(a);\n        injected.push(a);\n\n        // Stagger entrance\n        setTimeout(function () {\n          a.classList.add('prism-poster--visible');\n        }, i * 60 + 20);\n      });\n    });\n\n    strip.addEventListener('mouseleave', function () {\n      if (injected.length === 0) return;\n      injected.forEach(function (el) {\n        el.classList.remove('prism-poster--visible');\n      });\n      leaveTimer = setTimeout(function () {\n        injected.forEach(function (el) { el.remove(); });\n        injected = [];\n        leaveTimer = null;\n      }, 260);\n    });\n  });\n})();\n<\/script>"])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "PRISMA \u2014 Identidad Crom\xE1tica del Cine", "description": "Cada pel\xEDcula tiene un color. PRISMA traza el ADN visual del cine a trav\xE9s de una paleta emocional de 18 colores.", "jsonLd": homepageJsonLd, "data-astro-cid-j7pv25f6": true }, { "default": async ($$result2) => renderTemplate`  ${maybeRenderHead()}<section class="prism-hero" aria-label="PRISMA color spectrum" data-astro-cid-j7pv25f6> <!-- Layer 1: color strips --> <div class="prism-strips" id="prism-strips" data-astro-cid-j7pv25f6> ${colorStrips.map((strip, i) => renderTemplate`<div class="prism-strip"${addAttribute(`background: ${strip.hex}; animation-delay: ${i * 80}ms;`, "style")}${addAttribute(strip.id, "data-color-id")}${addAttribute(strip.hex, "data-hex")}${addAttribute(JSON.stringify(strip.posters), "data-posters")} aria-hidden="true" data-astro-cid-j7pv25f6></div>`)} </div> <!-- Layer 2: dark vignette for text legibility --> <div class="prism-vignette" aria-hidden="true" data-astro-cid-j7pv25f6></div> <!-- Layer 3: text overlay --> <div class="prism-text-wrap" data-astro-cid-j7pv25f6> <div class="prism-text" data-astro-cid-j7pv25f6> <p class="prism-eyebrow" data-astro-cid-j7pv25f6>Inteligencia cromática cinematográfica</p> <h1 class="prism-title" data-astro-cid-j7pv25f6>Cada película<br data-astro-cid-j7pv25f6>tiene un color.</h1> <p class="prism-body" data-astro-cid-j7pv25f6>
PRISMA traza el ADN visual del cine a través de una paleta emocional de 18 colores —
          asignando a cada película una identidad cromática singular definida por la memoria colectiva,
          la intención cinematográfica y la resonancia cultural.
</p> <div class="prism-actions" data-astro-cid-j7pv25f6> <a href="/rankings/films" class="prism-cta" data-astro-cid-j7pv25f6>Explorar rankings</a> <a href="/colors" class="prism-link" data-astro-cid-j7pv25f6>Ver la paleta →</a> </div> </div> </div> </section>  ${topFilms.length > 0 && renderTemplate`<section class="home-films" data-astro-cid-j7pv25f6> <div class="site-container" data-astro-cid-j7pv25f6> <div class="home-films__header" data-astro-cid-j7pv25f6> <h2 class="home-films__heading" data-astro-cid-j7pv25f6>Mejor rankeadas</h2> <a href="/rankings/films" class="home-films__see-all" data-astro-cid-j7pv25f6>Ver todas →</a> </div> <div class="home-films__scroll" data-astro-cid-j7pv25f6> ${topFilms.map((film) => {
    const cardColorHex = film.colorHex || "#1A1A1F";
    return renderTemplate`<a${addAttribute(`/films/${film.slug}`, "href")} class="home-film-card"${addAttribute(`--fc: ${cardColorHex};`, "style")} data-astro-cid-j7pv25f6> <div class="home-film-card__color-wash" data-astro-cid-j7pv25f6></div> <div class="home-film-card__content" data-astro-cid-j7pv25f6> ${film.rank && renderTemplate`<span class="home-film-card__rank" data-astro-cid-j7pv25f6>#${film.rank}</span>`} <h3 class="home-film-card__title" data-astro-cid-j7pv25f6>${film.title}</h3> ${film.year && renderTemplate`<span class="home-film-card__year" data-astro-cid-j7pv25f6>${film.year}</span>`} ${film.colorName && renderTemplate`<div class="home-film-card__color" data-astro-cid-j7pv25f6> <span class="home-film-card__color-dot"${addAttribute(`background: ${cardColorHex}`, "style")} data-astro-cid-j7pv25f6></span> <span class="home-film-card__color-name" data-astro-cid-j7pv25f6>${film.colorName}</span> </div>`} </div> </a>`;
  })} </div> </div> </section>`} ${featuredColors.length > 0 && renderTemplate`<section class="home-colors" data-astro-cid-j7pv25f6> <div class="site-container" data-astro-cid-j7pv25f6> <div class="home-colors__header" data-astro-cid-j7pv25f6> <h2 class="home-colors__heading" data-astro-cid-j7pv25f6>Explora la paleta</h2> <a href="/colors" class="home-colors__see-all" data-astro-cid-j7pv25f6>Los 18 colores →</a> </div> <div class="home-colors__grid" data-astro-cid-j7pv25f6> ${featuredColors.map((color) => {
    const light = isLightColor(color.id);
    return renderTemplate`<a${addAttribute(`/colors/${color.id}`, "href")} class="home-color-block"${addAttribute(`--c: ${color.hex}; --ct: ${light ? "#0A0A0F" : "#F0EEE8"}; --cs: ${light ? "rgba(10,10,15,0.55)" : "rgba(240,238,232,0.5)"};`, "style")} data-astro-cid-j7pv25f6> <div class="home-color-block__wash" data-astro-cid-j7pv25f6></div> <div class="home-color-block__content" data-astro-cid-j7pv25f6> <span class="home-color-block__name" data-astro-cid-j7pv25f6>${color.name}</span> <span class="home-color-block__context" data-astro-cid-j7pv25f6>${color.cultural_context}</span> <div class="home-color-block__moods" data-astro-cid-j7pv25f6> ${color.moods.slice(0, 3).map((m) => renderTemplate`<span class="home-color-block__mood" data-astro-cid-j7pv25f6>${m}</span>`)} </div> </div> </a>`;
  })} </div> </div> </section>`} <section class="home-manifesto" data-astro-cid-j7pv25f6> <div class="site-container" data-astro-cid-j7pv25f6> <div class="home-manifesto__inner" data-astro-cid-j7pv25f6> <h2 class="home-manifesto__heading" data-astro-cid-j7pv25f6>
El color no es decoración.<br data-astro-cid-j7pv25f6>Es argumento.
</h2> <div class="home-manifesto__body" data-astro-cid-j7pv25f6> <p data-astro-cid-j7pv25f6>
La paleta Prisma es un rechazo deliberado al conteo de píxeles. La identidad cromática
            en el cine la determina lo que el público se lleva consigo — el rojo lastimado de una
            confrontación final, el azul frío de un café nocturno, el amarillo difuso
            de una infancia recordada.
</p> <p data-astro-cid-j7pv25f6>
Nuestro sistema de 18 colores traza el registro emocional del lenguaje visual del cine.
            No lo más frecuente en pantalla, sino lo más verdadero.
</p> </div> <a href="/colors" class="home-manifesto__link" data-astro-cid-j7pv25f6>Leer la doctrina →</a> </div> </div> </section> ` }));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/index.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/index.astro";
const $$url = "";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
