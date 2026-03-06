# Phase 3: Visual Resolution Layer
# Deterministic, rule-based mapping from Phase 2 outputs to final UX fields.

from .resolver import resolve_visual_identity
from .schema import (
    VisualIdentityResolution,
    TemperaturaEmocional,
    RitmoVisual,
    GradoAbstraccionVisual
)

__all__ = [
    'resolve_visual_identity',
    'VisualIdentityResolution',
    'TemperaturaEmocional',
    'RitmoVisual',
    'GradoAbstraccionVisual'
]
