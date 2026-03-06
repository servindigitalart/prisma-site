/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, al as renderSlot, h as addAttribute, o as Fragment } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_QHw3iGXw.mjs';
/* empty css                                     */
import { g as getPaletteEntry, i as isLightColor } from '../../chunks/colorPalette_CcE_HP33.mjs';
import 'clsx';
import { g as getColorProfile } from '../../chunks/colors_QF5cQfB_.mjs';
import { R as RHYTHM_LABELS, r as rhythmSlug, T as TEMPERATURE_LABELS, t as temperatureSlug, A as ABSTRACTION_LABELS, b as abstractionSlug } from '../../chunks/filmDimensions_C2QdeXZj.mjs';
import { a as isoToFlag, i as isoToName, c as countryToSlug } from '../../chunks/countries_xwzpexnz.mjs';
import { g as getFestivalLogoUrl, i as isFestivalLogoLocal, a as getFestivalMonogram } from '../../chunks/festivalUtils_CMVWB9Ye.mjs';
import { a as getBunnyEmbedUrlSigned } from '../../chunks/bunny_oG5cOVSx.mjs';
import { a as loadWorkBySlugAsync } from '../../chunks/loadWork_B0uYB5uV.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
export { renderers } from '../../renderers.mjs';

const $$Astro$c = createAstro("https://prisma.film");
const $$FilmLayout = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$c, $$props, $$slots);
  Astro2.self = $$FilmLayout;
  const { title, description, ogImage, jsonLd } = Astro2.props;
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description, "ogImage": ogImage, "jsonLd": jsonLd, "data-astro-cid-h3sban4e": true }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="film-page page-enter" data-astro-cid-h3sban4e> ${renderSlot($$result2, $$slots["default"])} </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/layouts/FilmLayout.astro", void 0);

const $$Astro$b = createAstro("https://prisma.film");
const $$FilmHero = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$b, $$props, $$slots);
  Astro2.self = $$FilmHero;
  const { work } = Astro2.props;
  const colorId = "color_assignments" in work && work.color_assignments?.color_iconico ? work.color_assignments.color_iconico : "prisma_palette" in work && work.prisma_palette?.primary ? work.prisma_palette.primary : "azul_nocturno";
  const palette = getPaletteEntry(colorId);
  const hex = palette?.hex ?? "#1B2A41";
  const colorName = palette?.name ?? "";
  const lightText = isLightColor(colorId);
  let directorName = null;
  let directorSlug = null;
  if ("work_people" in work && Array.isArray(work.work_people)) {
    const dir = work.work_people.find((wp) => wp.role === "director");
    directorName = dir?.people?.name ?? null;
    directorSlug = dir?.people?.id?.replace(/^person_/, "") ?? null;
  } else if ("people" in work) {
    const fsWork = work;
    const dirs = fsWork.people?.director;
    if (dirs && dirs.length > 0) {
      directorSlug = dirs[0].replace(/^person_/, "");
      directorName = directorSlug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
    }
  }
  const heroTextColor = lightText ? "#0A0A0F" : "#F0EEE8";
  const heroSubColor = lightText ? "rgba(10,10,15,0.6)" : "rgba(240,238,232,0.5)";
  const TMDB_BASE = "https://image.tmdb.org/t/p/w500";
  let posterUrl = null;
  if ("tmdb_poster_path" in work && work.tmdb_poster_path) {
    posterUrl = `${TMDB_BASE}${work.tmdb_poster_path}`;
  } else if ("media" in work && work.media?.poster_path) {
    posterUrl = `${TMDB_BASE}${work.media.poster_path}`;
  }
  return renderTemplate`${maybeRenderHead()}<section class="film-hero"${addAttribute(`--hero-color: ${hex}; --hero-text: ${heroTextColor}; --hero-sub: ${heroSubColor};`, "style")} data-astro-cid-wg6y7s32> <div class="film-hero__wash" data-astro-cid-wg6y7s32></div> <div class="film-hero__inner site-container" data-astro-cid-wg6y7s32> ${posterUrl && renderTemplate`<div class="film-hero__poster" data-astro-cid-wg6y7s32> <img${addAttribute(posterUrl, "src")}${addAttribute(`${work.title} poster`, "alt")} loading="eager" data-astro-cid-wg6y7s32> </div>`} <div class="film-hero__content" data-astro-cid-wg6y7s32> ${colorName && renderTemplate`<div class="film-hero__color-chip" data-astro-cid-wg6y7s32> <span class="film-hero__color-dot"${addAttribute(`background:${hex}`, "style")} data-astro-cid-wg6y7s32></span> <a${addAttribute(`/colors/${colorId}`, "href")} class="film-hero__color-label" data-astro-cid-wg6y7s32>${colorName}</a> </div>`} <h1 class="film-hero__title" data-astro-cid-wg6y7s32>${work.title}</h1> <div class="film-hero__meta" data-astro-cid-wg6y7s32> ${directorName && (directorSlug ? renderTemplate`<a${addAttribute(`/people/${directorSlug}`, "href")} class="film-hero__director film-hero__director--link" data-astro-cid-wg6y7s32>${directorName}</a>` : renderTemplate`<span class="film-hero__director" data-astro-cid-wg6y7s32>${directorName}</span>`)} ${directorName && work.year && renderTemplate`<span class="film-hero__sep" data-astro-cid-wg6y7s32>·</span>`} ${work.year && renderTemplate`<span class="film-hero__year" data-astro-cid-wg6y7s32>${work.year}</span>`} ${"duration_min" in work && work.duration_min && renderTemplate`${renderComponent($$result, "Fragment", Fragment, { "data-astro-cid-wg6y7s32": true }, { "default": ($$result2) => renderTemplate` <span class="film-hero__sep" data-astro-cid-wg6y7s32>·</span> <span class="film-hero__runtime" data-astro-cid-wg6y7s32>${work.duration_min} min</span> ` })}`} </div> </div> </div> </section> `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmHero.astro", void 0);

const $$Astro$a = createAstro("https://prisma.film");
const $$FilmColorBlock = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$a, $$props, $$slots);
  Astro2.self = $$FilmColorBlock;
  const { work } = Astro2.props;
  const colorId = "color_assignments" in work && work.color_assignments?.color_iconico ? work.color_assignments.color_iconico : "prisma_palette" in work && work.prisma_palette?.primary ? work.prisma_palette.primary : "azul_nocturno";
  const palette = getPaletteEntry(colorId);
  const doctrine = getColorProfile(colorId);
  const lightBg = isLightColor(colorId);
  const editorialNote = "color_narrative" in work ? work.color_narrative ?? null : null;
  const contextNote = doctrine?.cultural_context ?? editorialNote ?? null;
  const cinematographicNote = doctrine?.cinematographic_notes ?? null;
  const secondaryIds = "color_assignments" in work && work.color_assignments?.colores_secundarios ? work.color_assignments.colores_secundarios : "prisma_palette" in work && work.prisma_palette?.secondary ? work.prisma_palette.secondary ?? [] : [];
  const secondaryPalettes = secondaryIds.slice(0, 4).map((id) => getPaletteEntry(id)).filter(Boolean);
  return renderTemplate`${maybeRenderHead()}<section class="film-color-block" data-astro-cid-2n3uilas> <div class="site-container" data-astro-cid-2n3uilas> <div class="film-color-block__layout" data-astro-cid-2n3uilas> <div class="film-color-block__swatch-col" data-astro-cid-2n3uilas> <div class="film-color-block__swatch"${addAttribute(`background: ${palette?.hex ?? "#1B2A41"}`, "style")} role="img"${addAttribute(`${palette?.name ?? colorId} color swatch`, "aria-label")} data-astro-cid-2n3uilas> <div${addAttribute(`film-color-block__swatch-label${lightBg ? " film-color-block__swatch-label--dark" : ""}`, "class")} data-astro-cid-2n3uilas> <span class="film-color-block__swatch-hex" data-astro-cid-2n3uilas>${palette?.hex}</span> </div> </div> ${secondaryPalettes.length > 0 && renderTemplate`<div class="film-color-block__secondary" data-astro-cid-2n3uilas> <span class="film-color-block__secondary-label" data-astro-cid-2n3uilas>Secondary palette</span> <div class="film-color-block__secondary-swatches" data-astro-cid-2n3uilas> ${secondaryPalettes.map((p) => renderTemplate`<a${addAttribute(`/colors/${p.id}`, "href")}${addAttribute(p.name, "title")} class="film-color-block__secondary-dot"${addAttribute(`background: ${p.hex}`, "style")} data-astro-cid-2n3uilas></a>`)} </div> </div>`} </div> <div class="film-color-block__info" data-astro-cid-2n3uilas> <div class="film-color-block__overline" data-astro-cid-2n3uilas>Prisma Color Identity</div> <h2 class="film-color-block__color-name" data-astro-cid-2n3uilas> <a${addAttribute(`/colors/${colorId}`, "href")} data-astro-cid-2n3uilas>${palette?.name ?? colorId}</a> </h2> ${contextNote && renderTemplate`<p class="film-color-block__context" data-astro-cid-2n3uilas>${contextNote}</p>`} ${cinematographicNote && renderTemplate`<p class="film-color-block__notes" data-astro-cid-2n3uilas>${cinematographicNote}</p>`} ${doctrine && doctrine.moods.length > 0 && renderTemplate`<div class="film-color-block__moods" data-astro-cid-2n3uilas> ${doctrine.moods.map((mood) => renderTemplate`<span class="film-color-block__mood-tag" data-astro-cid-2n3uilas>${mood}</span>`)} </div>`} </div> </div> </div> </section> `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmColorBlock.astro", void 0);

