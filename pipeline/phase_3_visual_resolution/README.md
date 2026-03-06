# Phase 3: Visual Resolution Layer

**Status:** Implementation Complete  
**Version:** 1.0  
**Last Updated:** 2026-02-06

---

## PURPOSE

Phase 3 is the final deterministic layer that transforms Phase 2 structured outputs into UX-facing visual identity fields.

**This phase does NOT:**
- Call AI or Gemini
- Perform research
- Modify Doctrine
- Invent data
- Make aesthetic opinions
- Learn or adapt

**This phase ONLY:**
- Takes structured inputs from Phase 2A, 2B, and 2C/2D
- Applies explicit, auditable resolution rules
- Produces final UX contract fields
- Returns deterministic outputs

---

## INPUTS (Phase 2 OUTPUTS)

### From Phase 2A: AI Reasoning
```json
{
  "color_assignment": {
    "primary": {
      "color_name": "string",
      "confidence": 0.0-1.0
    },
    "alternates": [
      {"color_name": "string", "confidence": 0.0-1.0}
    ]
  }
}
```

### From Phase 2B: Cultural Weight
```json
{
  "cultural_weight_score": 0.0-100.0,
  "signals": {...}
}
```

### From Phase 2C/2D: External Research (Optional)
```json
{
  "sources": [...],
  "findings": {
    "cinematographer_context": {...},
    "aesthetic_discourse": {...},
    "cultural_context": {...}
  },
  "conflicts": [...],
  "research_quality": "HIGH | MODERATE | LOW",
  "uncertainty_flags": [...]
}
```

### From Evidence Layer (Optional)
Indicates if work has existing color assignment in Evidence.

---

## OUTPUTS (FINAL UX CONTRACT)

```json
{
  "work_id": "string",
  "color_iconico": "string (Doctrine color ID)",
  "color_rank": 0.0-1.0,
  "colores_secundarios": ["string", ...],
  "temperatura_emocional": "enum",
  "ritmo_visual": "enum",
  "grado_abstraccion_visual": "enum"
}
```

### Output Field Reference

| Field | Type | Range | Notes |
|-------|------|-------|-------|
| `color_iconico` | String | Doctrine color ID | Primary canonical color |
| `color_rank` | Float | 0.0–1.0 | Confidence score |
| `colores_secundarios` | List[String] | 0–3 items | Supporting colors |
| `temperatura_emocional` | Enum | 5 values | Emotional temperature |
| `ritmo_visual` | Enum | 5 values | Visual rhythm |
| `grado_abstraccion_visual` | Enum | 5 values | Abstraction level |

---

## RESOLUTION RULES

All resolution rules are documented in `rules.md`.

Rules are:
- **Explicit:** Each step can be traced
- **Deterministic:** Same inputs → same outputs
- **Auditable:** Every field has a rule with rationale
- **Free of heuristics:** Uses only doctrine definitions and phase 2 data

### Rule Summary

1. **Select iconic color:** Evidence > External Research > AI reasoning
2. **Calculate confidence rank:** Base score + cumulative adjustments
3. **Select secondary colors:** Top 3 candidates by authority
4. **Infer emotional temperature:** Map research findings to temperature categories
5. **Infer visual rhythm:** Map research findings to rhythm categories
6. **Infer abstraction level:** Map research findings to abstraction categories

---

## ARCHITECTURE

### Files

- `schema.py` — Output dataclass and enums (FROZEN)
- `resolver.py` — Resolution engine with all rule implementations
- `adapters.py` — Thin passthrough adapters for Phase 2 inputs
- `rules.md` — Documented rules (reference, not executable)

### Key Functions

```python
resolve_visual_identity(
    work_id: str,
    color_assignment: Dict,
    cultural_weight: Dict,
    external_research: Optional[Dict] = None,
    evidence_coverage: Optional[Dict] = None,
    doctrine: Optional[Dict] = None
) -> VisualIdentityResolution
```

Returns a `VisualIdentityResolution` object (validated dataclass).

---

## ENUM VALUES

