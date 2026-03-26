#!/usr/local/bin/python3
"""
Phase 2: Cultural Memory Resolver
Aligned with color_doctrine.json v1.1
Uses google-genai SDK (replaces deprecated google-generativeai)
"""

import os
import json
from typing import Dict, Any, Optional
from .schema import (
    CulturalMemoryResult,
    TemperaturaEmocional,
    RitmoVisual,
    GradoAbstraccionVisual,
    PRISMA_COLOR_IDS
)
from .gemini_prompter import (
    SYSTEM_PROMPT,
    build_cultural_memory_prompt,
    extract_perception_response
)


# Map common LLM color words → official Prisma IDs (color_doctrine.json v1.1)
COLOR_NAME_TO_PRISMA = {
    # Reds
    "red": "rojo_pasional",
    "crimson": "rojo_pasional",
    "scarlet": "rojo_pasional",
    "dark red": "rojo_pasional",
    "blood red": "rojo_pasional",
    # Oranges
    "orange": "naranja_apocaliptico",
    "burnt orange": "naranja_apocaliptico",
    "fire": "naranja_apocaliptico",
    # Ambers / Yellows
    "amber": "ambar_desertico",
    "gold": "ambar_desertico",
    "golden": "ambar_desertico",
    "sepia": "ambar_desertico",
    "yellow": "amarillo_ludico",
    "bright yellow": "amarillo_ludico",
    # Greens
    "lime": "verde_lima",
    "lime green": "verde_lima",
    "light green": "verde_lima",
    "green": "verde_distopico",       # Default green → dystopic (Matrix)
    "dark green": "verde_distopico",
    "neon green": "verde_distopico",
    "acid green": "verde_distopico",
    "emerald": "verde_esmeralda",
    "emerald green": "verde_esmeralda",
    "jewel green": "verde_esmeralda",
    # Blues / Cyans
    "teal": "cian_melancolico",
    "cyan": "cian_melancolico",
    "blue green": "cian_melancolico",
    "blue": "azul_nocturno",
    "dark blue": "azul_nocturno",
    "navy": "azul_nocturno",
    "midnight blue": "azul_nocturno",
    "deep blue": "azul_nocturno",
    # Purples / Violets
    "purple": "purpura_onirico",
    "violet": "purpura_onirico",
    "lavender": "purpura_onirico",
    "electric purple": "violeta_cinetico",
    "neon purple": "violeta_cinetico",
    "electric violet": "violeta_cinetico",
    # Pinks / Magentas
    "pink": "magenta_pop",
    "hot pink": "magenta_pop",
    "magenta": "magenta_pop",
    "fuchsia": "magenta_pop",
    # Monochromes
    "black and white": "claroscuro_dramatico",
    "monochrome": "claroscuro_dramatico",
    "black": "claroscuro_dramatico",
    "white": "monocromatico_intimo",
    "grey": "monocromatico_intimo",
    "gray": "monocromatico_intimo",
}

TEMPERATURE_MAPPING = {
    "calido_apasionado": "calido_apasionado",
    "calido_nostalgico": "calido_nostalgico",
    "neutral_contemplativo": "neutral_contemplativo",
    "frio_melancolico": "frio_melancolico",
    "frio_perturbador": "frio_perturbador",
    # Legacy fallbacks
    "warm_passionate": "calido_apasionado",
    "warm_nostalgic": "calido_nostalgico",
    "neutral": "neutral_contemplativo",
    "cold_melancholic": "frio_melancolico",
    "cold_alienating": "frio_perturbador",
}

RHYTHM_MAPPING = {
    "dinamico_frenetico": "dinamico_frenetico",
    "dinamico_energico": "dinamico_energico",
    "moderado_balanceado": "moderado_balanceado",
    "lento_contemplativo": "lento_contemplativo",
    "estatico_ritualistico": "estatico_ritualistico",
    # Legacy fallbacks
    "frenetic": "dinamico_frenetico",
    "energetic": "dinamico_energico",
    "balanced": "moderado_balanceado",
    "contemplative": "lento_contemplativo",
    "meditative": "estatico_ritualistico",
}

