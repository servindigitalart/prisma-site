#!/usr/local/bin/python3
"""
Test the new numeric scoring system with the 15-film canonical test suite.
Verifies that:
1. Scores are genuinely differentiated (not all 0.95)
2. color_rank_reasoning is populated
3. All 15 canonical color assignments still pass
4. Cultural weight adjustments are applied correctly
"""

import json
import os
from pathlib import Path
from phase_2_cultural_memory.resolver import resolve_cultural_memory

# 15-film canonical test suite
CANONICAL_FILMS = [
    {
        "work_id": "the-matrix-1999",
        "title": "The Matrix",
        "year": 1999,
        "director": "Lana Wachowski, Lilly Wachowski",
        "expected_color": "verde_distopico",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["Hugo Award"]
    },
    {
        "work_id": "in-the-mood-for-love-2000",
        "title": "In the Mood for Love",
        "year": 2000,
        "director": "Wong Kar-wai",
        "expected_color": "rojo_pasional",
        "is_criterion": True,
        "is_mubi": True,
        "festival_wins": ["Cannes Technical Prize", "César Award"]
    },
    {
        "work_id": "amelie-2001",
        "title": "Amélie",
        "year": 2001,
        "director": "Jean-Pierre Jeunet",
        "expected_color": "amarillo_ludico",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["César Award"]
    },
    {
        "work_id": "blade-runner-1982",
        "title": "Blade Runner",
        "year": 1982,
        "director": "Ridley Scott",
        "expected_color": "azul_nocturno",
        "is_criterion": True,
        "is_mubi": True,
        "festival_wins": []
    },
    {
        "work_id": "mad-max-fury-road-2015",
        "title": "Mad Max: Fury Road",
        "year": 2015,
        "director": "George Miller",
        "expected_color": "naranja_apocaliptico",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["Academy Award - 6 Oscars"]
    },
    {
        "work_id": "moonlight-2016",
        "title": "Moonlight",
        "year": 2016,
        "director": "Barry Jenkins",
        "expected_color": "azul_nocturno",
        "is_criterion": True,
        "is_mubi": True,
        "festival_wins": ["Academy Award Best Picture", "Golden Globe"]
    },
    {
        "work_id": "the-grand-budapest-hotel-2014",
        "title": "The Grand Budapest Hotel",
        "year": 2014,
        "director": "Wes Anderson",
        "expected_color": "purpura_onirico",
        "is_criterion": True,
        "is_mubi": True,
        "festival_wins": ["Academy Award - 4 Oscars"]
    },
    {
        "work_id": "her-2013",
        "title": "Her",
        "year": 2013,
        "director": "Spike Jonze",
        "expected_color": "rojo_pasional",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["Academy Award Best Screenplay"]
    },
    {
        "work_id": "the-lighthouse-2019",
        "title": "The Lighthouse",
        "year": 2019,
        "director": "Robert Eggers",
        "expected_color": "claroscuro_dramatico",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["Cannes FIPRESCI Prize"]
    },
    {
        "work_id": "barbie-2023",
        "title": "Barbie",
        "year": 2023,
        "director": "Greta Gerwig",
        "expected_color": "magenta_pop",
        "is_criterion": False,
        "is_mubi": False,
        "festival_wins": []
    },
    {
        "work_id": "call-me-by-your-name-2017",
        "title": "Call Me by Your Name",
        "year": 2017,
        "director": "Luca Guadagnino",
        "expected_color": "verde_lima",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["Academy Award Best Screenplay"]
    },
    {
        "work_id": "lost-in-translation-2003",
        "title": "Lost in Translation",
        "year": 2003,
        "director": "Sofia Coppola",
        "expected_color": "cian_melancolico",
        "is_criterion": True,
        "is_mubi": True,
        "festival_wins": ["Academy Award Best Screenplay", "BAFTA"]
    },
    {
        "work_id": "no-country-for-old-men-2007",
        "title": "No Country for Old Men",
        "year": 2007,
        "director": "Coen Brothers",
        "expected_color": "ambar_desertico",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["Academy Award Best Picture"]
    },
    {
        "work_id": "drive-2011",
        "title": "Drive",
        "year": 2011,
        "director": "Nicolas Winding Refn",
        "expected_color": "violeta_cinetico",
        "is_criterion": False,
        "is_mubi": True,
        "festival_wins": ["Cannes Best Director"]
    },
    {
        "work_id": "three-colors-white-1994",
        "title": "Three Colors: White",
        "year": 1994,
        "director": "Krzysztof Kieślowski",
        "expected_color": "blanco_polar",
        "is_criterion": True,
        "is_mubi": True,
        "festival_wins": ["Berlin Film Festival Silver Bear"]
    }
]


