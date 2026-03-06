# Phase 2E: Cultural Consensus Engine

## Purpose

Phase 2E captures **collective cultural memory** of films — how they are perceived, remembered, and discussed in popular discourse.

This is NOT:
- Critical analysis
- Aesthetic theory
- Academic discourse
- Authoritative evidence
- Color grading analysis

This IS:
- Popular perception
- Cultural consensus
- Collective visual memory
- How films "feel" to audiences

## Authority Role

In the layered architecture, Cultural Consensus has **HIGH authority** for certain perceptual fields:

**Priority order (Phase 3 integration):**
1. **Cultural Consensus** (Phase 2E) ← For iconic color perception
2. Evidence Layer (Phase 1) ← For authoritative assignments
3. External Research (Phase 2C/2D) ← For critical discourse
4. AI Reasoning (Phase 2A) ← For fallback inference

**Rationale:** If a film is culturally remembered as "red" (even if that contradicts technical analysis), the cultural consensus wins. Cultural truth > theoretical purity.

## What This Phase Produces

Phase 2E outputs a `CulturalConsensusResult` with:

1. **color_consensus** — Prisma color ID from cultural memory
   - Example: `"rojo_pasion"`, `"azul_profundo"`, `"ambar_dorado"`

2. **color_consensus_strength** — Clarity of cultural agreement (0.0–1.0)
   - 0.9+: Near-universal consensus ("everyone knows Schindler's List is black & white")
   - 0.7–0.9: Strong consensus ("most people think Blade Runner is blue")
   - 0.5–0.7: Moderate consensus ("some agreement on color identity")
   - <0.5: Weak/no consensus (return fields but low strength)

3. **perceived_ritmo_visual** — How audiences perceive pacing/rhythm
   - Uses same enum as Phase 3: `dinamico_frenético`, `lento_contemplativo`, etc.

4. **perceived_temperatura_emocional** — Emotional temperature from cultural memory
   - Uses same enum as Phase 3: `calido_apasionado`, `frio_melancolico`, etc.

5. **perceived_grado_abstraccion** — Perceived abstraction level
   - Uses same enum as Phase 3: `extremadamente_abstracto`, `realista_con_estilizacion`, etc.

6. **supporting_terms** — Raw cultural signals found
   - List of strings justifying the consensus
   - Example: `["red dress", "neon chaos", "fast-paced", "surreal"]`

## What This Phase Is NOT

❌ **NOT a color assignment system** — Does not finalize decisions  
❌ **NOT a validation layer** — Does not check schemas  
❌ **NOT a reasoning engine** — Does not use ML inference  
❌ **NOT a persistence layer** — Does not store data  
❌ **NOT a confidence scorer** — Does not calculate `color_rank`  

✅ **IS a signal aggregator** — Collects and normalizes cultural signals  
✅ **IS deterministic** — Same input → same output  
✅ **IS explainable** — `supporting_terms` justify outputs  
✅ **IS conservative** — Low strength when consensus is weak  

## Input Contract

The module receives minimal film metadata:

```python
{
  "work_id": "work_blade_runner_1982",
  "title": "Blade Runner",
  "year": 1982,
  "countries": ["US", "UK"],
  "genres": ["science_fiction", "neo_noir"],
  "description": "A blade runner must pursue and terminate four replicants..."  # optional
}
```

**No other phases are required.**

## Output Contract

Returns a `CulturalConsensusResult`:

```python
CulturalConsensusResult(
    work_id="work_blade_runner_1982",
    color_consensus="azul_profundo",
    color_consensus_strength=0.85,
    perceived_ritmo_visual="moderado_balanceado",
    perceived_temperatura_emocional="frio_alienado",
    perceived_grado_abstraccion="estilizado",
    supporting_terms=["neon", "night", "rain", "noir", "cyberpunk", "blue lighting"]
)
```

## Design Philosophy

### Conservative > Aggressive

If consensus is unclear:
- Lower `color_consensus_strength` instead of guessing
- Return neutral defaults for enums
- Maintain `supporting_terms` for audit trail

### Cultural Truth > Theoretical Purity

If popular perception contradicts academic analysis:
- **Cultural consensus wins**
- This is intentional
- Example: "The Matrix is green" (even if technically more complex)

### Explainability > Magic

Every output must be justified by `supporting_terms`:
- Terms are extracted from cultural signals
- Terms map deterministically to outputs
- Humans can verify the reasoning

