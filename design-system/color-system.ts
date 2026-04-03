/**
 * design-system/color-system.ts
 * ──────────────────────────────
 * PRISMA Color System — TypeScript module for runtime color injection.
 *
 * Source: colorsxstudios.com premium-patterns "gradient-design, clip-path-shapes"
 *         — color identity is injected at runtime into CSS variables, allowing
 *           the entire UI to respond to a film's chromatic identity.
 *
 * Slugs and hex values match exactly those in src/lib/color/colorPalette.ts.
 */

// ─── Types ────────────────────────────────────────────────────────────────────

export type PrismaColorSlug =
  | 'rojo_pasional'
  | 'naranja_apocaliptico'
  | 'ambar_desertico'
  | 'amarillo_ludico'
  | 'verde_lima'
  | 'verde_esmeralda'
  | 'verde_distopico'
  | 'cian_melancolico'
  | 'azul_nocturno'
  | 'violeta_cinetico'
  | 'purpura_onirico'
  | 'magenta_pop'
  | 'blanco_polar'
  | 'negro_abismo'
  | 'titanio_mecanico'
  | 'rosa_pastel'
  | 'claroscuro_dramatico'
  | 'monocromatico_intimo';

export interface PrismaColorEntry {
  slug: PrismaColorSlug;
  hex: string;
  name: string;
  /** True if the color is light enough to need dark text on top of it */
  light: boolean;
}

// ─── Color Map ────────────────────────────────────────────────────────────────

/**
 * All 18 PRISMA iconic colors.
 * Hex values match src/lib/color/colorPalette.ts exactly.
 */
export const PRISMA_COLORS: Record<PrismaColorSlug, PrismaColorEntry> = {
  rojo_pasional:         { slug: 'rojo_pasional',         hex: '#8E1B1B', name: 'Rojo Pasional',        light: false },
  naranja_apocaliptico:  { slug: 'naranja_apocaliptico',  hex: '#C4471D', name: 'Naranja Apocalíptico',  light: false },
  ambar_desertico:       { slug: 'ambar_desertico',       hex: '#C98A2E', name: 'Ámbar Desértico',       light: false },
  amarillo_ludico:       { slug: 'amarillo_ludico',       hex: '#F2C94C', name: 'Amarillo Lúdico',       light: true  },
  verde_lima:            { slug: 'verde_lima',            hex: '#7BC96F', name: 'Verde Lima',             light: true  },
  verde_esmeralda:       { slug: 'verde_esmeralda',       hex: '#1F7A5C', name: 'Verde Esmeralda',        light: false },
  verde_distopico:       { slug: 'verde_distopico',       hex: '#2F4F3E', name: 'Verde Distópico',        light: false },
  cian_melancolico:      { slug: 'cian_melancolico',      hex: '#4A7C8C', name: 'Cian Melancólico',       light: false },
  azul_nocturno:         { slug: 'azul_nocturno',         hex: '#1B2A41', name: 'Azul Nocturno',          light: false },
  violeta_cinetico:      { slug: 'violeta_cinetico',      hex: '#5B3FA4', name: 'Violeta Cinético',       light: false },
  purpura_onirico:       { slug: 'purpura_onirico',       hex: '#7A3E6D', name: 'Púrpura Onírico',        light: false },
  magenta_pop:           { slug: 'magenta_pop',           hex: '#D63384', name: 'Magenta Pop',            light: false },
  blanco_polar:          { slug: 'blanco_polar',          hex: '#E8EEF2', name: 'Blanco Polar',           light: true  },
  negro_abismo:          { slug: 'negro_abismo',          hex: '#0A0A0F', name: 'Negro Abismo',           light: false },
  titanio_mecanico:      { slug: 'titanio_mecanico',      hex: '#8A9199', name: 'Titanio Mecánico',       light: false },
  rosa_pastel:           { slug: 'rosa_pastel',           hex: '#F4A7B9', name: 'Rosa Pastel',            light: true  },
  claroscuro_dramatico:  { slug: 'claroscuro_dramatico',  hex: '#1A1A1A', name: 'Claroscuro Dramático',   light: false },
  monocromatico_intimo:  { slug: 'monocromatico_intimo',  hex: '#4A4A4A', name: 'Monocromático Íntimo',   light: false },
};

