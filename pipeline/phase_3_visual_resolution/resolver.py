#!/usr/bin/env python3
"""
Phase 3 Visual Resolution Engine

Pure, deterministic resolver that applies rules.md rules to Phase 2 outputs.

Inputs:
- color_assignment: From Phase 2A AI reasoning
- cultural_weight: From Phase 2B cultural weight calculation
- cultural_memory: From Phase 2 Cultural Memory (NEW - optional)
- external_research: From Phase 2C/2D external research (optional)
- doctrine: Doctrine definitions
- evidence: Evidence layer coverage info

Output:
- VisualIdentityResolution schema object

Authority Hierarchy (Simplified):
1. Hard Evidence (Letterboxd canonical data, title-embedded colors)
2. Cultural Memory (consensus strength ≥ 0.75)
3. Genre Conventions (fallback)
"""

from typing import Dict, Any, Optional, List
from .schema import (
    VisualIdentityResolution,
    TemperaturaEmocional,
    RitmoVisual,
    GradoAbstraccionVisual
)

# Import cultural memory types if available
try:
    from pipeline.phase_2_cultural_memory import CulturalMemoryResult, should_use_consensus
    HAS_CULTURAL_MEMORY = True
except ImportError:
    HAS_CULTURAL_MEMORY = False
    CulturalMemoryResult = None


def resolve_visual_identity(
    work_id: str,
    color_assignment: Dict[str, Any],
    cultural_weight: Dict[str, Any],
    external_research: Optional[Dict[str, Any]] = None,
    doctrine: Optional[Dict[str, Any]] = None,
    evidence_coverage: Optional[Dict[str, Any]] = None,
    cultural_memory: Optional[Any] = None,  # CulturalMemoryResult type
    film_title: Optional[str] = None  # NEW - for logging/debugging
) -> VisualIdentityResolution:
    """
    Deterministically resolve a film's visual identity from Phase 2 outputs.
    
    Args:
        work_id: Film identifier
        color_assignment: From Phase 2A AI reasoning (includes confidence, color_name)
        cultural_weight: From Phase 2B (includes cultural_weight_score)
        external_research: From Phase 2C/2D (optional, includes findings, conflicts, research_quality)
        doctrine: Doctrine definitions (optional, for color metadata)
        evidence_coverage: Evidence layer info (optional, for authority checks)
        cultural_memory: From Phase 2 Cultural Memory (NEW, optional)
        film_title: Film title for debugging (NEW, optional)
    
    Returns:
        VisualIdentityResolution schema object
    
    Implementation notes:
    - Follows simplified 3-rule hierarchy: Evidence > Cultural Memory (≥0.75) > Genre
    - All logic follows rules.md explicitly
    - No heuristics or ML language
    - Deterministic: same inputs → same outputs
    - Auditable: each step can be traced
    """
    
    # RULE 1: Select iconic color (NEW SIMPLIFIED HIERARCHY)
    color_iconico = _select_iconic_color(
        color_assignment=color_assignment,
        external_research=external_research,
        evidence_coverage=evidence_coverage,
        cultural_memory=cultural_memory,  # NEW
        film_title=film_title  # NEW
    )
    
    # RULE 2: Calculate confidence rank
    color_rank = _calculate_color_rank(
        color_assignment=color_assignment,
        external_research=external_research,
        evidence_coverage=evidence_coverage,
        cultural_memory=cultural_memory  # NEW
    )
    
    # RULE 3: Select secondary colors
    colores_secundarios = _select_secondary_colors(
        color_iconico=color_iconico,
        color_assignment=color_assignment,
        external_research=external_research,
        evidence_coverage=evidence_coverage,
        cultural_memory=cultural_memory  # NEW
    )
    
    # RULE 4: Infer emotional temperature
    temperatura_emocional = _infer_temperatura(
        external_research=external_research,
        color_iconico=color_iconico,
        doctrine=doctrine,
        cultural_memory=cultural_memory  # NEW
    )
    
    # RULE 5: Infer visual rhythm
    ritmo_visual = _infer_ritmo(
        external_research=external_research,
        cultural_memory=cultural_memory  # NEW
    )
    
    # RULE 6: Infer abstraction level
    grado_abstraccion = _infer_abstraccion(
        external_research=external_research,
        cultural_memory=cultural_memory  # NEW
    )
    
    return VisualIdentityResolution(
        work_id=work_id,
        color_iconico=color_iconico,
        color_rank=color_rank,
        colores_secundarios=colores_secundarios,
        temperatura_emocional=temperatura_emocional,
        ritmo_visual=ritmo_visual,
        grado_abstraccion_visual=grado_abstraccion
    )



