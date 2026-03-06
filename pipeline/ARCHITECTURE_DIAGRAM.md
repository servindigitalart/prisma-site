# Prisma Cultural Memory Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRISMA VISUAL IDENTITY SYSTEM                    │
│                    "How Films Live in Cultural Memory"                   │
└─────────────────────────────────────────────────────────────────────────┘

                                    INPUT
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │   Film Metadata (TMDB)   │
                        │  - Title, Year, Genres   │
                        │  - Director, Plot        │
                        └──────────────────────────┘
                                      │
                ┌─────────────────────┴─────────────────────┐
                │                                            │
                ▼                                            ▼
    ┌───────────────────────┐                  ┌───────────────────────┐
    │   PHASE 1: EVIDENCE   │                  │  PHASE 2: INFERENCE   │
    │   (Hard Authority)    │                  │  (Soft Authority)     │
    └───────────────────────┘                  └───────────────────────┘
                │                                            │
                │                              ┌─────────────┴─────────────┐
                │                              │                           │
                │                              ▼                           ▼
                │                  ┌────────────────────────┐  ┌──────────────────────┐
                │                  │ Phase 2: Cultural      │  │ Phase 2E: Genre      │
                │                  │ Memory (NEW!)          │  │ Conventions          │
                │                  │                        │  │ (Fallback)           │
                │                  │ "What color do people  │  │                      │
                │                  │  think of?"            │  │ "What color should   │
                │                  │                        │  │  this genre be?"     │
                │                  │ Sources:               │  │                      │
                │                  │ - Posters/Marketing    │  │ Sources:             │
                │                  │ - Cultural Impact      │  │ - Genre signals      │
                │                  │ - Popular Memory       │  │ - Conventions        │
                │                  │ - Letterboxd           │  │ - Defaults           │
                │                  │                        │  │                      │
                │                  │ Gemini LLM (Perception)│  │ Rule-based           │
                │                  └────────────────────────┘  └──────────────────────┘
                │                              │                           │
                └──────────────────────────────┴───────────────────────────┘
                                              │
                                              ▼
                              ┌──────────────────────────────┐
                              │   PHASE 3: RESOLUTION        │
                              │   (Authority Hierarchy)      │
                              │                              │
                              │  1. Hard Evidence    (0.95)  │
                              │  2. Cultural Memory  (0.85)  │◄── NEW!
                              │  3. Genre Fallback   (0.50)  │
                              └──────────────────────────────┘
                                              │
                                              ▼
                                         OUTPUT
                              ┌──────────────────────────────┐
                              │   Visual Identity Result     │
                              │   - color_iconico            │
                              │   - color_rank (confidence)  │
                              │   - colores_secundarios      │
                              │   - temperatura_emocional    │
                              │   - ritmo_visual             │
                              │   - grado_abstraccion        │
                              └──────────────────────────────┘
```

## Authority Hierarchy (Simplified)

### Before Cultural Memory
```
┌─────────────────────────┐
│ Evidence (0.95)         │ ◄── Highest (but rare)
├─────────────────────────┤
│ External Research (0.70)│
├─────────────────────────┤
│ Genre Conventions (0.55)│ ◄── Too strong! Wrong authority
├─────────────────────────┤
│ AI Reasoning (0.50)     │
└─────────────────────────┘

Result: The Matrix → RED (genre sci-fi defaults)
```

### After Cultural Memory
```
┌─────────────────────────┐
│ Evidence (0.95)         │ ◄── Highest (Letterboxd canonical)
├─────────────────────────┤
│ Cultural Memory (0.85)  │ ◄── NEW! Strong consensus ≥0.75
├─────────────────────────┤
│ Genre Conventions (0.55)│ ◄── Weakened to fallback
├─────────────────────────┤
│ AI Reasoning (0.50)     │
└─────────────────────────┘

Result: The Matrix → GREEN (cultural memory)
```

## Data Flow Example: The Matrix

```
INPUT: The Matrix (1999)
│
├─ Phase 1: Evidence Layer
│  └─ No canonical color assignment
│     → Pass to Phase 2
│
├─ Phase 2: Cultural Memory (NEW)
│  ├─ Prompt: "What color do people associate with The Matrix?"
│  ├─ Gemini analyzes:
│  │  • Marketing: Green "digital rain" code
│  │  • Posters: Dominant green tint
│  │  • Cultural impact: "Matrix green" is iconic
│  │  • Popular memory: Code sequences universally recognized
│  ├─ Result:
│  │  • iconic_color: "verde_acido"
│  │  • consensus_strength: 0.92
│  │  • reasoning: "The iconic digital rain code..."
│  └─ Consensus ≥ 0.75? YES → Use in Phase 3
│
├─ Phase 2E: Genre Conventions (Fallback)
│  ├─ Genres: ["Science Fiction", "Action"]
│  ├─ Signals: ["cyberpunk", "neon", "dystopia"]
│  └─ Would default to: "azul_profundo" or "rojo_pasion"
│     → NOT USED (Cultural Memory has stronger authority)
│
└─ Phase 3: Visual Resolution
   ├─ Authority Check:
   │  1. Evidence? NO
   │  2. Cultural Memory (≥0.75)? YES → Use verde_acido
   │  3. Genre fallback? NOT NEEDED
   │
   └─ OUTPUT:
      • color_iconico: "verde_acido" ✅
      • color_rank: 0.85
      • temperatura: "frio_alienado"
      • ritmo: "dinamico_frenético"
