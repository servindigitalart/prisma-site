#!/usr/bin/env python3
"""
Canonical Test Suite for Cultural Memory Resolution

Tests the system against films with universally known iconic colors.
Expected pass rate: ≥90% on obvious cases.

Ground Truth Films:
- Barbie → rosa_melancolico (pink)
- The Matrix → verde_acido or verde_esperanza (green)
- Three Colors: Blue → azul_profundo (blue)
- Almodóvar films → rojo_pasion (red)
- Little Miss Sunshine → ambar_dorado (yellow)
- Roma → gris_industrial (monochrome)
- The Lighthouse → gris_industrial (chiaroscuro)
"""

import os
import sys
from dataclasses import dataclass
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase_2_cultural_memory import resolve_cultural_memory, should_use_consensus


@dataclass
class CanonicalFilm:
    """Ground truth film for testing"""
    tmdb_id: int
    title: str
    year: int
    genres: List[str]
    expected_color: str  # Primary expected Prisma color
    alternative_colors: List[str]  # Acceptable alternatives
    reasoning_keywords: List[str]  # Must appear in LLM reasoning
    

# Ground truth test cases
CANONICAL_FILMS = [
    CanonicalFilm(
        tmdb_id=603,
        title="The Matrix",
        year=1999,
        genres=["Science Fiction", "Action"],
        expected_color="verde_acido",
        alternative_colors=["verde_esperanza"],
        reasoning_keywords=["green", "code", "digital", "rain", "matrix"]
    ),
    CanonicalFilm(
        tmdb_id=346698,
        title="Barbie",
        year=2023,
        genres=["Comedy", "Adventure"],
        expected_color="rosa_melancolico",
        alternative_colors=[],
        reasoning_keywords=["pink", "barbie", "marketing", "poster"]
    ),
    CanonicalFilm(
        tmdb_id=597,
        title="Titanic",
        year=1997,
        genres=["Drama", "Romance"],
        expected_color="azul_profundo",
        alternative_colors=["azul_frio", "cian_melancolico"],
        reasoning_keywords=["blue", "ocean", "water", "iceberg"]
    ),
    CanonicalFilm(
        tmdb_id=389,
        title="12 Monkeys",
        year=1995,
        genres=["Science Fiction", "Thriller", "Mystery"],
        expected_color="ambar_dorado",
        alternative_colors=["sepia_vintage"],
        reasoning_keywords=["yellow", "sepia", "time", "decay"]
    ),
    CanonicalFilm(
        tmdb_id=424,
        title="Schindler's List",
        year=1993,
        genres=["Drama", "History", "War"],
        expected_color="gris_industrial",
        alternative_colors=[],
        reasoning_keywords=["black", "white", "monochrome", "holocaust"]
    ),
    CanonicalFilm(
        tmdb_id=530385,
        title="Midsommar",
        year=2019,
        genres=["Horror", "Drama", "Mystery"],
        expected_color="blanco_puro",
        alternative_colors=["amarillo_ludico"],
        reasoning_keywords=["white", "bright", "daylight", "sweden"]
    ),
    CanonicalFilm(
        tmdb_id=27205,
        title="Inception",
        year=2010,
        genres=["Action", "Science Fiction", "Mystery"],
        expected_color="azul_profundo",
        alternative_colors=["azul_nocturno", "gris_industrial"],
        reasoning_keywords=["blue", "dream", "corporate"]
    ),
]


