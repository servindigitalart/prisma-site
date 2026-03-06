#!/usr/bin/env python3
"""
Phase 3 Resolution Rules

DETERMINISTIC RULE SET for mapping Phase 2 outputs to final visual fields.
All rules are explicit, auditable, and free of heuristics.

---

## RULE 1: SELECT ICONIC COLOR (color_iconico)

INPUT: Doctrine definitions, Evidence coverage, External Research findings

PROCESS:
1. Check Evidence layer:
   - If Evidence contains a color assignment with HIGH authority → use it directly
   - Note: Evidence is curated and authoritative

2. If Evidence is ambiguous or missing:
   - Check External Research findings
   - Look for cited mentions of color identity in PRIMARY/SECONDARY sources
   - Map mentioned aesthetics to Doctrine color definitions
   - Select the color whose definition MOST CLOSELY ALIGNS with findings
   - Note: This is alignment, not assignment

3. If no research findings exist:
   - Check AI reasoning color_assignment.primary.color_name
   - Use the highest-confidence color from reasoning

4. If all sources conflict:
   - Lower color_rank to reflect uncertainty (see Rule 2)
   - Select the color with the broadest support (most sources mention alignment)

RESULT: Exactly one Doctrine color ID

---

## RULE 2: CALCULATE CONFIDENCE RANK (color_rank, 0.0–1.0)

INPUT: Source authority, conflicts, research quality, evidence coverage

PROCESS:

Start with a base score depending on source hierarchy:

Evidence layer exists and decisive: base = 0.95
AI reasoning with HIGH confidence (>0.80): base = 0.75
External Research with HIGH quality: base = 0.70
External Research with MODERATE quality: base = 0.55
External Research with LOW quality: base = 0.40
Doctrine only (no evidence/research): base = 0.50

Apply ADJUSTMENTS (cumulative, floors at 0.0, ceilings at 1.0):

Presence of conflicting perspectives in research: -0.15
Only TERTIARY sources available: -0.10
Multiple independent sources agree: +0.10
PRIMARY source directly supports alignment: +0.10
Non-English cinema with strong cultural context: +0.05 (corrects for bias)
Director/DP known for consistent visual style: +0.05

RESULT: Numeric score 0.0–1.0

---

## RULE 3: SELECT SECONDARY COLORS (colores_secundarios, max 3)

INPUT: Evidence, External Research findings, AI reasoning alternatives

PROCESS:

1. Gather candidates:
   - From Evidence: any colors mentioned as supporting or contextual
   - From AI reasoning: color_assignment.alternates (top 2)
   - From External Research: secondary colors mentioned in findings

2. Rank candidates by authority:
   - Evidence mentions → score 0.90+
   - PRIMARY source mentions → score 0.70+
   - SECONDARY source mentions → score 0.50+
   - TERTIARY/AI only → score 0.30+

3. Select top 3 that are NOT the iconic color

4. Order by rank score descending

5. Cap at 3 colors max

RESULT: Ordered list of 0–3 Doctrine color IDs

---

## RULE 4: INFER EMOTIONAL TEMPERATURE (temperatura_emocional)

INPUT: External Research findings, Doctrine color definitions

PROCESS:

DO NOT infer from visual appearance alone.
DO infer from cited discourse about mood, tone, emotion.

Map findings to Doctrine color semantics:

If research/evidence describes:
  "passion", "intensity", "violence", "heat", "fire" → rojo_pasional → calido_apasionado
  "chaos", "dystopia", "apocalypse", "burn" → naranja_apocaliptico → calido_apasionado
  "warmth", "nostalgia", "memory", "desert", "golden" → ambar_desertico → calido_nostalgico
  "joy", "whimsy", "sunlight", "playfulness" → amarillo_ludico → calido_nostalgico

  "contemplation", "sadness", "rain", "solitude", "introspection" → azul_nocturno → frio_melancolico
  "alienation", "isolation", "distance", "void", "loss" → azul_nocturno → frio_alienado
  "darkness", "mystery", "noir", "depth", "night" → azul_nocturno → neutral_contemplativo

  "balance", "harmony", "stability", "earth" → verde_lima/verde_esmeralda → neutral_contemplativo
  "growth", "nature", "freshness", "renewal" → verde_lima → calido_nostalgico

  "surrealism", "energy", "80s", "neon" → violeta_cinetico/magenta_pop → dinamico_energético
  "dreams", "romance", "mystery", "intimacy" → purpura_onirico → neutral_contemplativo

If no research available:
  Default to neutral_contemplativo (safe, non-prescriptive)

RESULT: One emotion category

---

## RULE 5: INFER VISUAL RHYTHM (ritmo_visual)

INPUT: External Research findings about pacing, editing, cinematography

PROCESS:

Map cited characteristics to rhythm:

If research describes:
  "fast-paced", "kinetic", "frenetic", "rushed", "chaotic editing" → dinamico_frenético
  "energetic", "vibrant", "active", "dynamic", "sharp cuts" → dinamico_energético
  "steady", "measured", "balanced", "rhythmic", "moderate pacing" → moderado_balanceado
  "slow", "contemplative", "meditative", "long takes", "languid" → lento_contemplativo
  "static", "frozen", "still life", "minimal movement", "locked camera" → estático_meditativo

If no research describes pace/rhythm:
  Default to moderado_balanceado (neutral)

RESULT: One rhythm category

---

## RULE 6: INFER ABSTRACTION LEVEL (grado_abstraccion_visual)

INPUT: External Research findings about style, realism, stylization

PROCESS:

Map cited aesthetic characteristics to abstraction:

If research describes:
  "naturalistic", "documentary", "observational", "verite", "realistic" → extremadamente_realista
  "grounded realism", "minimal stylization", "subtle color work" → realista_con_estilizacion
  "stylized", "deliberate", "composed", "artistic approach" → estilizado
  "heightened", "theatrical", "exaggerated", "artificial", "expressionistic" → muy_estilizado
  "abstract", "non-representational", "symbolic", "dreamlike", "surreal" → extremadamente_abstracto

If no research describes style:
  Default to estilizado (middle ground)

RESULT: One abstraction category

---

## GENERAL PRINCIPLES

- NO color assignment ever happens in Phase 3
- Rules produce FIELDS, not conclusions
- If data is weak or ambiguous, LOWER the rank — do NOT guess
- If conflicts exist, DOCUMENT them by lowering rank, not by silencing them
- All adjustments are CUMULATIVE but bounded
- Rules are DETERMINISTIC: same inputs → same outputs
- Rules are AUDITABLE: each step can be traced
"""

# No implementation in this file — rules are documented above for clarity.
# Implementation is in resolver.py
