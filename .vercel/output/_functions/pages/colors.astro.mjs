/* empty css                                  */
import { f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_BW8MRUf7.mjs';
import { a as getAllColorProfiles } from '../chunks/colors_QF5cQfB_.mjs';
import { i as isLightColor } from '../chunks/colorPalette_MBD9-pHi.mjs';
/* empty css                                 */
export { renderers } from '../renderers.mjs';

const $$Index = createComponent(($$result, $$props, $$slots) => {
  const colors = getAllColorProfiles();
  const SITE = "https://prisma.film";
  const colorsBreadcrumbs = [
    { name: "PRISMA", url: SITE },
    { name: "Colores", url: `${SITE}/colors` }
  ];
  const colorsJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "La Paleta Prisma \u2014 Colores del Cine de Autor",
    description: "Los 18 colores de la paleta Prisma. Cada pel\xEDcula tiene un color que define su identidad visual cinematogr\xE1fica.",
    url: `${SITE}/colors`,
    numberOfItems: colors.length,
    itemListElement: colors.map((c, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: c.name,
      url: `${SITE}/colors/${c.id}`
    }))
  };
  const MONO_MODES = [
    {
      id: "claroscuro_dramatico",
      slug: "claroscuro-dramatico",
      name: "Claroscuro Dram\xE1tico",
      hex: "#1A1A1A",
      gradient: "linear-gradient(to right, #0A0A0F 30%, #F0EEE8 70%)",
      context: "High contrast light and shadow. The drama of what is hidden and revealed."
    },
    {
      id: "monocromatico_intimo",
      slug: "monocromatico-intimo",
      name: "Monocrom\xE1tico \xCDntimo",
      hex: "#4A4A4A",
      gradient: "linear-gradient(135deg, #3A3A3A 0%, #909090 50%, #D8D8D8 100%)",
      context: "Desaturated grey tones. Texture and mood over chromatic spectacle."
    }
  ];
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Paleta de Colores \u2014 PRISMA", "description": "Los 18 colores de la paleta Prisma. Cada pel\xEDcula tiene un color.", "jsonLd": colorsJsonLd, "breadcrumbs": colorsBreadcrumbs, "data-astro-cid-ojideimc": true }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="colors-page page-enter" data-astro-cid-ojideimc> <!-- Hero --> <div class="colors-hero site-container" data-astro-cid-ojideimc> <div class="colors-hero__inner" data-astro-cid-ojideimc> <p class="colors-hero__eyebrow reveal" data-astro-cid-ojideimc>Identidad cromática</p> <h1 class="colors-hero__title reveal" data-delay="80" data-astro-cid-ojideimc>La Paleta Prisma</h1> <p class="colors-hero__subtitle reveal" data-delay="160" data-astro-cid-ojideimc>
Dieciocho colores. Cada uno un registro emocional distinto en el cine de autor.
</p> </div> </div> <!-- Color grid — chromatic spectrum (16 colors, mono excluded — shown separately below) --> <div class="colors-grid site-container" data-astro-cid-ojideimc> ${colors.filter((c) => c.id !== "claroscuro_dramatico" && c.id !== "monocromatico_intimo").map((color, i) => {
    const light = isLightColor(color.id);
    const swatchTextColor = light ? "rgba(10,10,15,0.55)" : "rgba(240,238,232,0.5)";
    return renderTemplate`<a${addAttribute(`/colors/${color.id}`, "href")} class="color-card reveal"${addAttribute(String(Math.min(i * 40, 400)), "data-delay")}${addAttribute(`--c: ${color.hex}; --ct: ${light ? "#0A0A0F" : "#F0EEE8"}; --cs: ${swatchTextColor};`, "style")} data-astro-cid-ojideimc> <!-- Full-color swatch block on top --> <div class="color-card__swatch" data-astro-cid-ojideimc> <span class="color-card__swatch-hex" data-astro-cid-ojideimc>${color.hex}</span> </div> <!-- Info --> <div class="color-card__body" data-astro-cid-ojideimc> <span class="color-card__name" data-astro-cid-ojideimc>${color.name}</span> <span class="color-card__context" data-astro-cid-ojideimc> ${color.cultural_context.length > 72 ? color.cultural_context.substring(0, 72) + "\u2026" : color.cultural_context} </span> </div> <!-- Color accent line at the bottom on hover --> <div class="color-card__accent" data-astro-cid-ojideimc></div> </a>`;
  })} </div> <!-- Monochromatic modes --> <div class="mono-section site-container" data-astro-cid-ojideimc> <div class="section-label reveal" data-astro-cid-ojideimc>Modos Monocromáticos</div> <div class="mono-grid" data-astro-cid-ojideimc> ${MONO_MODES.map((mono) => renderTemplate`<a${addAttribute(`/colors/${mono.slug}`, "href")} class="color-card color-card--mono"${addAttribute(`--c: ${mono.hex};`, "style")} data-astro-cid-ojideimc> <div class="color-card__swatch color-card__swatch--gradient"${addAttribute(`background: ${mono.gradient};`, "style")} data-astro-cid-ojideimc> <span class="color-card__swatch-hex" style="color: rgba(240,238,232,0.45)" data-astro-cid-ojideimc>B&W MODE</span> </div> <div class="color-card__body" data-astro-cid-ojideimc> <span class="color-card__name" data-astro-cid-ojideimc>${mono.name}</span> <span class="color-card__context" data-astro-cid-ojideimc>${mono.context}</span> </div> <div class="color-card__accent" data-astro-cid-ojideimc></div> </a>`)} </div> </div> </div> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/colors/index.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/colors/index.astro";
const $$url = "/colors";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
