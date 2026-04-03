/* empty css                                     */
import { e as createAstro, f as createComponent, r as renderTemplate, k as renderComponent, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_BW8MRUf7.mjs';
import { f as formatRole, g as getPaletteEntry } from '../../chunks/colorPalette_MBD9-pHi.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
/* empty css                                     */
export { renderers } from '../../renderers.mjs';

const PEOPLE_DIR = path.resolve("pipeline/normalized/people");
const WORKS_DIR = path.resolve("pipeline/normalized/works");
function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8"));
  } catch {
    return null;
  }
}
function loadPersonFromFilesystem(slug) {
  const personId = `person_${slug}`;
  const personPath = path.join(PEOPLE_DIR, `${personId}.json`);
  const raw = readJson(personPath);
  if (!raw) return null;
  const filmography = [];
  const personName = raw.name ?? slug;
  if (fs.existsSync(WORKS_DIR)) {
    const workFiles = fs.readdirSync(WORKS_DIR).filter((f) => f.endsWith(".json"));
    for (const file of workFiles) {
      const work = readJson(path.join(WORKS_DIR, file));
      if (!work) continue;
      const people = work.people ?? {};
      const roleMap = {
        director: "director",
        cinematography: "cinematography",
        writer: "writer",
        editor: "editor",
        composer: "composer",
        cast: "actor"
      };
      for (const [sourceRole, dbRole] of Object.entries(roleMap)) {
        const ids = people[sourceRole] ?? [];
        const matchesId = ids.includes(personId);
        const matchesName = ids.some((id) => {
          const idName = id.replace(/^person_/, "").split("-").join(" ").toLowerCase();
          return idName === personName.toLowerCase();
        });
        if (matchesId || matchesName) {
          const palette = work.prisma_palette;
          filmography.push({
            work: {
              id: work.id,
              title: work.title,
              year: work.year ?? null,
              tmdb_poster_path: work.media?.poster_path ?? null
            },
            role: dbRole,
            color: palette?.primary ? { color_iconico: palette.primary, tier: null } : null
          });
          break;
        }
      }
    }
  }
  filmography.sort((a, b) => (b.work.year ?? 0) - (a.work.year ?? 0));
  return {
    _source: "filesystem",
    id: personId,
    name: personName,
    birth_year: raw.birth_year ?? null,
    death_year: raw.death_year ?? null,
    bio: raw.bio ?? null,
    nationality: raw.nationality ?? [],
    profile_path: raw.profile_path ?? null,
    filmography,
    color_profile: null
  };
}
async function loadPersonBySlugAsync(slug) {
  if (isSupabaseConfigured()) {
    try {
      const { getPersonBySlug } = await import('../../chunks/people_Dx34GeC0.mjs');
      const result = await getPersonBySlug(slug);
      if (result) return result;
    } catch {
    }
  }
  return loadPersonFromFilesystem(slug);
}

