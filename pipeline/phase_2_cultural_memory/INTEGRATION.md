# Phase 2 Cultural Memory Integration Guide

## Overview

This guide shows how to integrate the new **Phase 2 Cultural Memory** module with the existing pipeline to solve the "wrong iconic color" problem (e.g., The Matrix → red instead of green, Barbie → purple instead of pink).

## Problem Statement

The old system had **authority inversion**: genre conventions were stronger than cultural memory. This caused:
- The Matrix → `rojo_pasion` (red) instead of `verde_acido` (green)
- Barbie → `violeta_onirico` (purple) instead of `rosa_melancolico` (pink)

## Solution Architecture

### New 3-Rule Hierarchy

1. **Hard Evidence** (highest authority)
   - Letterboxd canonical data
   - Title-embedded colors ("Three Colors: Blue")
   - Director signature styles

2. **Cultural Memory** (strong consensus ≥ 0.75)
   - LLM asking: "What color do people think of?"
   - Sources: posters, marketing, cultural impact
   - NOT: academic analysis or shot statistics

3. **Genre Conventions** (fallback)
   - Phase 2E cultural consensus
   - Genre-based defaults

## Integration Steps

### Step 1: Import Cultural Memory Module

```python
from pipeline.phase_2_cultural_memory import resolve_cultural_memory, should_use_consensus
```

### Step 2: Resolve Cultural Memory (NEW PHASE)

```python
# After Phase 2D, before Phase 3
cultural_memory = resolve_cultural_memory(
    tmdb_id=film_data['id'],
    title=film_data['title'],
    year=film_data['release_year'],
    genres=film_data['genres'],
    api_key=os.getenv('GEMINI_API_KEY')
)

print(f"Cultural memory: {cultural_memory.iconic_color}")
print(f"Consensus strength: {cultural_memory.color_consensus_strength}")
```

### Step 3: Pass to Phase 3 Visual Resolution

```python
from pipeline.phase_3_visual_resolution import resolve_visual_identity

# Updated function signature
identity = resolve_visual_identity(
    work_id=work_id,
    color_assignment=phase_2a_result,
    cultural_weight=phase_2b_result,
    external_research=phase_2d_result,  # Optional
    doctrine=doctrine,
    evidence_coverage=evidence,
    cultural_memory=cultural_memory,  # NEW
    film_title=film_data['title']  # NEW - for debugging
)
```

### Step 4: Phase 3 Automatically Uses Hierarchy

Phase 3's `_select_iconic_color()` now implements the 3-rule hierarchy:

```python
def _select_iconic_color(...):
    # 1. Check Hard Evidence first
    if evidence_coverage.has_color_assignment:
        return evidence_color  # 🏆 Highest authority
    
    # 2. Check Cultural Memory (if strong consensus)
    if should_use_consensus(cultural_memory):
        return cultural_memory.iconic_color  # 🎯 Strong consensus
    
    # 3. Fall back to Genre Conventions
    # ... external research, AI reasoning, defaults
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete pipeline with Cultural Memory integration
"""
import os
from pipeline.phase_2_cultural_memory import resolve_cultural_memory
from pipeline.phase_3_visual_resolution import resolve_visual_identity

# Film data
film = {
    'tmdb_id': 603,
    'title': 'The Matrix',
    'year': 1999,
    'genres': ['Science Fiction', 'Action']
}

# Phase 2 Cultural Memory (NEW)
cultural_memory = resolve_cultural_memory(
    tmdb_id=film['tmdb_id'],
    title=film['title'],
    year=film['year'],
    genres=film['genres'],
    api_key=os.getenv('GEMINI_API_KEY')
)

print(f"Cultural Memory Result:")
print(f"  Color: {cultural_memory.iconic_color}")
print(f"  Strength: {cultural_memory.color_consensus_strength}")
print(f"  Reasoning: {cultural_memory.reasoning}")

# Phase 3 Visual Resolution (UPDATED)
identity = resolve_visual_identity(
    work_id=f"tmdb_{film['tmdb_id']}",
    color_assignment={},  # Phase 2A result
    cultural_weight={},   # Phase 2B result
    cultural_memory=cultural_memory,  # NEW
    film_title=film['title']
)

print(f"\nFinal Visual Identity:")
print(f"  Iconic Color: {identity.color_iconico}")
print(f"  Confidence: {identity.color_rank}")
```