const $$Astro$9 = createAstro("https://prisma.film");
const $$FilmDimensionTags = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$9, $$props, $$slots);
  Astro2.self = $$FilmDimensionTags;
  const { work } = Astro2.props;
  let rhythm = null;
  let temperature = null;
  let abstraction = null;
  if ("color_assignments" in work && work.color_assignments) {
    rhythm = work.color_assignments.ritmo_visual ?? null;
    temperature = work.color_assignments.temperatura_emocional ?? null;
    abstraction = work.color_assignments.grado_abstraccion ?? null;
  } else if ("prisma_palette" in work) {
    const fsWork = work;
    const palette = fsWork.prisma_palette;
    rhythm = palette?.ritmo_visual ?? null;
    temperature = palette?.temperatura_emocional ?? null;
    abstraction = (palette?.grado_abstraccion_visual || palette?.grado_abstraccion) ?? null;
  }
  const hasDimensions = rhythm || temperature || abstraction;
  return renderTemplate`${hasDimensions && renderTemplate`${maybeRenderHead()}<div class="film-dimensions" data-astro-cid-ds5ynflv><div class="site-container" data-astro-cid-ds5ynflv><div class="film-dimensions__inner" data-astro-cid-ds5ynflv>${rhythm && renderTemplate`<a${addAttribute(`/ritmo/${rhythmSlug(rhythm)}`, "href")} class="dim-tag dim-tag--rhythm" title="Ritmo visual" data-astro-cid-ds5ynflv><span class="dim-tag__label" data-astro-cid-ds5ynflv>Ritmo</span><span class="dim-tag__value" data-astro-cid-ds5ynflv>${RHYTHM_LABELS[rhythm]}</span></a>`}${temperature && renderTemplate`<a${addAttribute(`/temperatura/${temperatureSlug(temperature)}`, "href")} class="dim-tag dim-tag--temperature" title="Temperatura emocional" data-astro-cid-ds5ynflv><span class="dim-tag__label" data-astro-cid-ds5ynflv>Temperatura</span><span class="dim-tag__value" data-astro-cid-ds5ynflv>${TEMPERATURE_LABELS[temperature]}</span></a>`}${abstraction && renderTemplate`<a${addAttribute(`/abstraccion/${abstractionSlug(abstraction)}`, "href")} class="dim-tag dim-tag--abstraction" title="Abstracción visual" data-astro-cid-ds5ynflv><span class="dim-tag__label" data-astro-cid-ds5ynflv>Imagen</span><span class="dim-tag__value" data-astro-cid-ds5ynflv>${ABSTRACTION_LABELS[abstraction]}</span></a>`}</div></div></div>`}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmDimensionTags.astro", void 0);

const $$Astro$8 = createAstro("https://prisma.film");
const $$FilmSynopsis = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$8, $$props, $$slots);
  Astro2.self = $$FilmSynopsis;
  const { work } = Astro2.props;
  const synopsis = "synopsis" in work ? work.synopsis : null;
  const tagline = "tagline" in work ? work.tagline : null;
  const genres = work.genres ?? [];
  const countries = work.countries ?? [];
  const TMDB_LOGO = "https://image.tmdb.org/t/p/w92";
  const studios = [];
  if ("work_studios" in work && Array.isArray(work.work_studios)) {
    for (const ws of work.work_studios) {
      studios.push({
        name: ws.studios.name,
        slug: ws.studios.id.replace(/^studio_/, ""),
        logoPath: ws.studios.logo_path ?? null
      });
    }
  } else if ("studios" in work) {
    for (const s of work.studios ?? []) {
      const slug = s.replace(/^studio_/, "");
      const name = slug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      studios.push({ name, slug, logoPath: null });
    }
  }
  const colorNarrative = "color_narrative" in work ? work.color_narrative ?? null : null;
  const hasContent = synopsis || tagline || colorNarrative;
  return renderTemplate`${hasContent && renderTemplate`${maybeRenderHead()}<section class="film-synopsis" data-astro-cid-mqlkldg4><div class="site-container" data-astro-cid-mqlkldg4><div class="film-synopsis__inner" data-astro-cid-mqlkldg4>${tagline && renderTemplate`<p class="film-synopsis__tagline" data-astro-cid-mqlkldg4>"${tagline}"</p>`}${synopsis && renderTemplate`<div class="film-synopsis__body" data-astro-cid-mqlkldg4><p data-astro-cid-mqlkldg4>${synopsis}</p></div>`}${!synopsis && colorNarrative && renderTemplate`<div class="film-synopsis__body film-synopsis__body--narrative" data-astro-cid-mqlkldg4><p data-astro-cid-mqlkldg4>${colorNarrative}</p></div>`}<div class="film-synopsis__meta" data-astro-cid-mqlkldg4>${genres.length > 0 && renderTemplate`<div class="film-synopsis__meta-row" data-astro-cid-mqlkldg4><span class="film-synopsis__meta-label" data-astro-cid-mqlkldg4>Genre</span><span class="film-synopsis__meta-value" data-astro-cid-mqlkldg4>${genres.join(", ")}</span></div>`}${countries.length > 0 && renderTemplate`<div class="film-synopsis__meta-row" data-astro-cid-mqlkldg4><span class="film-synopsis__meta-label" data-astro-cid-mqlkldg4>Origin</span><span class="film-synopsis__meta-value film-synopsis__countries" data-astro-cid-mqlkldg4>${countries.map((iso2) => renderTemplate`<a${addAttribute(`/countries/${countryToSlug(iso2)}`, "href")} class="film-synopsis__country" data-astro-cid-mqlkldg4><span aria-hidden="true" data-astro-cid-mqlkldg4>${isoToFlag(iso2)}</span><span data-astro-cid-mqlkldg4>${isoToName(iso2)}</span></a>`)}</span></div>`}${studios.length > 0 && renderTemplate`<div class="film-synopsis__meta-row" data-astro-cid-mqlkldg4><span class="film-synopsis__meta-label" data-astro-cid-mqlkldg4>Production</span><span class="film-synopsis__meta-value film-synopsis__studios" data-astro-cid-mqlkldg4>${studios.map((s) => renderTemplate`<a${addAttribute(`/studios/${s.slug}`, "href")} class="film-synopsis__studio" data-astro-cid-mqlkldg4>${s.logoPath && renderTemplate`<img${addAttribute(`${TMDB_LOGO}${s.logoPath}`, "src")} alt="" class="film-synopsis__studio-logo" loading="lazy" data-astro-cid-mqlkldg4>`}${s.name}</a>`)}</span></div>`}</div></div></div></section>`}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmSynopsis.astro", void 0);

