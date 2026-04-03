/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, h as addAttribute, m as maybeRenderHead } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_BW8MRUf7.mjs';
import { c as createSupabaseServerClient } from '../../chunks/server_Cbvb-X7K.mjs';
import { i as isSupabaseConfigured, c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { P as PRISMA_PALETTE } from '../../chunks/colorPalette_MBD9-pHi.mjs';
/* empty css                                   */
export { renderers } from '../../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Astro = createAstro("https://prisma.film");
const prerender = false;
const $$id = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$id;
  const { id } = Astro2.params;
  if (!id) {
    return Astro2.redirect("/404");
  }
  const supabase = createSupabaseServerClient(Astro2.cookies, Astro2.request);
  const db = isSupabaseConfigured() ? createServiceClient() : supabase;
  const { data: profile, error: profileError } = await db.from("user_profiles").select("*").eq("id", id).maybeSingle();
  console.log("[profile] query result:", JSON.stringify(profile), "error:", profileError?.message, "for id:", id);
  if (profileError || !profile) {
    console.error("[profile] Profile not found for id:", id, profileError?.message);
    return Astro2.redirect("/404");
  }
  const { data: watches, error: watchesError } = await db.from("user_watches").select(`
    work_id,
    watched_at,
    works (
      id,
      title,
      year,
      tmdb_poster_path
    )
  `).eq("user_id", id).order("watched_at", { ascending: false }).limit(12);
  if (watchesError) {
    console.error("[profile] watches query error:", watchesError.message);
  }
  const { data: ratings, error: ratingsError } = await db.from("user_ratings").select(`
    work_id,
    rating,
    review,
    updated_at,
    works (
      id,
      title,
      year,
      tmdb_poster_path
    )
  `).eq("user_id", id).order("updated_at", { ascending: false });
  if (ratingsError) {
    console.error("[profile] ratings query error:", ratingsError.message);
  }
  const { count: followerCount } = await db.from("follows").select("*", { count: "exact", head: true }).eq("following_id", id);
  const { count: followingCount } = await db.from("follows").select("*", { count: "exact", head: true }).eq("follower_id", id);
  const { data: watchlist, error: watchlistError } = await db.from("user_watchlist").select(`
    work_id,
    added_at,
    works (
      id,
      title,
      year,
      tmdb_poster_path
    )
  `).eq("user_id", id).order("added_at", { ascending: false }).limit(6);
  if (watchlistError) {
    console.error("[profile] watchlist query error:", watchlistError.message);
  }
  const ratingsMap = {};
  ratings?.forEach((r) => {
    ratingsMap[r.work_id] = r.rating;
  });
  const colorCounts = {};
  watches?.forEach((w) => {
    const colorId = w.works?.color_assignments?.[0]?.color_id;
    if (colorId) {
      colorCounts[colorId] = (colorCounts[colorId] || 0) + 1;
    }
  });
  const dominantColorId = Object.entries(colorCounts).sort(([, a], [, b]) => b - a)[0]?.[0];
  const dominantColor = dominantColorId ? PRISMA_PALETTE[dominantColorId] : null;
  const ratingCount = ratings?.filter((r) => r.rating)?.length || 0;
  const watchlistCount = watchlist?.length || 0;
  const seenCount = watches?.length || 0;
  const reviewCount = ratings?.filter((r) => r.review)?.length || 0;
  const currentUser = Astro2.locals.user;
  let isFollowing = false;
  if (currentUser && currentUser.id !== id) {
    const { data: followData } = await db.from("follows").select("*").eq("follower_id", currentUser.id).eq("following_id", id).maybeSingle();
    isFollowing = !!followData;
  }
  const pageTitle = `${profile.display_name || profile.username || "Usuario"} en PRISMA`;
  const pageDescription = `${ratingCount} rated \xB7 ${watchlistCount} watchlist${dominantColor ? ` \xB7 ${dominantColor.name}` : ""}`;
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "ogImage": profile.avatar_url ?? void 0, "data-astro-cid-dsbtqrwp": true }, { "default": async ($$result2) => renderTemplate(_a || (_a = __template([" ", '<div class="profile-page page-enter" data-astro-cid-dsbtqrwp> <div class="site-container" data-astro-cid-dsbtqrwp> <!-- Profile Header --> <header class="profile-header" data-astro-cid-dsbtqrwp> <div class="profile-avatar" data-astro-cid-dsbtqrwp> ', ' </div> <div class="profile-info" data-astro-cid-dsbtqrwp> <h1 class="profile-name" data-astro-cid-dsbtqrwp>', "</h1> ", " ", ' <div class="profile-stats" data-astro-cid-dsbtqrwp> <span class="profile-stat" data-astro-cid-dsbtqrwp>', ' calificadas</span> <span class="profile-stat" data-astro-cid-dsbtqrwp>', ' watchlist</span> <span class="profile-stat" id="follower-count-stat" data-astro-cid-dsbtqrwp>', ' seguidores</span> <span class="profile-stat" data-astro-cid-dsbtqrwp>', ' siguiendo</span> </div> <div class="profile-actions" data-astro-cid-dsbtqrwp> ', ' <button class="btn-share" id="btn-share-profile" data-astro-cid-dsbtqrwp>Compartir perfil</button> </div> </div> </header> <!-- Cinematic DNA --> ', ' <!-- Collapsible sections --> <!-- Watchlist (open by default) --> <section class="profile-section" id="section-watchlist" data-astro-cid-dsbtqrwp> <button class="section-toggle" data-astro-cid-dsbtqrwp>Watchlist <span data-astro-cid-dsbtqrwp>(', ')</span> \u25BE</button> <div class="section-content" data-astro-cid-dsbtqrwp> ', ' </div> </section> <!-- Ranked (closed by default) --> <section class="profile-section" id="section-ranked" data-astro-cid-dsbtqrwp> <button class="section-toggle" data-astro-cid-dsbtqrwp>Calificadas <span data-astro-cid-dsbtqrwp>(', ')</span> \u25B8</button> <div class="section-content" hidden data-astro-cid-dsbtqrwp> ', ' </div> </section> <!-- Seen (closed by default) --> <section class="profile-section" id="section-seen" data-astro-cid-dsbtqrwp> <button class="section-toggle" data-astro-cid-dsbtqrwp>Vistas <span data-astro-cid-dsbtqrwp>(', ')</span> \u25B8</button> <div class="section-content" hidden data-astro-cid-dsbtqrwp> ', ' </div> </section> <!-- Reviews (closed by default) --> <section class="profile-section" id="section-reviews" data-astro-cid-dsbtqrwp> <button class="section-toggle" data-astro-cid-dsbtqrwp>Rese\xF1as <span data-astro-cid-dsbtqrwp>(', ')</span> \u25B8</button> <div class="section-content" hidden data-astro-cid-dsbtqrwp> ', " </div> </section> </div> </div> <script>\n    // Section toggles\n    document.querySelectorAll('.section-toggle').forEach(function(btn) {\n      btn.addEventListener('click', function() {\n        var content = btn.nextElementSibling;\n        if (!content) return;\n        var isHidden = content.hasAttribute('hidden');\n        if (isHidden) {\n          content.removeAttribute('hidden');\n          btn.textContent = btn.textContent.replace('\u25B8', '\u25BE');\n        } else {\n          content.setAttribute('hidden', '');\n          btn.textContent = btn.textContent.replace('\u25BE', '\u25B8');\n        }\n      });\n    });\n\n    // Follow button\n    var followBtn = document.getElementById('follow-btn');\n    if (followBtn) {\n      var followBtnText = document.getElementById('follow-btn-text');\n      var profileId = followBtn.dataset.profileId;\n      var isFollowing = followBtn.dataset.isFollowing === '1';\n      var fCount = Number(followBtn.dataset.followerCount) || 0;\n\n      followBtn.addEventListener('click', async function() {\n        followBtn.setAttribute('disabled', 'true');\n        // Optimistic update\n        isFollowing = !isFollowing;\n        fCount += isFollowing ? 1 : -1;\n        followBtnText.textContent = isFollowing ? 'Siguiendo' : 'Seguir';\n        followBtn.classList.toggle('is-following', isFollowing);\n        var fcStat = document.getElementById('follower-count-stat');\n        if (fcStat) fcStat.textContent = fCount + ' seguidores';\n        \n        try {\n          var response = await fetch('/api/user/follow', {\n            method: 'POST',\n            headers: { 'Content-Type': 'application/json' },\n            body: JSON.stringify({ following_id: profileId })\n          });\n          if (response.ok) {\n            var data = await response.json();\n            // Correct if server disagrees\n            if (data.following !== isFollowing) {\n              isFollowing = data.following;\n              fCount += isFollowing ? 1 : -1;\n              followBtnText.textContent = isFollowing ? 'Siguiendo' : 'Seguir';\n              followBtn.classList.toggle('is-following', isFollowing);\n              if (fcStat) fcStat.textContent = fCount + ' seguidores';\n            }\n          }\n        } catch(e) {\n          // Revert on error\n          isFollowing = !isFollowing;\n          fCount += isFollowing ? 1 : -1;\n          followBtnText.textContent = isFollowing ? 'Siguiendo' : 'Seguir';\n          followBtn.classList.toggle('is-following', isFollowing);\n          var fcStat2 = document.getElementById('follower-count-stat');\n          if (fcStat2) fcStat2.textContent = fCount + ' seguidores';\n        }\n        followBtn.removeAttribute('disabled');\n      });\n    }\n\n    // Share button\n    document.getElementById('btn-share-profile')?.addEventListener('click', async function() {\n      var url = window.location.href;\n      var btn = this;\n      try {\n        await navigator.clipboard.writeText(url);\n        btn.textContent = '\u2713 \xA1Enlace copiado!';\n        setTimeout(function() { btn.textContent = 'Compartir perfil'; }, 2000);\n      } catch(e) {\n        if (navigator.share) {\n          navigator.share({ title: 'Mi perfil PRISMA', url: url });\n        } else {\n          prompt('Copia este enlace:', url);\n        }\n      }\n    });\n  <\/script>  "])), maybeRenderHead(), profile.avatar_url ? renderTemplate`<img${addAttribute(profile.avatar_url, "src")}${addAttribute(profile.display_name || profile.username, "alt")} class="profile-avatar__img" data-astro-cid-dsbtqrwp>` : renderTemplate`<div class="profile-avatar__placeholder" data-astro-cid-dsbtqrwp> ${(profile.display_name || profile.username || "?")[0].toUpperCase()} </div>`, profile.display_name || profile.username, profile.username && profile.display_name && renderTemplate`<p class="profile-username" data-astro-cid-dsbtqrwp>@${profile.username}</p>`, profile.bio && renderTemplate`<p class="profile-bio" data-astro-cid-dsbtqrwp>${profile.bio}</p>`, ratingCount, watchlistCount, followerCount ?? 0, followingCount ?? 0, currentUser && currentUser.id !== id && renderTemplate`<button class="follow-btn" id="follow-btn"${addAttribute(id, "data-profile-id")}${addAttribute(isFollowing ? "1" : "0", "data-is-following")}${addAttribute(followerCount ?? 0, "data-follower-count")} data-astro-cid-dsbtqrwp> <span id="follow-btn-text" data-astro-cid-dsbtqrwp>${isFollowing ? "Siguiendo" : "Seguir"}</span> </button>`, dominantColor && renderTemplate`<section class="dna-section" data-astro-cid-dsbtqrwp> <h2 class="dna-title" data-astro-cid-dsbtqrwp>ADN Cinematográfico</h2> <div class="dna-grid" data-astro-cid-dsbtqrwp> <div class="dna-item" data-astro-cid-dsbtqrwp> <div class="dna-label" data-astro-cid-dsbtqrwp>Color Dominante</div> <div class="dna-color" data-astro-cid-dsbtqrwp> <div class="dna-color__swatch"${addAttribute(`background: ${dominantColor.hex}`, "style")} data-astro-cid-dsbtqrwp></div> <span class="dna-color__name" data-astro-cid-dsbtqrwp>${dominantColor.name}</span> </div> </div> </div> </section>`, watchlistCount, watchlist && watchlist.length > 0 ? renderTemplate`<div class="film-grid" data-astro-cid-dsbtqrwp> ${watchlist.map((item) => {
    const work = item.works;
    if (!work) return null;
    const slug = work.id.replace(/^work_/, "");
    const posterUrl = work.tmdb_poster_path ? `https://image.tmdb.org/t/p/w300${work.tmdb_poster_path}` : null;
    return renderTemplate`<a${addAttribute(`/films/${slug}`, "href")} class="film-card" data-astro-cid-dsbtqrwp> ${posterUrl ? renderTemplate`<img${addAttribute(posterUrl, "src")}${addAttribute(work.title, "alt")} class="film-card__poster" loading="lazy" data-astro-cid-dsbtqrwp>` : renderTemplate`<div class="film-card__placeholder" data-astro-cid-dsbtqrwp>${work.title}</div>`} <div class="film-card__meta" data-astro-cid-dsbtqrwp> <div class="film-card__title" data-astro-cid-dsbtqrwp>${work.title}</div> <div class="film-card__year" data-astro-cid-dsbtqrwp>${work.year}</div> </div> </a>`;
  })} </div>` : renderTemplate`<p class="section-empty" data-astro-cid-dsbtqrwp>Aún no hay películas en watchlist.</p>`, ratingCount, ratings && ratings.filter((r) => r.rating).length > 0 ? renderTemplate`<div class="ranked-list" data-astro-cid-dsbtqrwp> ${ratings.filter((r) => r.rating).sort((a, b) => b.rating - a.rating).map((r) => {
    const work = r.works;
    if (!work) return null;
    const slug = work.id.replace(/^work_/, "");
    const posterUrl = work.tmdb_poster_path ? `https://image.tmdb.org/t/p/w92${work.tmdb_poster_path}` : null;
    return renderTemplate`<a${addAttribute(`/films/${slug}`, "href")} class="ranked-item" data-astro-cid-dsbtqrwp> ${posterUrl ? renderTemplate`<img${addAttribute(posterUrl, "src")}${addAttribute(work.title, "alt")} class="ranked-item__poster" loading="lazy" data-astro-cid-dsbtqrwp>` : renderTemplate`<div class="ranked-item__poster-placeholder" data-astro-cid-dsbtqrwp>${work.title[0]}</div>`} <div class="ranked-item__info" data-astro-cid-dsbtqrwp> <span class="ranked-item__title" data-astro-cid-dsbtqrwp>${work.title}</span> <span class="ranked-item__year" data-astro-cid-dsbtqrwp>${work.year}</span> </div> <span class="ranked-item__rating" data-astro-cid-dsbtqrwp>${r.rating}/10</span> </a>`;
  })} </div>` : renderTemplate`<p class="section-empty" data-astro-cid-dsbtqrwp>Aún no hay calificaciones.</p>`, seenCount, watches && watches.length > 0 ? renderTemplate`<div class="film-grid" data-astro-cid-dsbtqrwp> ${watches.map((watch) => {
    const work = watch.works;
    if (!work) return null;
    const slug = work.id.replace(/^work_/, "");
    const posterUrl = work.tmdb_poster_path ? `https://image.tmdb.org/t/p/w300${work.tmdb_poster_path}` : null;
    return renderTemplate`<a${addAttribute(`/films/${slug}`, "href")} class="film-card" data-astro-cid-dsbtqrwp> ${posterUrl ? renderTemplate`<img${addAttribute(posterUrl, "src")}${addAttribute(work.title, "alt")} class="film-card__poster" loading="lazy" data-astro-cid-dsbtqrwp>` : renderTemplate`<div class="film-card__placeholder" data-astro-cid-dsbtqrwp>${work.title}</div>`} <div class="film-card__meta" data-astro-cid-dsbtqrwp> <div class="film-card__title" data-astro-cid-dsbtqrwp>${work.title}</div> <div class="film-card__year" data-astro-cid-dsbtqrwp>${work.year}</div> </div> </a>`;
  })} </div>` : renderTemplate`<p class="section-empty" data-astro-cid-dsbtqrwp>Aún no hay películas vistas.</p>`, reviewCount, ratings && ratings.filter((r) => r.review).length > 0 ? renderTemplate`<div class="reviews-list" data-astro-cid-dsbtqrwp> ${ratings.filter((r) => r.review).map((r) => {
    const work = r.works;
    if (!work) return null;
    const slug = work.id.replace(/^work_/, "");
    const posterUrl = work.tmdb_poster_path ? `https://image.tmdb.org/t/p/w92${work.tmdb_poster_path}` : null;
    return renderTemplate`<div class="review-item" data-astro-cid-dsbtqrwp> <a${addAttribute(`/films/${slug}`, "href")} class="review-item__header" data-astro-cid-dsbtqrwp> ${posterUrl ? renderTemplate`<img${addAttribute(posterUrl, "src")}${addAttribute(work.title, "alt")} class="review-item__poster" loading="lazy" data-astro-cid-dsbtqrwp>` : renderTemplate`<div class="review-item__poster-placeholder" data-astro-cid-dsbtqrwp>${work.title[0]}</div>`} <div class="review-item__info" data-astro-cid-dsbtqrwp> <span class="review-item__title" data-astro-cid-dsbtqrwp>${work.title}</span> <span class="review-item__rating" data-astro-cid-dsbtqrwp>★ ${r.rating}/10</span> </div> </a> <p class="review-item__text" data-astro-cid-dsbtqrwp>${r.review}</p> </div>`;
  })} </div>` : renderTemplate`<p class="section-empty" data-astro-cid-dsbtqrwp>Aún no hay reseñas.</p>`) })}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/u/[id].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/u/[id].astro";
const $$url = "/u/[id]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$id,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
