"""
Phase 2: Cultural Memory Resolution

This module resolves a film's iconic color through the lens of collective cultural memory,
prioritizing popular perception over academic analysis or genre conventions.

Key Philosophy:
- Films exist in cultural memory through marketing, posters, and collective perception
- The "iconic color" is what people think of when they hear the title
- Sources: Letterboxd descriptions, poster colors, cultural impact, popular discourse
- NOT: Cinematographer interviews, academic color theory, shot-by-shot analysis

Usage:
    from pipeline.phase_2_cultural_memory import resolve_cultural_memory, should_use_consensus
    
    result = resolve_cultural_memory(
        tmdb_id=603,
        title="The Matrix",
        year=1999,
        genres=["Science Fiction", "Action"],
        api_key="your-gemini-api-key"
    )
    
    if should_use_consensus(result):
        print(f"Cultural consensus: {result.iconic_color} (strength: {result.color_consensus_strength})")
"""

from .schema import (
    CulturalMemoryResult, 
    RitmoVisual, 
    TemperaturaEmocional, 
    GradoAbstraccionVisual
)
from .resolver import resolve_cultural_memory, should_use_consensus

__all__ = [
    'CulturalMemoryResult',
    'RitmoVisual',
    'TemperaturaEmocional',
    'GradoAbstraccionVisual',
    'resolve_cultural_memory',
    'should_use_consensus',
]