// ─── Color Activation ─────────────────────────────────────────────────────────

/**
 * Injects a PRISMA color into :root CSS variables, making the entire UI
 * respond to a film's chromatic identity.
 *
 * Sets:
 *   --prisma-color         → raw hex
 *   --prisma-color-light   → '1' or '0' flag for text contrast decisions
 *
 * All derived variables (--prisma-color-mid, --prisma-color-glow, etc.)
 * are computed automatically via color-mix() in tokens.css.
 *
 * Source: colorsxstudios.com "gradient-design, clip-path-shapes, color injection"
 */
export function activatePrismaColor(slug: PrismaColorSlug | string): void {
  if (typeof document === 'undefined') return;

  const entry = PRISMA_COLORS[slug as PrismaColorSlug];
  if (!entry) {
    console.warn(`[PRISMA] Unknown color slug: "${slug}" — falling back to azul_nocturno`);
    activatePrismaColor('azul_nocturno');
    return;
  }

  const root = document.documentElement;
  root.style.setProperty('--prisma-color', entry.hex);
  root.style.setProperty('--prisma-color-light', entry.light ? '1' : '0');
}

/**
 * Reset to the default PRISMA color (azul_nocturno).
 */
export function resetPrismaColor(): void {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  root.style.removeProperty('--prisma-color');
  root.style.removeProperty('--prisma-color-light');
}

/**
 * Get a color entry by slug. Returns null if not found.
 */
export function getPrismaColor(slug: string): PrismaColorEntry | null {
  return PRISMA_COLORS[slug as PrismaColorSlug] ?? null;
}

// ─── Reveal Animations ────────────────────────────────────────────────────────

/**
 * Initialize scroll-based reveal animations for all .reveal elements.
 *
 * Adds `is-visible` class when an element enters the viewport.
 * Supports `data-delay` attribute for staggered entrances.
 *
 * Source: a24films.com "scroll-reveal, simultaneous timing, 5 delayed elements"
 *         lecinemaclub.com "css-keyframe-animations, 7 elements with delay"
 *
 * Usage:
 *   <div class="reveal" data-delay="100">…</div>
 *   initRevealAnimations();
 */
export function initRevealAnimations(
  rootMargin = '0px 0px -60px 0px',
  threshold = 0.1,
): () => void {
  if (typeof IntersectionObserver === 'undefined') {
    // SSR / no-JS: show everything
    document.querySelectorAll<HTMLElement>('.reveal').forEach((el) => {
      el.classList.add('is-visible');
    });
    return () => {};
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target as HTMLElement;

        const delay = el.dataset.delay;
        if (delay) {
          el.style.setProperty('--reveal-delay', `${delay}ms`);
        }

        el.classList.add('is-visible');
        observer.unobserve(el);
      });
    },
    { rootMargin, threshold },
  );

  const elements = document.querySelectorAll<HTMLElement>('.reveal');
  elements.forEach((el) => observer.observe(el));

  // Return cleanup function
  return () => observer.disconnect();
}

/**
 * Apply staggered delays to a list of sibling .reveal elements.
 * Call after inserting elements into the DOM.
 *
 * @param container  Parent element containing .reveal children
 * @param step       Delay increment in ms (default 80ms — A24 "simultaneous" feel)
 */
export function staggerReveal(container: Element, step = 80): void {
  const items = container.querySelectorAll<HTMLElement>('.reveal');
  items.forEach((el, i) => {
    el.dataset.delay = String(i * step);
  });
}
