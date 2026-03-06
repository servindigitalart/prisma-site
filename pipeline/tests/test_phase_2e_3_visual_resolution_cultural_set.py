#!/usr/bin/env python3
"""
Phase 2E → Phase 3 Integration Test — Canonical Cinematic Set

This test evaluates the flow from Cultural Consensus (Phase 2E) 
to Visual Resolution (Phase 3) using a fixed set of 13 canonical films.

This is an OBSERVATIONAL test:
- NO assertions
- NO modifications to engines
- Print-only output for expert review
- Designed to reveal discrepancies between cultural consensus and final resolution

Run with:
    python3 pipeline/tests/test_phase_2e_3_visual_resolution_cultural_set.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase_2e_cultural_consensus import resolve_cultural_consensus, schema as consensus_schema
from phase_3_visual_resolution import resolver as phase3_resolver, schema as phase3_schema

to_dict_consensus = consensus_schema.to_dict
to_dict_resolution = phase3_schema.to_dict


# Canonical film set (13 films) -------------------------------------------------------

CANONICAL_FILMS = [
    {
        "work_id": "work_little_miss_sunshine_2006",
        "title": "Little Miss Sunshine",
        "year": 2006,
        "countries": ["US"],
        "genres": ["comedy", "drama"],
        "description": "A family determined to get their young daughter into the finals of a beauty pageant take a cross-country trip in their VW bus."
    },
    
    {
        "work_id": "work_the_florida_project_2017",
        "title": "The Florida Project",
        "year": 2017,
        "countries": ["US"],
        "genres": ["drama"],
        "description": "Set over one summer, the film follows precocious six-year-old Moonee as she courts mischief and adventure with her ragtag playmates."
    },
    
    {
        "work_id": "work_trois_couleurs_blanc_1994",
        "title": "Trois couleurs: Blanc",
        "year": 1994,
        "countries": ["FR", "PL"],
        "genres": ["drama", "comedy"],
        "description": "After his wife divorces him, a Polish immigrant plots to get even with her."
    },
    
    {
        "work_id": "work_trois_couleurs_bleu_1993",
        "title": "Trois couleurs: Bleu",
        "year": 1993,
        "countries": ["FR", "PL"],
        "genres": ["drama"],
        "description": "A woman struggles to find a way to live her life after the death of her husband and child."
    },
    
    {
        "work_id": "work_mujeres_al_borde_de_un_ataque_de_nervios_1988",
        "title": "Mujeres al borde de un ataque de nervios",
        "year": 1988,
        "countries": ["ES"],
        "genres": ["comedy", "drama"],
        "description": "A television actress encounters a variety of eccentric characters after embarking on a journey to discover why her lover abruptly left her."
    },
    
    {
        "work_id": "work_barbie_2023",
        "title": "Barbie",
        "year": 2023,
        "countries": ["US"],
        "genres": ["comedy", "fantasy"],
        "description": "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land."
    },
    
    {
        "work_id": "work_roma_2018",
        "title": "Roma",
        "year": 2018,
        "countries": ["MX", "US"],
        "genres": ["drama"],
        "description": "A story that chronicles a year in the life of a middle-class family's maid in Mexico City in the early 1970s."
    },
    
    {
        "work_id": "work_solo_con_tu_pareja_1991",
        "title": "Solo con tu pareja",
        "year": 1991,
        "countries": ["MX"],
        "genres": ["comedy", "romance"],
        "description": "A womanizer is falsely diagnosed with AIDS by a jealous lover and falls in love while accepting his fate."
    },
    
    {
        "work_id": "work_the_matrix_1999",
        "title": "The Matrix",
        "year": 1999,
        "countries": ["US"],
        "genres": ["science_fiction", "action"],
        "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers."
    },
    
    {
        "work_id": "work_kill_bill_vol_1_2003",
        "title": "Kill Bill: Vol. 1",
        "year": 2003,
        "countries": ["US"],
        "genres": ["action", "thriller"],
        "description": "After awakening from a four-year coma, a former assassin wreaks vengeance on the team of assassins who betrayed her."
    },
    
    {
        "work_id": "work_moonlight_2016",
        "title": "Moonlight",
        "year": 2016,
        "countries": ["US"],
        "genres": ["drama"],
        "description": "A young African-American man grapples with his identity and sexuality while experiencing the everyday struggles of childhood, adolescence, and burgeoning adulthood."
    },
    
    {
        "work_id": "work_titane_2021",
        "title": "Titane",
        "year": 2021,
        "countries": ["FR"],
        "genres": ["horror", "thriller"],
        "description": "Following a series of unexplained crimes, a father is reunited with the son who has been missing for 10 years."
    },
    
    {
        "work_id": "work_the_substance_2024",
        "title": "The Substance",
        "year": 2024,
        "countries": ["US", "FR"],
        "genres": ["horror", "science_fiction"],
        "description": "A fading celebrity decides to use a black market drug, a cell-replicating substance that temporarily creates a younger, better version of herself."
    }
]


# Mock Phase 2A/2B inputs (minimal for Phase 3) ----------------------------------------

def make_mock_ai_reasoning(primary_color: str, confidence: float = 0.70):
    """Create minimal Phase 2A AI reasoning output."""
    return {
        "primary": {
            "color_name": primary_color,
            "confidence": confidence
        },
        "alternates": []
    }


def make_mock_cultural_weight(score: float = 50.0):
    """Create minimal Phase 2B cultural weight output."""
    return {
        "cultural_weight_score": score
    }


def make_mock_evidence_without_assignment(work_id: str, language: str = "English"):
    """Create minimal evidence coverage (no color assignment)."""
    return {
        "work_id": work_id,
        "has_color_assignment": False,
        "color_id": None,
        "secondary_colors": [],
        "language": language
    }


# Test runner --------------------------------------------------------------------------

def run_integration_test_for_film(film: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Phase 2E → Phase 3 integration for a single film.
    
    Returns:
        Dict with both Phase 2E and Phase 3 results
    """
    
    # Step 1: Resolve Cultural Consensus (Phase 2E)
    consensus = resolve_cultural_consensus(film)
    
    # Step 2: Create minimal Phase 2A/2B inputs for Phase 3
    # (In reality, these would come from earlier phases)
    ai_reasoning = make_mock_ai_reasoning(
        primary_color=consensus.color_consensus,  # Use consensus as AI input
        confidence=0.70
    )
    cultural_weight = make_mock_cultural_weight(50.0)
    evidence = make_mock_evidence_without_assignment(
        work_id=film["work_id"],
        language=film.get("countries", ["US"])[0]
    )
    
    # Step 3: Resolve Visual Identity (Phase 3)
    # NOTE: Phase 3 currently does NOT accept cultural_consensus as input
    # This test observes what WOULD happen if we passed it through AI reasoning
    resolution = phase3_resolver.resolve_visual_identity(
        work_id=film["work_id"],
        color_assignment=ai_reasoning,
        cultural_weight=cultural_weight,
        external_research=None,  # No external research for this test
        doctrine=None,
        evidence_coverage=evidence
    )
    
    return {
        "film": film,
        "consensus": consensus,
        "resolution": resolution
    }


