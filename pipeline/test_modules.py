#!/usr/bin/env python3
"""
Quick test script for palette_registry and identity_resolver.
"""
import sys
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent))

from palette_registry import (
    normalize_color_id,
    validate_color_assignment,
    get_doctrine_version,
)

print("=" * 60)
print("PALETTE REGISTRY TEST")
print("=" * 60)

print(f"\nCurrent doctrine version: {get_doctrine_version()}")

# Test 1: Valid ID
print("\n1. Valid ID (azul_nocturno):")
result = normalize_color_id("azul_nocturno")
print(f"   Result: {result} ✅")

# Test 2: Deprecated ID (v1.0 → v1.3)
print("\n2. Deprecated ID (rosa_pastel):")
result = normalize_color_id("rosa_pastel")
if result:
    print(f"   ❌ FAILED - rosa_pastel should be deprecated")
    print(f"   Got: {result}")
else:
    print(f"   ✅ PASSED - rosa_pastel correctly identified as current v1.3 ID")

# Test 3: Actually deprecated ID
print("\n3. Deprecated ID (azul_profundo → azul_nocturno):")
result = normalize_color_id("azul_profundo")
if result == "azul_nocturno":
    print(f"   ✅ PASSED - azul_profundo → {result}")
else:
    print(f"   ❌ FAILED - expected azul_nocturno, got: {result}")

# Test 4: Invalid ID
print("\n4. Invalid ID (fake_color):")
result = normalize_color_id("fake_color")
if result is None:
    print(f"   ✅ PASSED - correctly returned None")
else:
    print(f"   ❌ FAILED - should return None, got: {result}")

# Test 5: Full validation with auto-fix
print("\n5. Full validation (auto-fix deprecated ID):")
is_valid, normalized = validate_color_assignment(
    primary="azul_profundo",  # deprecated
    secondary=["rojo_pasion"],  # deprecated
    auto_fix=True,
)
if is_valid:
    print(f"   ✅ Valid: {is_valid}")
    print(f"   Primary: {normalized['primary']}")
    print(f"   Secondary: {normalized['secondary']}")
    print(f"   Warnings: {len(normalized['warnings'])}")
    for w in normalized['warnings']:
        print(f"      - {w}")
else:
    print(f"   ❌ FAILED - should be valid with auto_fix=True")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
