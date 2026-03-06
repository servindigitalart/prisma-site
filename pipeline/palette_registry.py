#!/usr/bin/env python3
"""
Centralized Prisma color palette registry.
Single source of truth for valid color IDs and version mapping.
"""
import json
from pathlib import Path
from typing import Any

# Current palette version
CURRENT_VERSION = "1.3"
DOCTRINE_DIR = Path(__file__).parent / "doctrine"
CURRENT_DOCTRINE_PATH = DOCTRINE_DIR / f"v{CURRENT_VERSION}" / "color_doctrine.json"

# V1.3 canonical IDs
CHROMATIC_IDS = {
    "rojo_pasional", "naranja_apocaliptico", "ambar_desertico", "amarillo_ludico",
    "verde_lima", "verde_esmeralda", "verde_distopico", "cian_melancolico",
    "azul_nocturno", "violeta_cinetico", "purpura_onirico", "magenta_pop",
    "blanco_polar", "negro_abismo", "titanio_mecanico", "rosa_pastel",
}

MONOCHROMATIC_IDS = {
    "claroscuro_dramatico",
    "monocromatico_intimo",
}

ALL_VALID_IDS = CHROMATIC_IDS | MONOCHROMATIC_IDS

# Deprecated ID mappings (v1.0/v1.1/v1.2 → v1.3)
DEPRECATED_ID_MAP = {
    "azul_profundo": "azul_nocturno",
    "verde_esperanza": "verde_esmeralda",
    "ambar_dorado": "ambar_desertico",
    "rojo_pasion": "rojo_pasional",
    "violeta_onirico": "purpura_onirico",
    "turquesa_retro": "cian_melancolico",
    "rosa_melancolico": "magenta_pop",
    "naranja_vibrante": "naranja_apocaliptico",
}

_doctrine_cache: dict[str, Any] | None = None


def load_current_doctrine() -> dict[str, Any]:
    """Load current color doctrine JSON."""
    global _doctrine_cache
    if _doctrine_cache is not None:
        return _doctrine_cache
    
    if not CURRENT_DOCTRINE_PATH.exists():
        raise FileNotFoundError(f"Doctrine not found: {CURRENT_DOCTRINE_PATH}")
    
    with open(CURRENT_DOCTRINE_PATH, encoding="utf-8") as f:
        _doctrine_cache = json.load(f)
    
    return _doctrine_cache


def get_doctrine_version() -> str:
    """Return current doctrine version."""
    return CURRENT_VERSION


def is_valid_color_id(color_id: str) -> bool:
    """Check if color ID is valid in current doctrine."""
    return color_id in ALL_VALID_IDS


def is_deprecated_color_id(color_id: str) -> bool:
    """Check if color ID is from old doctrine version."""
    return color_id in DEPRECATED_ID_MAP


def normalize_color_id(color_id: str) -> str | None:
    """
    Normalize color ID to current doctrine version.
    
    Returns:
        Current canonical ID if valid, mapped ID if deprecated, None if invalid
    """
    if is_valid_color_id(color_id):
        return color_id
    if is_deprecated_color_id(color_id):
        return DEPRECATED_ID_MAP[color_id]
    return None


def validate_color_assignment(
    primary: str,
    secondary: list[str] | None = None,
    mode: str | None = None,
    auto_fix: bool = False,
) -> tuple[bool, dict[str, Any]]:
    """
    Validate complete color assignment.
    
    Args:
        primary: Primary color ID
        secondary: Secondary color IDs
        mode: Color mode
        auto_fix: Auto-normalize deprecated IDs
    
    Returns:
        (is_valid, result_dict) where result_dict contains:
        - primary: Normalized primary
        - secondary: Normalized secondaries
        - mode: Corrected mode
        - errors: Validation errors
        - warnings: Warnings (auto-normalizations)
    """
    errors: list[str] = []
    warnings: list[str] = []
    
    # Normalize primary
    normalized_primary = normalize_color_id(primary)
    if normalized_primary is None:
        errors.append(f"Invalid primary color ID: '{primary}'")
        return (False, {
            "primary": primary,
            "secondary": secondary or [],
            "mode": mode or "color",
            "errors": errors,
            "warnings": warnings,
        })
    
    if normalized_primary != primary:
        if auto_fix:
            warnings.append(f"Auto-normalized '{primary}' → '{normalized_primary}'")
        else:
            errors.append(f"Deprecated color ID '{primary}' — should be '{normalized_primary}'")
    
    # Normalize secondary
    normalized_secondary: list[str] = []
    if secondary:
        for s in secondary[:3]:
            norm_s = normalize_color_id(s)
            if norm_s is None:
                warnings.append(f"Skipping invalid secondary: '{s}'")
                continue
            if norm_s != s:
                if auto_fix:
                    warnings.append(f"Auto-normalized secondary '{s}' → '{norm_s}'")
                else:
                    warnings.append(f"Deprecated secondary '{s}' → should be '{norm_s}'")
            normalized_secondary.append(norm_s)
    
    # Validate mode
    if normalized_primary in MONOCHROMATIC_IDS:
        correct_mode = "monochromatic"
        if mode != correct_mode and auto_fix:
            warnings.append(f"Auto-corrected mode to '{correct_mode}'")
        if normalized_secondary:
            warnings.append("Monochromatic cannot have secondaries — clearing")
            normalized_secondary = []
    else:
        correct_mode = mode or "color"
    
    is_valid = len(errors) == 0
    
    return (is_valid, {
        "primary": normalized_primary,
        "secondary": normalized_secondary,
        "mode": correct_mode,
        "errors": errors,
        "warnings": warnings,
    })


def get_color_hex(color_id: str) -> str | None:
    """Get hex code for color ID."""
    doctrine = load_current_doctrine()
    for color in doctrine.get("colors", []):
        if color["id"] == color_id:
            return color["hex"]
    return None


def get_color_name(color_id: str) -> str | None:
    """Get display name for color ID."""
    doctrine = load_current_doctrine()
    for color in doctrine.get("colors", []):
        if color["id"] == color_id:
            return color["name"]
    return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python palette_registry.py <color_id>")
        sys.exit(1)
    
    color_id = sys.argv[1]
    print(f"\nTesting: '{color_id}'")
    print(f"Current doctrine: v{get_doctrine_version()}\n")
    
    if is_valid_color_id(color_id):
        print(f"✅ Valid — '{color_id}'")
        print(f"   Hex: {get_color_hex(color_id)}")
        print(f"   Name: {get_color_name(color_id)}")
    elif is_deprecated_color_id(color_id):
        mapped = normalize_color_id(color_id)
        print(f"⚠️  Deprecated — '{color_id}' → '{mapped}'")
        print(f"   Hex: {get_color_hex(mapped)}")
    else:
        print(f"❌ Invalid — '{color_id}'")