const $$Astro$7 = createAstro("https://prisma.film");
const $$FilmPeople = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$7, $$props, $$slots);
  Astro2.self = $$FilmPeople;
  const { work, castAwardHighlights = {} } = Astro2.props;
  const TMDB_IMG = "https://image.tmdb.org/t/p/w185";
  const ROLE_LABELS = {
    director: "Director",
    cinematography: "D.P.",
    writer: "Writer",
    editor: "Editor",
    composer: "Composer",
    actor: "Actor",
    production_design: "Prod. Design"
  };
  function getInitials(name) {
    return name.split(" ").filter(Boolean).slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("");
  }
  const FILMMAKER_ROLES = ["director", "writer"];
  const CREW_ROLES = ["cinematography", "editor", "composer"];
  const filmmakersMap = /* @__PURE__ */ new Map();
  const crew = [];
  const cast = [];
  if ("work_people" in work && Array.isArray(work.work_people)) {
    const fw = work;
    for (const wp of fw.work_people) {
      const card = {
        name: wp.people.name,
        role: wp.role,
        slug: wp.people.id.replace(/^person_/, ""),
        initials: getInitials(wp.people.name),
        photoUrl: wp.people.profile_path ? `${TMDB_IMG}${wp.people.profile_path}` : null,
        billingOrder: wp.billing_order ?? null
      };
      if (FILMMAKER_ROLES.includes(wp.role)) {
        const key = wp.people.id;
        if (filmmakersMap.has(key)) {
          filmmakersMap.get(key).roles.push(wp.role);
        } else {
          filmmakersMap.set(key, { card, roles: [wp.role] });
        }
      } else if (CREW_ROLES.includes(wp.role)) {
        crew.push(card);
      } else if (wp.role === "actor") {
        cast.push(card);
      }
    }
    cast.sort((a, b) => (a.billingOrder ?? 999) - (b.billingOrder ?? 999));
  } else if ("people" in work) {
    const fsWork = work;
    const roleMap = fsWork.people ?? {};
    for (const role of FILMMAKER_ROLES) {
      const ids = roleMap[role] ?? [];
      for (const id of ids) {
        const name = id.replace(/^person_/, "").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
        const card = { name, role, slug: id.replace(/^person_/, ""), initials: getInitials(name), photoUrl: null, billingOrder: null };
        if (filmmakersMap.has(id)) {
          filmmakersMap.get(id).roles.push(role);
        } else {
          filmmakersMap.set(id, { card, roles: [role] });
        }
      }
    }
    for (const role of CREW_ROLES) {
      const ids = roleMap[role] ?? [];
      for (const id of ids) {
        const name = id.replace(/^person_/, "").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
        crew.push({ name, role, slug: id.replace(/^person_/, ""), initials: getInitials(name), photoUrl: null, billingOrder: null });
      }
    }
    const castIds = roleMap["cast"] ?? [];
    for (const id of castIds) {
      const name = id.replace(/^person_/, "").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      cast.push({ name, role: "actor", slug: id.replace(/^person_/, ""), initials: getInitials(name), photoUrl: null, billingOrder: null });
    }
  }
  const filmmakers = [...filmmakersMap.values()];
  if (filmmakers.length === 0 && crew.length === 0 && cast.length === 0) return;
  return renderTemplate`${maybeRenderHead()}<section class="film-people" data-astro-cid-fptzumd4> <div class="site-container" data-astro-cid-fptzumd4>  ${filmmakers.length > 0 && renderTemplate`<div class="people-section" data-astro-cid-fptzumd4> <h3 class="people-section__heading" data-astro-cid-fptzumd4>Key Filmmakers</h3> <div class="people-grid people-grid--filmmakers" data-astro-cid-fptzumd4> ${filmmakers.map((entry) => renderTemplate`<div class="person-card" data-astro-cid-fptzumd4> <div class="person-card__avatar" data-astro-cid-fptzumd4> ${entry.card.photoUrl ? renderTemplate`<img${addAttribute(entry.card.photoUrl, "src")}${addAttribute(entry.card.name, "alt")} class="person-card__photo" loading="lazy" decoding="async" data-astro-cid-fptzumd4>` : renderTemplate`<span class="person-card__initials" aria-hidden="true" data-astro-cid-fptzumd4>${entry.card.initials}</span>`} </div> <div class="person-card__info" data-astro-cid-fptzumd4> ${entry.card.slug ? renderTemplate`<a${addAttribute(`/people/${entry.card.slug}`, "href")} class="person-card__name" data-astro-cid-fptzumd4>${entry.card.name}</a>` : renderTemplate`<span class="person-card__name" data-astro-cid-fptzumd4>${entry.card.name}</span>`} <span class="role-badge" data-astro-cid-fptzumd4> ${entry.roles.map((r) => ROLE_LABELS[r] ?? r).join(" \xB7 ")} </span> </div> </div>`)} </div> </div>`}  ${crew.length > 0 && renderTemplate`<div class="people-section" data-astro-cid-fptzumd4> <h3 class="people-section__heading" data-astro-cid-fptzumd4>Crew</h3> <div class="people-grid people-grid--crew" data-astro-cid-fptzumd4> ${crew.map((person) => renderTemplate`<div class="person-card person-card--crew" data-astro-cid-fptzumd4> <div class="person-card__avatar person-card__avatar--sm" data-astro-cid-fptzumd4> ${person.photoUrl ? renderTemplate`<img${addAttribute(person.photoUrl, "src")}${addAttribute(person.name, "alt")} class="person-card__photo" loading="lazy" decoding="async" data-astro-cid-fptzumd4>` : renderTemplate`<span class="person-card__initials" aria-hidden="true" data-astro-cid-fptzumd4>${person.initials}</span>`} </div> <div class="person-card__info" data-astro-cid-fptzumd4> ${person.slug ? renderTemplate`<a${addAttribute(`/people/${person.slug}`, "href")} class="person-card__name" data-astro-cid-fptzumd4>${person.name}</a>` : renderTemplate`<span class="person-card__name" data-astro-cid-fptzumd4>${person.name}</span>`} <span class="role-badge" data-astro-cid-fptzumd4>${ROLE_LABELS[person.role] ?? person.role}</span> </div> </div>`)} </div> </div>`}  ${cast.length > 0 && renderTemplate`<div class="people-section" data-astro-cid-fptzumd4> <h3 class="people-section__heading" data-astro-cid-fptzumd4>Cast (${cast.length})</h3> <div class="people-grid people-grid--cast" data-astro-cid-fptzumd4> ${cast.map((person) => {
    const personFullId = person.slug ? `person_${person.slug}` : "";
    const awardBadges = castAwardHighlights[personFullId] ?? [];
    return renderTemplate`<div class="person-card person-card--crew" data-astro-cid-fptzumd4> <div class="person-card__avatar person-card__avatar--sm" data-astro-cid-fptzumd4> ${person.photoUrl ? renderTemplate`<img${addAttribute(person.photoUrl, "src")}${addAttribute(person.name, "alt")} class="person-card__photo" loading="lazy" decoding="async" data-astro-cid-fptzumd4>` : renderTemplate`<span class="person-card__initials" aria-hidden="true" data-astro-cid-fptzumd4>${person.initials}</span>`} </div> <div class="person-card__info" data-astro-cid-fptzumd4> ${person.slug ? renderTemplate`<a${addAttribute(`/people/${person.slug}`, "href")} class="person-card__name" data-astro-cid-fptzumd4>${person.name}</a>` : renderTemplate`<span class="person-card__name" data-astro-cid-fptzumd4>${person.name}</span>`} ${awardBadges.length > 0 ? renderTemplate`<div class="cast-award-badges" data-astro-cid-fptzumd4> ${awardBadges.map((award) => renderTemplate`<span class="cast-award-badge" data-astro-cid-fptzumd4>${award}</span>`)} </div>` : renderTemplate`<span class="role-badge" data-astro-cid-fptzumd4>Actor</span>`} </div> </div>`;
  })} </div> </div>`} </div> </section> `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmPeople.astro", void 0);

