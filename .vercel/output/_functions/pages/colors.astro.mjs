/* empty css                                  */
import { f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_CKaj1kxH.mjs';
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
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Paleta de Colores \u2014 PRISMA", "description": "Los 18 colores de la paleta Prisma. Cada pel\xEDcula tiene un color.", "jsonLd": colorsJsonLd, "breadcrumbs": colorsBreadcrumbs, "data-astro-cid-ojideimc": true }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="colors-page page-enter" data-astro-cid-ojideimc> <div class="colors-page__hero site-container" data-astro-cid-ojideimc> <h1 class="colors-page__title" data-astro-cid-ojideimc>La Paleta Prisma</h1> <p class="colors-page__subtitle" data-astro-cid-ojideimc>
Dieciocho colores. Cada uno un registro emocional distinto en el cine.
</p> </div> <div class="colors-page__grid site-container" data-astro-cid-ojideimc> ${colors.map((color) => {
    const light = isLightColor(color.id);
    return renderTemplate`<a${addAttribute(`/colors/${color.id}`, "href")} class="color-entry"${addAttribute(`--c: ${color.hex}; --ct: ${light ? "#0A0A0F" : "#F0EEE8"}; --cs: ${light ? "rgba(10,10,15,0.5)" : "rgba(240,238,232,0.45)"};`, "style")} data-astro-cid-ojideimc> <div class="color-entry__swatch" data-astro-cid-ojideimc></div> <div class="color-entry__info" data-astro-cid-ojideimc> <span class="color-entry__name" data-astro-cid-ojideimc>${color.name}</span> <span class="color-entry__hex" data-astro-cid-ojideimc>${color.hex}</span> <span class="color-entry__context" data-astro-cid-ojideimc> ${color.cultural_context.length > 55 ? color.cultural_context.substring(0, 55) + "..." : color.cultural_context} </span> </div> </a>`;
  })} </div> <!-- Monochromatic Modes — separate row, achromatic treatment --> <div class="mono-section site-container" data-astro-cid-ojideimc> <div class="mono-section__header" data-astro-cid-ojideimc> <span class="mono-section__label" data-astro-cid-ojideimc>Monochromatic Modes</span> <span class="mono-section__note" data-astro-cid-ojideimc>B&W and greyscale — achromatic registers</span> </div> <div class="mono-grid" data-astro-cid-ojideimc> ${MONO_MODES.map((mono) => renderTemplate`<a${addAttribute(`/colors/${mono.slug}`, "href")} class="color-entry color-entry--mono" data-astro-cid-ojideimc> <div class="color-entry__swatch color-entry__swatch--gradient"${addAttribute(`background: ${mono.gradient}`, "style")} data-astro-cid-ojideimc></div> <div class="color-entry__info" data-astro-cid-ojideimc> <span class="color-entry__name" data-astro-cid-ojideimc>${mono.name}</span> <span class="color-entry__hex mono-badge" data-astro-cid-ojideimc>B&W MODE</span> <span class="color-entry__context" data-astro-cid-ojideimc>${mono.context}</span> </div> </a>`)} </div> </div> </div> ` })} `;
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
