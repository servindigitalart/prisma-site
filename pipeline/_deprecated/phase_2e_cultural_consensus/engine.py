#!/usr/bin/env python3
"""
Phase 2E Cultural Consensus Engine

Core logic for aggregating cultural signals and resolving consensus descriptors.

This is a rule-based, deterministic system that maps cultural signals
(derived from title, year, genre, country) to consensus outputs.

NO external APIs. NO ML inference. NO heuristics.
"""

from typing import Dict, Any, List, Set
from .schema import (
    CulturalConsensusResult,
    TemperaturaEmocional,
    RitmoVisual,
    GradoAbstraccionVisual
)


def resolve_cultural_consensus(work: Dict[str, Any]) -> CulturalConsensusResult:
    """
    Resolve cultural consensus for a film from minimal metadata.
    
    Args:
        work: Film metadata dict with keys:
            - work_id (str, required)
            - title (str, required)
            - year (int, optional)
            - countries (list[str], optional)
            - genres (list[str], optional)
            - description (str, optional)
    
    Returns:
        CulturalConsensusResult with color consensus, strength, and perceptual fields
    
    Implementation:
        - Extracts cultural signals from metadata
        - Maps signals to color, rhythm, temperature, abstraction
        - Calculates consensus strength based on signal clarity
        - Returns deterministic result
    """
    
    work_id = work.get("work_id", "unknown")
    title = work.get("title", "").lower()
    year = work.get("year")
    countries = work.get("countries", [])
    genres = work.get("genres", [])
    description = work.get("description", "").lower()
    
    # Extract cultural signals
    signals = _extract_cultural_signals(title, year, countries, genres, description)
    
    # Resolve color consensus
    color_consensus = _resolve_color_from_signals(signals)
    
    # Calculate consensus strength
    color_consensus_strength = _calculate_consensus_strength(signals, color_consensus)
    
    # Resolve perceptual fields
    perceived_ritmo = _resolve_ritmo_from_signals(signals)
    perceived_temperatura = _resolve_temperatura_from_signals(signals)
    perceived_abstraccion = _resolve_abstraccion_from_signals(signals)
    
    # Supporting terms = all unique signals found
    supporting_terms = sorted(list(signals))
    
    return CulturalConsensusResult(
        work_id=work_id,
        color_consensus=color_consensus,
        color_consensus_strength=color_consensus_strength,
        perceived_ritmo_visual=perceived_ritmo,
        perceived_temperatura_emocional=perceived_temperatura,
        perceived_grado_abstraccion=perceived_abstraccion,
        supporting_terms=supporting_terms
    )