const $$Astro$6 = createAstro("https://prisma.film");
const $$FilmMetaAccordion = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$6, $$props, $$slots);
  Astro2.self = $$FilmMetaAccordion;
  const { work } = Astro2.props;
  const isCriterion = "criterion_title" in work ? work.criterion_title : false;
  const isMubi = "mubi_title" in work ? work.mubi_title : false;
  const isSightAndSound = "is_sight_and_sound" in work ? work.is_sight_and_sound : false;
  const imdbRating = "imdb_rating" in work ? work.imdb_rating : null;
  const duration = work.duration_min;
  const languages = work.languages ?? [];
  const studios = [];
  if ("work_studios" in work && Array.isArray(work.work_studios)) {
    for (const ws of work.work_studios) {
      studios.push({ name: ws.studios.name, slug: ws.studios.id.replace(/^studio_/, "") });
    }
  } else if ("studios" in work) {
    const fsWork = work;
    for (const s of fsWork.studios ?? []) {
      const slug = s.replace(/^studio_/, "");
      const name = slug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      studios.push({ name, slug });
    }
  }
  const sections = [
    { id: "technical", title: "Technical Details", hasContent: !!(duration || languages.length || studios.length || imdbRating) },
    { id: "distribution", title: "Distribution", hasContent: !!(isCriterion || isMubi || isSightAndSound) }
  ];
  return renderTemplate`${maybeRenderHead()}<section class="film-meta-accordion" data-astro-cid-pbstxzw3> <div class="site-container" data-astro-cid-pbstxzw3> <div class="film-meta-accordion__sections" data-astro-cid-pbstxzw3> ${sections.filter((s) => s.hasContent).map((section) => renderTemplate`<details class="accordion-item" name="film-meta" data-astro-cid-pbstxzw3> <summary class="accordion-item__header" data-astro-cid-pbstxzw3> <span class="accordion-item__title" data-astro-cid-pbstxzw3>${section.title}</span> <span class="accordion-item__icon" aria-hidden="true" data-astro-cid-pbstxzw3>+</span> </summary> <div class="accordion-item__body" data-astro-cid-pbstxzw3> ${section.id === "technical" && renderTemplate`<div class="accordion-facts" data-astro-cid-pbstxzw3> ${duration && renderTemplate`<div class="accordion-fact" data-astro-cid-pbstxzw3> <span class="accordion-fact__label" data-astro-cid-pbstxzw3>Runtime</span> <span class="accordion-fact__value" data-astro-cid-pbstxzw3>${duration} minutes</span> </div>`} ${languages.length > 0 && renderTemplate`<div class="accordion-fact" data-astro-cid-pbstxzw3> <span class="accordion-fact__label" data-astro-cid-pbstxzw3>Languages</span> <span class="accordion-fact__value" data-astro-cid-pbstxzw3>${languages.join(", ")}</span> </div>`} ${studios.length > 0 && renderTemplate`<div class="accordion-fact" data-astro-cid-pbstxzw3> <span class="accordion-fact__label" data-astro-cid-pbstxzw3>Studios</span> <span class="accordion-fact__value accordion-fact__value--studios" data-astro-cid-pbstxzw3> ${studios.map((s, i) => renderTemplate`${renderComponent($$result, "Fragment", Fragment, { "data-astro-cid-pbstxzw3": true }, { "default": ($$result2) => renderTemplate` <a${addAttribute(`/studios/${s.slug}`, "href")} class="accordion-studio-link" data-astro-cid-pbstxzw3>${s.name}</a> ${i < studios.length - 1 && renderTemplate`<span class="accordion-fact__sep" data-astro-cid-pbstxzw3>, </span>`}` })}`)} </span> </div>`} ${imdbRating && renderTemplate`<div class="accordion-fact" data-astro-cid-pbstxzw3> <span class="accordion-fact__label" data-astro-cid-pbstxzw3>IMDb Rating</span> <span class="accordion-fact__value" data-astro-cid-pbstxzw3>${imdbRating.toFixed(1)}</span> </div>`} </div>`} ${section.id === "distribution" && renderTemplate`<div class="accordion-dist" data-astro-cid-pbstxzw3> ${isCriterion && renderTemplate`<span class="dist-badge dist-badge--criterion" data-astro-cid-pbstxzw3>Criterion Collection</span>`} ${isMubi && renderTemplate`<span class="dist-badge dist-badge--mubi" data-astro-cid-pbstxzw3>MUBI</span>`} ${isSightAndSound && renderTemplate`<span class="dist-badge dist-badge--s-and-s" data-astro-cid-pbstxzw3>Sight &amp; Sound</span>`} </div>`} </div> </details>`)} </div> </div> </section> `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmMetaAccordion.astro", void 0);

const $$Astro$5 = createAstro("https://prisma.film");
const $$FilmAwards = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$5, $$props, $$slots);
  Astro2.self = $$FilmAwards;
  const { work } = Astro2.props;
  if (!("work_awards" in work) || !Array.isArray(work.work_awards) || work.work_awards.length === 0) {
    return;
  }
  const castMembers = "work_people" in work && Array.isArray(work.work_people) ? work.work_people.filter((wp) => wp.role === "actor").sort((a, b) => (a.billing_order ?? 999) - (b.billing_order ?? 999)).map((wp) => ({ name: wp.people.name, billing_order: wp.billing_order })) : [];
  const ACTING_PATTERNS = [
    "best actor",
    "best actress",
    "best supporting actor",
    "best supporting actress",
    "best performance",
    "volpi cup",
    "best male",
    "best female",
    "best lead"
  ];
  function inferActingActor(awardName) {
    const lower = awardName.toLowerCase();
    if (!ACTING_PATTERNS.some((p) => lower.includes(p))) return null;
    return castMembers[0]?.name ?? null;
  }
  const allAwards = work.work_awards;
  const TIER_ORDER = { A: 0, B: 1, C: 2, D: 3 };
  function sortFn(a, b) {
    const ta = TIER_ORDER[a.awards?.festivals?.tier ?? a.awards?.tier ?? "C"] ?? 3;
    const tb = TIER_ORDER[b.awards?.festivals?.tier ?? b.awards?.tier ?? "C"] ?? 3;
    if (ta !== tb) return ta - tb;
    return (b.year ?? 0) - (a.year ?? 0);
  }
  const wins = [...allAwards.filter((wa) => wa.result === "win")].sort(sortFn);
  const noms = [...allAwards.filter((wa) => wa.result === "nomination")].sort(sortFn);
  const TIER_COLOR = {
    A: "#C98A2E",
    B: "rgba(255,255,255,0.3)",
    C: "rgba(255,255,255,0.15)",
    D: "rgba(255,255,255,0.08)"
  };
  function tierColor(wa) {
    const t = wa.awards.festivals?.tier ?? wa.awards.tier ?? "";
    return TIER_COLOR[t] ?? TIER_COLOR["C"];
  }
  function festivalName(wa) {
    return wa.awards.festivals?.name ?? wa.awards.organization;
  }
  function festivalHref(wa) {
    const fid = wa.awards.festivals?.id;
    return fid ? `/festivals/${fid.replace(/^festival_/, "")}` : void 0;
  }
  return renderTemplate`${maybeRenderHead()}<section class="film-awards" data-astro-cid-vp5wcrti> <div class="site-container" data-astro-cid-vp5wcrti> <h2 class="awards-label" data-astro-cid-vp5wcrti>Awards & Recognition</h2>  ${wins.length > 0 && renderTemplate`<div class="wins-grid" data-astro-cid-vp5wcrti> ${wins.map((wa) => {
    const color = tierColor(wa);
    const tier = wa.awards.festivals?.tier ?? wa.awards.tier;
    const href = festivalHref(wa);
    const actor = inferActingActor(wa.awards.name);
    return renderTemplate`<a${addAttribute(href, "href")} class="award-card"${addAttribute(`--tc: ${color}`, "style")}${addAttribute(`${wa.awards.name} \u2014 ${festivalName(wa)} ${wa.year ?? ""}`, "aria-label")} data-astro-cid-vp5wcrti> ${(() => {
      const logoUrl = getFestivalLogoUrl(wa.awards.festivals?.logo_path ?? null);
      const isLocal = isFestivalLogoLocal(wa.awards.festivals?.logo_path ?? null);
      const monogram = getFestivalMonogram(festivalName(wa));
      return logoUrl ? renderTemplate`<img${addAttribute(logoUrl, "src")} alt=""${addAttribute(`award-fest-logo${isLocal ? " festival-logo--local" : ""}`, "class")} loading="lazy" data-astro-cid-vp5wcrti>` : renderTemplate`<span class="award-monogram" aria-hidden="true"${addAttribute(`background: color-mix(in srgb, ${tierColor(wa)} 15%, transparent)`, "style")} data-astro-cid-vp5wcrti>${monogram}</span>`;
    })()} <div class="award-body" data-astro-cid-vp5wcrti> <span class="award-name" data-astro-cid-vp5wcrti>${wa.awards.name}</span> <span class="award-meta" data-astro-cid-vp5wcrti> ${actor && renderTemplate`${renderComponent($$result, "Fragment", Fragment, { "data-astro-cid-vp5wcrti": true }, { "default": ($$result2) => renderTemplate`${actor} &middot; ` })}`} ${festivalName(wa)}${wa.year && renderTemplate`${renderComponent($$result, "Fragment", Fragment, { "data-astro-cid-vp5wcrti": true }, { "default": ($$result2) => renderTemplate` &middot; ${wa.year}` })}`} </span> </div> ${tier && renderTemplate`<span class="award-tier-badge"${addAttribute(`color: ${color}`, "style")} data-astro-cid-vp5wcrti>[${tier}]</span>`} </a>`;
  })} </div>`}  ${noms.length > 0 && renderTemplate`<div class="noms-block" data-astro-cid-vp5wcrti> <h3 class="noms-label" data-astro-cid-vp5wcrti>Nominations</h3> <ul class="noms-list" role="list" data-astro-cid-vp5wcrti> ${noms.map((wa) => {
    const tier = wa.awards.festivals?.tier ?? wa.awards.tier;
    return renderTemplate`<li class="nom-row" data-astro-cid-vp5wcrti> <span class="nom-name" data-astro-cid-vp5wcrti>${wa.awards.name}</span> <span class="nom-sep" aria-hidden="true" data-astro-cid-vp5wcrti>&middot;</span> <span class="nom-festival" data-astro-cid-vp5wcrti>${festivalName(wa)}</span> ${wa.year && renderTemplate`<span class="nom-year" data-astro-cid-vp5wcrti>${wa.year}</span>`} ${tier && renderTemplate`<span class="nom-tier" data-astro-cid-vp5wcrti>[${tier}]</span>`} </li>`;
  })} </ul> </div>`} </div> </section> `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmAwards.astro", void 0);