```

## Cultural Memory Perception Model

```
┌─────────────────────────────────────────────────────────────┐
│              CULTURAL MEMORY RESOLUTION                     │
│         "How does this film live in people's minds?"        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Gemini LLM      │
                    │  (Perception AI) │
                    └──────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
          ▼                                       ▼
┌─────────────────────┐              ┌─────────────────────┐
│ PRIMARY SOURCES     │              │ AVOID               │
│ (High Authority)    │              │ (Low Authority)     │
├─────────────────────┤              ├─────────────────────┤
│ • Posters           │              │ • Shot statistics   │
│ • Marketing         │              │ • Color theory      │
│ • Trailers          │              │ • Cinematography    │
│ • Cultural impact   │              │   interviews        │
│ • Letterboxd        │              │ • Academic analysis │
│ • Popular discourse │              │ • Frame extraction  │
│ • Memes/references  │              │                     │
└─────────────────────┘              └─────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ Perception Response          │
├──────────────────────────────┤
│ • iconic_color               │
│ • secondary_colors           │
│ • visual_rhythm              │
│ • color_temperature          │
│ • abstraction_level          │
│ • reasoning (why?)           │
│ • sources_cited (evidence)   │
└──────────────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ Consensus Strength           │
├──────────────────────────────┤
│ Base: 0.50                   │
│ + Clear color: +0.30         │
│ + Multiple sources: +0.20    │
│ + Marketing mention: +0.20   │
│ + Cultural impact: +0.20     │
│ ────────────────────         │
│ Total: 0.0 - 1.0             │
│                              │
│ Threshold: ≥ 0.75 = USE      │
└──────────────────────────────┘
```

## Consensus Strength Examples

```
┌─────────────────────┬──────────┬─────────────────────────────┐
│ Film                │ Strength │ Reasoning                   │
├─────────────────────┼──────────┼─────────────────────────────┤
│ Barbie              │   0.98   │ Hot pink marketing          │
│                     │          │ saturation, obvious         │
├─────────────────────┼──────────┼─────────────────────────────┤
│ The Matrix          │   0.92   │ Green "digital rain" iconic │
│                     │          │ in cultural memory          │
├─────────────────────┼──────────┼─────────────────────────────┤
│ Three Colors: Blue  │   0.95   │ Title explicitly mentions   │
│                     │          │ blue, visual motif          │
├─────────────────────┼──────────┼─────────────────────────────┤
│ Schindler's List    │   0.90   │ B&W cinematography          │
│                     │          │ universally known           │
├─────────────────────┼──────────┼─────────────────────────────┤
│ Generic Action Film │   0.45   │ No clear cultural memory,   │
│                     │          │ falls back to genre         │
└─────────────────────┴──────────┴─────────────────────────────┘
```

## Color Mapping

```
LLM Natural Language → Prisma Emotional Palette

"green", "digital green"  → verde_acido
"neon green", "acid"      → verde_acido
"emerald", "forest"       → verde_esperanza

"pink", "hot pink"        → rosa_melancolico  (FIXED!)
"magenta"                 → rosa_melancolico  (FIXED!)

"red", "passion"          → rojo_pasion
"crimson", "blood"        → rojo_pasion

"blue", "deep blue"       → azul_profundo
"cyan", "teal"            → azul_frio

"black and white"         → gris_industrial
"monochrome"              → gris_industrial

"yellow", "golden"        → ambar_dorado
"sepia", "amber"          → ambar_dorado
```

## Testing Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    TESTING PYRAMID                          │
└─────────────────────────────────────────────────────────────┘

                       ┌──────────┐
                       │   E2E    │  test_integration_matrix.py
                       │  Tests   │  (Full pipeline)
                       └──────────┘
                      ┌────────────┐
                      │ Canonical  │  test_cultural_memory_canonical.py
                      │   Suite    │  (7 ground truth films)
                      └────────────┘
                  ┌──────────────────┐
                  │   Unit Tests     │  (Individual components)
                  │   - Resolver     │
                  │   - Prompter     │
                  │   - Mapping      │
                  └──────────────────┘

Pass Criteria:
• Canonical Suite: ≥90% pass rate on obvious cases
• Integration Test: The Matrix → green with confidence ≥0.80
• Unit Tests: All components work in isolation
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────┐
│                  SYSTEM PERFORMANCE                         │
└─────────────────────────────────────────────────────────────┘

Latency:
• Cultural Memory Resolution: ~2-5 seconds (Gemini API call)
• Phase 3 Resolution: <100ms (deterministic rules)
• Total Added Latency: ~2-5 seconds per film

Cost:
• Gemini API (1.5 model): ~$0.001-0.003 per film
• 1000 films: ~$2.00
• Full catalog (10K): ~$20.00

Accuracy (Expected):
• Obvious cases (Barbie, Matrix): 95%+
• Clear marketing (blockbusters): 85%+
• Art house (subtle): 70%+
• Generic films: Falls back to genre

Cache Strategy (Future):
• Store cultural_memory results by TMDB ID
• TTL: 1 year (cultural memory stable)
• Invalidate on: Major re-release, remaster
```

---

## Key Innovation

**We now ask the RIGHT question:**

- ❌ OLD: "What color appears most in this film?"
- ✅ NEW: "What color do people think of when they hear the title?"

This shift from **technical analysis** to **cultural perception** is the core architectural breakthrough.

---

See Also:
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)
- [Integration Guide](./phase_2_cultural_memory/INTEGRATION.md)
- [Cultural Memory README](./phase_2_cultural_memory/README.md)