def _extract_cultural_signals(
    title: str,
    year: int,
    countries: List[str],
    genres: List[str],
    description: str
) -> Set[str]:
    """
    Extract cultural signals from film metadata.
    
    Signals are keywords that carry cultural meaning:
    - Color terms in title ("red", "blue", "black")
    - Genre conventions ("noir", "western", "horror")
    - Cultural markers ("neon", "desert", "urban")
    - Temporal markers ("80s", "vintage", "modern")
    - Aesthetic markers ("surreal", "realistic", "stylized")
    
    Returns:
        Set of signal strings (lowercase, normalized)
    """
    
    signals = set()
    combined_text = f"{title} {description}".lower()
    
    # Color signals in title/description
    color_keywords = {
        "red": "red", "rouge": "red", "rojo": "red", "crimson": "red", "scarlet": "red",
        "blue": "blue", "bleu": "blue", "azul": "blue", "cyan": "cyan",
        "green": "green", "vert": "green", "verde": "green",
        "yellow": "yellow", "jaune": "yellow", "amarillo": "yellow", "golden": "golden",
        "orange": "orange", "amber": "amber",
        "purple": "purple", "violet": "violet", "violeta": "violet",
        "pink": "pink", "magenta": "magenta",
        "white": "white", "blanc": "white", "blanco": "white",
        "black": "black", "noir": "noir", "negro": "black",
        "grey": "grey", "gray": "grey", "gris": "grey"
    }
    
    for keyword, signal in color_keywords.items():
        if keyword in combined_text:
            signals.add(signal)
    
    # Genre-based signals
    genre_signals = {
        "neo_noir": ["noir", "urban", "night", "rain"],
        "noir": ["noir", "night", "shadow"],
        "science_fiction": ["neon", "cyberpunk", "future", "space"],
        "horror": ["dark", "shadow", "nightmare"],
        "western": ["desert", "dust", "sunset"],
        "romance": ["warm", "intimate", "soft"],
        "action": ["dynamic", "fast", "intense"],
        "thriller": ["tense", "dark", "moody"],
        "drama": ["contemplative", "intimate"],
        "comedy": ["bright", "playful", "light"],
        "fantasy": ["dreamlike", "surreal", "magical"],
        "experimental": ["abstract", "surreal", "avant-garde"],
        "documentary": ["realistic", "observational"]
    }
    
    for genre in genres:
        genre_lower = genre.lower()  # Fixed: removed .replace("_", " ") to match dictionary keys
        if genre_lower in genre_signals:
            signals.update(genre_signals[genre_lower])
    
    # Aesthetic markers in description
    aesthetic_keywords = [
        "neon", "rain", "desert", "urban", "night", "day", "sunset", "sunrise",
        "chaos", "calm", "frenetic", "slow", "fast", "static", "kinetic",
        "surreal", "dreamlike", "realistic", "stylized", "abstract",
        "warm", "cold", "hot", "cool", "passionate", "melancholic",
        "nostalgic", "modern", "vintage", "retro", "futuristic",
        "intimate", "distant", "isolated", "crowded",
        "violent", "peaceful", "tense", "relaxed",
        "industrial", "organic", "natural", "artificial"
    ]
    
    for keyword in aesthetic_keywords:
        if keyword in combined_text:
            signals.add(keyword)
    
    # Temporal/era markers
    if year:
        if 1920 <= year < 1940:
            signals.add("classic-era")
        elif 1940 <= year < 1960:
            signals.add("noir-era")
        elif 1960 <= year < 1980:
            signals.add("new-wave-era")
        elif 1980 <= year < 2000:
            signals.add("80s-90s")
        elif 2000 <= year < 2020:
            signals.add("modern")
        else:
            signals.add("contemporary")
    
    # Country-based signals
    country_signals = {
        "HK": ["hong-kong", "neon", "urban"],
        "JP": ["japanese", "stylized"],
        "KR": ["korean"],
        "FR": ["french", "contemplative"],
        "IT": ["italian"],
        "DE": ["german"],
        "MX": ["mexican"],
        "IN": ["indian"]
    }
    
    for country in countries:
        if country in country_signals:
            signals.update(country_signals[country])
    
    return signals


def _resolve_color_from_signals(signals: Set[str]) -> str:
    """
    Map cultural signals to Prisma color identifier.
    
    Uses deterministic priority:
    1. Explicit color mentions (highest priority)
    2. Genre conventions
    3. Aesthetic markers
    4. Default fallback
    
    Returns:
        Prisma color ID string
    """
    
    # Direct color mappings (highest priority) — v1.2 canonical Prisma IDs
    direct_color_map = {
        "red": "rojo_pasional",
        "blue": "azul_nocturno",
        "green": "verde_esmeralda",
        "yellow": "amarillo_ludico",
        "golden": "ambar_desertico",
        "amber": "ambar_desertico",
        "orange": "naranja_apocaliptico",
        "purple": "purpura_onirico",
        "violet": "purpura_onirico",
        "magenta": "magenta_pop",
        "pink": "magenta_pop",
        "cyan": "cian_melancolico",
        "noir": "azul_nocturno",
        "black": "negro_abismo",
        "grey": "titanio_mecanico",
        "white": "blanco_polar",
    }
    
    # Check direct color signals first
    for signal in signals:
        if signal in direct_color_map:
            return direct_color_map[signal]
    
    # Genre/aesthetic-based inference
    if "neon" in signals or "cyberpunk" in signals:
        return "azul_nocturno"

    if "desert" in signals or "sunset" in signals:
        return "ambar_desertico"

    if "night" in signals or "urban" in signals or "rain" in signals:
        return "azul_nocturno"

    if "warm" in signals or "nostalgic" in signals:
        return "ambar_desertico"

    if "surreal" in signals or "dreamlike" in signals:
        return "purpura_onirico"

    if "natural" in signals or "organic" in signals:
        return "verde_esmeralda"

    if "passionate" in signals or "violent" in signals or "intense" in signals:
        return "rojo_pasional"

    # Default fallback
    return "azul_nocturno"