const $$Astro$4 = createAstro("https://prisma.film");
const $$FilmRankBadge = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$4, $$props, $$slots);
  Astro2.self = $$FilmRankBadge;
  const { rank, score, tier, context = "global" } = Astro2.props;
  if (!rank && !score) return;
  const tierClass = tier ? `tier-badge--${tier}` : "";
  return renderTemplate`${maybeRenderHead()}<div class="film-rank-badge" data-astro-cid-cp3h7fx3> ${rank && renderTemplate`<div class="film-rank-badge__rank" data-astro-cid-cp3h7fx3> <span class="film-rank-badge__rank-label" data-astro-cid-cp3h7fx3>Rank</span> <span class="film-rank-badge__rank-number" data-astro-cid-cp3h7fx3>#${rank}</span> </div>`} ${score && renderTemplate`<div class="film-rank-badge__score" data-astro-cid-cp3h7fx3> <span class="film-rank-badge__score-label" data-astro-cid-cp3h7fx3>Score</span> <span class="film-rank-badge__score-value" data-astro-cid-cp3h7fx3>${score.toFixed(1)}</span> </div>`} ${tier && renderTemplate`<span${addAttribute(`tier-badge ${tierClass}`, "class")} data-astro-cid-cp3h7fx3>${tier}</span>`} </div> `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmRankBadge.astro", void 0);

