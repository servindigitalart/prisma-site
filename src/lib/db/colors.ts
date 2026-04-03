/**
 * src/lib/db/colors.ts
 * ─────────────────────
 * Functions for color-related data.
 *
 * Color doctrine (the 17 canonical colors) is embedded directly as TypeScript
 * constants — NOT read from the filesystem — so it works on Vercel where the
 * pipeline/ directory is not deployed.
 *
 * Color-to-film assignments are fetched from Supabase via works.ts.
 */

import type { PrismaColorId, WorkCard } from "./types";
import { getWorksByColorTiered } from "./works";

// ─── Doctrine types ───────────────────────────────────────────────────────────

export interface ColorDoctrineEntry {
  id: PrismaColorId;
  hex: string;
  name: string;
  moods: string[];
  genre_associations: string[];
  cinematographer_signatures: string[];
  reference_examples: string[];
  cultural_context: string;
  cinematographic_notes: string;
}

export interface ColorDoctrine {
  version: string;
  last_updated: string;
  principles: Record<string, string>;
  colors: ColorDoctrineEntry[];
}

// ─── Embedded color doctrine (v1.2) ──────────────────────────────────────────
// Source: pipeline/doctrine/v1.1/color_doctrine.json
// Embedded here so the data is available on Vercel without filesystem access.

