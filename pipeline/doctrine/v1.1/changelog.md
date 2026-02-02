# Doctrine Changelog

## v1.1 (2026-02-02)

### Doctrinal Correction: Recanonization of Prisma Color Palette

This version corrects the color doctrine to align with Prisma's core editorial philosophy.

**CRITICAL CHANGES:**

**Color Palette Replaced**
- Removed generic 12-color palette from v1.0
- Replaced with canonical Prisma editorial palette:
  - Rojo Pasional, Naranja Apocalíptico, Ámbar Desértico
  - Amarillo Lúdico, Verde Lima, Verde Esmeralda, Verde Distópico
  - Cian Melancólico, Azul Nocturno
  - Violeta Cinético, Púrpura Onírico, Magenta Pop
- Each color now includes cinematographer signatures and cultural context
- Reference examples are illustrative only, not canonical assignments

**Assignment Rules Corrected**
- Removed frame dominance logic (pixel frequency, numeric thresholds)
- Established decision hierarchy: cultural memory → cinematographic intent → narrative function → genre associations
- Frame analysis role demoted to validation only
- AI explicitly prohibited from using pixel dominance or frame frequency
- Editorial override explicitly declared as absolute authority

**New Top-Level Principles**
Added `principles` key defining Prisma's foundational doctrine:
- Cultural memory over pixel data
- One film → one dominant color identity
- AI informs, editors decide
- Monochrome is editorial, not chromatic
- Examples are illustrative, never canonical

**Monochromatic Modes**
- Retained claroscuro_dramatico and monocromatico_intimo (unchanged)
- Assignment logic now explicitly editorial, not chromatic

**Reference Examples**
- All examples marked as illustrative references only
- Examples are non-exclusive and non-canonical
- No film may appear as reference example for more than one color

### Philosophy

This correction restores Prisma's core editorial stance:

**Color identity is a curatorial act, not a computational output.**

The AI color agent exists to inform and validate editorial judgment, never to replace it. Frame analysis provides evidence but cannot decide meaning. Cultural memory and cinematographic intent always supersede pixel dominance.

### Migration Notes

- v1.0 color IDs no longer valid (palette completely replaced)
- Any AI assignments from v1.0 must be re-evaluated against v1.1 palette
- Frame validators must be updated to flag contradictions only, not make decisions
- Editorial review required for all works assigned under v1.0 doctrine

### Unchanged from v1.0

- score_doctrine.json (scoring formula, tier thresholds, cultural weight signals)
- tier_doctrine.json (tier definitions, ranking rules, UI guidelines)

---

## v1.0 (2026-02-02)

### Initial Release

**color_doctrine.json**
- Defined 12 Prisma colors with hex values, moods, and genre associations [REPLACED IN v1.1]
- Established 2 monochromatic modes (claroscuro_dramatico, monocromatico_intimo)
- Created assignment rules for primary/secondary colors and monochromatic detection [CORRECTED IN v1.1]
- Documented edge cases (color shift films, desaturated films, multi-segment films)

**score_doctrine.json**
- Defined weighted scoring formula:
  - AI confidence: 30%
  - Authorship: 25%
  - Cultural recognition: 30%
  - Popularity: 15%
- Established tier thresholds (canon: 95+, core: 85+, strong: 70+, peripheral: 50+)
- Created tier ranking rules (canon: editorial, core: hybrid, strong/peripheral: numeric)
- Documented cultural weight signals (festivals, critical canon, cinematography awards, arthouse distribution)
- Defined authorship signals (DP prestige, director visual style, production design)
- Established popularity normalization (log scale to prevent blockbuster bias)

**tier_doctrine.json**
- Defined 5 tiers (canon, core, strong, peripheral, uncertain)
- Created tier transition rules (promotion/demotion criteria)
- Established ranking methodology per tier
- Defined UI design guidelines for visual hierarchy

### Notes

This was the foundational doctrine release with architectural structure preserved in all future versions.
