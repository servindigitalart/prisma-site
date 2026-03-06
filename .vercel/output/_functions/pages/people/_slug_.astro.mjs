/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_QHw3iGXw.mjs';
import { f as formatRole, g as getPaletteEntry } from '../../chunks/colorPalette_CcE_HP33.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { g as getFestivalLogoUrl, a as getFestivalMonogram } from '../../chunks/festivalUtils_CMVWB9Ye.mjs';
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
  const pageTitle = `${person.name} \u2014 PRISMA`;
  const nationalities = (person.nationality ?? []).join(", ");
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
    return wa.awards.festivals?.name ?? "\u2014";
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
  let profileUrl = null;
  if (person.profile_path) {
    profileUrl = `${TMDB_BASE}${person.profile_path}`;
  }
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "data-astro-cid-o2ocmoue": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="person-page page-enter" data-astro-cid-o2ocmoue> <!-- ── Header ── --> <section class="person-header" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <div class="person-header__inner" data-astro-cid-o2ocmoue> <div class="person-header__avatar" aria-hidden="true" data-astro-cid-o2ocmoue> ${profileUrl ? renderTemplate`<img${addAttribute(profileUrl, "src")}${addAttribute(person.name, "alt")} class="person-header__photo" data-astro-cid-o2ocmoue>` : person.name.split(" ").slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("")} </div> <div class="person-header__info" data-astro-cid-o2ocmoue> ${primaryRole && renderTemplate`<div class="person-header__role-label" data-astro-cid-o2ocmoue> <span class="role-badge" data-astro-cid-o2ocmoue>${formatRole(primaryRole)}</span> </div>`} ${personRanking && renderTemplate`<div class="person-ranking-badge" data-astro-cid-o2ocmoue> <span class="person-ranking-badge__rank" data-astro-cid-o2ocmoue>#${personRanking.rank}</span> <a${addAttribute(`/people?role=${personRanking.context}`, "href")} class="person-ranking-badge__role" data-astro-cid-o2ocmoue> ${formatRole(personRanking.context)} </a> <span class="person-ranking-badge__sep" data-astro-cid-o2ocmoue>·</span> <span class="person-ranking-badge__score" data-astro-cid-o2ocmoue>${personRanking.score.toFixed(1)} pts</span> </div>`} <h1 class="person-header__name" data-astro-cid-o2ocmoue>${person.name}</h1> <div class="person-header__meta" data-astro-cid-o2ocmoue> ${person.birth_year && renderTemplate`<span class="person-header__meta-item" data-astro-cid-o2ocmoue>
b. ${person.birth_year}${person.death_year ? ` \u2014 d. ${person.death_year}` : ""} </span>`} ${nationalities && renderTemplate`<span class="person-header__meta-item" data-astro-cid-o2ocmoue>${nationalities}</span>`} ${filmography.length > 0 && renderTemplate`<span class="person-header__meta-item" data-astro-cid-o2ocmoue>${filmography.length} works</span>`} </div> </div> </div> </div> </section> <!-- ── Biography ── --> ${person.bio && renderTemplate`<section class="person-bio" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> ${person.bio.split("\n\n").map((para) => renderTemplate`<p class="person-bio__para" data-astro-cid-o2ocmoue>${para}</p>`)} </div> </section>`} <!-- ── Awards & Recognition ── --> ${(personWins.length > 0 || personNoms.length > 0) && renderTemplate`<section class="person-awards" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <h2 class="person-awards__heading" data-astro-cid-o2ocmoue>Awards &amp; Recognition</h2> ${personWins.length > 0 && renderTemplate`<div class="person-awards__wins" data-astro-cid-o2ocmoue> ${personWins.map((wa) => {
    const color = awardTierColor(wa);
    const href = festHref(wa);
    const logoUrl = getFestivalLogoUrl(wa.awards.festivals?.logo_path ?? null);
    const monogram = getFestivalMonogram(festName(wa));
    const filmTitle = workTitleMap.get(wa.work_id);
    const filmSlug = wa.work_id.replace(/^work_/, "");
    return renderTemplate`<div class="person-award-card"${addAttribute(`--tc: ${color}`, "style")} data-astro-cid-o2ocmoue> ${logoUrl ? renderTemplate`<img${addAttribute(logoUrl, "src")} alt="" class="person-award-card__logo" loading="lazy" data-astro-cid-o2ocmoue>` : renderTemplate`<span class="person-award-card__monogram" aria-hidden="true"${addAttribute(`background: color-mix(in srgb, ${color} 15%, transparent)`, "style")} data-astro-cid-o2ocmoue>${monogram}</span>`} <div class="person-award-card__body" data-astro-cid-o2ocmoue> <span class="person-award-card__name" data-astro-cid-o2ocmoue>${wa.awards.name}</span> <span class="person-award-card__meta" data-astro-cid-o2ocmoue> ${filmTitle && renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="person-award-card__film" data-astro-cid-o2ocmoue>${filmTitle}</a>`} ${filmTitle && renderTemplate`<span aria-hidden="true" data-astro-cid-o2ocmoue> · </span>`} ${href ? renderTemplate`<a${addAttribute(href, "href")} class="person-award-card__fest" data-astro-cid-o2ocmoue>${festName(wa)}</a>` : renderTemplate`<span data-astro-cid-o2ocmoue>${festName(wa)}</span>`} ${wa.year && renderTemplate`<span data-astro-cid-o2ocmoue> · ${wa.year}</span>`} </span> </div> </div>`;
  })} </div>`} ${personWins.length === 0 && personNoms.length > 0 && renderTemplate`<ul class="person-noms-list" role="list" data-astro-cid-o2ocmoue> ${personNoms.slice(0, 3).map((wa) => {
    const filmTitle = workTitleMap.get(wa.work_id);
    const filmSlug = wa.work_id.replace(/^work_/, "");
    const href = festHref(wa);
    return renderTemplate`<li class="person-nom-row" data-astro-cid-o2ocmoue> <span class="person-nom-row__name" data-astro-cid-o2ocmoue>${wa.awards.name}</span> <span class="person-nom-row__sep" aria-hidden="true" data-astro-cid-o2ocmoue>·</span> ${filmTitle && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-o2ocmoue": true }, { "default": async ($$result3) => renderTemplate` <a${addAttribute(`/films/${filmSlug}`, "href")} class="person-nom-row__film" data-astro-cid-o2ocmoue>${filmTitle}</a> <span class="person-nom-row__sep" aria-hidden="true" data-astro-cid-o2ocmoue>·</span> ` })}`} ${href ? renderTemplate`<a${addAttribute(href, "href")} class="person-nom-row__fest" data-astro-cid-o2ocmoue>${festName(wa)}</a>` : renderTemplate`<span class="person-nom-row__fest" data-astro-cid-o2ocmoue>${festName(wa)}</span>`} ${wa.year && renderTemplate`<span class="person-nom-row__year" data-astro-cid-o2ocmoue>${wa.year}</span>`} </li>`;
  })} </ul>`} </div> </section>`} <!-- ── Color signature ── --> ${topColors.length > 0 && renderTemplate`<section class="person-colors" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <div class="person-colors__inner" data-astro-cid-o2ocmoue> <div class="person-colors__header" data-astro-cid-o2ocmoue> <h2 class="person-colors__heading" data-astro-cid-o2ocmoue>Visual Identity</h2> <p class="person-colors__sub" data-astro-cid-o2ocmoue>Colors recurring across their filmography</p> </div> <div class="person-colors__signature" data-astro-cid-o2ocmoue> ${topColors.map(([colorId, count]) => {
    const p = getPaletteEntry(colorId);
    if (!p) return null;
    const pct = Math.round(count / filmography.length * 100);
    return renderTemplate`<a${addAttribute(`/colors/${colorId}`, "href")} class="person-color-item" data-astro-cid-o2ocmoue> <div class="person-color-item__bar"${addAttribute(`background: ${p.hex}; height: ${Math.max(pct * 1.5, 12)}px;`, "style")}${addAttribute(`${count} films`, "title")} data-astro-cid-o2ocmoue></div> <span class="person-color-item__name" data-astro-cid-o2ocmoue>${p.name}</span> <span class="person-color-item__count" data-astro-cid-o2ocmoue>${count}</span> </a>`;
  })} </div> </div> </div> </section>`} <!-- ── Filmography ── --> ${filmography.length > 0 && renderTemplate`<section class="person-filmography" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <h2 class="person-filmography__heading" data-astro-cid-o2ocmoue>Filmography</h2> <div class="person-filmography__list" data-astro-cid-o2ocmoue> ${filmography.map((entry) => {
    const filmSlug = entry.work.id.replace(/^work_/, "");
    const colorPalette = entry.color ? getPaletteEntry(entry.color.color_iconico) : null;
    return renderTemplate`<a${addAttribute(`/films/${filmSlug}`, "href")} class="filmography-item" data-astro-cid-o2ocmoue> <div class="filmography-item__color-strip"${addAttribute(colorPalette ? `background: ${colorPalette.hex}` : "background: var(--surface-border)", "style")} data-astro-cid-o2ocmoue></div> <div class="filmography-item__year" data-astro-cid-o2ocmoue> ${entry.work.year ?? "\u2014"} </div> <div class="filmography-item__info" data-astro-cid-o2ocmoue> <span class="filmography-item__title" data-astro-cid-o2ocmoue>${entry.work.title}</span> <span class="role-badge" data-astro-cid-o2ocmoue>${formatRole(entry.role)}</span> </div> ${colorPalette && renderTemplate`<div class="filmography-item__color-name" data-astro-cid-o2ocmoue> ${colorPalette.name} </div>`} </a>`;
  })} </div> </div> </section>`} <!-- Empty state --> ${filmography.length === 0 && !person.bio && renderTemplate`<section class="person-empty" data-astro-cid-o2ocmoue> <div class="site-container" data-astro-cid-o2ocmoue> <p class="person-empty__message" data-astro-cid-o2ocmoue>
Filmography data for this person is being processed.
</p> </div> </section>`} </div> ` })} `;
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