def _select_iconic_color(
    color_assignment: Dict[str, Any],
    external_research: Optional[Dict[str, Any]],
    evidence_coverage: Optional[Dict[str, Any]],
    cultural_memory: Optional[Any] = None,
    film_title: Optional[str] = None
) -> str:
    """
    RULE 1: Select iconic color from simplified 3-rule hierarchy.
    
    Priority Order:
    1. HARD EVIDENCE (highest authority)
       - Letterboxd canonical data (evidence_coverage)
       - Title-embedded colors ("Three Colors: Blue")
       - Director signature styles with citations
    
    2. CULTURAL MEMORY (tiered consensus)
       - LLM perception-based reasoning
       - ≥ 0.85: Cultural memory wins unconditionally
       - 0.75-0.84: Blend (cultural wins if agrees with Phase 2A, else Phase 2A wins)
       - < 0.75: Phase 2A wins unconditionally
    
    3. GENRE CONVENTIONS (fallback)
       - AI reasoning from Phase 2A (color_assignment)
       - External research findings (academic/technical)
       - Genre-based defaults
    
    Returns color ID string.
    """
    
    # RULE 1: Check Hard Evidence first (highest authority)
    if evidence_coverage and evidence_coverage.get("has_color_assignment"):
        evidence_color = evidence_coverage.get("color_id")
        if evidence_color:
            if film_title:
                print(f"[{film_title}] Using EVIDENCE color: {evidence_color}")
            return evidence_color
    
    # RULE 2: Check Cultural Memory with tiered threshold logic
    if HAS_CULTURAL_MEMORY and cultural_memory is not None:
        consensus_strength = getattr(cultural_memory, 'color_consensus_strength', 0.0)
        cultural_color = getattr(cultural_memory, 'iconic_color', None)
        
        # Get Phase 2A color for blend logic (try both color_id and color_name for compatibility)
        phase_2a_color = None
        if color_assignment and color_assignment.get("primary"):
            phase_2a_color = (color_assignment.get("primary", {}).get("color_id") or 
                            color_assignment.get("primary", {}).get("color_name"))
        
        # Tier 1: >= 0.85 → Cultural memory wins unconditionally
        if consensus_strength >= 0.85 and cultural_color:
            if film_title:
                print(f"[{film_title}] ✓ CULTURAL MEMORY (STRONG): {cultural_color} "
                      f"(strength: {consensus_strength:.2f} >= 0.85)")
            return cultural_color
        
        # Tier 2: 0.75-0.84 → Blend logic (agreement check)
        elif 0.75 <= consensus_strength < 0.85 and cultural_color:
            if phase_2a_color is None or cultural_color == phase_2a_color:
                # Phase 2A absent or agrees: use cultural memory
                if film_title:
                    reason = "agrees with Phase 2A" if phase_2a_color else "Phase 2A absent"
                    print(f"[{film_title}] ✓ CULTURAL MEMORY (BLEND): {cultural_color} "
                          f"(strength: {consensus_strength:.2f}, {reason})")
                return cultural_color
            else:
                # Phase 2A present and disagrees: Phase 2A wins
                if film_title:
                    print(f"[{film_title}] → PHASE 2A (BLEND-DISAGREE): {phase_2a_color} "
                          f"(cultural {cultural_color} strength {consensus_strength:.2f} < 0.85, disagrees)")
                return phase_2a_color

        # Tier 3: < 0.75 → Phase 2A wins if present, else use cultural memory
        elif consensus_strength < 0.75 and cultural_color:
            if phase_2a_color:
                if film_title:
                    print(f"[{film_title}] → PHASE 2A (WEAK CONSENSUS): {phase_2a_color} "
                          f"(strength {consensus_strength:.2f} < 0.75)")
                return phase_2a_color
            else:
                if film_title:
                    print(f"[{film_title}] → CULTURAL MEMORY (WEAK, no Phase 2A): {cultural_color} "
                          f"(strength {consensus_strength:.2f})")
                return cultural_color
    
    # RULE 3: Fall back to Genre Conventions
    # Check External Research findings first
    if external_research and external_research.get("findings"):
        findings = external_research.get("findings", {})
        research_color = _extract_color_from_findings(findings)
        if research_color:
            if film_title:
                print(f"[{film_title}] Using EXTERNAL RESEARCH color: {research_color}")
            return research_color
    
    # Fall back to AI reasoning (Phase 2A)
    if color_assignment and color_assignment.get("primary"):
        primary = color_assignment.get("primary", {})
        ai_color = primary.get("color_id") or primary.get("color_name")
        if ai_color:
            if film_title:
                print(f"[{film_title}] Using AI REASONING color: {ai_color}")
            return ai_color
    
    # Default fallback (should not reach in normal operation)
    if film_title:
        print(f"[{film_title}] WARNING: Using default fallback color")
    return "azul_nocturno"