def print_film_result(result: Dict[str, Any]):
    """Print results for a single film in human-readable format."""
    film = result["film"]
    consensus = result["consensus"]
    resolution = result["resolution"]
    
    print("\n" + "=" * 80)
    print(f"🎬 {film['title']} ({film['year']})")
    print(f"   Countries: {', '.join(film['countries'])}")
    print(f"   Genres: {', '.join(film['genres'])}")
    print("=" * 80)
    
    # Phase 2E Cultural Consensus
    print("\n📊 PHASE 2E: Cultural Consensus")
    print(f"   color_consensus:          {consensus.color_consensus}")
    print(f"   consensus_strength:       {consensus.color_consensus_strength:.2f}")
    print(f"   perceived_ritmo:          {consensus.perceived_ritmo_visual}")
    print(f"   perceived_temperatura:    {consensus.perceived_temperatura_emocional}")
    print(f"   perceived_abstraccion:    {consensus.perceived_grado_abstraccion}")
    print(f"   supporting_terms:         {consensus.supporting_terms[:8]}")
    
    # Phase 3 Visual Resolution
    print("\n🎨 PHASE 3: Visual Resolution (Final)")
    print(f"   color_iconico:            {resolution.color_iconico}")
    print(f"   color_rank:               {resolution.color_rank:.2f}")
    print(f"   colores_secundarios:      {resolution.colores_secundarios}")
    print(f"   temperatura_emocional:    {resolution.temperatura_emocional}")
    print(f"   ritmo_visual:             {resolution.ritmo_visual}")
    print(f"   grado_abstraccion:        {resolution.grado_abstraccion_visual}")
    
    # Highlight discrepancies
    discrepancies = []
    if consensus.color_consensus != resolution.color_iconico:
        discrepancies.append(
            f"COLOR MISMATCH: Consensus={consensus.color_consensus}, "
            f"Final={resolution.color_iconico}"
        )
    if consensus.perceived_ritmo_visual != resolution.ritmo_visual:
        discrepancies.append(
            f"RHYTHM MISMATCH: Consensus={consensus.perceived_ritmo_visual}, "
            f"Final={resolution.ritmo_visual}"
        )
    if consensus.perceived_temperatura_emocional != resolution.temperatura_emocional:
        discrepancies.append(
            f"TEMPERATURE MISMATCH: Consensus={consensus.perceived_temperatura_emocional}, "
            f"Final={resolution.temperatura_emocional}"
        )
    if consensus.perceived_grado_abstraccion != resolution.grado_abstraccion_visual:
        discrepancies.append(
            f"ABSTRACTION MISMATCH: Consensus={consensus.perceived_grado_abstraccion}, "
            f"Final={resolution.grado_abstraccion_visual}"
        )
    
    if discrepancies:
        print("\n⚠️  DISCREPANCIES:")
        for disc in discrepancies:
            print(f"   • {disc}")
    else:
        print("\n✅ No discrepancies (consensus matches final resolution)")