const EMBEDDED_DOCTRINE: ColorDoctrine = {
  version: "1.2",
  last_updated: "2026-02-24",
  principles: {
    cultural_memory_over_pixels:
      "Color identity is determined by collective cultural memory and cinematographic intent, not by pixel dominance or frame frequency.",
    one_film_one_color:
      "A film can never be canonically associated with more than one primary color. The color identity is singular and defining.",
    ai_informs_editors_decide:
      "AI analysis provides reasoning and validation, but editorial judgment always has final authority over color assignments.",
    monochrome_is_editorial:
      "Monochromatic mode assignment (claroscuro_dramatico vs monocromatico_intimo) is an editorial decision based on cinematographic style, not chromatic analysis.",
    examples_are_illustrative:
      "All film examples in this doctrine are illustrative references only. They are non-exclusive, non-canonical, and not assignments. No film may appear as a reference example for more than one color.",
  },
  colors: [
    {
      id: "rojo_pasional" as PrismaColorId,
      hex: "#8E1B1B",
      name: "Rojo Pasional",
      moods: ["passion", "violence", "desire", "intensity", "danger"],
      genre_associations: ["thriller", "melodrama", "horror", "romance"],
      cinematographer_signatures: ["Vittorio Storaro", "Dante Spinotti"],
      reference_examples: ["The Conformist", "Suspiria"],
      cultural_context: "Blood, love, revolution, emotional extremity",
      cinematographic_notes:
        "Associated with intense emotional states, bloodshed, desire, and moments of dramatic revelation",
    },
    {
      id: "naranja_apocaliptico" as PrismaColorId,
      hex: "#C4471D",
      name: "Naranja Apocalíptico",
      moods: ["chaos", "heat", "collapse", "aggression", "survival"],
      genre_associations: ["action", "war", "dystopian_sci_fi"],
      cinematographer_signatures: ["Roger Deakins"],
      reference_examples: ["Mad Max: Fury Road", "Apocalypse Now"],
      cultural_context: "Fire, desert warfare, end-of-world imagery",
      cinematographic_notes:
        "Explosive energy, desert heat, civilizational collapse, kinetic warfare",
    },
    {
      id: "ambar_desertico" as PrismaColorId,
      hex: "#C98A2E",
      name: "Ámbar Desértico",
      moods: ["nostalgia", "decay", "isolation", "warmth", "memory"],
      genre_associations: ["western", "period_drama"],
      cinematographer_signatures: ["Roger Deakins", "Rodrigo Prieto"],
      reference_examples: ["No Country for Old Men", "Lawrence of Arabia"],
      cultural_context: "Frontier mythology, faded sunlight, dust",
      cinematographic_notes:
        "Golden hour light in arid landscapes, temporal distance, weathered textures",
    },
    {
      id: "amarillo_ludico" as PrismaColorId,
      hex: "#F2C94C",
      name: "Amarillo Lúdico",
      moods: ["joy", "whimsy", "innocence", "optimism"],
      genre_associations: ["comedy", "coming_of_age"],
      cinematographer_signatures: ["Bruno Delbonnel"],
      reference_examples: ["Amélie", "Little Miss Sunshine"],
      cultural_context: "Playfulness, childhood, imagination",
      cinematographic_notes:
        "Bright, saturated palettes expressing joy, curiosity, and youthful energy",
    },
    {
      id: "verde_lima" as PrismaColorId,
      hex: "#7BC96F",
      name: "Verde Lima",
      moods: ["vitality", "youth", "nature", "renewal"],
      genre_associations: ["naturalistic_drama", "coming_of_age"],
      cinematographer_signatures: ["Emmanuel Lubezki"],
      reference_examples: ["The Tree of Life", "Call Me By Your Name"],
      cultural_context: "Natural light, growth, countryside",
      cinematographic_notes:
        "Organic, sun-dappled environments, pastoral beauty, life force",
    },
    {
      id: "verde_esmeralda" as PrismaColorId,
      hex: "#1F7A5C",
      name: "Verde Esmeralda",
      moods: ["elegance", "mystery", "depth", "refinement"],
      genre_associations: ["mystery", "period_drama"],
      cinematographer_signatures: ["Robert Yeoman"],
      reference_examples: ["Vertigo", "Solo con tu pareja"],
      cultural_context: "Jewel tones, opulence, hidden worlds",
      cinematographic_notes:
        "Rich, saturated greens suggesting luxury, obsession, or concealed truth",
    },
    {
      id: "verde_distopico" as PrismaColorId,
      hex: "#2F4F3E",
      name: "Verde Distópico",
      moods: ["decay", "surveillance", "toxicity", "oppression"],
      genre_associations: ["dystopia", "sci_fi"],
      cinematographer_signatures: ["Jordan Cronenweth"],
      reference_examples: ["The Matrix", "Alien"],
      cultural_context: "Control systems, night vision, industrial fear",
      cinematographic_notes:
        "Sickly, artificial greens associated with technological dread and systemic control",
    },
    {
      id: "cian_melancolico" as PrismaColorId,
      hex: "#4A7C8C",
      name: "Cian Melancólico",
      moods: ["loneliness", "rain", "contemplation"],
      genre_associations: ["drama", "arthouse"],
      cinematographer_signatures: ["Harris Savides"],
      reference_examples: ["Lost in Translation"],
      cultural_context: "Urban melancholy, emotional distance",
      cinematographic_notes:
        "Cool, desaturated blues expressing isolation and quiet introspection",
    },
    {
      id: "azul_nocturno" as PrismaColorId,
      hex: "#1B2A41",
      name: "Azul Nocturno",
      moods: ["night", "mystery", "contemplation"],
      genre_associations: ["neo_noir", "sci_fi"],
      cinematographer_signatures: ["Jordan Cronenweth", "Roger Deakins"],
      reference_examples: ["Blade Runner"],
      cultural_context: "Neon nights, urban solitude",
      cinematographic_notes:
        "Deep, saturated blues of artificial night, rain-slicked streets, existential searching",
    },
    {
      id: "violeta_cinetico" as PrismaColorId,
      hex: "#5B3FA4",
      name: "Violeta Cinético",
      moods: ["energy", "neon", "surreal_motion"],
      genre_associations: ["sci_fi", "action"],
      cinematographer_signatures: ["Newton Thomas Sigel"],
      reference_examples: ["Mandy"],
      cultural_context: "Electric color, kinetic intensity",
      cinematographic_notes:
        "Vibrant, aggressive purples expressing heightened states and sensory overload",
    },
    {
      id: "purpura_onirico" as PrismaColorId,
      hex: "#7A3E6D",
      name: "Púrpura Onírico",
      moods: ["dreamlike", "romantic", "otherworldly"],
      genre_associations: ["romance", "surrealism"],
      cinematographer_signatures: ["Christopher Doyle"],
      reference_examples: ["Florida Project"],
      cultural_context: "Memory, longing, dream logic",
      cinematographic_notes:
        "Soft, suffused purples suggesting reverie, nostalgia, or liminal spaces",
    },
    {
      id: "magenta_pop" as PrismaColorId,
      hex: "#D63384",
      name: "Magenta Pop",
      moods: ["rebellion", "excess", "pop_energy"],
      genre_associations: ["music_films", "youth_culture"],
      cinematographer_signatures: ["Robert Richardson"],
      reference_examples: ["Barbie"],
      cultural_context: "Counterculture, maximalism",
      cinematographic_notes:
        "Bold, saturated magentas expressing defiance, spectacle, and cultural commentary",
    },
    {
      id: "blanco_polar" as PrismaColorId,
      hex: "#E8EEF2",
      name: "Blanco Polar",
      moods: ["isolation", "void", "clinical", "existential", "minimalism"],
      genre_associations: ["arthouse", "thriller", "drama", "psychological_horror"],
      cinematographer_signatures: ["Sven Nykvist", "Edward Lachman"],
      reference_examples: ["Three Colors: White", "Fargo"],
      cultural_context:
        "Moral void, institutional coldness, existential emptiness, winter isolation",
      cinematographic_notes:
        "Cold white environments suggesting absence, clinical detachment, or blankness of extreme moral situations",
    },
    {
      id: "negro_abismo" as PrismaColorId,
      hex: "#0A0A0F",
      name: "Negro Abismo",
      moods: ["darkness", "gothic", "void", "power", "menace"],
      genre_associations: ["superhero", "noir", "gothic", "thriller"],
      cinematographer_signatures: ["Gordon Willis", "Bruno Delbonnel"],
      reference_examples: ["Batman (1989)", "Se7en"],
      cultural_context: "Gotham darkness, gothic menace, total visual void, noir extremity",
      cinematographic_notes:
        "Near-total darkness as aesthetic choice, silhouettes, gothic architecture consumed by shadow",
    },
    {
      id: "titanio_mecanico" as PrismaColorId,
      hex: "#8A9199",
      name: "Titanio Mecánico",
      moods: ["mechanical", "cold_future", "industrial", "artificial", "inhuman"],
      genre_associations: ["sci_fi", "dystopia", "cyberpunk", "action"],
      cinematographer_signatures: ["Douglas Trumbull", "Roger Deakins"],
      reference_examples: ["Terminator 2", "2001: A Space Odyssey", "Ex Machina"],
      cultural_context:
        "Metal bodies, spacecraft interiors, artificial intelligence, industrial dystopia",
      cinematographic_notes:
        "Cold metallic grays of machines, robots, and spacecraft — technology as overwhelming physical presence",
    },
    // Monochromatic modes (editorial, not chromatic)
    {
      id: "claroscuro_dramatico" as PrismaColorId,
      hex: "#1A1A1A",
      name: "Claroscuro Dramático",
      moods: ["dramatic", "expressionist", "theatrical", "timeless", "stark"],
      genre_associations: ["noir", "thriller", "drama", "horror"],
      cinematographer_signatures: [],
      reference_examples: [],
      cultural_context: "Film noir, German expressionism, high-contrast photography",
      cinematographic_notes:
        "Deep blacks, harsh shadows, chiaroscuro lighting, expressionist influence, sculptural faces",
    },
    {
      id: "monocromatico_intimo" as PrismaColorId,
      hex: "#4A4A4A",
      name: "Monocromático Íntimo",
      moods: ["intimate", "contemplative", "lyrical", "humanistic", "tender"],
      genre_associations: ["drama", "romance", "character_study", "documentary"],
      cinematographer_signatures: [],
      reference_examples: [],
      cultural_context: "Italian neorealism, French New Wave, naturalistic photography",
      cinematographic_notes:
        "Soft grays, gentle lighting, natural textures, documentary realism, emotional proximity",
    },
  ],
};