def _calculate_consensus_strength(signals: Set[str], color: str) -> float:
    """
    Calculate consensus strength (0.0–1.0) based on signal clarity.
    
    High strength = many signals agree on same color family
    Low strength = few signals, or conflicting signals
    
    Args:
        signals: Set of cultural signals
        color: Resolved color ID
    
    Returns:
        Float between 0.0 and 1.0
    """
    
    # Base strength from signal count
    signal_count = len(signals)
    if signal_count == 0:
        return 0.3  # Minimal data
    elif signal_count < 3:
        base_strength = 0.4
    elif signal_count < 6:
        base_strength = 0.6
    elif signal_count < 10:
        base_strength = 0.75
    else:
        base_strength = 0.85
    
    # Boost for direct color mentions
    color_keywords = {"red", "blue", "green", "yellow", "golden", "noir", "black", "white", "grey"}
    direct_color_count = len(signals & color_keywords)
    if direct_color_count >= 2:
        base_strength += 0.10
    elif direct_color_count == 1:
        base_strength += 0.05
    
    # Boost for genre coherence
    genre_markers = {"noir", "cyberpunk", "desert", "night", "surreal", "dreamlike"}
    coherent_genre = len(signals & genre_markers) >= 2
    if coherent_genre:
        base_strength += 0.05
    
    # Cap at 1.0
    return min(1.0, base_strength)


def _resolve_ritmo_from_signals(signals: Set[str]) -> RitmoVisual:
    """
    Map cultural signals to perceived visual rhythm.
    
    Returns:
        RitmoVisual enum value
    """
    
    # Fast/frenetic signals
    if any(s in signals for s in ["frenetic", "chaos", "fast", "kinetic"]):
        return "dinamico_frenético"
    
    # Dynamic/energetic signals
    if any(s in signals for s in ["dynamic", "intense", "violent", "urban"]):
        return "dinamico_energético"
    
    # Slow/contemplative signals
    if any(s in signals for s in ["slow", "contemplative", "intimate", "nostalgic"]):
        return "lento_contemplativo"
    
    # Static/meditative signals
    if any(s in signals for s in ["static", "calm", "peaceful", "observational"]):
        return "estático_meditativo"
    
    # Default: balanced
    return "moderado_balanceado"


def _resolve_temperatura_from_signals(signals: Set[str]) -> TemperaturaEmocional:
    """
    Map cultural signals to perceived emotional temperature.
    
    Returns:
        TemperaturaEmocional enum value
    """
    
    # Hot/passionate signals
    if any(s in signals for s in ["passionate", "violent", "intense", "red", "chaos"]):
        return "calido_apasionado"
    
    # Warm/nostalgic signals
    if any(s in signals for s in ["warm", "nostalgic", "golden", "intimate", "sunset"]):
        return "calido_nostalgico"
    
    # Cold/alienated signals
    if any(s in signals for s in ["isolated", "distant", "cyberpunk", "urban", "noir"]):
        return "frio_alienado"
    
    # Cold/melancholic signals
    if any(s in signals for s in ["melancholic", "rain", "night", "blue", "contemplative"]):
        return "frio_melancolico"
    
    # Default: neutral/contemplative
    return "neutral_contemplativo"


def _resolve_abstraccion_from_signals(signals: Set[str]) -> GradoAbstraccionVisual:
    """
    Map cultural signals to perceived abstraction level.
    
    Returns:
        GradoAbstraccionVisual enum value
    """
    
    # Extremely abstract signals
    if any(s in signals for s in ["abstract", "surreal", "dreamlike", "avant-garde"]):
        return "extremadamente_abstracto"
    
    # Highly stylized signals
    if any(s in signals for s in ["stylized", "neon", "cyberpunk", "artificial"]):
        return "muy_estilizado"
    
    # Stylized (moderate)
    if any(s in signals for s in ["noir", "retro", "vintage"]):
        return "estilizado"
    
    # Realistic with stylization
    if any(s in signals for s in ["realistic", "intimate", "natural"]):
        return "realista_con_estilizacion"
    
    # Extremely realistic
    if any(s in signals for s in ["documentary", "observational"]):
        return "extremadamente_realista"
    
    # Default: stylized
    return "estilizado"
