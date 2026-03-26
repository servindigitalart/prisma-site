#!/usr/local/bin/python3
"""
Phase 2E Cultural Consensus Schema

Defines the output contract for cultural consensus aggregation.
Reuses Phase 3 enums where applicable for consistency.
"""

from typing import List, Literal
from dataclasses import dataclass


# Import Phase 3 enums for consistency
TemperaturaEmocional = Literal[
    "calido_apasionado",
    "calido_nostalgico",
    "neutral_contemplativo",
    "frio_melancolico",
    "frio_alienado"
]

RitmoVisual = Literal[
    "dinamico_frenético",
    "dinamico_energético",
    "moderado_balanceado",
    "lento_contemplativo",
    "estático_meditativo"
]

GradoAbstraccionVisual = Literal[
    "extremadamente_realista",
    "realista_con_estilizacion",
    "estilizado",
    "muy_estilizado",
    "extremadamente_abstracto"
]


@dataclass
class CulturalConsensusResult:
    """
    Cultural consensus output for a single film.
    
    Represents collective cultural memory and perception,
    NOT critical analysis or aesthetic theory.
    
    Attributes:
        work_id: Film identifier (passed through from input)
        color_consensus: Prisma color ID from cultural memory (e.g., "rojo_pasion")
        color_consensus_strength: Clarity of cultural agreement (0.0–1.0)
        perceived_ritmo_visual: How audiences perceive pacing/rhythm
        perceived_temperatura_emocional: Emotional temperature from cultural memory
        perceived_grado_abstraccion: Perceived abstraction level
        supporting_terms: Raw cultural signals justifying outputs (list of strings)
    """
    work_id: str
    color_consensus: str
    color_consensus_strength: float
    perceived_ritmo_visual: RitmoVisual
    perceived_temperatura_emocional: TemperaturaEmocional
    perceived_grado_abstraccion: GradoAbstraccionVisual
    supporting_terms: List[str]
    
    def __post_init__(self):
        """Validate schema constraints."""
        # color_consensus_strength must be bounded
        if not (0.0 <= self.color_consensus_strength <= 1.0):
            raise ValueError(
                f"color_consensus_strength {self.color_consensus_strength} "
                f"out of bounds [0.0, 1.0]"
            )
        
        # supporting_terms should not be empty (for auditability)
        if not self.supporting_terms:
            raise ValueError("supporting_terms cannot be empty")


def to_dict(result: CulturalConsensusResult) -> dict:
    """Convert result to serializable dict."""
    return {
        "work_id": result.work_id,
        "color_consensus": result.color_consensus,
        "color_consensus_strength": result.color_consensus_strength,
        "perceived_ritmo_visual": result.perceived_ritmo_visual,
        "perceived_temperatura_emocional": result.perceived_temperatura_emocional,
        "perceived_grado_abstraccion": result.perceived_grado_abstraccion,
        "supporting_terms": result.supporting_terms
    }