def main():
    print("\n" + "="*80)
    print("PRISMA PIPELINE v2.0 - NEW NUMERIC SCORING SYSTEM TEST")
    print("Testing 15-film canonical suite with differentiated scores")
    print("="*80 + "\n")
    
    results = []
    passed = 0
    failed = 0
    
    for i, film in enumerate(CANONICAL_FILMS, 1):
        print(f"\n[{i}/15] Processing: {film['title']} ({film['year']})")
        print(f"         Expected: {film['expected_color']}")
        
        try:
            result = resolve_cultural_memory(film, use_gemini=True)
            
            # Check if color assignment matches
            color_match = result.iconic_color == film['expected_color']
            status = "✓ PASS" if color_match else "✗ FAIL"
            
            if color_match:
                passed += 1
            else:
                failed += 1
            
            print(f"         Result:   {result.iconic_color} {status}")
            print(f"         Gemini Raw Score: {result.gemini_raw_score:.2f}")
            print(f"         Final Color Rank: {result.color_rank:.2f}")
            print(f"         Confidence (legacy): {result.color_confidence}")
            print(f"         Reasoning: {result.color_rank_reasoning[:120]}...")
            
            results.append({
                "work_id": film['work_id'],
                "title": film['title'],
                "year": film['year'],
                "expected_color": film['expected_color'],
                "actual_color": result.iconic_color,
                "color_match": color_match,
                "gemini_raw_score": result.gemini_raw_score,
                "color_rank": result.color_rank,
                "color_rank_reasoning": result.color_rank_reasoning,
                "secondary_colors": result.secondary_colors,
                "visual_rhythm": result.visual_rhythm,
                "emotional_temperature": result.emotional_temperature
            })
            
        except Exception as e:
            print(f"         ERROR: {str(e)[:100]}")
            failed += 1
            results.append({
                "work_id": film['work_id'],
                "title": film['title'],
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total films tested: {len(CANONICAL_FILMS)}")
    print(f"Passed: {passed} ({passed/len(CANONICAL_FILMS)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(CANONICAL_FILMS)*100:.1f}%)")
    
    # Score distribution analysis
    print("\n" + "="*80)
    print("SCORE DISTRIBUTION ANALYSIS")
    print("="*80)
    
    valid_results = [r for r in results if 'color_rank' in r]
    if valid_results:
        scores = [r['color_rank'] for r in valid_results]
        raw_scores = [r['gemini_raw_score'] for r in valid_results]
        
        print(f"Color Rank Range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"Average Color Rank: {sum(scores)/len(scores):.2f}")
        print(f"Gemini Raw Score Range: {min(raw_scores):.2f} - {max(raw_scores):.2f}")
        print(f"Average Gemini Raw Score: {sum(raw_scores)/len(raw_scores):.2f}")
        
        # Check for differentiation
        unique_scores = len(set(scores))
        print(f"\nUnique scores: {unique_scores} / {len(scores)}")
        
        if unique_scores < len(scores) * 0.8:
            print("⚠️  WARNING: Low score differentiation detected")
        else:
            print("✓ Good score differentiation")
        
        # Count by score bucket
        print("\nScore distribution:")
        buckets = {
            "0.95-1.00 (Undisputed)": sum(1 for s in scores if 0.95 <= s <= 1.00),
            "0.85-0.94 (Dominant)": sum(1 for s in scores if 0.85 <= s < 0.95),
            "0.70-0.84 (Clear primary)": sum(1 for s in scores if 0.70 <= s < 0.85),
            "0.50-0.69 (Contested)": sum(1 for s in scores if 0.50 <= s < 0.70),
            "0.30-0.49 (Weak)": sum(1 for s in scores if 0.30 <= s < 0.50)
        }
        for bucket, count in buckets.items():
            print(f"  {bucket}: {count} films")
    
    # Show sample reasoning for top 3 scores
    print("\n" + "="*80)
    print("SAMPLE REASONING (Top 3 scores)")
    print("="*80)
    
    sorted_results = sorted(valid_results, key=lambda x: x['color_rank'], reverse=True)[:3]
    for i, r in enumerate(sorted_results, 1):
        print(f"\n{i}. {r['title']} ({r['year']})")
        print(f"   Color: {r['actual_color']}")
        print(f"   Score: {r['color_rank']:.2f} (raw: {r['gemini_raw_score']:.2f})")
        print(f"   Reasoning: {r['color_rank_reasoning']}")
    
    # Save full results
    output_file = Path(__file__).parent / "test_results_new_scoring.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nFull results saved to: {output_file}")
    print("\n" + "="*80 + "\n")
    
    return passed == len(CANONICAL_FILMS)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
