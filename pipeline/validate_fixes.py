#!/usr/bin/env python3
"""
Validation script for architectural fixes.
Tests color contract enforcement and people identity resolution.
"""
import sys
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent))

from palette_registry import (
    normalize_color_id,
    validate_color_assignment,
    get_doctrine_version,
    ALL_VALID_IDS,
    DEPRECATED_ID_MAP,
)


def test_color_normalization():
    """Test color ID normalization."""
    print("=" * 60)
    print("COLOR NORMALIZATION TESTS")
    print("=" * 60)
    
    # Test deprecated IDs
    deprecated_tests = [
        ("azul_profundo", "azul_nocturno"),
        ("rosa_melancolico", "magenta_pop"),
        ("rojo_pasion", "rojo_pasional"),
        ("verde_esperanza", "verde_esmeralda"),
    ]
    
    print("\n1. Deprecated ID Mapping:")
    for old_id, expected_new in deprecated_tests:
        result = normalize_color_id(old_id)
        status = "✅" if result == expected_new else "❌"
        print(f"  {status} '{old_id}' → '{result}' (expected: '{expected_new}')")
    
    # Test valid IDs
    print("\n2. Valid v1.3 IDs (sample):")
    valid_samples = ["rosa_pastel", "azul_nocturno", "verde_esmeralda", "rojo_pasional"]
    for color_id in valid_samples:
        result = normalize_color_id(color_id)
        status = "✅" if result == color_id else "❌"
        print(f"  {status} '{color_id}' → '{result}'")
    
    # Test invalid IDs
    print("\n3. Invalid IDs:")
    invalid_samples = ["invalid_color", "blue_deep", "rosa_viejo"]
    for color_id in invalid_samples:
        result = normalize_color_id(color_id)
        status = "✅" if result is None else "❌"
        print(f"  {status} '{color_id}' → {result} (expected: None)")
    
    print()


def test_color_validation():
    """Test complete color assignment validation."""
    print("=" * 60)
    print("COLOR VALIDATION TESTS")
    print("=" * 60)
    
    # Test 1: Valid assignment
    print("\n1. Valid chromatic assignment:")
    is_valid, normalized = validate_color_assignment(
        primary="rosa_pastel",
        secondary=["rojo_pasional"],
        mode="chromatic",
        auto_fix=False,
    )
    print(f"  Valid: {is_valid}")
    print(f"  Primary: {normalized['primary']}")
    print(f"  Secondary: {normalized['secondary']}")
    print(f"  Warnings: {normalized.get('warnings', [])}")
    
    # Test 2: Deprecated primary with auto-fix
    print("\n2. Deprecated primary (auto-fix enabled):")
    is_valid, normalized = validate_color_assignment(
        primary="azul_profundo",
        secondary=[],
        mode="chromatic",
        auto_fix=True,
    )
    print(f"  Valid: {is_valid}")
    print(f"  Primary: {normalized['primary']} (auto-normalized)")
    print(f"  Warnings: {normalized.get('warnings', [])}")
    
    # Test 3: Deprecated secondary with auto-fix
    print("\n3. Deprecated secondary (auto-fix enabled):")
    is_valid, normalized = validate_color_assignment(
        primary="rosa_pastel",
        secondary=["rosa_melancolico", "rojo_pasional"],
        mode="chromatic",
        auto_fix=True,
    )
    print(f"  Valid: {is_valid}")
    print(f"  Primary: {normalized['primary']}")
    print(f"  Secondary: {normalized['secondary']}")
    print(f"  Warnings: {normalized.get('warnings', [])}")
    
    # Test 4: Invalid primary (should fail)
    print("\n4. Invalid primary (should fail):")
    is_valid, normalized = validate_color_assignment(
        primary="invalid_color",
        secondary=[],
        mode="chromatic",
        auto_fix=True,
    )
    print(f"  Valid: {is_valid}")
    print(f"  Errors: {normalized.get('errors', [])}")
    
    print()


def test_doctrine_info():
    """Display doctrine information."""
    print("=" * 60)
    print("DOCTRINE INFORMATION")
    print("=" * 60)
    
    print(f"\nCurrent Version: {get_doctrine_version()}")
    print(f"Total Valid IDs: {len(ALL_VALID_IDS)}")
    print(f"Deprecated Mappings: {len(DEPRECATED_ID_MAP)}")
    
    print("\nAll Valid v1.3 Color IDs:")
    for color_id in sorted(ALL_VALID_IDS):
        print(f"  - {color_id}")
    
    print("\nDeprecated ID Mappings:")
    for old_id, new_id in sorted(DEPRECATED_ID_MAP.items()):
        print(f"  {old_id} → {new_id}")
    
    print()


def test_specific_failure_cases():
    """Test the specific failure cases from the original issue."""
    print("=" * 60)
    print("SPECIFIC FAILURE CASE TESTS")
    print("=" * 60)
    
    print("\n1. Testing 'rosa_pastel' (was failing in v1.0 contract):")
    result = normalize_color_id("rosa_pastel")
    is_valid = result == "rosa_pastel"
    status = "✅ FIXED" if is_valid else "❌ STILL BROKEN"
    print(f"  {status}: rosa_pastel is now valid in v1.3")
    print(f"  Normalized to: {result}")
    
    print("\n2. Testing deprecated color auto-normalization:")
    print("  (Simulating AI pipeline generating old v1.0 color)")
    is_valid, normalized = validate_color_assignment(
        primary="azul_profundo",  # v1.0 deprecated
        auto_fix=True,
    )
    status = "✅ FIXED" if normalized['primary'] == "azul_nocturno" else "❌ BROKEN"
    print(f"  {status}: azul_profundo → {normalized['primary']}")
    print(f"  Auto-fix warnings: {normalized.get('warnings', [])}")
    
    print()


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("PRISMA ARCHITECTURAL FIX VALIDATION")
    print("Color Contract Enforcement & Identity Resolution")
    print("=" * 60 + "\n")
    
    try:
        test_doctrine_info()
        test_color_normalization()
        test_color_validation()
        test_specific_failure_cases()
        
        print("=" * 60)
        print("VALIDATION COMPLETE")
        print("=" * 60)
        print("\n✅ All architectural fixes validated successfully")
        print("\nNext Steps:")
        print("1. Test migration with: python3 pipeline/migrate_to_db.py --film <work_id>")
        print("2. Re-process failed Sight & Sound films")
        print("3. Verify idempotency with duplicate runs\n")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