ABSTRACTION_MAPPING = {
    "extremadamente_realista": "extremadamente_realista",
    "realista_con_estilizacion": "realista_con_estilizacion",
    "estilizado": "estilizado",
    "muy_estilizado": "muy_estilizado",
    "extremadamente_abstracto": "extremadamente_abstracto",
    # New prompt values (Step 7 rewrite)
    "hiperrealista": "extremadamente_realista",
    "realista_estilizado": "realista_con_estilizacion",
    "abstracto_experimental": "extremadamente_abstracto",
    # Legacy fallbacks
    "extremely_realistic": "extremadamente_realista",
    "realistic_with_style": "realista_con_estilizacion",
    "stylized": "estilizado",
    "very_stylized": "muy_estilizado",
    "extremely_abstract": "extremadamente_abstracto",
}


def resolve_cultural_memory(
    work: Dict[str, Any],
    use_gemini: bool = True
) -> CulturalMemoryResult:

    work_id = work.get("work_id")
    title = work.get("title")
    year = work.get("year")

    if not all([work_id, title, year]):
        raise ValueError("work_id, title, and year are required")

    if not use_gemini:
        return _create_fallback_result(work)

    prompt = build_cultural_memory_prompt(
        work_id=work_id,
        title=title,
        year=year,
        director=work.get("director"),
        countries=work.get("countries"),
        genres=work.get("genres")
    )

    try:
        llm_response = _call_gemini_api(prompt)
    except Exception as e:
        raise ValueError("Gemini API call failed: " + str(e))

    try:
        parsed = extract_perception_response(llm_response)
    except ValueError as e:
        raise ValueError("Failed to parse LLM response: " + str(e))

    # Map iconic color — LLM should return Prisma ID directly, fallback to name mapping
    iconic_color = _resolve_color_id(parsed["iconic_color"])

    # Map secondary colors (up to 3)
    secondary_colors = [
        _resolve_color_id(c)
        for c in parsed.get("secondary_colors", [])
        if c and c.lower() not in ["none", ""]
    ][:3]

    # Extract Gemini's raw numeric score
    gemini_raw_score = float(parsed["color_rank"])
    color_rank_reasoning = parsed["color_rank_reasoning"]
    
    # Apply cultural weight adjustments
    color_rank = apply_cultural_weight(gemini_raw_score, work)

    visual_rhythm = RHYTHM_MAPPING.get(
        parsed.get("visual_rhythm", "moderado_balanceado"),
        "moderado_balanceado"
    )

    emotional_temperature = TEMPERATURE_MAPPING.get(
        parsed.get("emotional_temperature", "neutral_contemplativo"),
        "neutral_contemplativo"
    )

    abstraction_level = ABSTRACTION_MAPPING.get(
        parsed.get("abstraction_level", "estilizado"),
        "estilizado"
    )

    return CulturalMemoryResult(
        work_id=work_id,
        iconic_color=iconic_color,
        color_rank=color_rank,
        gemini_raw_score=gemini_raw_score,
        color_rank_reasoning=color_rank_reasoning,
        secondary_colors=secondary_colors,
        visual_rhythm=visual_rhythm,
        emotional_temperature=emotional_temperature,
        abstraction_level=abstraction_level,
        supporting_evidence=parsed.get("supporting_evidence", []),
        llm_raw_response=llm_response
    )


def _resolve_color_id(color_input: str) -> str:
    """
    Resolve color input to official Prisma ID.
    Accepts either a Prisma ID directly or a common color name.
    """
    color_lower = color_input.lower().strip()

    # If it's already a valid Prisma ID, use it directly
    if color_lower in PRISMA_COLOR_IDS:
        return color_lower

    # Try direct name mapping
    if color_lower in COLOR_NAME_TO_PRISMA:
        return COLOR_NAME_TO_PRISMA[color_lower]

    # Partial match
    for key, value in COLOR_NAME_TO_PRISMA.items():
        if key in color_lower or color_lower in key:
            return value

    # Last resort fallback
    print(f"  ⚠️  Unknown color '{color_input}' — defaulting to azul_nocturno")
    return "azul_nocturno"


