/* empty css                                     */
import { e as createAstro, f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_QHw3iGXw.mjs';
import { c as createSupabaseServerClient } from '../../chunks/server_DDrZ4Pp_.mjs';
import { P as PRISMA_PALETTE } from '../../chunks/colorPalette_CcE_HP33.mjs';
/* empty css                                        */
export { renderers } from '../../renderers.mjs';

const $$Astro = createAstro("https://prisma.film");
const prerender = false;
const $$workId = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$workId;
  const { work_id } = Astro2.params;
  if (!work_id) {
    return Astro2.redirect("/404");
  }
  const workId = `work_${work_id}`;
  const userIdParam = Astro2.url.searchParams.get("user");
  const supabase = createSupabaseServerClient(Astro2.cookies);
  const { data: work, error: workError } = await supabase.from("works").select(`
    title,
    year,
    poster_path,
    color_assignments (
      color_id
    )
  `).eq("id", workId).single();
  if (workError || !work) {
    return Astro2.redirect("/404");
  }
  const colorId = work.color_assignments?.[0]?.color_id;
  const color = colorId ? PRISMA_PALETTE[colorId] : null;
  let userRating = null;
  let userName = null;
  if (userIdParam) {
    const { data: ratingData } = await supabase.from("user_ratings").select("rating").eq("user_id", userIdParam).eq("work_id", workId).single();
    userRating = ratingData?.rating || null;
    const { data: profileData } = await supabase.from("user_profiles").select("display_name, username").eq("id", userIdParam).single();
    userName = profileData?.display_name || profileData?.username || "A PRISMA user";
  }
  const posterUrl = work.poster_path ? `https://image.tmdb.org/t/p/w500${work.poster_path}` : null;
  const pageTitle = userRating ? `${userName} rated ${work.title} ${userRating}/10 on PRISMA` : `${work.title} (${work.year}) on PRISMA`;
  const pageDescription = color ? `Cinematic color: ${color.name}` : "Discover cinematic visual identity on PRISMA";
  const bgColor = color?.hex || "#0a0a0a";
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": pageTitle, "description": pageDescription, "ogImage": posterUrl || void 0, "data-astro-cid-jzuv5kpb": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="share-page"${addAttribute(`--share-color: ${bgColor}`, "style")} data-astro-cid-jzuv5kpb> <div class="share-container" data-astro-cid-jzuv5kpb> <div class="share-card" data-astro-cid-jzuv5kpb> ${posterUrl ? renderTemplate`<img${addAttribute(posterUrl, "src")}${addAttribute(work.title, "alt")} class="share-poster" data-astro-cid-jzuv5kpb>` : renderTemplate`<div class="share-poster-placeholder" data-astro-cid-jzuv5kpb>${work.title}</div>`} <div class="share-content" data-astro-cid-jzuv5kpb> <h1 class="share-title" data-astro-cid-jzuv5kpb>${work.title}</h1> <p class="share-year" data-astro-cid-jzuv5kpb>${work.year}</p> ${color && renderTemplate`<div class="share-color" data-astro-cid-jzuv5kpb> <div class="share-color__swatch"${addAttribute(`background: ${color.hex}`, "style")} data-astro-cid-jzuv5kpb></div> <span class="share-color__name" data-astro-cid-jzuv5kpb>${color.name}</span> </div>`} ${userRating && renderTemplate`<div class="share-rating" data-astro-cid-jzuv5kpb> <span class="share-rating__score" data-astro-cid-jzuv5kpb>${userRating}/10</span> <span class="share-rating__by" data-astro-cid-jzuv5kpb>rated by ${userName}</span> </div>`} </div> </div> ${!Astro2.locals.user && renderTemplate`<div class="share-cta" data-astro-cid-jzuv5kpb> <a href="/" class="share-cta__button" data-astro-cid-jzuv5kpb>Join PRISMA</a> <p class="share-cta__text" data-astro-cid-jzuv5kpb>Track, rate, and discover films by their cinematic color</p> </div>`} <div class="share-view-film" data-astro-cid-jzuv5kpb> <a${addAttribute(`/films/${work_id}`, "href")} class="share-link" data-astro-cid-jzuv5kpb>View full film page →</a> </div> </div> </div>  ` })}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/share/[work_id].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/share/[work_id].astro";
const $$url = "/share/[work_id]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$workId,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
