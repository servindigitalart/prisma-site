#!/usr/local/bin/python3
"""
Phase 2E: Cultural Consensus Engine

Captures collective cultural memory and perception of films.
This is NOT critical analysis or aesthetic theory.
This is how films are remembered, perceived, and discussed culturally.
"""

from .schema import CulturalConsensusResult
from .engine import resolve_cultural_consensus

__all__ = [
    "CulturalConsensusResult",
    "resolve_cultural_consensus"
]
