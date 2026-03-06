#!/usr/bin/env python3
"""
Phase 2E Cultural Consensus — Dry Run Test

Evaluates the Cultural Consensus Engine over 6 canonical films.
NO assertions. NO pytest. Human-readable output only.

Run with:
    python3 pipeline/tests/test_phase_2e_cultural_consensus_dry_run.py
"""

import json
import sys
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase_2e_cultural_consensus import resolve_cultural_consensus, schema

to_dict = schema.to_dict


# Test film definitions ----------------------------------------------------------------

films = [
    {
        "work_id": "work_in_the_mood_for_love_2000",
        "title": "In the Mood for Love",
        "year": 2000,
        "countries": ["HK"],
        "genres": ["romance", "drama"],
        "description": "Two neighbors form a strong bond after both suspect extramarital activities of their spouses."
    },
    
    {
        "work_id": "work_mad_max_fury_road_2015",
        "title": "Mad Max: Fury Road",
        "year": 2015,
        "countries": ["AU", "US"],
        "genres": ["action", "science_fiction"],
        "description": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max."
    },
    
    {
        "work_id": "work_eraserhead_1977",
        "title": "Eraserhead",
        "year": 1977,
        "countries": ["US"],
        "genres": ["horror", "experimental"],
        "description": "Henry Spencer tries to survive his industrial environment, his angry girlfriend, and the unbearable screams of his newly born mutant child."
    },
    
    {
        "work_id": "work_the_lighthouse_2019",
        "title": "The Lighthouse",
        "year": 2019,
        "countries": ["US", "CA"],
        "genres": ["horror", "drama"],
        "description": "Two lighthouse keepers try to maintain their sanity while living on a remote and mysterious New England island in the 1890s."
    },
    
    {
        "work_id": "work_uncut_gems_2019",
        "title": "Uncut Gems",
        "year": 2019,
        "countries": ["US"],
        "genres": ["thriller", "crime"],
        "description": "With his debts mounting and angry collectors closing in, a fast-talking New York City jeweler risks everything in hope of staying afloat and alive."
    },
    
    {
        "work_id": "work_mulholland_drive_2001",
        "title": "Mulholland Drive",
        "year": 2001,
        "countries": ["US", "FR"],
        "genres": ["mystery", "thriller"],
        "description": "After a car wreck on the winding Mulholland Drive renders a woman amnesiac, she and a perky Hollywood-hopeful search for clues and answers across Los Angeles in a twisting venture beyond dreams and reality."
    }
]


# Runner and reporter ------------------------------------------------------------------

def run_and_print(film: dict):
    """Run consensus engine and print results."""
    print("\n" + "=" * 80)
    print(f"Film: {film['title']} ({film['year']})")
    print("=" * 80)
    
    try:
        result = resolve_cultural_consensus(film)
        
        print(f"\n✓ Cultural Consensus Resolved:")
        print(f"  color_consensus: {result.color_consensus}")
        print(f"  color_consensus_strength: {result.color_consensus_strength:.2f}")
        print(f"  perceived_ritmo_visual: {result.perceived_ritmo_visual}")
        print(f"  perceived_temperatura_emocional: {result.perceived_temperatura_emocional}")
        print(f"  perceived_grado_abstraccion: {result.perceived_grado_abstraccion}")
        print(f"  supporting_terms: {result.supporting_terms[:10]}...")  # Show first 10
        
        print(f"\n✓ Output JSON:")
        print(json.dumps(to_dict(result), indent=2))
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def summarize_results(results):
    """Print comparative summary."""
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Color consensus distribution
    print("\nColor Consensus Distribution:")
    color_counts = {}
    for title, res in results:
        if res:
            color_counts[res.color_consensus] = color_counts.get(res.color_consensus, 0) + 1
    for color, count in sorted(color_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {color}: {count} film(s)")
    
    # Consensus strength ranges
    print("\nConsensus Strength Ranges:")
    strong = [(t, r.color_consensus_strength) for t, r in results if r and r.color_consensus_strength >= 0.70]
    moderate = [(t, r.color_consensus_strength) for t, r in results if r and 0.50 <= r.color_consensus_strength < 0.70]
    weak = [(t, r.color_consensus_strength) for t, r in results if r and r.color_consensus_strength < 0.50]
    
    print(f"  Strong (≥0.70): {len(strong)} film(s)")
    for t, s in strong:
        print(f"    - {t}: {s:.2f}")
    
    print(f"  Moderate (0.50–0.70): {len(moderate)} film(s)")
    for t, s in moderate:
        print(f"    - {t}: {s:.2f}")
    
    print(f"  Weak (<0.50): {len(weak)} film(s)")
    for t, s in weak:
        print(f"    - {t}: {s:.2f}")
    
    # Rhythm distribution
    print("\nPerceived Rhythm Distribution:")
    ritmo_counts = {}
    for title, res in results:
        if res:
            ritmo_counts[res.perceived_ritmo_visual] = ritmo_counts.get(res.perceived_ritmo_visual, 0) + 1
    for ritmo, count in sorted(ritmo_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ritmo}: {count} film(s)")
    
    # Temperature distribution
    print("\nPerceived Temperature Distribution:")
    temp_counts = {}
    for title, res in results:
        if res:
            temp_counts[res.perceived_temperatura_emocional] = temp_counts.get(res.perceived_temperatura_emocional, 0) + 1
    for temp, count in sorted(temp_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {temp}: {count} film(s)")
    
    # Abstraction distribution
    print("\nPerceived Abstraction Distribution:")
    abs_counts = {}
    for title, res in results:
        if res:
            abs_counts[res.perceived_grado_abstraccion] = abs_counts.get(res.perceived_grado_abstraccion, 0) + 1
    for abs_level, count in sorted(abs_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {abs_level}: {count} film(s)")


def main():
    """Run all test cases."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + "Phase 2E: Cultural Consensus Engine — DRY RUN".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    
    results = []
    
    for film in films:
        result = run_and_print(film)
        results.append((film["title"], result))
    
    summarize_results(results)
    
    print("\n" + "=" * 80)
    print("✓ All test cases completed")
    print("=" * 80)
    print("\nNOTE: This is a dry-run evaluation (no assertions)")
    print("Review outputs above for cultural coherence\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
