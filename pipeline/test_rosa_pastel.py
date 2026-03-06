#!/usr/bin/env python3
"""
Test script for rosa_pastel color addition (v1.3)
Tests 5 films that should resolve to rosa_pastel
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from phase_2_cultural_memory.gemini_prompter import build_cultural_memory_prompt
from phase_2_cultural_memory.schema import PRISMA_COLOR_IDS

# Test films that should resolve to rosa_pastel
ROSA_PASTEL_TEST_FILMS = [
    {
        "work_id": "work_portrait-of-a-lady-on-fire_2019",
        "title": "Portrait of a Lady on Fire",
        "year": 2019,
        "director": "Céline Sciamma",
        "genres": ["Romance", "Drama", "Historical"],
        "countries": ["France"]
    },
    {
        "work_id": "work_carol_2015",
        "title": "Carol",
        "year": 2015,
        "director": "Todd Haynes",
        "genres": ["Romance", "Drama"],
        "countries": ["USA", "UK"]
    },
    {
        "work_id": "work_lost-in-translation_2003",
        "title": "Lost in Translation",
        "year": 2003,
        "director": "Sofia Coppola",
        "genres": ["Romance", "Drama"],
        "countries": ["USA", "Japan"]
    },
    {
        "work_id": "work_mustang_2015",
        "title": "Mustang",
        "year": 2015,
        "director": "Deniz Gamze Ergüven",
        "genres": ["Drama"],
        "countries": ["France", "Turkey"]
    },
    {
        "work_id": "work_cleo-from-5-to-7_1962",
        "title": "Cléo from 5 to 7",
        "year": 1962,
        "director": "Agnès Varda",
        "genres": ["Drama"],
        "countries": ["France"]
    }
]


def main():
    print("=" * 80)
    print("ROSA PASTEL TEST SUITE — v1.3")
    print("=" * 80)
    print()
    
    # Verify rosa_pastel is in the color list
    if "rosa_pastel" not in PRISMA_COLOR_IDS:
        print("❌ ERROR: rosa_pastel not found in PRISMA_COLOR_IDS")
        sys.exit(1)
    
    print(f"✅ rosa_pastel found in PRISMA_COLOR_IDS")
    print(f"✅ Total colors in palette: {len(PRISMA_COLOR_IDS)}")
    print()
    
    # Test prompt generation for each film
    print("-" * 80)
    print("TESTING PROMPT GENERATION")
    print("-" * 80)
    print()
    
    for film in ROSA_PASTEL_TEST_FILMS:
        print(f"Film: {film['title']} ({film['year']})")
        
        try:
            prompt = build_cultural_memory_prompt(
                work_id=film['work_id'],
                title=film['title'],
                year=film['year'],
                director=film.get('director'),
                countries=film.get('countries'),
                genres=film.get('genres')
            )
            
            # Check if rosa_pastel appears in the prompt
            if "rosa_pastel" in prompt:
                print("  ✅ rosa_pastel found in generated prompt")
            else:
                print("  ❌ rosa_pastel NOT found in generated prompt")
            
            # Check if the disambiguation rule is present
            if "rosa_pastel vs magenta_pop vs purpura_onirico" in prompt:
                print("  ✅ Disambiguation rule #9 found")
            else:
                print("  ❌ Disambiguation rule #9 NOT found")
                
        except Exception as e:
            print(f"  ❌ Error generating prompt: {e}")
        
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("1. Run canonical 15-film test to ensure no regression")
    print("2. Optionally run full AI analysis on rosa_pastel test films")
    print()


if __name__ == "__main__":
    main()