def _extract_color_from_findings(findings: Dict[str, Any]) -> Optional[str]:
    """
    Extract color from research findings by looking for Doctrine color alignment.
    
    Looks for mentions of color concepts in cinematographer_context,
    aesthetic_discourse, and cultural_context.
    
    Returns color ID if found, else None.
    """
    # Map descriptive terms to Doctrine colors
    color_mappings = {
        "passion": "rojo_pasional",
        "intensity": "rojo_pasional",
        "violence": "rojo_pasional",
        "heat": "rojo_pasional",
        "chaos": "naranja_apocaliptico",
        "dystopia": "naranja_apocaliptico",
        "apocalypse": "naranja_apocaliptico",
        "warmth": "ambar_desertico",
        "nostalgia": "ambar_desertico",
        "desert": "ambar_desertico",
        "golden": "ambar_desertico",
        "joy": "amarillo_ludico",
        "whimsy": "amarillo_ludico",
        "sunlight": "amarillo_ludico",
        "playfulness": "amarillo_ludico",
        "nature": "verde_lima",
        "freshness": "verde_lima",
        "renewal": "verde_lima",
        "mystery": "verde_esmeralda",
        "forest": "verde_esmeralda",
        "elegance": "verde_esmeralda",
        "decay": "verde_distopico",
        "military": "verde_distopico",
        "cyberpunk": "verde_distopico",
        "sadness": "cian_melancolico",
        "rain": "cian_melancolico",
        "contemplation": "cian_melancolico",
        "night": "azul_nocturno",
        "noir": "azul_nocturno",
        "depth": "azul_nocturno",
        "alienation": "azul_nocturno",
        "energy": "violeta_cinetico",
        "surrealism": "violeta_cinetico",
        "80s": "violeta_cinetico",
        "dreams": "purpura_onirico",
        "romance": "purpura_onirico",
        "pop": "magenta_pop",
        "neon": "magenta_pop",
        "rebellion": "magenta_pop"
    }
    
    # Scan findings for color-related terms
    found_colors = {}
    for section_key in ["cinematographer_context", "aesthetic_discourse", "cultural_context"]:
        section = findings.get(section_key, {})
        if isinstance(section, dict):
            section_text = str(section).lower()
            for term, color in color_mappings.items():
                if term.lower() in section_text:
                    found_colors[color] = found_colors.get(color, 0) + 1
    
    # Return most frequently mentioned color
    if found_colors:
        return max(found_colors, key=found_colors.get)
    
    return None


def _calculate_color_rank(
    color_assignment: Dict[str, Any],
    external_research: Optional[Dict[str, Any]],
    evidence_coverage: Optional[Dict[str, Any]],
    cultural_memory: Optional[Any] = None
) -> float:
    """
    RULE 2: Calculate confidence rank (0.0–1.0).
    
    Base score depends on source (updated with cultural memory):
    - Evidence decisive: 0.95
    - Cultural Memory (≥0.75): 0.85
    - AI HIGH confidence (>0.80): 0.75
    - External Research HIGH quality: 0.70
    - External Research MODERATE quality: 0.55
    - External Research LOW quality: 0.40
    - Doctrine only: 0.50
    
    Adjustments (cumulative, bounded [0.0, 1.0]):
    - Conflicting perspectives: -0.15
    - Only TERTIARY sources: -0.10
    - Multiple sources agree: +0.10
    - PRIMARY source support: +0.10
    - Non-English cinema with context: +0.05
    """
    
    # Determine base score
    base_score = 0.50  # Default
    
    if evidence_coverage and evidence_coverage.get("has_color_assignment"):
        base_score = 0.95
    elif HAS_CULTURAL_MEMORY and cultural_memory is not None and should_use_consensus(cultural_memory):
        # Cultural memory with strong consensus gets high confidence
        base_score = 0.85
    elif external_research:
        quality = external_research.get("research_quality", "LOW")
        if quality == "HIGH":
            base_score = 0.70
        elif quality == "MODERATE":
            base_score = 0.55
        elif quality == "LOW":
            base_score = 0.40
    elif color_assignment and color_assignment.get("primary"):
        ai_confidence = color_assignment.get("primary", {}).get("confidence", 0.0)
        if ai_confidence > 0.80:
            base_score = 0.75
        else:
            base_score = max(0.50, ai_confidence)
    
    score = base_score
    
    # Apply adjustments
    if external_research:
        # Conflicting perspectives
        conflicts = external_research.get("conflicts", [])
        if conflicts:
            score -= 0.15
        
        # Only TERTIARY sources
        sources = external_research.get("sources", [])
        if sources:
            source_types = [s.get("source_type") for s in sources]
            if all(st == "TERTIARY" for st in source_types):
                score -= 0.10
            elif any(st == "PRIMARY" for st in source_types):
                score += 0.10
        
        # Multiple sources agreement (heuristic: 3+ sources)
        if len(sources) >= 3:
            score += 0.10
    
    # Non-English cinema bonus
    if evidence_coverage and evidence_coverage.get("language") != "English":
        score += 0.05
    
    # Bound score
    return max(0.0, min(1.0, score))