var __freeze$1 = Object.freeze;
var __defProp$1 = Object.defineProperty;
var __template$1 = (cooked, raw) => __freeze$1(__defProp$1(cooked, "raw", { value: __freeze$1(cooked.slice()) }));
var _a$1;
const $$Astro$3 = createAstro("https://prisma.film");
const $$FilmActions = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$3, $$props, $$slots);
  Astro2.self = $$FilmActions;
  const {
    workId,
    userId,
    initialRating = null,
    initialSeen = false,
    initialWatchlist = false,
    initialReview = null
  } = Astro2.props;
  const user = Astro2.locals.user;
  const effectiveUserId = userId || user?.id || null;
  return renderTemplate(_a$1 || (_a$1 = __template$1(["", '<div class="film-actions"', "", "", "", "", "", ' data-astro-cid-mctugfxd> <!-- Rate --> <div class="film-action film-action--rate" data-astro-cid-mctugfxd> <button class="film-action__btn" id="fa-rate-btn" aria-label="Rate this film" aria-expanded="false" data-astro-cid-mctugfxd> <span class="film-action__icon" aria-hidden="true" data-astro-cid-mctugfxd>\u2605</span> <span class="film-action__label" id="fa-rate-label" data-astro-cid-mctugfxd>Rate</span> </button> <div class="rating-picker" id="fa-rating-picker" hidden aria-label="Select rating" data-astro-cid-mctugfxd> ', ` <button class="rating-clear" id="fa-rating-clear" aria-label="Clear rating" title="Clear" data-astro-cid-mctugfxd>\u2715</button> </div> </div> <!-- Seen --> <div class="film-action film-action--seen" data-astro-cid-mctugfxd> <button class="film-action__btn" id="fa-seen-btn" aria-label="Mark as seen" aria-expanded="false" data-astro-cid-mctugfxd> <span class="film-action__icon" aria-hidden="true" data-astro-cid-mctugfxd>\u2713</span> <span class="film-action__label" data-astro-cid-mctugfxd>Seen</span> </button> <div class="seen-picker" id="fa-seen-picker" hidden data-astro-cid-mctugfxd> <button class="seen-option" id="fa-seen-today" data-astro-cid-mctugfxd>Just watched</button> <button class="seen-option" id="fa-seen-before" data-astro-cid-mctugfxd>I saw this before</button> </div> </div> <!-- Watchlist --> <button class="film-action__btn film-action--watchlist" id="fa-watchlist-btn" aria-label="Add to watchlist" data-astro-cid-mctugfxd> <span class="film-action__icon" aria-hidden="true" id="fa-watchlist-icon" data-astro-cid-mctugfxd>+</span> <span class="film-action__label" id="fa-watchlist-label" data-astro-cid-mctugfxd>Watchlist</span> </button> <!-- Review (visible after rating) --> <div class="film-action film-action--review" id="fa-review-wrapper" hidden data-astro-cid-mctugfxd> <button class="film-action__btn" id="fa-review-btn" aria-label="Write a review" data-astro-cid-mctugfxd> <span class="film-action__icon" aria-hidden="true" data-astro-cid-mctugfxd>\u270E</span> <span class="film-action__label" id="fa-review-label" data-astro-cid-mctugfxd>Review</span> </button> <div class="review-editor" id="fa-review-editor" hidden data-astro-cid-mctugfxd> <textarea id="fa-review-textarea" class="review-textarea" maxlength="500" placeholder="Write your review\u2026" data-astro-cid-mctugfxd></textarea> <div class="review-footer" data-astro-cid-mctugfxd> <span class="review-charcount" id="fa-review-charcount" data-astro-cid-mctugfxd>0/500</span> <button class="review-submit" id="fa-review-submit" data-astro-cid-mctugfxd>Save review</button> </div> </div> </div> </div> <script>
(function() {
  function initFilmActions() {
    var root = document.querySelector('.film-actions');
    if (!root) return;

    var workId = root.dataset.workId;
    var userIdRaw = root.dataset.userId;
    var userId = (userIdRaw && userIdRaw !== '' && userIdRaw !== 'null' && userIdRaw !== 'undefined') ? userIdRaw : null;
    var currentRating = root.dataset.initialRating ? Number(root.dataset.initialRating) : null;
    var isSeen = root.dataset.initialSeen === '1';
    var inWatchlist = root.dataset.initialWatchlist === '1';
    var currentReview = root.dataset.initialReview || '';

    function requireAuth() {
      if (!userId) {
        if (window.showAuthModal) window.showAuthModal();
        return false;
      }
      return true;
    }

    function showToast(msg) {
      var notif = document.createElement('div');
      notif.textContent = msg;
      notif.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#1a1a1a;color:#aaa;padding:8px 16px;border-radius:6px;font-size:0.8rem;z-index:999;border:1px solid #333';
      document.body.appendChild(notif);
      setTimeout(function() { notif.remove(); }, 2500);
    }

    /* \u2500\u2500 Rate \u2500\u2500 */
    var rateBtn = document.getElementById('fa-rate-btn');
    var rateLabel = document.getElementById('fa-rate-label');
    var ratingPicker = document.getElementById('fa-rating-picker');
    var ratingClear = document.getElementById('fa-rating-clear');
    if (!rateBtn || !rateLabel || !ratingPicker || !ratingClear) return;

    function updateRateUI() {
      if (currentRating) {
        rateLabel.textContent = currentRating + '/10';
        rateBtn.classList.add('is-active');
      } else {
        rateLabel.textContent = 'Rate';
        rateBtn.classList.remove('is-active');
      }
      ratingPicker.querySelectorAll('.rating-pip').forEach(function(pip) {
        pip.classList.toggle('is-selected', Number(pip.dataset.value) === currentRating);
      });
      updateReviewVisibility();
    }

    function closeSeen() {
      var sp = document.getElementById('fa-seen-picker');
      var sb = document.getElementById('fa-seen-btn');
      if (sp) sp.setAttribute('hidden', '');
      if (sb) sb.setAttribute('aria-expanded', 'false');
    }

    rateBtn.addEventListener('click', function() {
      if (!requireAuth()) return;
      var open = !ratingPicker.hasAttribute('hidden');
      ratingPicker.toggleAttribute('hidden', open);
      rateBtn.setAttribute('aria-expanded', String(!open));
      if (!open) closeSeen();
    });

    ratingPicker.querySelectorAll('.rating-pip').forEach(function(pip) {
      pip.addEventListener('click', async function() {
        try {
          var value = Number(pip.dataset.value);
          var response = await fetch('/api/user/rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ work_id: workId, rating: value })
          });
          if (response.ok) {
            currentRating = value;
            updateRateUI();
            ratingPicker.setAttribute('hidden', '');
            if (inWatchlist) {
              inWatchlist = false;
              updateWatchlistUI();
              showToast('Removed from Watchlist');
            }
          }
        } catch(e) {
          console.error('Rate error:', e);
        }
      });
    });

    ratingClear.addEventListener('click', function() {
      currentRating = null;
      updateRateUI();
      ratingPicker.setAttribute('hidden', '');
    });

    updateRateUI();

    /* \u2500\u2500 Seen \u2500\u2500 */
    var seenBtn = document.getElementById('fa-seen-btn');
    var seenPicker = document.getElementById('fa-seen-picker');
    var seenToday = document.getElementById('fa-seen-today');
    var seenBefore = document.getElementById('fa-seen-before');
    if (!seenBtn || !seenPicker || !seenToday || !seenBefore) return;

    function updateSeenUI() {
      seenBtn.classList.toggle('is-active', isSeen);
    }

    async function markSeen(date) {
      try {
        var response = await fetch('/api/user/seen', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ work_id: workId, watched_at: date })
        });
        if (response.ok) {
          var data = await response.json();
          isSeen = data.seen !== false;
          updateSeenUI();
          if (isSeen && inWatchlist) {
            inWatchlist = false;
            updateWatchlistUI();
            showToast('Removed from Watchlist');
          }
        }
      } catch(e) {
        console.error('Seen error:', e);
      }
      closeSeen();
    }

    seenBtn.addEventListener('click', function() {
      if (!requireAuth()) return;
      if (isSeen) {
        markSeen(null);
        return;
      }
      var open = !seenPicker.hasAttribute('hidden');
      seenPicker.toggleAttribute('hidden', open);
      seenBtn.setAttribute('aria-expanded', String(!open));
      if (!open) ratingPicker.setAttribute('hidden', '');
    });

    seenToday.addEventListener('click', function() {
      markSeen(new Date().toISOString().slice(0, 10));
    });

    seenBefore.addEventListener('click', function() {
      markSeen(null);
    });

    updateSeenUI();

    /* \u2500\u2500 Watchlist \u2500\u2500 */
    var wlBtn = document.getElementById('fa-watchlist-btn');
    var wlIcon = document.getElementById('fa-watchlist-icon');
    var wlLabel = document.getElementById('fa-watchlist-label');
    if (!wlBtn || !wlIcon || !wlLabel) return;

    function updateWatchlistUI() {
      wlBtn.classList.toggle('is-active', inWatchlist);
      wlIcon.textContent = inWatchlist ? '\u2713' : '+';
      wlLabel.textContent = inWatchlist ? 'In Watchlist' : 'Watchlist';
    }

    wlBtn.addEventListener('click', async function() {
      if (!requireAuth()) return;
      try {
        var response = await fetch('/api/user/watchlist', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ work_id: workId })
        });
        if (response.ok) {
          var data = await response.json();
          inWatchlist = data.added;
          updateWatchlistUI();
        }
      } catch(e) {
        console.error('Watchlist error:', e);
      }
    });

    updateWatchlistUI();

    /* \u2500\u2500 Review \u2500\u2500 */
    var reviewWrapper = document.getElementById('fa-review-wrapper');
    var reviewBtn = document.getElementById('fa-review-btn');
    var reviewLabel = document.getElementById('fa-review-label');
    var reviewEditor = document.getElementById('fa-review-editor');
    var reviewTextarea = document.getElementById('fa-review-textarea');
    var reviewCharcount = document.getElementById('fa-review-charcount');
    var reviewSubmit = document.getElementById('fa-review-submit');

    function updateReviewVisibility() {
      if (!reviewWrapper) return;
      if (currentRating) {
        reviewWrapper.removeAttribute('hidden');
        if (reviewLabel) reviewLabel.textContent = currentReview ? 'Edit review' : 'Review';
      } else {
        reviewWrapper.setAttribute('hidden', '');
      }
    }

    if (reviewBtn && reviewEditor && reviewTextarea && reviewCharcount && reviewSubmit) {
      if (currentReview) reviewTextarea.value = currentReview;

      reviewTextarea.addEventListener('input', function() {
        reviewCharcount.textContent = reviewTextarea.value.length + '/500';
      });

      reviewBtn.addEventListener('click', function() {
        if (!requireAuth()) return;
        var open = !reviewEditor.hasAttribute('hidden');
        reviewEditor.toggleAttribute('hidden', open);
        if (!open) {
          reviewTextarea.focus();
          reviewCharcount.textContent = reviewTextarea.value.length + '/500';
        }
      });

      reviewSubmit.addEventListener('click', async function() {
        var text = reviewTextarea.value.trim();
        if (!text) return;
        if (text.length > 500) { showToast('Review too long (max 500)'); return; }
        reviewSubmit.disabled = true;
        try {
          var response = await fetch('/api/user/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ work_id: workId, review: text })
          });
          if (response.ok) {
            currentReview = text;
            reviewEditor.setAttribute('hidden', '');
            if (reviewLabel) reviewLabel.textContent = 'Edit review';
            showToast('Review saved');
          }
        } catch(e) {
          console.error('Review error:', e);
        }
        reviewSubmit.disabled = false;
      });
    }

    updateReviewVisibility();

    /* \u2500\u2500 Close on outside click \u2500\u2500 */
    document.addEventListener('click', function(e) {
      if (!root.contains(e.target)) {
        ratingPicker.setAttribute('hidden', '');
        rateBtn.setAttribute('aria-expanded', 'false');
        closeSeen();
        if (reviewEditor) reviewEditor.setAttribute('hidden', '');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFilmActions);
  } else {
    initFilmActions();
  }
})();
<\/script> `])), maybeRenderHead(), addAttribute(workId, "data-work-id"), addAttribute(effectiveUserId || "", "data-user-id"), addAttribute(initialRating ?? "", "data-initial-rating"), addAttribute(initialSeen ? "1" : "", "data-initial-seen"), addAttribute(initialWatchlist ? "1" : "", "data-initial-watchlist"), addAttribute(initialReview ?? "", "data-initial-review"), Array.from({ length: 10 }, (_, i) => i + 1).map((n) => renderTemplate`<button class="rating-pip"${addAttribute(n, "data-value")}${addAttribute(`${n} out of 10`, "aria-label")} data-astro-cid-mctugfxd>${n}</button>`));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmActions.astro", void 0);

