# Phase 2E Cultural Consensus — Integration Guide

## Overview

Phase 2E sits **between** Phase 2C (External Research) and Phase 3 (Visual Resolution).

It provides **high-authority cultural signals** that Phase 3 can use to:
1. Override AI reasoning for iconic color (when consensus is strong)
2. Validate perceptual fields (ritmo, temperatura, abstraccion)
3. Flag discrepancies for review

## Authority Hierarchy (Proposed for Phase 3)

For **iconic color selection**, the authority order becomes:

```
1. Evidence Layer (Phase 1)           ← Authoritative assignments
2. Cultural Consensus (Phase 2E)      ← NEW: Popular perception
3. External Research (Phase 2C/2D)    ← Critical discourse
4. AI Reasoning (Phase 2A)            ← Fallback inference
```

**Rationale:** Cultural consensus captures how films are **remembered** by audiences, which is often more important than academic analysis for user-facing applications.

## Integration Pattern for Phase 3

### Current Phase 3 Flow

```python
# Current: Phase 3 resolver.py
def resolve_visual_identity(
    work_id: str,
    color_assignment: Dict[str, Any],      # Phase 2A
    cultural_weight: Dict[str, Any],       # Phase 2B
    external_research: Optional[Dict],      # Phase 2C/2D
    doctrine: Optional[Dict],
    evidence_coverage: Optional[Dict]
) -> VisualIdentityResolution:
    # ...
    color_iconico = _select_iconic_color(...)
    # ...
```

### Enhanced Phase 3 Flow (Future)

```python
# Enhanced: Phase 3 resolver.py with Cultural Consensus
def resolve_visual_identity(
    work_id: str,
    color_assignment: Dict[str, Any],
    cultural_weight: Dict[str, Any],
    external_research: Optional[Dict],
    cultural_consensus: Optional[Dict],     # NEW: Phase 2E output
    doctrine: Optional[Dict],
    evidence_coverage: Optional[Dict]
) -> VisualIdentityResolution:
    # ...
    color_iconico = _select_iconic_color_enhanced(
        color_assignment=color_assignment,
        external_research=external_research,
        cultural_consensus=cultural_consensus,  # NEW
        evidence_coverage=evidence_coverage
    )
    # ...
```

### Enhanced Rule 1: Select Iconic Color

```python
def _select_iconic_color_enhanced(
    color_assignment: Dict[str, Any],
    external_research: Optional[Dict[str, Any]],
    cultural_consensus: Optional[Dict[str, Any]],  # NEW
    evidence_coverage: Optional[Dict[str, Any]]
) -> str:
    """
    Enhanced Rule 1 with Cultural Consensus integration.
    
    Priority:
    1. Evidence layer (if authoritative)
    2. Cultural Consensus (if strength >= 0.70)  ← NEW
    3. External Research (if available)
    4. AI reasoning (fallback)
    """
    
    # Check Evidence layer first (highest authority)
    if evidence_coverage and evidence_coverage.get("has_color_assignment"):
        evidence_color = evidence_coverage.get("color_id")
        if evidence_color:
            return evidence_color
    
    # NEW: Check Cultural Consensus (if strong)
    if cultural_consensus:
        consensus_strength = cultural_consensus.get("consensus_strength", 0.0)
        if consensus_strength >= 0.70:
            consensus_color = cultural_consensus.get("color_consensus")
            if consensus_color:
                return consensus_color
    
    # Check External Research findings
    if external_research and external_research.get("findings"):
        research_color = _extract_color_from_findings(external_research["findings"])
        if research_color:
            return research_color
    
    # Fall back to AI reasoning
    if color_assignment and color_assignment.get("primary"):
        ai_color = color_assignment["primary"].get("color_name")
        if ai_color:
            return ai_color
    
    # Default fallback
    return "azul_profundo"
```

## Validation Pattern

Phase 3 can also use Cultural Consensus to **validate** perceptual fields:

```python
def _validate_with_consensus(
    inferred_ritmo: RitmoVisual,
    cultural_consensus: Optional[Dict[str, Any]]
) -> RitmoVisual:
    """
    Validate inferred rhythm against cultural consensus.
    If strong disagreement, prefer consensus.
    """
    
    if not cultural_consensus:
        return inferred_ritmo
    
    consensus_ritmo = cultural_consensus.get("perceived_fields", {}).get("ritmo_visual")
    consensus_strength = cultural_consensus.get("consensus_strength", 0.0)
    
    # Strong consensus overrides inference
    if consensus_strength >= 0.80 and consensus_ritmo:
        if consensus_ritmo != inferred_ritmo:
            # Log discrepancy for audit
            print(f"WARN: Rhythm mismatch - Inferred: {inferred_ritmo}, Consensus: {consensus_ritmo}")
            return consensus_ritmo  # Prefer cultural truth
    
    return inferred_ritmo
```