def _select_secondary_colors(
    color_iconico: str,
    color_assignment: Dict[str, Any],
    external_research: Optional[Dict[str, Any]],
    evidence_coverage: Optional[Dict[str, Any]],
    cultural_memory: Optional[Any] = None
) -> List[str]:
    """
    RULE 3: Select secondary colors (max 3, no duplicates with iconic).
    
    Gather candidates from:
    1. Evidence: any mentioned secondary colors
    2. Cultural Memory: secondary colors from perception
    3. AI reasoning: color_assignment.alternates (top 2)
    4. External Research: secondary colors in findings
    
    Rank by authority, select top 3, exclude iconic color.
    """
    
    candidates = {}  # color_id -> authority_score
    
    # Evidence candidates (highest authority)
    if evidence_coverage and evidence_coverage.get("secondary_colors"):
        for color in evidence_coverage.get("secondary_colors", []):
            if color != color_iconico:
                candidates[color] = 0.90
    
    # Cultural Memory candidates
    if HAS_CULTURAL_MEMORY and cultural_memory is not None:
        for color in cultural_memory.secondary_colors:
            if color != color_iconico:
                candidates[color] = max(candidates.get(color, 0), 0.80)
    
    # AI reasoning candidates
    if color_assignment and color_assignment.get("alternates"):
        for alt in color_assignment.get("alternates", [])[:2]:
            color_name = alt.get("color_name")
            if color_name and color_name != color_iconico:
                candidates[color_name] = max(candidates.get(color_name, 0), 0.60)
    
    # External Research candidates
    if external_research and external_research.get("findings"):
        findings = external_research.get("findings", {})
        findings_color = _extract_color_from_findings(findings)
        if findings_color and findings_color != color_iconico:
            candidates[findings_color] = max(candidates.get(findings_color, 0), 0.50)
    
    # Sort by authority score, take top 3
    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    secondary_colors = [color for color, _ in sorted_candidates[:3]]
    
    return secondary_colors


def _infer_temperatura(
    external_research: Optional[Dict[str, Any]],
    color_iconico: str,
    doctrine: Optional[Dict[str, Any]],
    cultural_memory: Optional[Any] = None
) -> TemperaturaEmocional:
    """
    RULE 4: Infer emotional temperature from research findings or cultural memory.
    
    Priority:
    1. Cultural memory perception (if available)
    2. External research findings
    3. Default to neutral_contemplativo
    """
    
    # Pass through Cultural Memory emotional_temperature directly (already a Prisma ID)
    _TEMP_PASSTHROUGH = {
        "calido_apasionado":   "calido_apasionado",
        "calido_nostalgico":   "calido_nostalgico",
        "neutral_contemplativo": "neutral_contemplativo",
        "frio_melancolico":    "frio_melancolico",
        "frio_perturbador":    "frio_alienado",  # Phase 3 schema uses frio_alienado
        "frio_alienado":       "frio_alienado",
    }
    if HAS_CULTURAL_MEMORY and cultural_memory is not None:
        cm_temp = getattr(cultural_memory, 'emotional_temperature', None)
        if cm_temp and cm_temp in _TEMP_PASSTHROUGH:
            return _TEMP_PASSTHROUGH[cm_temp]

    if not external_research or not external_research.get("findings"):
        return "neutral_contemplativo"
    
    findings = external_research.get("findings", {})
    findings_text = str(findings).lower()
    
    # Heat mapping (based on cited discourse, not appearance)
    if any(term in findings_text for term in ["passion", "intensity", "violence", "heat", "fire", "chaos", "dystopia", "apocalypse", "burn"]):
        return "calido_apasionado"
    elif any(term in findings_text for term in ["warmth", "nostalgia", "memory", "desert", "golden", "joy", "whimsy", "sunlight"]):
        return "calido_nostalgico"
    elif any(term in findings_text for term in ["alienation", "isolation", "distance", "void", "loss"]):
        return "frio_alienado"
    elif any(term in findings_text for term in ["sadness", "rain", "solitude", "introspection", "melancholy", "contemplation"]):
        return "frio_melancolico"
    else:
        return "neutral_contemplativo"