const $$Astro$2 = createAstro("https://prisma.film");
const $$FilmReviews = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$2, $$props, $$slots);
  Astro2.self = $$FilmReviews;
  const { reviews } = Astro2.props;
  return renderTemplate`${reviews.length > 0 && renderTemplate`${maybeRenderHead()}<section class="film-reviews" data-astro-cid-qu2mrlpg><div class="site-container" data-astro-cid-qu2mrlpg><h2 class="film-reviews__title" data-astro-cid-qu2mrlpg>Reviews</h2><div class="film-reviews__list" data-astro-cid-qu2mrlpg>${reviews.map((r) => {
    const profile = r.user_profiles;
    const name = profile?.display_name || profile?.username || "Anonymous";
    const avatar = profile?.avatar_url;
    return renderTemplate`<div class="review-card" data-astro-cid-qu2mrlpg><a${addAttribute(`/u/${r.user_id}`, "href")} class="review-card__author" data-astro-cid-qu2mrlpg>${avatar ? renderTemplate`<img${addAttribute(avatar, "src")}${addAttribute(name, "alt")} class="review-card__avatar" data-astro-cid-qu2mrlpg>` : renderTemplate`<div class="review-card__avatar-placeholder" data-astro-cid-qu2mrlpg>${name[0].toUpperCase()}</div>`}<div class="review-card__meta" data-astro-cid-qu2mrlpg><span class="review-card__name" data-astro-cid-qu2mrlpg>${name}</span><span class="review-card__rating" data-astro-cid-qu2mrlpg>★ ${r.rating}/10</span></div></a><p class="review-card__text" data-astro-cid-qu2mrlpg>${r.review}</p></div>`;
  })}</div></div></section>`}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/FilmReviews.astro", void 0);

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Astro$1 = createAstro("https://prisma.film");
const $$StreamingPlayer = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$1, $$props, $$slots);
  Astro2.self = $$StreamingPlayer;
  const { workId, bunnyVideoId, title } = Astro2.props;
  const embedUrl = getBunnyEmbedUrlSigned(bunnyVideoId);
  return renderTemplate(_a || (_a = __template(["", '<div class="streaming-player" id="streaming-player"', ' data-astro-cid-idfvpghl> <div class="player-header" data-astro-cid-idfvpghl> <span class="player-badge" data-astro-cid-idfvpghl>PRISMA STREAMING</span> </div> <div class="player-wrapper" data-astro-cid-idfvpghl> <iframe id="bunny-iframe"', ' class="bunny-player" loading="lazy" allow="accelerometer;gyroscope;autoplay;encrypted-media;picture-in-picture;fullscreen" allowfullscreen data-astro-cid-idfvpghl></iframe> </div> <p class="player-credit" data-astro-cid-idfvpghl>Streamed exclusively on PRISMA \xB7 \xA9 ', "</p> </div> <script>\n// Refresh the signed token before it expires (every 3.5 hours)\n(function() {\n  var player = document.getElementById('streaming-player');\n  if (!player) return;\n\n  var workId = player.dataset.workId;\n  var refreshMs = 3.5 * 60 * 60 * 1000; // 3.5 hours\n\n  setInterval(async function() {\n    try {\n      var res = await fetch('/api/stream-token/' + workId);\n      var data = await res.json();\n      if (data.embedUrl) {\n        var iframe = document.getElementById('bunny-iframe');\n        if (iframe) iframe.src = data.embedUrl;\n      }\n    } catch (e) {\n      // Silent fail \u2014 current token still valid for ~30 min\n    }\n  }, refreshMs);\n})();\n<\/script> "])), maybeRenderHead(), addAttribute(workId, "data-work-id"), addAttribute(embedUrl, "src"), title);
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/film/StreamingPlayer.astro", void 0);

const SITE_URL = "https://prisma.film";
const TMDB_IMAGE = "https://image.tmdb.org/t/p";
function getPosterPath(work) {
  if ("tmdb_poster_path" in work && work.tmdb_poster_path) {
    return work.tmdb_poster_path;
  }
  if ("media" in work && work.media?.poster_path) {
    return work.media.poster_path;
  }
  return null;
}
function buildPosterUrl(posterPath, size = "w780") {
  if (!posterPath) return null;
  return `${TMDB_IMAGE}/${size}${posterPath}`;
}
function getDirectorNames(work) {
  if ("work_people" in work && Array.isArray(work.work_people)) {
    return work.work_people.filter((p) => p.role === "director").map((p) => p.person?.name ?? "").filter(Boolean);
  }
  if ("people" in work && work.people?.director) {
    return work.people.director.map(
      (id) => id.replace(/^person_/, "").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
    );
  }
  return [];
}
function getSynopsis(work) {
  if ("synopsis" in work && work.synopsis) return work.synopsis;
  return null;
}
function getColorNarrative(work) {
  if ("color_narrative" in work && typeof work.color_narrative === "string") {
    return work.color_narrative;
  }
  return null;
}
function buildDescription(work) {
  const year = work.year ? ` (${work.year})` : "";
  const dirs = getDirectorNames(work);
  const dirStr = dirs.length ? ` Directed by ${dirs.join(", ")}.` : "";
  const synopsis = getSynopsis(work) ?? getColorNarrative(work);
  if (synopsis) {
    const trimmed = synopsis.length > 155 ? synopsis.slice(0, 152) + "…" : synopsis;
    return trimmed;
  }
  return `${work.title}${year} on PRISMA — cinematic color identity.${dirStr}`;
}
function buildJsonLd(work, posterUrl) {
  const directors = getDirectorNames(work);
  const filmSlug = work.id.replace(/^work_/, "");
  const filmUrl = `${SITE_URL}/films/${filmSlug}`;
  const schema = {
    "@context": "https://schema.org",
    "@type": "Movie",
    name: work.title,
    url: filmUrl
  };
  if (work.year) {
    schema.datePublished = String(work.year);
  }
  const synopsis = getSynopsis(work);
  if (synopsis) {
    schema.description = synopsis;
  }
  if (posterUrl) {
    schema.image = posterUrl;
  }
  if (directors.length) {
    schema.director = directors.map((name) => ({
      "@type": "Person",
      name
    }));
  }
  if ("duration_min" in work && work.duration_min) {
    const h = Math.floor(work.duration_min / 60);
    const m = work.duration_min % 60;
    schema.duration = h > 0 ? `PT${h}H${m}M` : `PT${m}M`;
  }
  if ("genres" in work && Array.isArray(work.genres) && work.genres.length) {
    schema.genre = work.genres;
  }
  if ("countries" in work && Array.isArray(work.countries) && work.countries.length) {
    schema.countryOfOrigin = work.countries.map((c) => ({
      "@type": "Country",
      name: c
    }));
  }
  const dps = [];
  if ("work_people" in work && Array.isArray(work.work_people)) {
    work.work_people.filter((p) => p.role === "cinematography").forEach((p) => {
      if (p.person?.name) dps.push(p.person.name);
    });
  } else if ("people" in work && work.people?.cinematography) {
    work.people.cinematography.forEach((id) => {
      dps.push(id.replace(/^person_/, "").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()));
    });
  }
  if (dps.length) {
    schema.cinematographer = dps.map((name) => ({ "@type": "Person", name }));
  }
  const actors = [];
  if ("work_people" in work && Array.isArray(work.work_people)) {
    work.work_people.filter((p) => p.role === "actor").slice(0, 5).forEach((p) => {
      if (p.person?.name) actors.push(p.person.name);
    });
  } else if ("people" in work && work.people?.cast) {
    work.people.cast.slice(0, 5).forEach((id) => {
      actors.push(id.replace(/^person_/, "").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()));
    });
  }
  if (actors.length) {
    schema.actor = actors.map((name) => ({ "@type": "Person", name }));
  }
  const imdbRating = "imdb_rating" in work ? work.imdb_rating : null;
  if (imdbRating) {
    schema.aggregateRating = {
      "@type": "AggregateRating",
      ratingValue: imdbRating,
      bestRating: 10,
      ratingCount: 1e3
      // conservative placeholder — real votes not in schema
    };
  }
  return JSON.stringify(schema);
}
function buildFilmSeo(work) {
  const posterPath = getPosterPath(work);
  const posterUrl = buildPosterUrl(posterPath, "w1280");
  const yearSuffix = work.year ? ` (${work.year})` : "";
  const pageTitle = `${work.title}${yearSuffix} — PRISMA`;
  const description = buildDescription(work);
  const ogImage = posterUrl ?? `${SITE_URL}/og-default.jpg`;
  return {
    title: pageTitle,
    description,
    ogImage,
    jsonLd: buildJsonLd(work, posterUrl)
  };
}

const $$Astro = createAstro("https://prisma.film");
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$slug;
  const { slug } = Astro2.params;
  if (!slug) {
    return Astro2.redirect("/404");
  }
  const work = await loadWorkBySlugAsync(slug);
  if (!work) {
    return Astro2.redirect("/404");
  }
  let rankScore = null;
  if (isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const workId = `work_${slug}`;
      const { data } = await db.from("ranking_scores").select("rank, score").eq("entity_id", workId).eq("entity_type", "work").eq("context", "global").maybeSingle();
      if (data) {
        rankScore = { rank: data.rank, score: data.score };
      }
    } catch {
    }
  }
  const colorTier = "color_assignments" in work && work.color_assignments?.tier ? work.color_assignments.tier : null;
  const HIGHLIGHT_AWARD_IDS = /* @__PURE__ */ new Set([
    "award_oscar-best-picture",
    "award_oscar-best-director",
    "award_oscar-best-actress",
    "award_oscar-best-actor",
    "award_oscar-best-intl-film",
    "award_oscar-best-cinematography",
    "award_oscar-best-original-screenplay",
    "award_oscar-best-adapted-screenplay",
    "award_oscar-best-original-score",
    "award_oscar-best-production-design",
    "award_cannes-palme-dor",
    "award_cannes-grand-prix",
    "award_cannes-best-director",
    "award_cannes-best-actress",
    "award_cannes-best-actor",
    "award_berlin-golden-bear",
    "award_berlin-silver-bear-director",
    "award_venice-golden-lion",
    "award_venice-silver-lion-director",
    "award_bafta-best-film",
    "award_bafta-best-director",
    "award_cesar-best-film",
    "award_cesar-best-director",
    "award_gg-best-film-drama",
    "award_gg-best-director"
  ]);
  function awardShortName(id) {
    if (id.includes("oscar")) return "Oscar";
    if (id.includes("cannes")) return "Palme d'Or";
    if (id.includes("berlin")) return "Berlin";
    if (id.includes("venice")) return "Venice";
    if (id.includes("bafta")) return "BAFTA";
    if (id.includes("cesar")) return "C\xE9sar";
    if (id.includes("gg-")) return "Golden Globe";
    return id.split("-")[1]?.toUpperCase() ?? id;
  }
  const castAwardHighlights = {};
  if (isSupabaseConfigured() && "work_people" in work) {
    try {
      const db = createServiceClient();
      const workFull = work;
      const actorIds = workFull.work_people.filter((wp) => wp.role === "actor").map((wp) => wp.people.id);
      if (actorIds.length > 0) {
        const wpRes = await db.from("work_people").select("work_id, person_id").in("person_id", actorIds).eq("role", "actor");
        if (wpRes.data && wpRes.data.length > 0) {
          const allWorkIds = [...new Set(wpRes.data.map((r) => r.work_id))];
          const waRes = await db.from("work_awards").select("work_id, award_id").eq("result", "win").in("work_id", allWorkIds).in("award_id", [...HIGHLIGHT_AWARD_IDS]);
          if (waRes.data && waRes.data.length > 0) {
            const workWins = {};
            for (const row of waRes.data) {
              const wid = row.work_id;
              const shortName = awardShortName(row.award_id);
              if (!workWins[wid]) workWins[wid] = [];
              if (!workWins[wid].includes(shortName)) workWins[wid].push(shortName);
            }
            for (const wpRow of wpRes.data) {
              const personId = wpRow.person_id;
              const wins = workWins[wpRow.work_id];
              if (!wins) continue;
              if (!castAwardHighlights[personId]) castAwardHighlights[personId] = [];
              for (const award of wins) {
                if (!castAwardHighlights[personId].includes(award) && castAwardHighlights[personId].length < 2) {
                  castAwardHighlights[personId].push(award);
                }
              }
            }
          }
        }
      }
    } catch {
    }
  }
  const seo = buildFilmSeo(work);
  const user = Astro2.locals.user;
  console.log("[Film Page] User auth state:", {
    hasUser: !!user,
    userId: user?.id,
    userEmail: user?.email
  });
  let initialRating = null;
  let initialSeen = false;
  let initialWatchlist = false;
  let initialReview = null;
  if (user && isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const workId = `work_${slug}`;
      const [ratingRes, seenRes, wlRes] = await Promise.all([
        db.from("user_ratings").select("rating, review").eq("user_id", user.id).eq("work_id", workId).maybeSingle(),
        db.from("user_watches").select("work_id").eq("user_id", user.id).eq("work_id", workId).limit(1),
        db.from("user_watchlist").select("work_id").eq("user_id", user.id).eq("work_id", workId).maybeSingle()
      ]);
      initialRating = ratingRes.data?.rating ?? null;
      initialReview = ratingRes.data?.review ?? null;
      initialSeen = (seenRes.data?.length ?? 0) > 0;
      initialWatchlist = !!wlRes.data;
    } catch {
    }
  }
  let filmReviews = [];
  if (isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const { data } = await db.from("user_ratings").select("rating, review, user_id, user_profiles(display_name, avatar_url, username)").eq("work_id", `work_${slug}`).eq("is_public", true).not("review", "is", null).order("updated_at", { ascending: false }).limit(5);
      filmReviews = data || [];
    } catch {
    }
  }
  return renderTemplate`${renderComponent($$result, "FilmLayout", $$FilmLayout, { "title": seo.title, "description": seo.description, "ogImage": seo.ogImage, "jsonLd": seo.jsonLd, "data-astro-cid-ujmyk5wk": true }, { "default": async ($$result2) => renderTemplate` ${renderComponent($$result2, "FilmHero", $$FilmHero, { "work": work, "data-astro-cid-ujmyk5wk": true })}  ${maybeRenderHead()}<div class="film-actions-bar" data-astro-cid-ujmyk5wk> <div class="site-container" data-astro-cid-ujmyk5wk> ${renderComponent($$result2, "FilmActions", $$FilmActions, { "workId": `work_${slug}`, "userId": user?.id ?? null, "initialRating": initialRating, "initialSeen": initialSeen, "initialWatchlist": initialWatchlist, "initialReview": initialReview, "data-astro-cid-ujmyk5wk": true })} </div> </div> ${"is_streamable" in work && work.is_streamable && work.bunny_video_id && renderTemplate`<div class="film-streaming" data-astro-cid-ujmyk5wk> <div class="site-container" data-astro-cid-ujmyk5wk> ${renderComponent($$result2, "StreamingPlayer", $$StreamingPlayer, { "workId": `work_${slug}`, "bunnyVideoId": work.bunny_video_id, "title": work.title, "data-astro-cid-ujmyk5wk": true })} </div> </div>`}<div class="film-body" data-astro-cid-ujmyk5wk> <!-- Rank badge (shown if we have ranking data) --> ${rankScore && renderTemplate`<div class="film-body__rank" data-astro-cid-ujmyk5wk> <div class="site-container" data-astro-cid-ujmyk5wk> ${renderComponent($$result2, "FilmRankBadge", $$FilmRankBadge, { "rank": rankScore.rank, "score": rankScore.score, "tier": colorTier, "data-astro-cid-ujmyk5wk": true })} </div> </div>`} ${renderComponent($$result2, "FilmColorBlock", $$FilmColorBlock, { "work": work, "data-astro-cid-ujmyk5wk": true })} ${renderComponent($$result2, "FilmDimensionTags", $$FilmDimensionTags, { "work": work, "data-astro-cid-ujmyk5wk": true })} ${renderComponent($$result2, "FilmSynopsis", $$FilmSynopsis, { "work": work, "data-astro-cid-ujmyk5wk": true })} ${renderComponent($$result2, "FilmPeople", $$FilmPeople, { "work": work, "castAwardHighlights": castAwardHighlights, "data-astro-cid-ujmyk5wk": true })} ${renderComponent($$result2, "FilmReviews", $$FilmReviews, { "reviews": filmReviews, "data-astro-cid-ujmyk5wk": true })} ${renderComponent($$result2, "FilmAwards", $$FilmAwards, { "work": work, "data-astro-cid-ujmyk5wk": true })} ${renderComponent($$result2, "FilmMetaAccordion", $$FilmMetaAccordion, { "work": work, "data-astro-cid-ujmyk5wk": true })} </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/films/[slug].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/films/[slug].astro";
const $$url = "/films/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