### TemperaturaEmocional
- `calido_apasionado` — Passion, intensity, heat
- `calido_nostalgico` — Warmth, memory, nostalgia
- `neutral_contemplativo` — Balance, stability, contemplation
- `frio_melancolico` — Sadness, introspection, melancholy
- `frio_alienado` — Isolation, distance, alienation

### RitmoVisual
- `dinamico_frenético` — Chaotic, rushed, kinetic
- `dinamico_energético` — Vibrant, active, energetic
- `moderado_balanceado` — Steady, measured, balanced
- `lento_contemplativo` — Slow, meditative, contemplative
- `estático_meditativo` — Still, frozen, static

### GradoAbstraccionVisual
- `extremadamente_realista` — Documentary, observational realism
- `realista_con_estilizacion` — Subtle stylization
- `estilizado` — Deliberate artistic style
- `muy_estilizado` — Heightened, theatrical, exaggerated
- `extremadamente_abstracto` — Symbolic, surreal, abstract

---

## VALIDATION

All outputs are validated by the `VisualIdentityResolution` dataclass:

- `color_rank` must be bounded [0.0, 1.0]
- `colores_secundarios` must not contain duplicates
- `colores_secundarios` must not include the iconic color
- `colores_secundarios` max 3 items

If validation fails, an exception is raised immediately.

---

## EXAMPLE USAGE

```python
from phase_3_visual_resolution.resolver import resolve_visual_identity
from phase_3_visual_resolution.schema import to_dict

resolution = resolve_visual_identity(
    work_id="work_blade_runner_1982",
    color_assignment={
        "primary": {"color_name": "azul_nocturno", "confidence": 0.92},
        "alternates": [{"color_name": "cian_melancolico", "confidence": 0.65}]
    },
    cultural_weight={"cultural_weight_score": 65.0},
    external_research={...},
    evidence_coverage=None
)

output = to_dict(resolution)
# {
#   "work_id": "work_blade_runner_1982",
#   "color_iconico": "azul_nocturno",
#   "color_rank": 0.85,
#   "colores_secundarios": ["cian_melancolico"],
#   "temperatura_emocional": "frio_melancolico",
#   "ritmo_visual": "moderado_balanceado",
#   "grado_abstraccion_visual": "estilizado"
# }
```

---

## TESTING

### Dry-Run Test

A dry-run test is provided in `pipeline/tests/test_phase_3_visual_resolution_dry_run.py`.

Run with:
```bash
python3 pipeline/tests/test_phase_3_visual_resolution_dry_run.py
```

Test cases:
1. Evidence layer decisive (rank ~0.95)
2. External research HIGH quality (rank ~0.70-0.80)
3. External research LOW quality (rank ~0.40-0.50)
4. Doctrine + AI only (rank ~0.60-0.75)

---

## CONSTRAINTS (NON-NEGOTIABLE)

- Do NOT assign colors in Phase 2
- Do NOT modify Gemini behavior
- Do NOT add new Doctrine colors
- Do NOT invent data
- Do NOT reduce plurality
- Do NOT collapse conflicts silently
- If information is weak, LOWER the rank — do NOT guess

---

## EPISTEMIC POSITION

Phase 3 is a **pure deterministic resolver** with NO epistemic authority.

**Authority Hierarchy (maintained):**
1. Doctrine (highest — constrains all)
2. Editorial Override (final decision)
3. Internal Evidence (curated, versioned)
4. External Research (contextual enrichment)
5. AI Reasoning (applies doctrine + context)
6. **Phase 3 Resolution** (deterministic field calculation)

Phase 3 does NOT:
- Override Doctrine
- Bypass Editorial authority
- Replace Evidence
- Assign colors

Phase 3 ONLY:
- Applies explicit rules
- Produces UX fields
- Documents uncertainty (via rank)

---

## VERSION HISTORY

**v1.0 (2026-02-06)**
- Initial complete implementation
- All 6 resolution rules implemented
- Schema with full validation
- Dry-run test suite passing
- Deterministic and auditable

---

**Contract Owner:** Prisma Systems Architecture  
**Frozen:** Yes (Phase 2 complete, Phase 3 final)  
**Dependencies:** Phase 2A, 2B, 2C/2D outputs only