## Expected Results

### Before Cultural Memory

```python
# The Matrix (WRONG)
color_iconico: "rojo_pasion"  # ❌ Red (from genre sci-fi)
color_rank: 0.55

# Barbie (WRONG)
color_iconico: "violeta_onirico"  # ❌ Purple (pink→purple mapping bug)
color_rank: 0.60
```

### After Cultural Memory

```python
# The Matrix (CORRECT)
cultural_memory.iconic_color: "verde_acido"  # ✅ Green
cultural_memory.consensus_strength: 0.92
cultural_memory.reasoning: "The Matrix is universally associated with green 
  due to the iconic 'digital rain' code sequences visible throughout the film..."

identity.color_iconico: "verde_acido"  # ✅ Green used
identity.color_rank: 0.85

# Barbie (CORRECT)
cultural_memory.iconic_color: "rosa_melancolico"  # ✅ Pink
cultural_memory.consensus_strength: 0.95
cultural_memory.reasoning: "Barbie's marketing campaign saturated culture with 
  hot pink, making it the film's universally recognized color..."

identity.color_iconico: "rosa_melancolico"  # ✅ Pink used
identity.color_rank: 0.85
```

## Testing

### Unit Test (Single Film)

```bash
# Set API key
export GEMINI_API_KEY='your-gemini-api-key'

# Run canonical test suite
python pipeline/tests/test_cultural_memory_canonical.py
```

### Expected Output

```
Testing: The Matrix (1999)
Expected: verde_acido
================================================================================

📊 RESULT:
  Iconic Color: verde_acido
  Consensus Strength: 0.92
  Visual Rhythm: KINETIC
  Temperature: COOL
  Abstraction: SYMBOLIC

💭 REASONING:
  The Matrix is universally associated with green due to the iconic 
  "digital rain" code sequences...

✅ Strong Consensus: YES
✅ COLOR MATCH: verde_acido is acceptable
✅ REASONING KEYWORDS: Found green, code, digital, matrix

================================================================================
✅ TEST PASSED for The Matrix
```

## Confidence Ranking

Cultural Memory updates the confidence calculation in Phase 3:

```python
def _calculate_color_rank(...):
    if evidence_coverage.has_color_assignment:
        base_score = 0.95  # Evidence decisive
    elif should_use_consensus(cultural_memory):
        base_score = 0.85  # Strong cultural consensus (NEW)
    elif external_research.quality == "HIGH":
        base_score = 0.70  # Academic research
    # ... etc
```

## Debugging Output

Enable film title logging to see which authority is used:

```python
identity = resolve_visual_identity(
    # ... other params
    film_title="The Matrix"  # Enables debug output
)

# Output:
# [The Matrix] Using CULTURAL MEMORY color: verde_acido (strength: 0.92)
```

## Migration Checklist

- [ ] Install `phase_2_cultural_memory` module
- [ ] Set `GEMINI_API_KEY` environment variable
- [ ] Update Phase 3 calls to include `cultural_memory` parameter
- [ ] Run canonical test suite (expect ≥90% pass rate)
- [ ] Verify The Matrix → green, Barbie → pink
- [ ] Monitor consensus strength on production data
- [ ] (Optional) Deprecate old Phase 2E to `_deprecated/` folder

## API Costs

Gemini API calls add ~$0.001-0.003 per film (1.5 model):
- 7 films @ $0.002 = ~$0.014 per test run
- 1000 films @ $0.002 = ~$2.00 for full catalog

## Rollback Plan

If issues arise, cultural memory is **optional**:

```python
# Old behavior (no cultural memory)
identity = resolve_visual_identity(
    work_id=work_id,
    color_assignment=phase_2a,
    cultural_weight=phase_2b,
    # cultural_memory=None,  # Omit or pass None
    # film_title=None
)
# System falls back to genre conventions automatically
```

## See Also

- [Phase 2 Cultural Memory README](../phase_2_cultural_memory/README.md)
- [Phase 3 Visual Resolution](../phase_3_visual_resolution/README.md)
- [Canonical Test Suite](../tests/test_cultural_memory_canonical.py)
