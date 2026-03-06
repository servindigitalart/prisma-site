#!/usr/bin/env python3
"""
Test the numeric scoring system with peripheral films that should score in 0.50-0.84 range.
These are films WITH color identity but NOT iconic enough to deserve 0.90+.
"""

import json
import os
from pathlib import Path
from phase_2_cultural_memory.resolver import resolve_cultural_memory

# Peripheral film test suite - films that should NOT score 0.90+
PERIPHERAL_FILMS = [
    # Should score 0.70-0.84 (clear primary, genuinely contested)
    {
        "work_id": "kill-bill-vol1-2003",
        "title": "Kill Bill: Volume 1",
        "year": 2003,
        "director": "Quentin Tarantino",
        "expected_color": "amarillo_ludico",
        "expected_range": (0.70, 0.84),
        "note": "Yellow tracksuit is iconic but red blood competes equally"
    },
    {
        "work_id": "apocalypse-now-1979",
        "title": "Apocalypse Now",
        "year": 1979,
        "director": "Francis Ford Coppola",
        "expected_color": "naranja_apocaliptico",
        "expected_range": (0.70, 0.84),
        "note": "Napalm orange is iconic but jungle green dominates screen time"
    },
    {
        "work_id": "midnight-in-paris-2011",
        "title": "Midnight in Paris",
        "year": 2011,
        "director": "Woody Allen",
        "expected_color": "ambar_desertico",
        "expected_range": (0.65, 0.82),
        "note": "Warm amber present but no single color dominates"
    },
    {
        "work_id": "vertigo-1958",
        "title": "Vertigo",
        "year": 1958,
        "director": "Alfred Hitchcock",
        "expected_color": "verde_esmeralda",
        "expected_range": (0.72, 0.85),
        "note": "Iconic green lighting but not dominant throughout runtime"
    },
    {
        "work_id": "lost-highway-1997",
        "title": "Lost Highway",
        "year": 1997,
        "director": "David Lynch",
        "expected_color": "negro_abismo",
        "expected_range": (0.65, 0.82),
        "note": "Very dark but Lynch's palette is contested"
    },
    # Should score 0.50-0.69 (contested, weak identity)
    {
        "work_id": "pulp-fiction-1994",
        "title": "Pulp Fiction",
        "year": 1994,
        "director": "Quentin Tarantino",
        "expected_color": "ambar_desertico",
        "expected_range": (0.50, 0.69),
        "note": "Warm but genuinely no dominant color — multiple colors compete"
    },
    {
        "work_id": "garden-state-2004",
        "title": "Garden State",
        "year": 2004,
        "director": "Zach Braff",
        "expected_color": "verde_lima",
        "expected_range": (0.55, 0.75),
        "note": "Green present but naturalistic — not stylized enough for high score"
    },
    {
        "work_id": "the-godfather-1972",
        "title": "The Godfather",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "expected_color": "ambar_desertico",
        "expected_range": (0.50, 0.70),
        "note": "Warm but so desaturated multiple viewers would name different colors"
    },
]


def main():
    print("\n" + "="*80)
    print("PRISMA PIPELINE v2.0 - PERIPHERAL SCORING TEST")
    print("Testing films that should score 0.50-0.84 (not iconic enough for 0.90+)")
    print("="*80 + "\n")
    
    results = []
    passed = 0
    warnings = 0
    failed = 0
    
    for i, film in enumerate(PERIPHERAL_FILMS, 1):
        print(f"\n[{i}/{len(PERIPHERAL_FILMS)}] Processing: {film['title']} ({film['year']})")
        print(f"         Expected color: {film['expected_color']}")
        print(f"         Expected range: {film['expected_range'][0]:.2f} - {film['expected_range'][1]:.2f}")
        print(f"         Note: {film['note']}")
        
        try:
            result = resolve_cultural_memory(film, use_gemini=True)
            
            # Check if color assignment matches
            color_match = result.iconic_color == film['expected_color']
            
            # Check if score is in expected range
            in_range = film['expected_range'][0] <= result.color_rank <= film['expected_range'][1]
            above_range = result.color_rank > film['expected_range'][1]
            
            if not color_match:
                status = "✗ FAIL (WRONG COLOR)"
                failed += 1
            elif above_range:
                status = "⚠️  HIGH (SCORE INFLATION)"
                warnings += 1
            elif in_range:
                status = "✅ PASS"
                passed += 1
            else:
                status = "⚠️  LOW (UNDERSCORED)"
                warnings += 1
            
            print(f"         Result: {result.iconic_color} - {result.color_rank:.2f} {status}")
            print(f"         Gemini Raw: {result.gemini_raw_score:.2f}")
            print(f"         Reasoning: {result.color_rank_reasoning[:120]}...")
            
            results.append({
                "work_id": film['work_id'],
                "title": film['title'],
                "year": film['year'],
                "expected_color": film['expected_color'],
                "expected_range": film['expected_range'],
                "actual_color": result.iconic_color,
                "color_match": color_match,
                "gemini_raw_score": result.gemini_raw_score,
                "color_rank": result.color_rank,
                "in_range": in_range,
                "above_range": above_range,
                "color_rank_reasoning": result.color_rank_reasoning,
                "secondary_colors": result.secondary_colors,
                "note": film['note']
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
    print(f"Total films tested: {len(PERIPHERAL_FILMS)}")
    print(f"✅ Passed (in range): {passed} ({passed/len(PERIPHERAL_FILMS)*100:.1f}%)")
    print(f"⚠️  Warnings (out of range): {warnings} ({warnings/len(PERIPHERAL_FILMS)*100:.1f}%)")
    print(f"✗ Failed (wrong color): {failed} ({failed/len(PERIPHERAL_FILMS)*100:.1f}%)")
    
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
        
        # Inflation check
        inflation_count = sum(1 for r in valid_results if r.get('above_range', False))
        if inflation_count > 0:
            print(f"\n⚠️  SCORE INFLATION DETECTED: {inflation_count} films scored above expected range")
            print("    Films with inflation:")
            for r in valid_results:
                if r.get('above_range', False):
                    print(f"      - {r['title']}: {r['color_rank']:.2f} (expected max: {r['expected_range'][1]:.2f})")
    
    # Show detailed reasoning for a few films
    print("\n" + "="*80)
    print("SAMPLE REASONING (3 films)")
    print("="*80)
    
    sample_results = valid_results[:3] if len(valid_results) >= 3 else valid_results
    for i, r in enumerate(sample_results, 1):
        print(f"\n{i}. {r['title']} ({r['year']})")
        print(f"   Color: {r['actual_color']}")
        print(f"   Score: {r['color_rank']:.2f} (raw: {r['gemini_raw_score']:.2f})")
        print(f"   Expected: {r['expected_range'][0]:.2f}-{r['expected_range'][1]:.2f}")
        print(f"   Reasoning: {r['color_rank_reasoning']}")
    
    # Save full results
    output_file = Path(__file__).parent / "test_results_peripheral_scoring.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nFull results saved to: {output_file}")
    print("\n" + "="*80 + "\n")
    
    # Return success if no failures and inflation under 30%
    success = failed == 0 and (inflation_count / len(valid_results) if valid_results else 1.0) < 0.3
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
