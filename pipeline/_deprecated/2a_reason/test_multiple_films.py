"""
Test AI Color Reasoning with multiple films
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ai_color_agent import reason_about_color, save_reasoning_result
from review_reasoning import review_reasoning_chain, generate_human_readable_report

# Test films
test_films = [
    {
        "id": "work_amelie_2001",
        "title": "Amélie",
        "year": 2001,
        "genres": ["comedy", "romance"],
        "people": {
            "director": ["Jean-Pierre Jeunet"],
            "cinematography": ["Bruno Delbonnel"]
        }
    },
    {
        "id": "work_the_matrix_1999",
        "title": "The Matrix",
        "year": 1999,
        "genres": ["sci_fi", "action"],
        "people": {
            "director": ["Lana Wachowski", "Lilly Wachowski"],
            "cinematography": ["Bill Pope"]
        }
    },
    {
        "id": "work_mad_max_fury_road_2015",
        "title": "Mad Max: Fury Road",
        "year": 2015,
        "genres": ["action", "dystopian_sci_fi"],
        "people": {
            "director": ["George Miller"],
            "cinematography": ["John Seale"]
        }
    }
]

def test_multiple_films():
    """Test reasoning with multiple films and review compliance."""
    
    print("Testing AI Color Reasoning with Multiple Films...")
    print("="*60)
    
    results = []
    
    for film in test_films:
        print(f"\nProcessing: {film['title']} ({film['year']})")
        
        try:
            # Generate reasoning
            reasoning_result = reason_about_color(film)
            
            # Save result
            result_file = save_reasoning_result(reasoning_result)
            
            # Review compliance
            review_result = review_reasoning_chain(reasoning_result)
            
            # Display summary
            primary = reasoning_result['color_assignment']['primary']
            print(f"  Primary: {primary['color_id']} (confidence: {primary['confidence']:.2f})")
            print(f"  Status: {review_result['overall_status'].upper()}")
            print(f"  Violations: {review_result['total_violations']}")
            
            results.append({
                'film': film,
                'reasoning': reasoning_result,
                'review': review_result,
                'file': result_file
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"Total films processed: {len(results)}")
    
    compliant = sum(1 for r in results if r['review']['overall_status'] == 'compliant')
    needs_review = sum(1 for r in results if r['review']['overall_status'] == 'needs_review')
    non_compliant = sum(1 for r in results if r['review']['overall_status'] == 'non_compliant')
    
    print(f"Compliant: {compliant}")
    print(f"Needs review: {needs_review}")
    print(f"Non-compliant: {non_compliant}")
    
    # Show detailed review for any non-compliant
    for result in results:
        if result['review']['overall_status'] != 'compliant':
            print(f"\n{result['film']['title']} DETAILED REVIEW:")
            print("-" * 40)
            report = generate_human_readable_report(result['review'])
            print(report)
    
    print("\n✅ Multiple film test completed!")
    return results

if __name__ == "__main__":
    test_multiple_films()