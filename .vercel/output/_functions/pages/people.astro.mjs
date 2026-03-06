/* empty css                                  */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_QHw3iGXw.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../chunks/client_DzNyPYKT.mjs';
/* empty css                                 */
export { renderers } from '../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$Index;
  const TMDB_BASE = "https://image.tmdb.org/t/p/w185";
  const TABS = [
    { id: "director", label: "Directors", dbContext: "director", genderFilter: null },
    { id: "cinematography", label: "Cinematography", dbContext: "cinematography", genderFilter: null },
    { id: "writer", label: "Writers", dbContext: "writer", genderFilter: null },
    { id: "actor", label: "Actors", dbContext: "actor", genderFilter: [2, 0] },
    { id: "actress", label: "Actresses", dbContext: "actor", genderFilter: [1, 3] },
    { id: "editor", label: "Editors", dbContext: "editor", genderFilter: null },
    { id: "composer", label: "Composers", dbContext: "composer", genderFilter: null }
  ];
  const activeTabId = Astro2.url.searchParams.get("role") ?? "director";
  const activeTab = TABS.find((t) => t.id === activeTabId) ?? TABS[0];
  function getInitials(name) {
    return name.split(" ").filter(Boolean).slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("");
  }
  let rankings = [];
  let maxScore = 1;
  if (isSupabaseConfigured()) {
    const db = createServiceClient();
    const fetchLimit = activeTab.genderFilter ? 400 : 100;
    const rsRes = await db.from("ranking_scores").select("entity_id, score, rank").eq("entity_type", "person").eq("context", activeTab.dbContext).order("rank").limit(fetchLimit);
    if (rsRes.data && rsRes.data.length > 0) {
      const entityIds = rsRes.data.map((r) => r.entity_id);
      const peopleRes = await db.from("people").select("id, name, profile_path, gender").in("id", entityIds);
      if (peopleRes.data) {
        const peopleMap = new Map(
          peopleRes.data.map((p) => [p.id, p])
        );
        const merged = rsRes.data.map((r) => {
          const p = peopleMap.get(r.entity_id);
          if (!p) return null;
          return {
            rank: r.rank,
            score: r.score,
            entityId: r.entity_id,
            slug: r.entity_id.replace(/^person_/, ""),
            name: p.name,
            initials: getInitials(p.name),
            profilePath: p.profile_path ?? null,
            gender: p.gender ?? 0
          };
        }).filter((x) => x !== null);
        if (activeTab.genderFilter) {
          const gf = activeTab.genderFilter;
          const filtered = merged.filter((p) => gf.includes(p.gender));
          rankings = filtered.slice(0, 100).map((p, i) => ({ ...p, rank: i + 1 }));
        } else {
          rankings = merged.slice(0, 100);
        }
        maxScore = rankings[0]?.score ?? 1;
      }
    }
  }
  const pageTitle = "Filmmakers \u2014 PRISMA";
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": "Rankings of the most decorated directors, cinematographers, actors, and key creatives in the PRISMA catalog.", "data-astro-cid-z5amknga": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="people-index page-enter" data-astro-cid-z5amknga> <!-- Header --> <section class="people-header" data-astro-cid-z5amknga> <div class="site-container" data-astro-cid-z5amknga> <h1 class="people-header__title" data-astro-cid-z5amknga>Filmmakers</h1> <p class="people-header__subtitle" data-astro-cid-z5amknga>Ranked by awards, cultural weight, and prestige</p> </div> </section> <!-- Tab nav --> <nav class="people-tabs" aria-label="Role filter" data-astro-cid-z5amknga> <div class="site-container" data-astro-cid-z5amknga> <div class="people-tabs__inner" data-astro-cid-z5amknga> ${TABS.map((tab) => renderTemplate`<a${addAttribute(`/people?role=${tab.id}`, "href")}${addAttribute(`people-tabs__tab ${activeTabId === tab.id ? "people-tabs__tab--active" : ""}`, "class")} data-astro-cid-z5amknga> ${tab.label} </a>`)} </div> </div> </nav> <!-- Ranked list --> <section class="people-rankings" data-astro-cid-z5amknga> <div class="site-container" data-astro-cid-z5amknga> ${rankings.length === 0 ? renderTemplate`<p class="people-rankings__empty" data-astro-cid-z5amknga>No rankings available for this category.</p>` : renderTemplate`<ol class="rankings-list"${addAttribute(`${activeTab.label} rankings`, "aria-label")} data-astro-cid-z5amknga> ${rankings.map((person) => {
    const barWidth = Math.max(4, Math.round(person.score / maxScore * 120));
    const photoUrl = person.profilePath ? `${TMDB_BASE}${person.profilePath}` : null;
    return renderTemplate`<li class="rankings-item" data-astro-cid-z5amknga> <span class="rankings-item__rank"${addAttribute(`Rank ${person.rank}`, "aria-label")} data-astro-cid-z5amknga>
#${person.rank} </span> <div class="rankings-item__avatar" aria-hidden="true" data-astro-cid-z5amknga> ${photoUrl ? renderTemplate`<img${addAttribute(photoUrl, "src")} alt="" loading="lazy" decoding="async" class="rankings-item__photo" data-astro-cid-z5amknga>` : renderTemplate`<span class="rankings-item__initials" data-astro-cid-z5amknga>${person.initials}</span>`} </div> <div class="rankings-item__body" data-astro-cid-z5amknga> <a${addAttribute(`/people/${person.slug}`, "href")} class="rankings-item__name" data-astro-cid-z5amknga> ${person.name} </a> <div class="rankings-item__bar-wrap" data-astro-cid-z5amknga> <div class="rankings-item__bar"${addAttribute(`width: ${barWidth}px`, "style")}${addAttribute(`Score: ${person.score.toFixed(1)}`, "aria-label")} data-astro-cid-z5amknga></div> <span class="rankings-item__score" data-astro-cid-z5amknga>${person.score.toFixed(1)} pts</span> </div> </div> </li>`;
  })} </ol>`} </div> </section> </div>  ` })}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/people/index.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/people/index.astro";
const $$url = "/people";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
