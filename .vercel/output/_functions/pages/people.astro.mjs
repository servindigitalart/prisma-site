/* empty css                                  */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_BW8MRUf7.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../chunks/client_DzNyPYKT.mjs';
/* empty css                                 */
export { renderers } from '../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$Index;
  const TMDB_BASE = "https://image.tmdb.org/t/p/w185";
  const TMDB_LG = "https://image.tmdb.org/t/p/w342";
  const TABS = [
    { id: "director", label: "Directores", dbContext: "director", genderFilter: null },
    { id: "cinematography", label: "Fotograf\xEDa", dbContext: "cinematography", genderFilter: null },
    { id: "writer", label: "Guionistas", dbContext: "writer", genderFilter: null },
    { id: "actor", label: "Actores", dbContext: "actor", genderFilter: null },
    { id: "actress", label: "Actrices", dbContext: "actress", genderFilter: null },
    { id: "editor", label: "Editores", dbContext: "editor", genderFilter: null },
    { id: "composer", label: "Compositores", dbContext: "composer", genderFilter: null }
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
    const rsRes = await db.from("ranking_scores").select("entity_id, score, rank").eq("entity_type", "person").eq("context", activeTab.dbContext).gt("score", 0).order("rank").limit(100);
    if (rsRes.data && rsRes.data.length > 0) {
      const entityIds = rsRes.data.map((r) => r.entity_id);
      const peopleRes = await db.from("people").select("id, name, profile_path, gender").in("id", entityIds);
      if (peopleRes.data) {
        const peopleMap = new Map(
          peopleRes.data.map((p) => [p.id, p])
        );
        rankings = rsRes.data.map((r) => {
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
        maxScore = rankings[0]?.score ?? 1;
      }
    }
  }
  const featured = rankings[0] ?? null;
  const rest = rankings.slice(1);
  const pageTitle = "Cineastas \u2014 PRISMA";
  const pageDescription = "Rankings de los directores, cinefot\xF3grafos, actores y creativos m\xE1s reconocidos del cat\xE1logo PRISMA.";
  const SITE = "https://prisma.film";
  const peopleBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Cineastas", url: `${SITE}/people` }
  ];
  const peopleJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "Cineastas \u2014 Rankings de Directores, Actores y Creativos",
    description: pageDescription,
    url: `${SITE}/people`,
    itemListElement: rankings.slice(0, 20).map((p, i) => ({
      "@type": "ListItem",
      position: i + 1,
      item: {
        "@type": "Person",
        name: p.name,
        url: `${SITE}/people/${p.slug}`
      }
    }))
  };
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "jsonLd": peopleJsonLd, "breadcrumbs": peopleBreadcrumbs, "data-astro-cid-z5amknga": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="people-index page-enter" data-astro-cid-z5amknga> <!-- Header --> <section class="people-header" data-astro-cid-z5amknga> <div class="site-container" data-astro-cid-z5amknga> <p class="people-header__eyebrow reveal" data-astro-cid-z5amknga>Catálogo</p> <h1 class="people-header__title reveal" data-delay="60" data-astro-cid-z5amknga>Cineastas</h1> <p class="people-header__subtitle reveal" data-delay="120" data-astro-cid-z5amknga>
Clasificados por premios, peso cultural y prestigio
</p> </div> </section> <!-- Tab nav — editorial pill style --> <nav class="people-tabs" aria-label="Filtrar por rol" data-astro-cid-z5amknga> <div class="site-container" data-astro-cid-z5amknga> <div class="people-tabs__inner" data-astro-cid-z5amknga> ${TABS.map((tab) => renderTemplate`<a${addAttribute(`/people?role=${tab.id}`, "href")}${addAttribute(`people-tabs__tab ${activeTabId === tab.id ? "people-tabs__tab--active" : ""}`, "class")} data-astro-cid-z5amknga> ${tab.label} </a>`)} </div> </div> </nav> <!-- Rankings --> <section class="people-rankings" data-astro-cid-z5amknga> <div class="site-container" data-astro-cid-z5amknga> ${rankings.length === 0 ? renderTemplate`<p class="people-rankings__empty" data-astro-cid-z5amknga>No hay rankings disponibles para esta categoría.</p>` : renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-z5amknga": true }, { "default": async ($$result3) => renderTemplate`  ${featured && renderTemplate`<a${addAttribute(`/people/${featured.slug}`, "href")} class="featured-person reveal" data-astro-cid-z5amknga> <div class="featured-person__photo-wrap" data-astro-cid-z5amknga> ${featured.profilePath ? renderTemplate`<img${addAttribute(`${TMDB_LG}${featured.profilePath}`, "src")}${addAttribute(featured.name, "alt")} loading="eager" class="featured-person__photo" data-astro-cid-z5amknga>` : renderTemplate`<span class="featured-person__initials" data-astro-cid-z5amknga>${featured.initials}</span>`} </div> <div class="featured-person__body" data-astro-cid-z5amknga> <span class="featured-person__rank" data-astro-cid-z5amknga>#1</span> <h2 class="featured-person__name" data-astro-cid-z5amknga>${featured.name}</h2> <div class="featured-person__score-wrap" data-astro-cid-z5amknga> <div class="featured-person__score-bar" data-astro-cid-z5amknga> <div class="featured-person__score-fill" style="width: 100%" data-astro-cid-z5amknga></div> </div> <span class="featured-person__score" data-astro-cid-z5amknga>${featured.score.toFixed(1)} pts</span> </div> <span class="featured-person__role" data-astro-cid-z5amknga>${activeTab.label}</span> </div> </a>`} <ol class="rankings-list"${addAttribute(`${activeTab.label} rankings`, "aria-label")} data-astro-cid-z5amknga> ${rest.map((person, i) => {
    const barPct = Math.max(4, Math.round(person.score / maxScore * 100));
    const photoUrl = person.profilePath ? `${TMDB_BASE}${person.profilePath}` : null;
    return renderTemplate`<li class="rankings-item reveal"${addAttribute(String(Math.min(i * 25, 300)), "data-delay")} data-astro-cid-z5amknga> <span class="rankings-item__rank"${addAttribute(`Rank ${person.rank}`, "aria-label")} data-astro-cid-z5amknga> ${person.rank} </span> <div class="rankings-item__avatar" aria-hidden="true" data-astro-cid-z5amknga> ${photoUrl ? renderTemplate`<img${addAttribute(photoUrl, "src")} alt="" loading="lazy" decoding="async" class="rankings-item__photo" data-astro-cid-z5amknga>` : renderTemplate`<span class="rankings-item__initials" data-astro-cid-z5amknga>${person.initials}</span>`} </div> <div class="rankings-item__body" data-astro-cid-z5amknga> <a${addAttribute(`/people/${person.slug}`, "href")} class="rankings-item__name" data-astro-cid-z5amknga> ${person.name} </a> <div class="rankings-item__bar-wrap" data-astro-cid-z5amknga> <div class="rankings-item__bar-track" data-astro-cid-z5amknga> <div class="rankings-item__bar"${addAttribute(`width: ${barPct}%`, "style")}${addAttribute(`Score: ${person.score.toFixed(1)}`, "aria-label")} data-astro-cid-z5amknga></div> </div> <span class="rankings-item__score" data-astro-cid-z5amknga>${person.score.toFixed(1)}</span> </div> </div> </li>`;
  })} </ol> ` })}`} </div> </section> </div>  ` })}`;
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
