#!/usr/local/bin/python3
"""
Phase 2E Cultural Consensus Adapters

Thin adapters to convert Cultural Consensus outputs for downstream consumption.
These adapters do NOT modify logic or mutate data.
"""

from typing import Dict, Any
from .schema import CulturalConsensusResult, to_dict


def to_phase_3_input(result: CulturalConsensusResult) -> Dict[str, Any]:
    """
    Adapt Cultural Consensus output for Phase 3 Visual Resolution consumption.
    
    Phase 3 can use these fields to:
    - Override AI reasoning for iconic color (if consensus_strength >= threshold)
    - Validate perceptual fields (temperatura, ritmo, abstraccion)
    - Flag discrepancies for review
    
    Args:
        result: CulturalConsensusResult from Phase 2E
    
    Returns:
        Dict formatted for Phase 3 integration
    """
    
    return {
        "source": "cultural_consensus",
        "work_id": result.work_id,
        "color_consensus": result.color_consensus,
        "consensus_strength": result.color_consensus_strength,
        "perceived_fields": {
            "ritmo_visual": result.perceived_ritmo_visual,
            "temperatura_emocional": result.perceived_temperatura_emocional,
            "grado_abstraccion": result.perceived_grado_abstraccion
        },
        "supporting_evidence": result.supporting_terms
    }


def to_audit_format(result: CulturalConsensusResult) -> Dict[str, Any]:
    """
    Adapt Cultural Consensus output for audit/logging purposes.
    
    Includes all fields plus metadata for traceability.
    
    Args:
        result: CulturalConsensusResult from Phase 2E
    
    Returns:
        Dict formatted for audit trail
    """
    
    return {
        "phase": "2e_cultural_consensus",
        "work_id": result.work_id,
        "outputs": to_dict(result),
        "metadata": {
            "signal_count": len(result.supporting_terms),
            "consensus_threshold": "0.70",
            "deterministic": True
        }
    }


def to_json_serializable(result: CulturalConsensusResult) -> Dict[str, Any]:
    """
    Convert result to fully JSON-serializable dict (alias for to_dict).
    
    Args:
        result: CulturalConsensusResult from Phase 2E
    
    Returns:
        JSON-serializable dict
    """
    
    return to_dict(result)