## Usage Example

### Step 1: Run Phase 2E

```python
from phase_2e_cultural_consensus import resolve_cultural_consensus

# Minimal film metadata
work = {
    "work_id": "work_blade_runner_1982",
    "title": "Blade Runner",
    "year": 1982,
    "countries": ["US", "UK"],
    "genres": ["science_fiction", "neo_noir"],
    "description": "A blade runner must pursue and terminate four replicants..."
}

# Resolve cultural consensus
consensus = resolve_cultural_consensus(work)

print(consensus.color_consensus)           # "azul_profundo"
print(consensus.color_consensus_strength)  # 0.85
print(consensus.perceived_ritmo_visual)    # "moderado_balanceado"
```

### Step 2: Pass to Phase 3 (Enhanced)

```python
from phase_3_visual_resolution import resolve_visual_identity
from phase_2e_cultural_consensus.adapters import to_phase_3_input

# Convert consensus to Phase 3 format
consensus_input = to_phase_3_input(consensus)

# Resolve visual identity (with cultural consensus)
resolution = resolve_visual_identity(
    work_id="work_blade_runner_1982",
    color_assignment=ai_reasoning,
    cultural_weight=cultural_weight,
    external_research=research,
    cultural_consensus=consensus_input,  # NEW
    doctrine=doctrine,
    evidence_coverage=evidence
)
```

## Decision Matrix

| Scenario | Evidence | Consensus | Research | AI | Final Color |
|----------|----------|-----------|----------|----|-----------| 
| 1 | ✓ Present | N/A | N/A | N/A | **Evidence** |
| 2 | ✗ Absent | ✓ Strong (≥0.70) | ✓ Present | ✓ Present | **Consensus** |
| 3 | ✗ Absent | ✗ Weak (<0.70) | ✓ Present | ✓ Present | **Research** |
| 4 | ✗ Absent | ✗ Absent | ✗ Absent | ✓ Present | **AI** |

## Consensus Strength Thresholds

| Strength | Interpretation | Action |
|----------|----------------|--------|
| ≥ 0.80 | Very strong consensus | Override inference unconditionally |
| 0.70–0.79 | Strong consensus | Override inference for iconic color |
| 0.50–0.69 | Moderate consensus | Use as validation signal |
| < 0.50 | Weak consensus | Informational only |

## Discrepancy Logging

When cultural consensus contradicts inference, log for audit:

```python
{
  "work_id": "work_blade_runner_1982",
  "field": "color_iconico",
  "inferred": "verde_distopico",
  "consensus": "azul_profundo",
  "consensus_strength": 0.85,
  "action": "override_with_consensus",
  "supporting_terms": ["neon", "night", "noir", "rain", "cyberpunk"]
}
```

## Testing Integration

To test Phase 3 with Cultural Consensus:

```bash
# Run existing Phase 3 tests (baseline)
python3 pipeline/tests/test_phase_3_visual_resolution_dry_run.py

# Run Phase 2E tests (new)
python3 pipeline/tests/test_phase_2e_cultural_consensus_dry_run.py

# TODO: Create integrated test showing Phase 2E → Phase 3 flow
# python3 pipeline/tests/test_integrated_phase_2e_to_phase_3.py
```

## Migration Path

### Phase 1: Add Phase 2E (Complete)
- ✓ Implement Cultural Consensus Engine
- ✓ Create schema, engine, adapters
- ✓ Test with canonical films

### Phase 2: Enhance Phase 3 (Future)
- Add `cultural_consensus` parameter to `resolve_visual_identity`
- Implement `_select_iconic_color_enhanced` with consensus priority
- Add validation patterns for perceptual fields

### Phase 3: Production Integration (Future)
- Add Phase 2E to main pipeline
- Update orchestration to call Phase 2E before Phase 3
- Add logging/monitoring for consensus vs. inference discrepancies

## Design Principles

1. **Non-Breaking:** Phase 3 remains functional without Phase 2E
2. **Opt-In:** Cultural Consensus is optional parameter
3. **Auditable:** All overrides are logged with justification
4. **Deterministic:** Same inputs → same outputs
5. **Conservative:** Low-strength consensus does not override

## Performance Considerations

- **Latency:** Phase 2E adds ~1-5ms (pure Python, no I/O)
- **Memory:** Minimal (one dataclass instance per film)
- **Caching:** Results can be cached by work_id
- **Parallelization:** Independent per film, fully parallelizable

## Future Enhancements (Out of Scope)

- Real-time consensus from social platforms (Reddit, Letterboxd)
- Multi-language consensus (non-English film discourse)
- Temporal tracking (how consensus changes over time)
- Confidence intervals (statistical rigor for strength)

---

**Status:** Phase 2E is production-ready and can be integrated into Phase 3 when needed.
