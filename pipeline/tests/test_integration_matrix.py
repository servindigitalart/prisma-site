#!/usr/local/bin/python3
"""
Quick integration test for Cultural Memory + Phase 3

Tests The Matrix to verify:
1. Cultural memory resolves to green (verde_acido)
2. Phase 3 uses cultural memory over genre conventions
3. Confidence rank reflects cultural consensus
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase_2_cultural_memory import resolve_cultural_memory, should_use_consensus
from phase_3_visual_resolution import resolve_visual_identity


def test_matrix_integration():
    """Test The Matrix end-to-end with cultural memory"""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not set")
        return False
    
    print("\n" + "="*80)
    print("INTEGRATION TEST: The Matrix")
    print("="*80)
    
    # Film data (format for resolver)
    film = {
        'work_id': 'tmdb_603',
        'title': 'The Matrix',
        'year': 1999,
        'genres': ['Science Fiction', 'Action'],
        'director': 'The Wachowskis',
        'countries': ['USA']
    }
    
    print(f"\n📽️  Film: {film['title']} ({film['year']})")
    print(f"Genres: {', '.join(film['genres'])}")
    
    # Step 1: Resolve Cultural Memory
    print(f"\n{'─'*80}")
    print("STEP 1: Resolving Cultural Memory...")
    print("─"*80)
    
    cultural_memory = resolve_cultural_memory(
        work=film,
        use_gemini=True
    )
    
    print(f"\n📊 Cultural Memory Result:")
    print(f"  Iconic Color: {cultural_memory.iconic_color}")
    print(f"  Secondary: {', '.join(cultural_memory.secondary_colors)}")
    print(f"  Consensus Strength: {cultural_memory.color_consensus_strength:.2f}")
    print(f"  Visual Rhythm: {cultural_memory.visual_rhythm}")
    print(f"  Temperature: {cultural_memory.color_temperature}")
    print(f"  Abstraction: {cultural_memory.abstraction_level}")
    
    print(f"\n💭 Reasoning:")
    print(f"  {cultural_memory.reasoning[:200]}...")
    
    has_consensus = should_use_consensus(cultural_memory)
    print(f"\n✅ Strong Consensus (≥0.75): {'YES' if has_consensus else 'NO'}")
    
    # Validate cultural memory
    expected_colors = ['verde_acido', 'verde_esperanza']
    color_correct = cultural_memory.iconic_color in expected_colors
    
    if color_correct:
        print(f"✅ Cultural memory color is CORRECT (expected green)")
    else:
        print(f"❌ Cultural memory color is WRONG: {cultural_memory.iconic_color}")
        print(f"   Expected one of: {', '.join(expected_colors)}")
    
    # Step 2: Phase 3 Visual Resolution
    print(f"\n{'─'*80}")
    print("STEP 2: Phase 3 Visual Resolution...")
    print("─"*80)
    
    # Mock Phase 2A (genre-based would give wrong color)
    mock_phase_2a = {
        'primary': {
            'color_name': 'azul_profundo',  # Wrong: genre defaults to blue
            'confidence': 0.60
        }
    }
    
    identity = resolve_visual_identity(
        work_id=film['work_id'],
        color_assignment=mock_phase_2a,
        cultural_weight={},
        cultural_memory=cultural_memory,  # NEW
        film_title=film['title']  # Enables debug output
    )
    
    print(f"\n🎨 Final Visual Identity:")
    print(f"  Iconic Color: {identity.color_iconico}")
    print(f"  Confidence Rank: {identity.color_rank:.2f}")
    print(f"  Secondary Colors: {', '.join(identity.colores_secundarios)}")
    print(f"  Temperature: {identity.temperatura_emocional}")
    print(f"  Rhythm: {identity.ritmo_visual}")
    print(f"  Abstraction: {identity.grado_abstraccion_visual}")
    
    # Validate Phase 3 used cultural memory
    phase3_correct = identity.color_iconico in expected_colors
    
    if phase3_correct:
        print(f"\n✅ Phase 3 CORRECTLY used cultural memory (green)")
    else:
        print(f"\n❌ Phase 3 FAILED to use cultural memory")
        print(f"   Got: {identity.color_iconico}")
        print(f"   Expected: {cultural_memory.iconic_color}")
    
    # Validate confidence is high
    confidence_good = identity.color_rank >= 0.80
    
    if confidence_good:
        print(f"✅ Confidence rank is HIGH ({identity.color_rank:.2f} ≥ 0.80)")
    else:
        print(f"⚠️  Confidence rank is MODERATE ({identity.color_rank:.2f} < 0.80)")
    
    # Overall result
    print(f"\n{'='*80}")
    all_passed = color_correct and has_consensus and phase3_correct and confidence_good
    
    if all_passed:
        print("✅ INTEGRATION TEST PASSED")
        print("\nThe Matrix correctly resolves to GREEN via cultural memory!")
        print("The system now models how films live in people's minds.")
    else:
        print("❌ INTEGRATION TEST FAILED")
        if not color_correct:
            print("  - Cultural memory color incorrect")
        if not has_consensus:
            print("  - Consensus strength too low")
        if not phase3_correct:
            print("  - Phase 3 didn't use cultural memory")
        if not confidence_good:
            print("  - Confidence rank below threshold")
    
    print("="*80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = test_matrix_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
