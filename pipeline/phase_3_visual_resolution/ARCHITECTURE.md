# Prisma Phase 3: Architecture Overview

## System Context

Phase 3 sits at the **final deterministic layer** of Prisma's film visual identity resolution system.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRISMA VISUAL IDENTITY SYSTEM                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DOCTRINE LAYER (Fixed, Immutable)                             │
│  ├─ 12 Canonical colors + monochromatic modes                 │
│  └─ Doctrine constrains ALL downstream decisions              │
│                                                                 │
│  EVIDENCE LAYER (Curated, Versioned)                           │
│  ├─ Authoritative film color assignments                      │
│  ├─ Prioritized in resolution hierarchy                       │
│  └─ v1.0, v2.0, v3.0+ versions supported                      │
│                                                                 │
│  PHASE 2A: AI REASONING                                        │
│  ├─ Analyzes film frames + metadata                           │
│  ├─ Produces color_assignment + confidence                    │
│  └─ Used as fallback when Evidence absent                     │
│                                                                 │
│  PHASE 2B: CULTURAL WEIGHT                                     │
│  ├─ Aggregates festival, critical, award signals             │
│  ├─ Produces 0–100 cultural score                            │
│  └─ Feeds into confidence calculations                        │
│                                                                 │
│  PHASE 2C/2D: EXTERNAL RESEARCH                                │
│  ├─ Gemini-powered research on demand                         │
│  ├─ HIGH/MODERATE/LOW quality grades                          │
│  └─ Findings map to Doctrine vocabulary                       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐
│  │  PHASE 3: VISUAL RESOLUTION (YOU ARE HERE)                │
│  ├───────────────────────────────────────────────────────────┤
│  │  INPUT:  Phase 2A + 2B + 2C/2D outputs + Evidence         │
│  │  RULES:  6 explicit deterministic rules                   │
│  │  OUTPUT: 7 final UX-facing fields                         │
│  └───────────────────────────────────────────────────────────┘
│
│  DOWNSTREAM (Post-Phase 3)
│  ├─ Tier Assignment (canon/core/strong/peripheral)
│  ├─ UI Template Selection
│  ├─ Search & Filtering
│  └─ Public API Response
│
└─────────────────────────────────────────────────────────────────┘
```

## Phase 3 Data Flow

```
Phase 2A Output          Phase 2B Output          Phase 2C/2D Output
(color_assignment)       (cultural_weight)       (external_research)
      │                         │                        │
      └─────────────────────────┼────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Adapters Layer      │
                    │  (normalize inputs)   │
                    └───────────┬───────────┘
                                │
         Evidence Coverage      │
              │                 │
              └────────┬────────┘
                       │
            ┌──────────▼──────────┐
            │  Resolver Engine    │
            │  (6 rules applied)  │
            └──────────┬──────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    Rule 1        Rule 2-3         Rules 4-6
   (Iconic)    (Rank, Secondary)  (Temp, Rhythm, Abst)
        │              │              │
        └──────────────┼──────────────┘
                       │
            ┌──────────▼──────────┐
            │  Validation Layer   │
            │  (schema checks)    │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │   Output Schema     │
            │ (VisualIdentity)    │
            └────────────────────┘
```

## Resolution Priority Hierarchy

When determining the iconic color, Phase 3 follows strict priority:

```
1. EVIDENCE LAYER (if has color assignment)
   └─ Authority Score: 0.95 (highest)
   └─ Rationale: Editorial curation, versioned, authoritative

2. EXTERNAL RESEARCH (if exists and quality ≥ MODERATE)
   └─ Authority Score: 0.55–0.70 (based on quality)
   └─ Rationale: Contextual enrichment, sourced perspectives

3. AI REASONING (fallback)
   └─ Authority Score: 0.50–0.75 (based on confidence)
   └─ Rationale: Frame analysis + metadata inference

If all sources conflict:
   └─ Lower color_rank to document uncertainty
   └─ Select color with broadest support
   └─ Flag uncertainty_flags in downstream systems
```

## Confidence Rank Calculation

```
Base Score (source priority):
┌─────────────────────────────────────────────────────┐
│ Evidence Exists & Decisive        → 0.95             │
│ AI Confidence > 0.80               → 0.75             │
│ External Research: HIGH quality   → 0.70             │
│ External Research: MODERATE       → 0.55             │
│ External Research: LOW quality    → 0.40             │
│ Doctrine Only                      → 0.50             │
└─────────────────────────────────────────────────────┘

Adjustments (cumulative, bounded [0.0, 1.0]):
┌─────────────────────────────────────────────────────┐
│ Conflicting perspectives in research  → -0.15        │
│ Only TERTIARY sources available      → -0.10        │
│ Multiple sources agree (3+)           → +0.10        │
│ PRIMARY source direct support         → +0.10        │
│ Non-English cinema context            → +0.05        │
└─────────────────────────────────────────────────────┘

