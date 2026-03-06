/**
 * src/lib/color/colorPalette.ts
 * ─────────────────────────────
 * Static Prisma palette map — hex values and display names.
 * Sourced from doctrine v1.2. Used for CSS, rendering, and UI.
 */

export interface PaletteEntry {
  id: string;
  hex: string;
  name: string;
  cssVar: string; // e.g. var(--color-rojo-pasional)
}

export const PRISMA_PALETTE: Record<string, PaletteEntry> = {
  rojo_pasional:         { id: 'rojo_pasional',         hex: '#8E1B1B', name: 'Rojo Pasional',        cssVar: 'var(--color-rojo-pasional)' },
  naranja_apocaliptico:  { id: 'naranja_apocaliptico',  hex: '#C4471D', name: 'Naranja Apocalíptico',  cssVar: 'var(--color-naranja-apocaliptico)' },
  ambar_desertico:       { id: 'ambar_desertico',       hex: '#C98A2E', name: 'Ámbar Desértico',       cssVar: 'var(--color-ambar-desertico)' },
  amarillo_ludico:       { id: 'amarillo_ludico',       hex: '#F2C94C', name: 'Amarillo Lúdico',       cssVar: 'var(--color-amarillo-ludico)' },
  verde_lima:            { id: 'verde_lima',            hex: '#7BC96F', name: 'Verde Lima',             cssVar: 'var(--color-verde-lima)' },
  verde_esmeralda:       { id: 'verde_esmeralda',       hex: '#1F7A5C', name: 'Verde Esmeralda',        cssVar: 'var(--color-verde-esmeralda)' },
  verde_distopico:       { id: 'verde_distopico',       hex: '#2F4F3E', name: 'Verde Distópico',        cssVar: 'var(--color-verde-distopico)' },
  cian_melancolico:      { id: 'cian_melancolico',      hex: '#4A7C8C', name: 'Cian Melancólico',       cssVar: 'var(--color-cian-melancolico)' },
  azul_nocturno:         { id: 'azul_nocturno',         hex: '#1B2A41', name: 'Azul Nocturno',          cssVar: 'var(--color-azul-nocturno)' },
  violeta_cinetico:      { id: 'violeta_cinetico',      hex: '#5B3FA4', name: 'Violeta Cinético',       cssVar: 'var(--color-violeta-cinetico)' },
  purpura_onirico:       { id: 'purpura_onirico',       hex: '#7A3E6D', name: 'Púrpura Onírico',        cssVar: 'var(--color-purpura-onirico)' },
  magenta_pop:           { id: 'magenta_pop',           hex: '#D63384', name: 'Magenta Pop',            cssVar: 'var(--color-magenta-pop)' },
  blanco_polar:          { id: 'blanco_polar',          hex: '#E8EEF2', name: 'Blanco Polar',           cssVar: 'var(--color-blanco-polar)' },
  negro_abismo:          { id: 'negro_abismo',          hex: '#0A0A0F', name: 'Negro Abismo',           cssVar: 'var(--color-negro-abismo)' },
  titanio_mecanico:      { id: 'titanio_mecanico',      hex: '#8A9199', name: 'Titanio Mecánico',       cssVar: 'var(--color-titanio-mecanico)' },
  rosa_pastel:           { id: 'rosa_pastel',           hex: '#F4A7B9', name: 'Rosa Pastel',            cssVar: 'var(--color-rosa-pastel)' },
  claroscuro_dramatico:  { id: 'claroscuro_dramatico',  hex: '#1A1A1A', name: 'Claroscuro Dramático',   cssVar: 'var(--color-claroscuro-dramatico)' },
  monocromatico_intimo:  { id: 'monocromatico_intimo',  hex: '#4A4A4A', name: 'Monocromático Íntimo',   cssVar: 'var(--color-monocromatico-intimo)' },
};

/**
 * Returns the palette entry for a color ID, or null if not found.
 */
export function getPaletteEntry(colorId: string): PaletteEntry | null {
  return PRISMA_PALETTE[colorId] ?? null;
}

/**
 * Returns the hex value for a color ID, falling back to a neutral gray.
 */
export function getColorHex(colorId: string): string {
  return PRISMA_PALETTE[colorId]?.hex ?? '#4A4A4A';
}

/**
 * Returns true if the color is "light" (needs dark text on it).
 * Used to decide text color on colored backgrounds.
 */
export function isLightColor(colorId: string): boolean {
  const LIGHT_COLORS = new Set(['amarillo_ludico', 'verde_lima', 'blanco_polar', 'rosa_pastel']);
  return LIGHT_COLORS.has(colorId);
}

/**
 * Returns a role display label.
 */
export function formatRole(role: string): string {
  const map: Record<string, string> = {
    director:          'Director',
    cinematography:    'Cinematography',
    actor:             'Cast',
    writer:            'Writer',
    editor:            'Editor',
    composer:          'Composer',
    production_design: 'Production Design',
  };
  return map[role] ?? role;
}