/**
 * Returns the embedded color doctrine singleton.
 * No filesystem access — safe for Vercel and all edge environments.
 */
export function loadColorDoctrine(): ColorDoctrine {
  return EMBEDDED_DOCTRINE;
}

/**
 * Returns the doctrine entry for a specific color ID.
 * Returns null if the color ID is not found in the doctrine.
 */
export function getColorProfile(
  colorId: string
): ColorDoctrineEntry | null {
  return loadColorDoctrine().colors.find((c) => c.id === colorId) ?? null;
}

/**
 * Returns all color doctrine entries (chromatic + monochromatic modes).
 * Used by /colors/[slug] static paths and color index pages.
 */
export function getAllColorProfiles(): ColorDoctrineEntry[] {
  return loadColorDoctrine().colors;
}

/**
 * Returns all valid color IDs from the doctrine.
 * Includes monochromatic modes (already embedded in the doctrine).
 */
export function getAllColorIds(): PrismaColorId[] {
  return getAllColorProfiles().map((c) => c.id) as PrismaColorId[];
}

// ─── Color page data (doctrine + tiered films) ───────────────────────────────

export interface ColorPageData {
  doctrine: ColorDoctrineEntry;
  films: {
    canon: WorkCard[];
    core: WorkCard[];
    strong: WorkCard[];
    peripheral: WorkCard[];
  };
}

/**
 * Aggregates everything needed to render a color page:
 * - Doctrine entry (hex, name, moods, etc.)
 * - Films grouped by tier (from Supabase)
 *
 * Returns null if the color ID is not found in doctrine.
 */
export async function getColorPageData(
  colorId: string
): Promise<ColorPageData | null> {
  const doctrine = getColorProfile(colorId);
  if (!doctrine) return null;

  const films = await getWorksByColorTiered(colorId as PrismaColorId);

  return { doctrine, films };
}