Final Score = max(0.0, min(1.0, base + adjustments))
```

## Six Resolution Rules (Simplified)

```
RULE 1: Select Iconic Color
├─ Check Evidence → if exists, use it
├─ Else check External Research → extract from findings
└─ Else use AI reasoning primary color

RULE 2: Calculate Color Rank
├─ Start with base score (source hierarchy)
├─ Apply adjustments (conflicts, sources, agreement)
└─ Bound result to [0.0, 1.0]

RULE 3: Select Secondary Colors
├─ Gather candidates from Evidence, AI, Research
├─ Rank by authority score
└─ Return top 3 (exclude iconic color)

RULE 4: Infer Emotional Temperature
├─ Scan research findings for emotion keywords
├─ Map to one of 5 temperature categories
└─ Default to neutral_contemplativo if no research

RULE 5: Infer Visual Rhythm
├─ Scan research findings for pacing keywords
├─ Map to one of 5 rhythm categories
└─ Default to moderado_balanceado if no research

RULE 6: Infer Abstraction Level
├─ Scan research findings for style keywords
├─ Map to one of 5 abstraction categories
└─ Default to estilizado if no research
```

## Output Enums (Closed, No Free Text)

```
TemperaturaEmocional (5 values):
├─ calido_apasionado       (passion, intensity, fire)
├─ calido_nostalgico       (warmth, memory, golden)
├─ neutral_contemplativo   (balance, stability, calm)
├─ frio_melancolico        (sadness, introspection)
└─ frio_alienado           (isolation, distance)

RitmoVisual (5 values):
├─ dinamico_frenético      (chaotic, kinetic, rushed)
├─ dinamico_energético     (vibrant, active, sharp)
├─ moderado_balanceado     (steady, measured, even)
├─ lento_contemplativo     (slow, meditative, long takes)
└─ estático_meditativo     (still, frozen, minimal)

GradoAbstraccionVisual (5 values):
├─ extremadamente_realista (documentary, observational)
├─ realista_con_estilizacion (subtle stylization)
├─ estilizado              (deliberate artistic style)
├─ muy_estilizado          (heightened, theatrical)
└─ extremadamente_abstracto (symbolic, surreal, abstract)
```

## Constraints & Guarantees

```
GUARANTEES:
✓ Same inputs always produce same outputs
✓ All outputs are within schema bounds
✓ No external API calls
✓ No data persistence or side effects
✓ All fields always present (no optionals)
✓ No color assignment (only fields)

CONSTRAINTS:
✗ Cannot override Doctrine
✗ Cannot assign colors
✗ Cannot use Evidence directly (reads via adapters)
✗ Cannot cache results
✗ Cannot learn or adapt between calls
✗ Cannot reduce conflict plurality
```

## Testing Strategy

```
DRY-RUN TEST (pipeline/tests/test_phase_3_visual_resolution_dry_run.py)

Test Case 1: Evidence Decisive
├─ Input: Evidence has color assignment
├─ Expected: color_rank ≈ 0.95–1.0
└─ Status: ✓ PASS

Test Case 2: High-Quality Research
├─ Input: PRIMARY + SECONDARY sources, no conflicts
├─ Expected: color_rank ≈ 0.70–0.85
└─ Status: ✓ PASS

Test Case 3: Low-Quality Research
├─ Input: TERTIARY sources only
├─ Expected: color_rank ≈ 0.35–0.40
└─ Status: ✓ PASS

Test Case 4: AI Only
├─ Input: No Evidence, no Research
├─ Expected: color_rank ≈ 0.60–0.75
└─ Status: ✓ PASS

All outputs: Human-readable JSON, no assertions (dry-run)
```

## Extending Phase 3 (NOT IMPLEMENTED)

Post-Phase 3 systems can extend using output fields:

```
Tier Assignment System
├─ Uses: color_rank, color_iconico
├─ Logic: color_rank ≥ 0.95 → canon, etc.
└─ Output: tier assignment

UI Template Selection
├─ Uses: temperatura_emocional, ritmo_visual
├─ Logic: Select template matching emotional profile
└─ Output: UI template ID

Color Palette Generator
├─ Uses: color_iconico, colores_secundarios
├─ Logic: Generate complementary palette
└─ Output: Complete color palette

Search & Filtering
├─ Uses: grado_abstraccion_visual, temperatura_emocional
├─ Logic: Index on enum values
└─ Output: Faceted search
```

All extensions are **independent of Phase 3** and can evolve without changing resolution logic.

## Version History

```
v1.0 (2026-02-06)
├─ Initial complete implementation
├─ All 6 rules implemented
├─ Schema with full validation
├─ Dry-run tests passing
└─ FROZEN for production
```

---

**System Design:** Deterministic, auditable, rule-based  
**Philosophy:** Doctrine > Evidence > External Research > AI  
**Scope:** UX field production ONLY  
**Authority:** Final UX contract for visual identity