def apply_cultural_weight(
    gemini_raw_score: float,
    work: Dict[str, Any]
) -> float:
    """
    Applies a subtle prestige adjustment to the raw Gemini score.
    
    Design principle: adjustments are small (+/- 0.05 max) so Gemini's
    assessment remains the dominant signal. Cultural weight breaks ties,
    it does not override Gemini's judgment.
    
    Adjustments:
      +0.02 for Criterion Collection membership (definitive arthouse canon)
      +0.02 for major festival win (Palme d'Or, Golden Lion, Golden Bear only)
      -0.05 for films from 2023+ (very recent - memory still forming)
      -0.03 for films from 2020-2022
      -0.02 for films from 2017-2019
      -0.01 for films from 2015-2016
    
    Returns clamped score between 0.0 and 1.0.
    """
    adjustment = 0.0
    year = work.get("year", 2000)
    
    # --- PRESTIGE SIGNALS (max total boost: +0.04) ---
    
    # Criterion Collection: definitive arthouse canon signal
    if work.get("is_criterion", False) or work.get("criterion_title", False):
        adjustment += 0.02
    
    # Major festival win (Palme d'Or, Golden Lion, Golden Bear only)
    # NOT nominations, NOT secondary prizes
    if work.get("top_festival_win", False):
        adjustment += 0.02
    
    # --- UNCERTAINTY SIGNALS (max total penalty: -0.05) ---
    
    # Recency penalty: cultural memory not yet settled for recent films
    if year >= 2023:
        adjustment -= 0.05   # very recent — memory still forming
    elif year >= 2020:
        adjustment -= 0.03
    elif year >= 2017:
        adjustment -= 0.02
    elif year >= 2015:
        adjustment -= 0.01
    
    # MUBI removed from boost — MUBI catalog is too large to be a
    # meaningful prestige signal at this stage
    
    # Apply adjustment and clamp strictly to [0.0, 1.0]
    adjusted_score = gemini_raw_score + adjustment
    final_score = max(0.0, min(1.0, adjusted_score))
    
    return round(final_score, 4)


def normalize_color_rankings(films_with_scores: list) -> list:
    """
    Called once per color when building the color ranking page.
    Normalizes scores within a color so the top film = 1.000 
    and all others are proportionally ranked below it.
    
    This ensures:
    - Within azul_nocturno: Three Colors: Blue might be 1.000, 
      Blade Runner 0.947, some random blue film 0.723
    - Within rojo_pasional: In the Mood for Love might be 1.000,
      Her 0.891, a lesser red film 0.654
    
    The raw color_rank scores remain unchanged in the DB.
    Normalized scores are computed at query time for display only.
    
    Args:
        films_with_scores: List of dicts with at least {"color_rank": float}
    
    Returns:
        Same list with added "normalized_rank" field, sorted by normalized_rank desc
    """
    if not films_with_scores:
        return films_with_scores
    
    scores = [f.get("color_rank", 0.0) for f in films_with_scores]
    max_score = max(scores) if scores else 0.0
    
    if max_score == 0:
        return films_with_scores
    
    for film in films_with_scores:
        film["normalized_rank"] = round(film.get("color_rank", 0.0) / max_score, 4)
    
    return sorted(films_with_scores, key=lambda x: x.get("normalized_rank", 0.0), reverse=True)


def _call_gemini_api(prompt: str) -> str:
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )

    if not response.text:
        raise ValueError("Empty response from Gemini API")

    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def _create_fallback_result(work: Dict[str, Any]) -> CulturalMemoryResult:
    return CulturalMemoryResult(
        work_id=work["work_id"],
        iconic_color="azul_nocturno",
        color_rank=0.30,
        gemini_raw_score=0.30,
        color_rank_reasoning="Fallback result - Gemini not used",
        secondary_colors=[],
        visual_rhythm="moderado_balanceado",
        emotional_temperature="neutral_contemplativo",
        abstraction_level="estilizado",
        supporting_evidence=["Fallback result - Gemini not used"],
        llm_raw_response="N/A - fallback mode"
    )


def should_use_consensus(result: CulturalMemoryResult) -> bool:
    """Check if consensus is strong enough to use (backward compatibility helper)"""
    if result.color_rank < 0.75:
        return False

    uncertain_phrases = ["no clear", "unclear", "ambiguous", "not strongly"]
    for evidence in result.supporting_evidence:
        if any(phrase in evidence.lower() for phrase in uncertain_phrases):
            return False

    if len(result.supporting_evidence) < 2:
        return False

    return True