def print_summary(results: list):
    """Print comparative summary across all films."""
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    # Group by final color_iconico
    print("\n🎨 Films Grouped by Final color_iconico:")
    color_groups = {}
    for r in results:
        color = r["resolution"].color_iconico
        color_groups.setdefault(color, []).append(r["film"]["title"])
    
    for color, films in sorted(color_groups.items()):
        print(f"   {color}:")
        for film in films:
            print(f"      • {film}")
    
    # Group by ritmo_visual
    print("\n🏃 Films Grouped by ritmo_visual:")
    ritmo_groups = {}
    for r in results:
        ritmo = r["resolution"].ritmo_visual
        ritmo_groups.setdefault(ritmo, []).append(r["film"]["title"])
    
    for ritmo, films in sorted(ritmo_groups.items()):
        print(f"   {ritmo}:")
        for film in films:
            print(f"      • {film}")
    
    # Group by grado_abstraccion
    print("\n🎭 Films Grouped by grado_abstraccion_visual:")
    abs_groups = {}
    for r in results:
        abs_level = r["resolution"].grado_abstraccion_visual
        abs_groups.setdefault(abs_level, []).append(r["film"]["title"])
    
    for abs_level, films in sorted(abs_groups.items()):
        print(f"   {abs_level}:")
        for film in films:
            print(f"      • {film}")
    
    # Highlight all color mismatches
    print("\n⚠️  Color Mismatches (Consensus ≠ Final):")
    color_mismatches = []
    for r in results:
        consensus_color = r["consensus"].color_consensus
        final_color = r["resolution"].color_iconico
        if consensus_color != final_color:
            color_mismatches.append({
                "title": r["film"]["title"],
                "consensus": consensus_color,
                "final": final_color,
                "strength": r["consensus"].color_consensus_strength
            })
    
    if color_mismatches:
        for mismatch in color_mismatches:
            print(f"   • {mismatch['title']}:")
            print(f"      Consensus: {mismatch['consensus']} (strength: {mismatch['strength']:.2f})")
            print(f"      Final:     {mismatch['final']}")
    else:
        print("   (None — all films match)")
    
    # Highlight rhythm mismatches
    print("\n⚠️  Rhythm Mismatches (Consensus ≠ Final):")
    rhythm_mismatches = []
    for r in results:
        consensus_ritmo = r["consensus"].perceived_ritmo_visual
        final_ritmo = r["resolution"].ritmo_visual
        if consensus_ritmo != final_ritmo:
            rhythm_mismatches.append({
                "title": r["film"]["title"],
                "consensus": consensus_ritmo,
                "final": final_ritmo
            })
    
    if rhythm_mismatches:
        for mismatch in rhythm_mismatches:
            print(f"   • {mismatch['title']}: {mismatch['consensus']} → {mismatch['final']}")
    else:
        print("   (None — all films match)")
    
    # Consensus strength distribution
    print("\n📊 Consensus Strength Distribution:")
    strong = [r for r in results if r["consensus"].color_consensus_strength >= 0.70]
    moderate = [r for r in results if 0.50 <= r["consensus"].color_consensus_strength < 0.70]
    weak = [r for r in results if r["consensus"].color_consensus_strength < 0.50]
    
    print(f"   Strong (≥0.70):     {len(strong)} films")
    print(f"   Moderate (0.50–0.70): {len(moderate)} films")
    print(f"   Weak (<0.50):       {len(weak)} films")


def main():
    """Run integration test for all canonical films."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + "Phase 2E → Phase 3 Integration Test — Canonical Set".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print("\nThis test evaluates the flow from Cultural Consensus (Phase 2E)")
    print("to Visual Resolution (Phase 3) using 13 canonical films.")
    print("\nNOTE: This is an observational test (no assertions).")
    print("Phase 3 currently does NOT integrate Phase 2E consensus directly.")
    print("This test reveals what WOULD happen if consensus were integrated.\n")
    
    results = []
    
    for film in CANONICAL_FILMS:
        try:
            result = run_integration_test_for_film(film)
            print_film_result(result)
            results.append(result)
        except Exception as e:
            print(f"\n✗ Error processing {film['title']}: {e}")
            import traceback
            traceback.print_exc()
    
    print_summary(results)
    
    print("\n" + "=" * 80)
    print("✅ Integration test completed")
    print("=" * 80)
    print("\nINTERPRETATION GUIDE:")
    print("• Color mismatches show where cultural consensus differs from final resolution")
    print("• Strong consensus (≥0.70) suggests cultural memory is clear")
    print("• Phase 3 currently uses: Evidence > Research > AI (no consensus yet)")
    print("• Future: Phase 3 could prioritize strong consensus (≥0.70) over AI reasoning")
    print("\nFor integration strategy, see:")
    print("  pipeline/phase_2e_cultural_consensus/INTEGRATION.md\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
