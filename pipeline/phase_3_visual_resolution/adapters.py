#!/usr/bin/env python3
"""
Phase 3 Input Adapters

Thin adapter functions to normalize Phase 2 outputs into resolver inputs.
These are PASSTHROUGH adapters — they do NOT transform data, only reshape it.

No renaming of existing fields.
No breaking changes to Phase 2 contracts.
"""

from typing import Dict, Any, Optional


def adapt_ai_reasoning(reasoning_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt Phase 2A AI reasoning output to resolver input.
    
    Expects:
    {
        "work_id": str,
        "color_assignment": {
            "primary": {
                "color_name": str,
                "confidence": float,
                ...
            },
            "alternates": [
                {"color_name": str, "confidence": float, ...}
            ],
            ...
        },
        ...
    }
    
    Returns: color_assignment dict for resolver
    """
    return reasoning_output.get("color_assignment", {})


def adapt_cultural_weight(weight_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt Phase 2B cultural weight output to resolver input.
    
    Expects:
    {
        "work_id": str,
        "cultural_weight_score": float,
        "signals": {...},
        ...
    }
    
    Returns: cultural_weight dict for resolver
    """
    return {
        "cultural_weight_score": weight_output.get("cultural_weight_score", 0.0),
        "signals": weight_output.get("signals", {})
    }


def adapt_external_research(research_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt Phase 2C/2D external research output to resolver input.
    
    Expects:
    {
        "work_id": str,
        "trigger_reason": str,
        "conducted_at": str,
        "sources": [...],
        "findings": {...},
        "conflicts": [...],
        "uncertainty_flags": [...],
        "research_quality": str,
        "promotion_eligible": bool,
        ...
    }
    
    Returns: external_research dict for resolver (passthrough)
    """
    return {
        "work_id": research_output.get("work_id"),
        "trigger_reason": research_output.get("trigger_reason"),
        "conducted_at": research_output.get("conducted_at"),
        "sources": research_output.get("sources", []),
        "findings": research_output.get("findings", {}),
        "conflicts": research_output.get("conflicts", []),
        "uncertainty_flags": research_output.get("uncertainty_flags", []),
        "research_quality": research_output.get("research_quality", "LOW"),
        "promotion_eligible": research_output.get("promotion_eligible", False)
    }


def adapt_evidence_coverage(
    work_id: str,
    has_color_assignment: bool = False,
    color_id: Optional[str] = None,
    secondary_colors: Optional[list] = None,
    language: str = "Unknown"
) -> Dict[str, Any]:
    """
    Create evidence coverage info object for resolver.
    
    This is typically built by checking Evidence layer for a given work.
    If Evidence has a color assignment for the work, pass has_color_assignment=True
    and color_id=<assigned_color>.
    """
    return {
        "work_id": work_id,
        "has_color_assignment": has_color_assignment,
        "color_id": color_id,
        "secondary_colors": secondary_colors or [],
        "language": language
    }


def build_resolver_inputs(
    work_id: str,
    ai_reasoning: Dict[str, Any],
    cultural_weight: Dict[str, Any],
    external_research: Optional[Dict[str, Any]] = None,
    evidence_coverage: Optional[Dict[str, Any]] = None,
    doctrine: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build complete resolver input dict from Phase 2 outputs.
    
    Args:
        work_id: Film identifier
        ai_reasoning: Phase 2A output
        cultural_weight: Phase 2B output
        external_research: Phase 2C/2D output (optional)
        evidence_coverage: Evidence layer info (optional)
        doctrine: Doctrine definitions (optional)
    
    Returns:
        Dict of all inputs for resolve_visual_identity()
    """
    return {
        "work_id": work_id,
        "color_assignment": adapt_ai_reasoning(ai_reasoning),
        "cultural_weight": adapt_cultural_weight(cultural_weight),
        "external_research": adapt_external_research(external_research) if external_research else None,
        "evidence_coverage": evidence_coverage,
        "doctrine": doctrine
    }
