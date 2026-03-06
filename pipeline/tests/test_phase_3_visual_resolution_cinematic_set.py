#!/usr/bin/env python3
"""
Phase 3 Visual Resolution — Cinematic Set Dry-Run

This script runs the Phase 3 resolver over a fixed set of 10 canonical films
and prints human-readable results for expert review. This is an evaluation
harness only: no assertions, no external deps, no modifications to production
code.

Run with:
    python3 pipeline/tests/test_phase_3_visual_resolution_cinematic_set.py
"""

import json
import sys
from pathlib import Path

# Make pipeline importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase_3_visual_resolution import resolver, schema

resolve_visual_identity = resolver.resolve_visual_identity
to_dict = schema.to_dict


# Helper constructors for mock inputs -------------------------------------------------

def make_external_research(work_id: str, quality: str, findings_text: str, sources=None):
    return {
        "work_id": work_id,
        "trigger_reason": "cultural_context",
        "conducted_at": "2026-02-06T12:00:00Z",
        "sources": sources or [],
        "findings": {
            "aesthetic_discourse": {"perspectives": [findings_text]},
            "cinematographer_context": {"perspectives": [findings_text]},
            "cultural_context": {"notes": findings_text}
        },
        "conflicts": [],
        "uncertainty_flags": [],
        "research_quality": quality,
        "promotion_eligible": False
    }


def make_ai_reasoning(primary_color: str, confidence: float, alternates=None):
    return {
        "primary": {"color_name": primary_color, "confidence": confidence},
        "alternates": alternates or []
    }


def evidence_with_assignment(work_id: str, color_id: str, secondaries=None, language="English"):
    return {
        "work_id": work_id,
        "has_color_assignment": True,
        "color_id": color_id,
        "secondary_colors": secondaries or [],
        "language": language
    }


def evidence_without_assignment(work_id: str, language="English"):
    return {
        "work_id": work_id,
        "has_color_assignment": False,
        "color_id": None,
        "secondary_colors": [],
        "language": language
    }


# Cinematic set definitions -----------------------------------------------------------
films = [
    {
        "title": "Blade Runner (1982)",
        "work_id": "work_blade_runner_1982",
        "ai": make_ai_reasoning("azul_nocturno", 0.92, alternates=[{"color_name": "cian_melancolico", "confidence": 0.65}, {"color_name": "verde_distopico", "confidence": 0.58}]),
        "research": make_external_research(
            "work_blade_runner_1982",
            "HIGH",
            "night noir neon dystopia alienation cyberpunk neon lighting"
        ),
        "evidence": evidence_without_assignment("work_blade_runner_1982", language="English")
    },

    {
        "title": "In the Mood for Love (2000)",
        "work_id": "work_in_the_mood_for_love_2000",
        "ai": make_ai_reasoning("ambar_desertico", 0.75, alternates=[{"color_name": "rojo_pasional", "confidence": 0.40}]),
        "research": make_external_research(
            "work_in_the_mood_for_love_2000",
            "HIGH",
            "warmth nostalgia slow contemplative romance memory golden sunlight"
        ),
        "evidence": evidence_without_assignment("work_in_the_mood_for_love_2000", language="Chinese")
    },

    {
        "title": "Uncut Gems (2019)",
        "work_id": "work_uncut_gems_2019",
        "ai": make_ai_reasoning("magenta_pop", 0.68, alternates=[{"color_name": "naranja_apocaliptico", "confidence": 0.50}]),
        "research": make_external_research(
            "work_uncut_gems_2019",
            "HIGH",
            "frenetic chaotic fast-paced sensory overload tension anxiety"
        ),
        "evidence": evidence_without_assignment("work_uncut_gems_2019", language="English")
    },

    {
        "title": "Chungking Express (1994)",
        "work_id": "work_chungking_express_1994",
        "ai": make_ai_reasoning("magenta_pop", 0.70, alternates=[{"color_name": "amarillo_ludico", "confidence": 0.45}]),
        "research": make_external_research(
            "work_chungking_express_1994",
            "MODERATE",
            "kinetic energetic vibrant neon pop urban rhythm"
        ),
        "evidence": evidence_without_assignment("work_chungking_express_1994", language="Chinese")
    },

    {
        "title": "The Matrix (1999)",
        "work_id": "work_the_matrix_1999",
        "ai": make_ai_reasoning("verde_distopico", 0.80, alternates=[{"color_name": "azul_nocturno", "confidence": 0.60}]),
        "research": make_external_research(
            "work_the_matrix_1999",
            "HIGH",
            "cyberpunk noir green tint controlled choreography minimal movement"
        ),
        "evidence": evidence_without_assignment("work_the_matrix_1999", language="English")
    },

    {
        "title": "Eraserhead (1977)",
        "work_id": "work_eraserhead_1977",
        "ai": make_ai_reasoning("purpura_onirico", 0.60, alternates=[{"color_name": "violeta_cinetico", "confidence": 0.30}]),
        "research": make_external_research(
            "work_eraserhead_1977",
            "HIGH",
            "surreal dreamlike abstract oppressive industrial atmosphere"
        ),
        "evidence": evidence_without_assignment("work_eraserhead_1977", language="English")
    },

    {
        "title": "Mulholland Drive (2001)",
        "work_id": "work_mulholland_drive_2001",
        "ai": make_ai_reasoning("purpura_onirico", 0.66, alternates=[{"color_name": "cian_melancolico", "confidence": 0.40}]),
        "research": make_external_research(
            "work_mulholland_drive_2001",
            "MODERATE",
            "dreams surreal mystery ambiguity nonlinear narrative"
        ),
        "evidence": evidence_without_assignment("work_mulholland_drive_2001", language="English")
    },

    {
        "title": "Mad Max: Fury Road (2015)",
        "work_id": "work_mad_max_fury_road_2015",
        "ai": make_ai_reasoning("naranja_apocaliptico", 0.88, alternates=[{"color_name": "ambar_desertico", "confidence": 0.62}]),
        "research": None,
        "evidence": evidence_without_assignment("work_mad_max_fury_road_2015", language="English")
    },

    {
        "title": "Her (2013)",
        "work_id": "work_her_2013",
        "ai": make_ai_reasoning("ambar_desertico", 0.78, alternates=[{"color_name": "rojo_pasional", "confidence": 0.35}]),
        "research": make_external_research(
            "work_her_2013",
            "HIGH",
            "warmth nostalgia contemplative romance slow pacing intimacy"
        ),
        "evidence": evidence_without_assignment("work_her_2013", language="English")
    },

    {
        "title": "The Lighthouse (2019)",
        "work_id": "work_the_lighthouse_2019",
        "ai": make_ai_reasoning("gris_monocromatico", 0.58, alternates=[{"color_name": "verde_esmeralda", "confidence": 0.30}]),
        "research": make_external_research(
            "work_the_lighthouse_2019",
            "MODERATE",
            "monochrome oppressive ritualistic pacing static minimal movement"
        ),
        "evidence": evidence_without_assignment("work_the_lighthouse_2019", language="English")
    }
]