## Examples

### Example 1: Strong Consensus — In the Mood for Love (2000)

**Input:**
```python
{
  "work_id": "work_in_the_mood_for_love_2000",
  "title": "In the Mood for Love",
  "year": 2000,
  "countries": ["HK"],
  "genres": ["romance", "drama"]
}
```

**Output:**
```python
CulturalConsensusResult(
    work_id="work_in_the_mood_for_love_2000",
    color_consensus="rojo_pasion",
    color_consensus_strength=0.88,
    perceived_ritmo_visual="lento_contemplativo",
    perceived_temperatura_emocional="calido_nostalgico",
    perceived_grado_abstraccion="estilizado",
    supporting_terms=["red dress", "cheongsam", "warm", "slow", "longing", "intimate"]
)
```

### Example 2: Strong Consensus — Mad Max: Fury Road (2015)

**Input:**
```python
{
  "work_id": "work_mad_max_fury_road_2015",
  "title": "Mad Max: Fury Road",
  "year": 2015,
  "countries": ["AU", "US"],
  "genres": ["action", "science_fiction"]
}
```

**Output:**
```python
CulturalConsensusResult(
    work_id="work_mad_max_fury_road_2015",
    color_consensus="naranja_apocaliptico",  # if this color exists in doctrine
    color_consensus_strength=0.92,
    perceived_ritmo_visual="dinamico_frenético",
    perceived_temperatura_emocional="calido_apasionado",
    perceived_grado_abstraccion="muy_estilizado",
    supporting_terms=["orange", "desert", "fire", "chaos", "fast", "visceral", "apocalypse"]
)
```

### Example 3: Moderate Consensus — Eraserhead (1977)

**Input:**
```python
{
  "work_id": "work_eraserhead_1977",
  "title": "Eraserhead",
  "year": 1977,
  "countries": ["US"],
  "genres": ["horror", "experimental"]
}
```

**Output:**
```python
CulturalConsensusResult(
    work_id="work_eraserhead_1977",
    color_consensus="gris_monocromatico",  # if exists, else closest match
    color_consensus_strength=0.65,
    perceived_ritmo_visual="lento_contemplativo",
    perceived_temperatura_emocional="frio_alienado",
    perceived_grado_abstraccion="extremadamente_abstracto",
    supporting_terms=["black and white", "industrial", "nightmare", "surreal", "slow", "oppressive"]
)
```

## Integration with Phase 3

Phase 3 (Visual Resolution) will consume Cultural Consensus outputs as **high-priority signals**:

```python
# In Phase 3 resolver (future enhancement)
if cultural_consensus and cultural_consensus.color_consensus_strength >= 0.70:
    # Cultural consensus overrides AI reasoning for iconic color
    color_iconico = cultural_consensus.color_consensus
else:
    # Fall back to existing priority: Evidence > Research > AI
    color_iconico = _select_iconic_color(...)
```

Phase 3 will also use perceived enums to **validate or adjust** inference:

```python
# If cultural consensus strongly disagrees with inference, flag for review
if cultural_consensus.perceived_ritmo_visual == "dinamico_frenético":
    if inferred_ritmo == "lento_contemplativo":
        # Log discrepancy, prefer cultural consensus for user-facing output
        ritmo_visual = cultural_consensus.perceived_ritmo_visual
```

## Testing

See `test_phase_2e_cultural_consensus_dry_run.py` for evaluation harness.

Films tested:
- In the Mood for Love (2000)
- Mad Max: Fury Road (2015)
- Eraserhead (1977)
- The Lighthouse (2019)
- Uncut Gems (2019)
- Mulholland Drive (2001)

## Constraints

1. **Deterministic:** Same input → same output
2. **No external APIs:** All logic is rule-based
3. **No ML inference:** Uses pattern matching only
4. **No persistence:** Pure function, no side effects
5. **No validation:** Assumes inputs are pre-validated
6. **No mutations:** Returns new objects only

## Future Extensions (Out of Scope)

- Real-time cultural signal aggregation (Reddit, Letterboxd, Twitter)
- Multi-language consensus (current implementation is English-centric)
- Temporal consensus tracking (how perception changes over time)
- Consensus confidence intervals (statistical rigor)

---

**Status:** Production-ready, deterministic, rule-based signal aggregation.
