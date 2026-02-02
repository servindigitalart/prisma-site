# PHASE 1 COMPLETE
# Files created:
#   - pipeline/doctrine/v1.0/color_doctrine.json
#   - pipeline/doctrine/v1.0/score_doctrine.json
#   - pipeline/doctrine/v1.0/tier_doctrine.json
#   - pipeline/doctrine/v1.0/changelog.md
#   - pipeline/doctrine/current (symlink → v1.0)
#   - pipeline/lib/doctrine.py
#   - pipeline/schema/color_assignment.schema.json
#   - pipeline/schema/collection.schema.json
#   - pipeline/schema/color_doctrine.schema.json
#   - pipeline/schema/score_doctrine.schema.json
#   - pipeline/schema/tier_doctrine.schema.json
# Files modified:
#   - pipeline/schema/work.schema.json
# Next phase: Phase 2: Enrichment Pipeline (AI + Scoring)
# Blockers: None

"""
Doctrine Loader Module

Provides functions to load doctrine JSON files from pipeline/doctrine/current/.
Doctrine files define the rules, thresholds, and configurations for:
- Color definitions and assignment rules
- Scoring formulas and tier thresholds
- Tier definitions and ranking rules

All doctrine content is read-only; this module never modifies doctrine files.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


# Path to current doctrine version (symlink)
DOCTRINE_DIR = Path(__file__).parent.parent / "doctrine" / "current"


def load_doctrine(name: str) -> Dict[str, Any]:
    """
    Load a doctrine JSON file by name.
    
    Args:
        name: Name of the doctrine file without extension (e.g., "color_doctrine", "score_doctrine")
    
    Returns:
        Parsed JSON content as a dictionary
    
    Raises:
        FileNotFoundError: If doctrine file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    
    Example:
        color_doctrine = load_doctrine("color_doctrine")
        colors = color_doctrine["colors"]
    """
    doctrine_path = DOCTRINE_DIR / f"{name}.json"
    
    if not doctrine_path.exists():
        raise FileNotFoundError(
            f"Doctrine file not found: {doctrine_path}\n"
            f"Available doctrine files should be in: {DOCTRINE_DIR}"
        )
    
    with open(doctrine_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_color_palette() -> list[Dict[str, Any]]:
    """
    Get the 12 Prisma colors from color doctrine.
    
    Returns:
        List of color dictionaries with id, hex, name, moods, etc.
    
    Example:
        colors = get_color_palette()
        azul = next(c for c in colors if c["id"] == "azul_profundo")
    """
    doctrine = load_doctrine("color_doctrine")
    return doctrine["colors"]


def get_monochromatic_modes() -> list[Dict[str, Any]]:
    """
    Get monochromatic mode definitions from color doctrine.
    
    Returns:
        List of monochromatic mode dictionaries
    """
    doctrine = load_doctrine("color_doctrine")
    return doctrine["monochromatic_modes"]


def get_scoring_weights() -> Dict[str, float]:
    """
    Get formula weights from score doctrine.
    
    Returns:
        Dictionary mapping component names to weight values
        e.g., {"ai_confidence": 0.30, "authorship": 0.25, ...}
    """
    doctrine = load_doctrine("score_doctrine")
    return {
        key: value["value"]
        for key, value in doctrine["formula"]["weights"].items()
    }


def get_tier_thresholds() -> Dict[str, Optional[int]]:
    """
    Get tier minimum score thresholds from score doctrine.
    
    Returns:
        Dictionary mapping tier names to minimum scores
        e.g., {"canon": 95, "core": 85, "strong": 70, ...}
    """
    doctrine = load_doctrine("score_doctrine")
    return {
        tier: data["min_score"]
        for tier, data in doctrine["tier_thresholds"].items()
    }


def get_tier_definitions() -> list[Dict[str, Any]]:
    """
    Get full tier definitions from tier doctrine.
    
    Returns:
        List of tier definition dictionaries with id, name, description, etc.
    """
    doctrine = load_doctrine("tier_doctrine")
    return doctrine["tiers"]


def get_color_by_id(color_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific color definition by ID.
    
    Args:
        color_id: Color identifier (e.g., "azul_profundo")
    
    Returns:
        Color dictionary or None if not found
    """
    colors = get_color_palette()
    return next((c for c in colors if c["id"] == color_id), None)


def get_assignment_rules() -> Dict[str, Any]:
    """
    Get color assignment rules from color doctrine.
    
    Returns:
        Dictionary containing primary_color, secondary_colors, and monochromatic_detection rules
    """
    doctrine = load_doctrine("color_doctrine")
    return doctrine["assignment_rules"]


# Convenience function for validation
def validate_doctrine_integrity() -> bool:
    """
    Validate that all required doctrine files exist and are valid JSON.
    
    Returns:
        True if all doctrine files are valid, raises exception otherwise
    """
    required_doctrines = ["color_doctrine", "score_doctrine", "tier_doctrine"]
    
    for name in required_doctrines:
        doctrine = load_doctrine(name)
        
        # Basic structure checks
        if name == "color_doctrine":
            assert "colors" in doctrine, "color_doctrine missing 'colors' key"
            assert len(doctrine["colors"]) == 12, "Expected 12 colors in palette"
            assert "monochromatic_modes" in doctrine, "color_doctrine missing 'monochromatic_modes'"
            
        elif name == "score_doctrine":
            assert "formula" in doctrine, "score_doctrine missing 'formula' key"
            assert "tier_thresholds" in doctrine, "score_doctrine missing 'tier_thresholds'"
            weights = get_scoring_weights()
            weight_sum = sum(weights.values())
            assert abs(weight_sum - 1.0) < 0.01, f"Formula weights should sum to 1.0, got {weight_sum}"
            
        elif name == "tier_doctrine":
            assert "tiers" in doctrine, "tier_doctrine missing 'tiers' key"
            tier_ids = [t["id"] for t in doctrine["tiers"]]
            expected_tiers = ["canon", "core", "strong", "peripheral", "uncertain"]
            assert tier_ids == expected_tiers, f"Expected tiers {expected_tiers}, got {tier_ids}"
    
    return True


if __name__ == "__main__":
    # Test doctrine loading
    print("Testing doctrine loader...")
    
    try:
        # Test basic loading
        color_doctrine = load_doctrine("color_doctrine")
        print(f"✓ Loaded color_doctrine (version {color_doctrine['version']})")
        
        score_doctrine = load_doctrine("score_doctrine")
        print(f"✓ Loaded score_doctrine (version {score_doctrine['version']})")
        
        tier_doctrine = load_doctrine("tier_doctrine")
        print(f"✓ Loaded tier_doctrine (version {tier_doctrine['version']})")
        
        # Test convenience functions
        colors = get_color_palette()
        print(f"✓ Loaded {len(colors)} colors from palette")
        
        weights = get_scoring_weights()
        print(f"✓ Loaded scoring weights: {weights}")
        
        thresholds = get_tier_thresholds()
        print(f"✓ Loaded tier thresholds: {thresholds}")
        
        # Test validation
        validate_doctrine_integrity()
        print("✓ Doctrine integrity validated")
        
        print("\n✅ All doctrine tests passed!")
        
    except Exception as e:
        print(f"\n❌ Doctrine test failed: {e}")
        raise