# Runner and reporter -----------------------------------------------------------------

def run_and_collect(entry):
    try:
        res = resolve_visual_identity(
            work_id=entry["work_id"],
            color_assignment=entry["ai"],
            cultural_weight={"cultural_weight_score": 50.0},
            external_research=entry.get("research"),
            doctrine=None,
            evidence_coverage=entry.get("evidence")
        )
        return res
    except Exception as e:
        print(f"Error resolving {entry['title']}: {e}")
        return None


def print_film_result(title, res):
    print("\n" + "-" * 80)
    print(f"Film: {title}")
    if res is None:
        print("  Resolution failed")
        return
    print(f"  color_iconico: {res.color_iconico}")
    print(f"  color_rank: {res.color_rank:.2f}")
    print(f"  secondary_colors: {res.colores_secundarios}")
    print(f"  temperatura_emocional: {res.temperatura_emocional}")
    print(f"  ritmo_visual: {res.ritmo_visual}")
    print(f"  grado_abstraccion_visual: {res.grado_abstraccion_visual}")


def summarize(results):
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    # Rhythm extremes
    fast = [r for t, r in results if r and r.ritmo_visual == "dinamico_frenético"]
    slow = [r for t, r in results if r and r.ritmo_visual == "lento_contemplativo"]
    static = [r for t, r in results if r and r.ritmo_visual == "estático_meditativo"]

    print(f"Extremely fast (dinamico_frenético): {[t for t, r in results if r and r.ritmo_visual == 'dinamico_frenético']}")
    print(f"Slow / contemplative (lento_contemplativo): {[t for t, r in results if r and r.ritmo_visual == 'lento_contemplativo']}")
    print(f"Static / ritualistic (estático_meditativo): {[t for t, r in results if r and r.ritmo_visual == 'estático_meditativo']}")

    # Abstraction extremes
    extremely_abstract = [t for t, r in results if r and r.grado_abstraccion_visual == "extremadamente_abstracto"]
    extremely_realist = [t for t, r in results if r and r.grado_abstraccion_visual == "extremadamente_realista"]

    print(f"High abstraction (extremadamente_abstracto): {extremely_abstract}")
    print(f"Low abstraction (extremadamente_realista): {extremely_realist}")

    # Emotional temperature spread
    temps = {}
    for t, r in results:
        if not r:
            continue
        temps.setdefault(r.temperatura_emocional, []).append(t)

    print("\nEmotional temperature spread:")
    for temp, films_list in temps.items():
        print(f"  {temp}: {films_list}")

    # Color rank distribution
    ranks = [(t, r.color_rank) for t, r in results if r]
    ranks_sorted = sorted(ranks, key=lambda x: x[1], reverse=True)
    print("\nTop color_rank by film:")
    for t, v in ranks_sorted:
        print(f"  {t}: {v:.2f}")


def main():
    print("\nPhase 3 Visual Resolution — Cinematic Set Dry-Run\n")
    collected = []
    for film in films:
        res = run_and_collect(film)
        print_film_result(film["title"], res)
        collected.append((film["title"], res))

    summarize(collected)


if __name__ == "__main__":
    sys.exit(main())