const SITE_URL = "https://prisma.film";
const TMDB_IMAGE = "https://image.tmdb.org/t/p";
const ROLE_LABELS = {
  director: "director/a",
  cinematography: "director/a de fotografía",
  actor: "actor/actriz",
  writer: "guionista",
  editor: "editor/a",
  composer: "compositor/a",
  production_design: "director/a de arte"
};
function buildProfileUrl(profilePath) {
  if (!profilePath) return null;
  return `${TMDB_IMAGE}/w500${profilePath}`;
}
function buildDescription(input, primaryRole) {
  if (input.bio) {
    return input.bio.length > 155 ? input.bio.slice(0, 152) + "…" : input.bio;
  }
  const roleLabel = primaryRole ? ROLE_LABELS[primaryRole] ?? "cineasta" : "cineasta";
  const filmCount = input.filmography.length;
  const nat = input.nationality?.length ? ` (${input.nationality.join(", ")})` : "";
  return `${input.name}${nat}, ${roleLabel} con ${filmCount} película${filmCount !== 1 ? "s" : ""} en el catálogo PRISMA.`;
}
function buildJsonLd(input, description, profileUrl) {
  const personSlug = input.id.replace(/^person_/, "");
  const personUrl = `${SITE_URL}/people/${personSlug}`;
  const schema = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: input.name,
    url: personUrl,
    description
  };
  if (profileUrl) {
    schema.image = profileUrl;
  }
  if (input.nationality?.length) {
    schema.nationality = input.nationality.map((n) => ({
      "@type": "Country",
      name: n
    }));
  }
  if (input.birth_year) {
    schema.birthDate = String(input.birth_year);
  }
  if (input.death_year) {
    schema.deathDate = String(input.death_year);
  }
  const sameAs = [];
  if (input.imdb_id) {
    sameAs.push(`https://www.imdb.com/name/${input.imdb_id}/`);
  }
  if (input.wikidata_id) {
    sameAs.push(`https://www.wikidata.org/wiki/${input.wikidata_id}`);
  }
  if (sameAs.length) {
    schema.sameAs = sameAs;
  }
  const topWorks = input.filmography.filter((e) => e.role === "director").slice(0, 5);
  if (topWorks.length === 0) {
    topWorks.push(...input.filmography.slice(0, 5));
  }
  if (topWorks.length) {
    schema.knowsAbout = topWorks.map((e) => ({
      "@type": "Movie",
      name: e.work.title,
      dateCreated: e.work.year ? String(e.work.year) : void 0
    }));
  }
  return schema;
}
function buildPersonSeo(input, primaryRole) {
  const profileUrl = buildProfileUrl(input.profile_path);
  const description = buildDescription(input, primaryRole);
  const ogImage = profileUrl ?? `${SITE_URL}/og-default.jpg`;
  return {
    title: `${input.name} — PRISMA`,
    description,
    ogImage,
    ogType: "profile",
    jsonLd: buildJsonLd(input, description, profileUrl)
  };
}

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Astro = createAstro("https://prisma.film");
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$slug;
  const { slug } = Astro2.params;
  if (!slug) return Astro2.redirect("/404");
  const person = await loadPersonBySlugAsync(slug);
  if (!person) {
    return Astro2.redirect("/404");
  }
  const roleCounts = {};
  for (const entry of person.filmography) {
    roleCounts[entry.role] = (roleCounts[entry.role] ?? 0) + 1;
  }
  const primaryRole = Object.entries(roleCounts).sort((a, b) => b[1] - a[1])[0]?.[0];
  const colorCounts = {};
  for (const entry of person.filmography) {
    const c = entry.color?.color_iconico;
    if (c) colorCounts[c] = (colorCounts[c] ?? 0) + 1;
  }
  const topColors = Object.entries(colorCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const filmography = [...person.filmography].sort(
    (a, b) => (b.work.year ?? 0) - (a.work.year ?? 0)
  );
  `${person.name} — PRISMA`;
  const nationalities = (person.nationality ?? []).join(", ");
  const personSeo = buildPersonSeo(
    {
      name: person.name,
      id: "id" in person ? person.id : `person_${slug}`,
      bio: person.bio ?? null,
      nationality: person.nationality,
      birth_year: person.birth_year ?? null,
      death_year: person.death_year ?? null,
      profile_path: person.profile_path ?? null,
      imdb_id: "imdb_id" in person ? person.imdb_id : null,
      wikidata_id: "wikidata_id" in person ? person.wikidata_id : null,
      filmography: person.filmography
    },
    primaryRole
  );
  const SITE = "https://prisma.film";
  const personBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Cineastas", url: `${SITE}/people` },
    { name: person.name, url: `${SITE}/people/${slug}` }
  ];
  let personRanking = null;
  if (isSupabaseConfigured()) {
    try {
      const db = createServiceClient();
      const { data } = await db.from("ranking_scores").select("rank, score, context").eq("entity_type", "person").eq("entity_id", `person_${slug}`).order("score", { ascending: false }).limit(1).maybeSingle();
      if (data) {
        personRanking = {
          rank: data.rank,
          score: data.score,
          context: data.context
        };
      }
    } catch {
    }
  }
  const TIER_ORDER_A = { A: 0, B: 1, C: 2, D: 3 };
  function sortAwardRows(a, b) {
    if (a.awards.is_grand_prize !== b.awards.is_grand_prize) return a.awards.is_grand_prize ? -1 : 1;
    const ta = TIER_ORDER_A[a.awards.festivals?.tier ?? a.awards.tier ?? "C"] ?? 3;
    const tb = TIER_ORDER_A[b.awards.festivals?.tier ?? b.awards.tier ?? "C"] ?? 3;
    if (ta !== tb) return ta - tb;
    return (b.year ?? 0) - (a.year ?? 0);
  }
  let personWins = [];
  let personNoms = [];
  if (isSupabaseConfigured() && filmography.length > 0) {
    try {
      const db2 = createServiceClient();
      const uniqueWorkIds = [...new Set(filmography.map((e) => e.work.id))];
      const { data: awardsData } = await db2.from("work_awards").select("result, year, work_id, awards!inner(id, name, is_grand_prize, tier, festival_id, festivals(id, name, country, tier, logo_path))").in("work_id", uniqueWorkIds).order("year", { ascending: false });
      if (awardsData) {
        const all = awardsData;
        personWins = all.filter((r) => r.result === "win").sort(sortAwardRows);
        personNoms = all.filter((r) => r.result === "nomination").sort(sortAwardRows);
      }
    } catch {
    }
  }
  const workTitleMap = new Map(filmography.map((e) => [e.work.id, e.work.title]));
  function festName(wa) {
    return wa.awards.festivals?.name ?? "—";
  }
  function festHref(wa) {
    return wa.awards.festival_id ? `/festivals/${wa.awards.festival_id.replace(/^festival_/, "")}` : void 0;
  }
  const AWARD_TIER_COLOR = {
    A: "#C98A2E",
    B: "rgba(255,255,255,0.3)",
    C: "rgba(255,255,255,0.15)"
  };
  function awardTierColor(wa) {
    const t = wa.awards.festivals?.tier ?? wa.awards.tier ?? "";
    return AWARD_TIER_COLOR[t] ?? AWARD_TIER_COLOR["C"];
  }
  const TMDB_BASE = "https://image.tmdb.org/t/p/w185";
  const TMDB_POSTER = "https://image.tmdb.org/t/p/w92";
  const TMDB_W780 = "https://image.tmdb.org/t/p/w780";
  let profileUrl = null;
  if (person.profile_path) {
    profileUrl = `${TMDB_BASE}${person.profile_path}`;
  }
  const personTmdbId = "tmdb_id" in person ? person.tmdb_id : null;
  const TMDB_API_KEY = "2ffbaff6288d7216beeca2bbea207176";
  let personPhotos = [];
  if (personTmdbId && TMDB_API_KEY) {
    try {
      const res = await fetch(
        `https://api.themoviedb.org/3/person/${personTmdbId}/images?api_key=${TMDB_API_KEY}`
      );
      if (res.ok) {
        const json = await res.json();
        personPhotos = (json.profiles ?? []).sort((a, b) => b.vote_average - a.vote_average).slice(0, 8).map((p) => ({
          src: `${TMDB_W780}${p.file_path}`,
          thumb: `${TMDB_BASE}${p.file_path}`
        }));
      }
    } catch {
    }
  }
  const fullBio = person.bio ?? null;
  let shortBio = null;
  if (fullBio) {
    const sentences = fullBio.split(/(?<=\. )/).filter(Boolean);
    shortBio = sentences.slice(0, 2).join(" ").trim();
    if (shortBio === fullBio.trim()) shortBio = null;
  }
  const topRole = primaryRole ? formatRole(primaryRole) : null;
  const activeYears = filmography.length > 0 ? (() => {
    const years = filmography.map((e) => e.work.year).filter(Boolean);
    if (!years.length) return null;
    const min = Math.min(...years);
    const max = Math.max(...years);
    return min === max ? String(min) : `${min}–${max}`;
  })() : null;
  const editorialSubtitle = [
    topRole,
    nationalities || null,
    activeYears
  ].filter(Boolean).join(" · ");
  const awardGroups = (() => {
    const allAwardRows = [...personWins, ...personNoms];
    const grouped = /* @__PURE__ */ new Map();
    for (const wa of allAwardRows) {
      if (!grouped.has(wa.work_id)) {
        const filmEntry = filmography.find((e) => e.work.id === wa.work_id);
        grouped.set(wa.work_id, {
          work_id: wa.work_id,
          filmTitle: workTitleMap.get(wa.work_id) ?? wa.work_id,
          filmSlug: wa.work_id.replace(/^work_/, ""),
          posterPath: filmEntry?.work?.tmdb_poster_path ?? null,
          wins: [],
          noms: []
        });
      }
      const g = grouped.get(wa.work_id);
      if (wa.result === "win") g.wins.push(wa);
      else g.noms.push(wa);
    }
    return Array.from(grouped.values()).sort(
      (a, b) => b.wins.length - a.wins.length || b.noms.length - a.noms.length
    );
  })();
  return renderTemplate(_a || (_a = __template(["", "  <script>\n(function () {\n  // Bio toggle\n  var toggle = document.getElementById('bio-toggle');\n  var bioShort = document.getElementById('bio-short');\n  var bioFull = document.getElementById('bio-full');\n  if (toggle && bioFull) {\n    toggle.addEventListener('click', function () {\n      var expanded = !bioFull.hidden;\n      bioFull.hidden = expanded;\n      if (bioShort) bioShort.style.display = expanded ? '' : 'none';\n      toggle.textContent = expanded ? 'Leer más' : 'Leer menos';\n    });\n  }\n\n  // Award group collapsible\n  document.querySelectorAll('.award-group__header').forEach(function (btn) {\n    btn.addEventListener('click', function () {\n      var group = btn.closest('.award-group');\n      if (!group) return;\n      var list = group.querySelector('.award-group__list');\n      if (!list) return;\n      var open = btn.getAttribute('aria-expanded') === 'true';\n      btn.setAttribute('aria-expanded', open ? 'false' : 'true');\n      list.hidden = open;\n    });\n  });\n})();\n</script>"])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": personSeo.title, "description": personSeo.description, "ogImage": personSeo.ogImage, "ogType": personSeo.ogType, "jsonLd": personSeo.jsonLd, "breadcrumbs": personBreadcrumbs, "data-astro-cid-o2ocmoue": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="person-page page-enter" data-astro-cid-o2ocmoue> <!-- ── Header ── --> <section class="person-header" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <div class="person-header__inner" data-astro-cid-o2ocmoue> <div class="person-header__avatar" aria-hidden="true" data-astro-cid-o2ocmoue> ${profileUrl ? renderTemplate`<img${addAttribute(profileUrl, "src")}${addAttribute(person.name, "alt")} class="person-header__photo" data-astro-cid-o2ocmoue>` : person.name.split(" ").slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("")} </div> <div class="person-header__info" data-astro-cid-o2ocmoue> ${primaryRole && renderTemplate`<div class="person-header__role-label" data-astro-cid-o2ocmoue> <span class="role-badge" data-astro-cid-o2ocmoue>${formatRole(primaryRole)}</span> </div>`} ${personRanking && renderTemplate`<div class="person-ranking-badge" data-astro-cid-o2ocmoue> <span class="person-ranking-badge__rank" data-astro-cid-o2ocmoue>#${personRanking.rank}</span> <a${addAttribute(`/people?role=${personRanking.context}`, "href")} class="person-ranking-badge__role" data-astro-cid-o2ocmoue> ${formatRole(personRanking.context)} </a> <span class="person-ranking-badge__sep" data-astro-cid-o2ocmoue>·</span> <span class="person-ranking-badge__score" data-astro-cid-o2ocmoue>${personRanking.score.toFixed(1)} pts</span> </div>`} <h1 class="person-header__name" data-astro-cid-o2ocmoue>${person.name}</h1> <div class="person-header__meta" data-astro-cid-o2ocmoue> ${person.birth_year && renderTemplate`<span class="person-header__meta-item" data-astro-cid-o2ocmoue>
b. ${person.birth_year}${person.death_year ? ` — d. ${person.death_year}` : ""} </span>`} ${nationalities && renderTemplate`<span class="person-header__meta-item" data-astro-cid-o2ocmoue>${nationalities}</span>`} ${filmography.length > 0 && renderTemplate`<span class="person-header__meta-item" data-astro-cid-o2ocmoue>${filmography.length} obras</span>`} </div> </div> </div> </div> </section> <!-- ── Person photo strip ── --> ${personPhotos.length > 0 && renderTemplate`<section class="person-photos" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <div class="person-photos__strip" data-astro-cid-o2ocmoue> ${personPhotos.map((photo) => renderTemplate`<a class="person-photos__thumb"${addAttribute(photo.src, "href")} target="_blank" rel="noopener noreferrer"${addAttribute(`Ver foto de ${person.name}`, "aria-label")} data-astro-cid-o2ocmoue> <img${addAttribute(photo.thumb, "src")}${addAttribute(person.name, "alt")} loading="lazy" decoding="async" data-astro-cid-o2ocmoue> </a>`)} </div> </div> </section>`} <!-- ── Biography ── --> ${fullBio && renderTemplate`<section class="person-bio" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> ${editorialSubtitle && renderTemplate`<p class="person-bio__subtitle" data-astro-cid-o2ocmoue>${editorialSubtitle}</p>`} <p class="person-bio__para" id="bio-short" data-astro-cid-o2ocmoue>${shortBio ?? fullBio}</p> ${shortBio && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-o2ocmoue": true }, { "default": async ($$result3) => renderTemplate` <div class="person-bio__full" id="bio-full" hidden data-astro-cid-o2ocmoue> ${fullBio.split("\n\n").map((para) => renderTemplate`<p class="person-bio__para" data-astro-cid-o2ocmoue>${para}</p>`)} </div> <button class="person-bio__toggle" id="bio-toggle" type="button" data-astro-cid-o2ocmoue>Leer más</button> ` })}`} </div> </section>`} <!-- ── Awards grouped by film ── --> ${awardGroups.length > 0 && renderTemplate`<section class="person-awards" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <h2 class="person-awards__heading" data-astro-cid-o2ocmoue>Premios y Reconocimientos</h2> <div class="award-groups" data-astro-cid-o2ocmoue> ${awardGroups.map((group, gi) => renderTemplate`<div class="award-group" data-astro-cid-o2ocmoue> <button class="award-group__header" type="button" aria-expanded="false"${addAttribute(gi, "data-group")} data-astro-cid-o2ocmoue> ${group.posterPath && renderTemplate`<img${addAttribute(`${TMDB_POSTER}${group.posterPath}`, "src")} alt="" class="award-group__poster" loading="lazy" data-astro-cid-o2ocmoue>`} <div class="award-group__film-info" data-astro-cid-o2ocmoue> <span class="award-group__film-title" data-astro-cid-o2ocmoue>${group.filmTitle}</span> <span class="award-group__counts" data-astro-cid-o2ocmoue> ${group.wins.length > 0 && `${group.wins.length} premio${group.wins.length > 1 ? "s" : ""}`} ${group.wins.length > 0 && group.noms.length > 0 && " · "} ${group.noms.length > 0 && `${group.noms.length} nominación${group.noms.length > 1 ? "es" : ""}`} </span> </div> <span class="award-group__chevron" aria-hidden="true" data-astro-cid-o2ocmoue>›</span> </button> <ul class="award-group__list" hidden data-astro-cid-o2ocmoue> ${[...group.wins, ...group.noms].map((wa) => {
    const isWin = wa.result === "win";
    const color = awardTierColor(wa);
    const href = festHref(wa);
    return renderTemplate`<li class="award-group__item"${addAttribute(`--tc: ${color}`, "style")} data-astro-cid-o2ocmoue> <span${addAttribute(`award-group__badge award-group__badge--${isWin ? "win" : "nom"}`, "class")} data-astro-cid-o2ocmoue> ${isWin ? "WIN" : "NOM"} </span> <div class="award-group__item-body" data-astro-cid-o2ocmoue> <span class="award-group__item-name" data-astro-cid-o2ocmoue>${wa.awards.name}</span> <span class="award-group__item-meta" data-astro-cid-o2ocmoue> ${href ? renderTemplate`<a${addAttribute(href, "href")} class="award-group__item-fest" data-astro-cid-o2ocmoue>${festName(wa)}</a>` : renderTemplate`<span data-astro-cid-o2ocmoue>${festName(wa)}</span>`} ${wa.year && ` · ${wa.year}`} </span> </div> </li>`;
  })} </ul> </div>`)} </div> </div> </section>`} <!-- ── Color signature ── --> ${topColors.length > 0 && renderTemplate`<section class="person-colors" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <div class="person-colors__inner" data-astro-cid-o2ocmoue> <div class="person-colors__header" data-astro-cid-o2ocmoue> <h2 class="person-colors__heading" data-astro-cid-o2ocmoue>Identidad Visual</h2> <p class="person-colors__sub" data-astro-cid-o2ocmoue>Colores recurrentes a lo largo de su filmografía</p> </div> <div class="person-colors__signature" data-astro-cid-o2ocmoue> ${topColors.map(([colorId, count]) => {
    const p = getPaletteEntry(colorId);
    if (!p) return null;
    const pct = Math.round(count / filmography.length * 100);
    return renderTemplate`<a${addAttribute(`/colors/${colorId}`, "href")} class="person-color-item" data-astro-cid-o2ocmoue> <div class="person-color-item__bar"${addAttribute(`background: ${p.hex}; height: ${Math.max(pct * 1.5, 12)}px;`, "style")}${addAttribute(`${count} películas`, "title")} data-astro-cid-o2ocmoue></div> <span class="person-color-item__name" data-astro-cid-o2ocmoue>${p.name}</span> <span class="person-color-item__count" data-astro-cid-o2ocmoue>${count}</span> </a>`;
  })} </div> </div> </div> </section>`} <!-- ── Filmography ── --> ${filmography.length > 0 && renderTemplate`<section class="person-filmography" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <h2 class="person-filmography__heading" data-astro-cid-o2ocmoue>Filmografía</h2> <div class="person-filmography__list" data-astro-cid-o2ocmoue> ${filmography.map((entry) => {
    const filmSlug = entry.work.id.replace(/^work_/, "");
    const colorPalette = entry.color ? getPaletteEntry(entry.color.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="filmography-item" data-astro-cid-o2ocmoue> <div class="filmography-item__color-strip"${addAttribute(colorPalette ? `background: ${colorPalette.hex}` : "background: var(--surface-border)", "style")} data-astro-cid-o2ocmoue></div> <div class="filmography-item__year" data-astro-cid-o2ocmoue> ${entry.work.year ?? "—"} </div> <div class="filmography-item__info" data-astro-cid-o2ocmoue> <span class="filmography-item__title" data-astro-cid-o2ocmoue>${entry.work.title}</span> <span class="role-badge" data-astro-cid-o2ocmoue>${formatRole(entry.role)}</span> </div> ${colorPalette && renderTemplate`<div class="filmography-item__color-name" data-astro-cid-o2ocmoue> ${colorPalette.name} </div>`} </a>`;
  })} </div> </div> </section>`} <!-- Empty state --> ${filmography.length === 0 && !person.bio && renderTemplate`<section class="person-empty" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <p class="person-empty__message" data-astro-cid-o2ocmoue>
Filmography data for this person is being processed.
</p> </div> </section>`} </div> ` }));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/people/[slug].astro", void 0);
const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/people/[slug].astro";
const $$url = "/people/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