def test_canonical_film(film: CanonicalFilm, verbose: bool = True) -> bool:
    """
    Test a single canonical film against ground truth.
    
    Returns True if test passes (expected color or acceptable alternative).
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"Testing: {film.title} ({film.year})")
        print(f"Expected: {film.expected_color}")
        if film.alternative_colors:
            print(f"Alternatives: {', '.join(film.alternative_colors)}")
        print(f"{'='*80}")
    
    try:
        # Resolve cultural memory with correct format
        work = {
            'work_id': f'tmdb_{film.tmdb_id}',
            'title': film.title,
            'year': film.year,
            'genres': film.genres,
            'director': None,  # Not provided in test data
            'countries': None
        }
        
        result = resolve_cultural_memory(
            work=work,
            use_gemini=True
        )
        
        if verbose:
            print(f"\n📊 RESULT:")
            print(f"  Iconic Color: {result.iconic_color}")
            print(f"  Secondary Colors: {', '.join(result.secondary_colors)}")
            print(f"  Consensus Strength: {result.color_consensus_strength:.2f}")
            print(f"  Visual Rhythm: {result.visual_rhythm}")
            print(f"  Temperature: {result.color_temperature}")
            print(f"  Abstraction: {result.abstraction_level}")
            print(f"\n💭 REASONING:")
            print(f"  {result.reasoning}")
            print(f"\n📚 SOURCES:")
            for source in result.sources_cited:
                print(f"  - {source}")
        
        # Check if consensus is strong enough
        has_consensus = should_use_consensus(result)
        if verbose:
            print(f"\n✅ Strong Consensus: {'YES' if has_consensus else 'NO'}")
        
        # Check if color matches expectations
        acceptable_colors = [film.expected_color] + film.alternative_colors
        color_match = result.iconic_color in acceptable_colors
        
        if verbose:
            if color_match:
                print(f"✅ COLOR MATCH: {result.iconic_color} is acceptable")
            else:
                print(f"❌ COLOR MISMATCH: Got {result.iconic_color}, expected {film.expected_color}")
        
        # Check if reasoning contains expected keywords
        reasoning_lower = result.reasoning.lower()
        keyword_matches = [kw for kw in film.reasoning_keywords if kw.lower() in reasoning_lower]
        
        if verbose:
            if keyword_matches:
                print(f"✅ REASONING KEYWORDS: Found {', '.join(keyword_matches)}")
            else:
                print(f"⚠️  REASONING KEYWORDS: None of {', '.join(film.reasoning_keywords)} found")
        
        # Test passes if:
        # 1. Color matches expectations
        # 2. Has strong consensus (≥0.75)
        # 3. At least one reasoning keyword present
        test_passed = (
            color_match and 
            has_consensus and 
            len(keyword_matches) > 0
        )
        
        if verbose:
            print(f"\n{'='*80}")
            if test_passed:
                print(f"✅ TEST PASSED for {film.title}")
            else:
                print(f"❌ TEST FAILED for {film.title}")
                if not color_match:
                    print(f"   - Color mismatch")
                if not has_consensus:
                    print(f"   - Weak consensus ({result.color_consensus_strength:.2f} < 0.75)")
                if not keyword_matches:
                    print(f"   - Missing reasoning keywords")
            print(f"{'='*80}")
        
        return test_passed
        
    except Exception as e:
        if verbose:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
        return False


def run_canonical_test_suite(verbose: bool = True):
    """
    Run the full canonical test suite.
    
    Reports pass/fail rate and detailed results.
    """
    print(f"\n{'#'*80}")
    print(f"# CANONICAL CULTURAL MEMORY TEST SUITE")
    print(f"# Testing {len(CANONICAL_FILMS)} films with universally known iconic colors")
    print(f"{'#'*80}\n")
    
    results = []
    for film in CANONICAL_FILMS:
        passed = test_canonical_film(film, verbose=verbose)
        results.append((film, passed))
    
    # Calculate statistics
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed
    pass_rate = (passed / total) * 100
    
    # Print summary
    print(f"\n{'#'*80}")
    print(f"# TEST SUMMARY")
    print(f"{'#'*80}")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"\nExpected Pass Rate: ≥90%")
    
    if pass_rate >= 90:
        print(f"✅ SUITE PASSED - System meets quality threshold")
    else:
        print(f"❌ SUITE FAILED - System below quality threshold")
        print(f"\nFailed Tests:")
        for film, passed in results:
            if not passed:
                print(f"  - {film.title} ({film.year})")
    
    print(f"{'#'*80}\n")
    
    return pass_rate >= 90


if __name__ == "__main__":
    # Check if API key is set (for informational purposes)
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("The resolver will use the key from its configuration.\n")
    
    # Run test suite with verbose output
    suite_passed = run_canonical_test_suite(verbose=True)
    
    sys.exit(0 if suite_passed else 1)
