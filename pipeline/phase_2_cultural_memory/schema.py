#!/usr/bin/env python3
"""
Phase 2: Cultural Memory Schema
Aligned with color_doctrine.json v1.3 — 18 colors
"""

from typing import List, Literal, Optional
from dataclasses import dataclass


TemperaturaEmocional = Literal[
    "calido_apasionado",
    "calido_nostalgico",
    "neutral_contemplativo",
    "frio_melancolico",
    "frio_perturbador"
]

RitmoVisual = Literal[
    "dinamico_frenetico",
    "dinamico_energico",
    "moderado_balanceado",
    "lento_contemplativo",
    "estatico_ritualistico"
]

GradoAbstraccionVisual = Literal[
    "extremadamente_realista",
    "realista_con_estilizacion",
    "estilizado",
    "muy_estilizado",
    "extremadamente_abstracto"
]

# Official Prisma palette IDs — color_doctrine.json v1.3
PRISMA_COLOR_IDS = [
    # Chromatic colors
    "rojo_pasional",
    "naranja_apocaliptico",
    "ambar_desertico",
    "amarillo_ludico",
    "verde_lima",
    "verde_esmeralda",
    "verde_distopico",
    "cian_melancolico",
    "azul_nocturno",
    "violeta_cinetico",
    "purpura_onirico",
    "magenta_pop",
    # New in v1.2
    "blanco_polar",
    "negro_abismo",
    "titanio_mecanico",
    # New in v1.3
    "rosa_pastel",
    # Monochromatic modes
    "claroscuro_dramatico",
    "monocromatico_intimo",
]


@dataclass
class CulturalMemoryResult:
    """
    Result of cultural memory resolution via Gemini LLM.
    Represents collective perception of a film's visual identity.
    
    Scoring System (v2.0 - Two-Component):
      1. Gemini numeric score (0.0-1.0) - raw AI perception confidence
      2. Cultural weight multiplier - deterministic adjustments based on canon signals
      
    Final color_rank = gemini_raw_score × cultural_weight (clamped to 0.0-1.0)
    """
    work_id: str
    iconic_color: str
    color_rank: float  # Final score after cultural weight adjustment
    gemini_raw_score: float  # Pre-adjustment Gemini score (for auditability)
    color_rank_reasoning: str  # Gemini's justification for the exact numeric score
    secondary_colors: List[str]
    visual_rhythm: RitmoVisual
    emotional_temperature: TemperaturaEmocional
    abstraction_level: GradoAbstraccionVisual
    supporting_evidence: List[str]
    llm_raw_response: str
    
    # Legacy field for backward compatibility (mapped from color_rank)
    @property
    def color_consensus_strength(self) -> float:
        """Alias for color_rank to maintain backward compatibility"""
        return self.color_rank
    
    @property
    def color_confidence(self) -> str:
        """Legacy field: maps color_rank to high/medium/low for backward compatibility"""
        if self.color_rank >= 0.85:
            return "high"
        elif self.color_rank >= 0.70:
            return "medium"
        else:
            return "low"

    def __post_init__(self):
        if not (0.0 <= self.color_rank <= 1.0):
            raise ValueError(
                f"color_rank {self.color_rank} out of bounds [0.0, 1.0]"
            )
        if not (0.0 <= self.gemini_raw_score <= 1.0):
            raise ValueError(
                f"gemini_raw_score {self.gemini_raw_score} out of bounds [0.0, 1.0]"
            )
        if len(self.secondary_colors) > 3:
            raise ValueError("secondary_colors exceeds max 3")
        if not self.supporting_evidence:
            raise ValueError("supporting_evidence cannot be empty")

    @property
    def reasoning(self) -> str:
        return "; ".join(self.supporting_evidence) if self.supporting_evidence else ""

    @property
    def sources_cited(self) -> List[str]:
        return self.supporting_evidence

    @property
    def color_temperature(self) -> str:
        if "calido" in self.emotional_temperature:
            return "WARM"
        elif "frio" in self.emotional_temperature:
            return "COOL"
        else:
            return "NEUTRAL"


def to_dict(result: CulturalMemoryResult) -> dict:
    return {
        "work_id": result.work_id,
        "iconic_color": result.iconic_color,
        "color_confidence": result.color_confidence,
        "color_consensus_strength": result.color_consensus_strength,
        "secondary_colors": result.secondary_colors,
        "visual_rhythm": result.visual_rhythm,
        "emotional_temperature": result.emotional_temperature,
        "abstraction_level": result.abstraction_level,
        "supporting_evidence": result.supporting_evidence,
        "llm_raw_response": result.llm_raw_response[:500] + "..."
    }
