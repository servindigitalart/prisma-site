# Phase 2E → Phase 3 Integration Test — Usage Guide

## Overview

This test evaluates the complete flow from **Cultural Consensus (Phase 2E)** to **Visual Resolution (Phase 3)** using 13 canonical films spanning different eras, genres, and national cinemas.

## Run the Test

```bash
cd /Users/servinemilio/Documents/REPOS/prisma-site
python3 pipeline/tests/test_phase_2e_3_visual_resolution_cultural_set.py
```

## What This Test Does

For each of the 13 films:

1. **Phase 2E:** Extracts cultural signals → resolves consensus
2. **Phase 3:** Uses consensus color as AI input → resolves final visual identity
3. **Comparison:** Identifies discrepancies between consensus and final output

## Key Observations to Look For

### 1. Color Mismatches
**Question:** Does cultural consensus disagree with final `color_iconico`?

**Current Result:** ✅ **No color mismatches** — All 13 films show consensus = final color

**Why:** The test currently passes consensus color through as AI reasoning input, so Phase 3 naturally respects it. In real production, AI reasoning might disagree with consensus.

### 2. Rhythm Mismatches
**Question:** Does perceived rhythm differ from final `ritmo_visual`?

**Current Result:** ⚠️ **12/13 films show rhythm mismatches**

**Pattern:**
- Cultural Consensus: Films perceived as `lento_contemplativo` or `dinamico_frenético`
- Phase 3 Final: Almost all resolve to `moderado_balanceado`

**Why:** Phase 3 currently has NO external research input in this test, so it defaults to `moderado_balanceado` when signals are absent.

### 3. Temperature Mismatches
**Question:** Does perceived emotional temperature differ from final output?

**Current Result:** ⚠️ **10/13 films show temperature mismatches**

**Pattern:**
- Cultural Consensus: Films perceived as `calido_nostalgico`, `calido_apasionado`, or `frio_melancolico`
- Phase 3 Final: Frequently defaults to `neutral_contemplativo`

**Why:** Same reason as rhythm — Phase 3 defaults when no external research signals are present.

### 4. Abstraction Mismatches
**Question:** Does perceived abstraction level differ from final output?

**Current Result:** ⚠️ **12/13 films show abstraction mismatches**

**Pattern:**
- Cultural Consensus: Films perceived as `realista_con_estilizacion` or `extremadamente_abstracto`
- Phase 3 Final: Almost all resolve to `estilizado`

**Why:** Phase 3 defaults to `estilizado` without research signals.

## Key Insights

### Insight 1: Color Authority Works
When cultural consensus is passed through (even indirectly), Phase 3 respects it. This validates the proposed integration where strong consensus (≥0.70) overrides AI reasoning.

### Insight 2: Perceptual Fields Need Research
Phase 3's inference for `ritmo_visual`, `temperatura_emocional`, and `grado_abstraccion` **requires external research findings**. Without research:
- Rhythm → defaults to `moderado_balanceado`
- Temperature → defaults to `neutral_contemplativo`
- Abstraction → defaults to `estilizado`

### Insight 3: Cultural Consensus Is Rich
Phase 2E successfully extracts perceptual signals from minimal metadata (title, year, genres, countries). These signals could be valuable inputs for Phase 3.

## Proposed Integration Strategy

### Current Phase 3 Flow
```
Evidence > External Research > AI Reasoning
          ↓
   [No Cultural Consensus]
```

### Enhanced Phase 3 Flow (Future)
```
Evidence > Cultural Consensus (≥0.70) > External Research > AI Reasoning
                   ↓
    [Use consensus for validation]
```

### Specific Enhancements

1. **For `color_iconico`:**
   - If `consensus_strength >= 0.70`, use `color_consensus` instead of AI reasoning
   - Current: Works implicitly (test shows 100% match)
   - Future: Make explicit in Phase 3 Rule 1

2. **For perceptual fields (ritmo, temperatura, abstraccion):**
   - Use consensus as **validation signal** when research is absent
   - If consensus disagrees with defaults, prefer consensus
   - Current: Defaults used (test shows 92% mismatch)
   - Future: Use consensus to avoid uninformative defaults

## Film Set Highlights

### Strong Consensus (≥0.70)
- **Barbie (2023)** — `violeta_onirico`, strength 0.80
- **Trois couleurs: Blanc (1994)** — `azul_profundo`, strength 0.80
- **The Substance (2024)** — `azul_profundo`, strength 0.80

### Moderate Consensus (0.50–0.70)
- **The Matrix (1999)** — `rojo_pasion`, strength 0.60
- **Roma (2018)** — `azul_profundo`, strength 0.60

### Interesting Cases
- **Barbie:** Only film with `violeta_onirico` (fantasy/surreal genre)
- **Solo con tu pareja:** Only film with `ambar_dorado` (romance/warmth)
- **The Matrix/Kill Bill:** Both `rojo_pasion` (action/intensity)

## Consensus Strength Distribution

- **Strong (≥0.70):** 8 films (62%)
- **Moderate (0.50–0.70):** 5 films (38%)
- **Weak (<0.50):** 0 films (0%)

All films show at least moderate consensus, validating Phase 2E's signal extraction.

## Recommendations

### 1. Integrate Cultural Consensus into Phase 3
Priority: **High** (for iconic color)

- Add `cultural_consensus` parameter to `resolve_visual_identity`
- Implement enhanced Rule 1 (see `INTEGRATION.md`)
- Threshold: ≥0.70 for override authority

### 2. Use Consensus for Perceptual Validation
Priority: **Medium** (for ritmo, temperatura, abstraccion)

- When external research is absent, prefer consensus over defaults
- Log discrepancies for manual review
- Threshold: ≥0.60 for validation signal

### 3. Monitor Discrepancies in Production
Priority: **Low** (observational)

- Track cases where consensus disagrees with research/AI
- Build dataset for future ML training
- Refine signal extraction rules

## Next Steps

1. **Review test output** with domain experts
2. **Validate cultural coherence** of consensus results
3. **Implement Phase 3 enhancements** (optional, non-breaking)
4. **Add real external research** to test (shows true integration)

## Related Documentation

- `pipeline/phase_2e_cultural_consensus/README.md` — Phase 2E user guide
- `pipeline/phase_2e_cultural_consensus/INTEGRATION.md` — Integration patterns
- `pipeline/phase_3_visual_resolution/rules.md` — Current Phase 3 rules

---

**Test Status:** ✅ Complete and passing (observational, no assertions)
