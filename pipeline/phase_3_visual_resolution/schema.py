#!/usr/bin/env python3
"""
Phase 3 Visual Resolution Schema

Defines the FINAL UX contract for visual identity resolution.
All outputs MUST conform to these types.
"""

from typing import List, Literal
from dataclasses import dataclass


# Enums for constrained outputs
TemperaturaEmocional = Literal[
    "calido_apasionado",
    "calido_nostalgico", 
    "neutral_contemplativo",
    "frio_melancolico",
    "frio_alienado"
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


@dataclass
class VisualIdentityResolution:
    """
    Final visual identity for a film.
    
    All fields are non-optional and deterministically derived
    from Phase 2 inputs.
    
    Attributes:
        work_id: Film identifier (passed through from input)
        color_iconico: Primary Doctrine color ID (e.g., "azul_nocturno")
        color_rank: Confidence score for primary color (0.0–1.0)
        colores_secundarios: Up to 3 secondary Doctrine colors (no duplicates)
        temperatura_emocional: Emotional temperature category
        ritmo_visual: Visual rhythm classification
        grado_abstraccion_visual: Abstraction level classification
    """
    work_id: str
    color_iconico: str
    color_rank: float
    colores_secundarios: List[str]
    temperatura_emocional: TemperaturaEmocional
    ritmo_visual: RitmoVisual
    grado_abstraccion_visual: GradoAbstraccionVisual
    
    def __post_init__(self):
        """Validate schema constraints."""
        # color_rank must be bounded
        if not (0.0 <= self.color_rank <= 1.0):
            raise ValueError(f"color_rank {self.color_rank} out of bounds [0.0, 1.0]")
        
        # No duplicate secondary colors
        if len(self.colores_secundarios) != len(set(self.colores_secundarios)):
            raise ValueError("colores_secundarios contains duplicates")
        
        # Secondary colors must not include iconic color
        if self.color_iconico in self.colores_secundarios:
            raise ValueError("iconic color cannot be in secondary colors")
        
        # Max 3 secondary colors
        if len(self.colores_secundarios) > 3:
            raise ValueError("colores_secundarios exceeds max 3")


def to_dict(resolution: VisualIdentityResolution) -> dict:
    """Convert resolution to serializable dict."""
    return {
        "work_id": resolution.work_id,
        "color_iconico": resolution.color_iconico,
        "color_rank": resolution.color_rank,
        "colores_secundarios": resolution.colores_secundarios,
        "temperatura_emocional": resolution.temperatura_emocional,
        "ritmo_visual": resolution.ritmo_visual,
        "grado_abstraccion_visual": resolution.grado_abstraccion_visual
    }