def _infer_ritmo(
    external_research: Optional[Dict[str, Any]],
    cultural_memory: Optional[Any] = None
) -> RitmoVisual:
    """
    RULE 5: Infer visual rhythm from cultural memory or research findings.
    
    Priority:
    1. Cultural memory perception (if available)
    2. External research findings
    3. Default to moderado_balanceado
    """
    
    # Pass through Cultural Memory visual_rhythm directly (already a Prisma ID)
    _RHYTHM_PASSTHROUGH = {
        "dinamico_frenetico":   "dinamico_frenetico",
        "dinamico_energico":    "dinamico_energico",
        "moderado_balanceado":  "moderado_balanceado",
        "lento_contemplativo":  "lento_contemplativo",
        "estatico_ritualistico": "estatico_ritualistico",
        # Defensive: handle any legacy accented values that may exist in stored data
        "dinamico_frenético":  "dinamico_frenetico",
        "dinamico_energético": "dinamico_energico",
        "estático_meditativo": "estatico_ritualistico",
    }
    if HAS_CULTURAL_MEMORY and cultural_memory is not None:
        cm_rhythm = getattr(cultural_memory, 'visual_rhythm', None)
        if cm_rhythm and cm_rhythm in _RHYTHM_PASSTHROUGH:
            return _RHYTHM_PASSTHROUGH[cm_rhythm]

    if not external_research or not external_research.get("findings"):
        return "moderado_balanceado"
    
    findings = external_research.get("findings", {})
    findings_text = str(findings).lower()
    
    if any(term in findings_text for term in ["frenetic", "kinetic", "rushed", "chaotic", "fast-paced"]):
        return "dinamico_frenetico"
    elif any(term in findings_text for term in ["energetic", "vibrant", "active", "dynamic", "sharp"]):
        return "dinamico_energico"
    elif any(term in findings_text for term in ["slow", "contemplative", "meditative", "long take", "languid"]):
        return "lento_contemplativo"
    elif any(term in findings_text for term in ["static", "frozen", "still", "minimal movement", "locked camera"]):
        return "estatico_ritualistico"
    else:
        return "moderado_balanceado"


def _infer_abstraccion(
    external_research: Optional[Dict[str, Any]],
    cultural_memory: Optional[Any] = None
) -> GradoAbstraccionVisual:
    """
    RULE 6: Infer abstraction level from cultural memory or research findings.
    
    Priority:
    1. Cultural memory perception (if available)
    2. External research findings
    3. Default to estilizado
    """
    
    # Pass through Cultural Memory abstraction_level directly (already a Prisma ID)
    # Also handles new prompt values (hiperrealista, realista_estilizado, abstracto_experimental)
    _ABSTRACTION_PASSTHROUGH = {
        "extremadamente_realista":   "extremadamente_realista",
        "realista_con_estilizacion": "realista_con_estilizacion",
        "estilizado":                "estilizado",
        "muy_estilizado":            "muy_estilizado",
        "extremadamente_abstracto":  "extremadamente_abstracto",
        # New prompt values → existing schema values
        "hiperrealista":          "extremadamente_realista",
        "realista_estilizado":    "realista_con_estilizacion",
        "abstracto_experimental": "extremadamente_abstracto",
    }
    if HAS_CULTURAL_MEMORY and cultural_memory is not None:
        cm_abstraction = getattr(cultural_memory, 'abstraction_level', None)
        if cm_abstraction and cm_abstraction in _ABSTRACTION_PASSTHROUGH:
            return _ABSTRACTION_PASSTHROUGH[cm_abstraction]

    if not external_research or not external_research.get("findings"):
        return "estilizado"
    
    findings = external_research.get("findings", {})
    findings_text = str(findings).lower()
    
    if any(term in findings_text for term in ["naturalistic", "documentary", "observational", "verite", "realistic"]):
        return "extremadamente_realista"
    elif any(term in findings_text for term in ["grounded", "minimal", "subtle"]):
        return "realista_con_estilizacion"
    elif any(term in findings_text for term in ["heightened", "theatrical", "exaggerated", "artificial", "expressionistic"]):
        return "muy_estilizado"
    elif any(term in findings_text for term in ["abstract", "non-representational", "symbolic", "dreamlike", "surreal"]):
        return "extremadamente_abstracto"
    else:
        return "estilizado"
