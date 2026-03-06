#!/usr/bin/env python3
"""
validate_color_ids.py
─────────────────────
Validates that all color references in pipeline/normalized/works/ and
pipeline/derived/ use canonical Prisma palette v1.2 IDs, not display names.

Usage:
    python pipeline/validate_color_ids.py           # report only
    python pipeline/validate_color_ids.py --fix     # auto-correct unambiguous display names

Exit codes:
    0 — all OK (or all fixable violations were fixed with --fix)
    1 — violations found (and --fix was not specified, or some violations unfixable)
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ─── Prisma palette v1.3 canonical IDs ────────────────────────────────────────

CHROMATIC_IDS = {
    "rojo_pasional",
    "naranja_apocaliptico",
    "ambar_desertico",
    "amarillo_ludico",
    "verde_lima",
    "verde_esmeralda",
    "verde_distopico",
    "cian_melancolico",
    "azul_nocturno",
    "violeta_cinetico",
    "purpura_onirico",
    "magenta_pop",
    "blanco_polar",
    "negro_abismo",
    "titanio_mecanico",
    "rosa_pastel",
}

MONOCHROMATIC_IDS = {
    "claroscuro_dramatico",
    "monocromatico_intimo",
}

ALL_VALID_IDS = CHROMATIC_IDS | MONOCHROMATIC_IDS

# ─── Display name → canonical ID mapping ──────────────────────────────────────
# Used by --fix to auto-correct ambiguous display names.
# Keys are lowercase stripped versions for fuzzy matching.

DISPLAY_NAME_MAP: dict[str, str] = {
    # Chromatic
    "rojo pasional": "rojo_pasional",
    "naranja apocalíptico": "naranja_apocaliptico",
    "naranja apocaliptico": "naranja_apocaliptico",
    "ámbar desértico": "ambar_desertico",
    "ambar desertico": "ambar_desertico",
    "amarillo lúdico": "amarillo_ludico",
    "amarillo ludico": "amarillo_ludico",
    "verde lima": "verde_lima",
    "verde esmeralda": "verde_esmeralda",
    "verde distópico": "verde_distopico",
    "verde distopico": "verde_distopico",
    "cian melancólico": "cian_melancolico",
    "cian melancolico": "cian_melancolico",
    "azul nocturno": "azul_nocturno",
    "violeta cinético": "violeta_cinetico",
    "violeta cinetico": "violeta_cinetico",
    "púrpura onírico": "purpura_onirico",
    "purpura onirico": "purpura_onirico",
    "magenta pop": "magenta_pop",
    "blanco polar": "blanco_polar",
    "negro abismo": "negro_abismo",
    "titanio mecánico": "titanio_mecanico",
    "titanio mecanico": "titanio_mecanico",
    # Monochromatic
    "claroscuro dramático": "claroscuro_dramatico",
    "claroscuro dramatico": "claroscuro_dramatico",
    "monocromático íntimo": "monocromatico_intimo",
    "monocromatico intimo": "monocromatico_intimo",
    # Old v1.0 IDs (map to closest v1.2 equivalent)
    "azul_profundo": "azul_nocturno",
    "azul profundo": "azul_nocturno",
    "verde_esperanza": "verde_esmeralda",
    "verde esperanza": "verde_esmeralda",
    "ambar_dorado": "ambar_desertico",
    "ambar dorado": "ambar_desertico",
    "rojo_pasion": "rojo_pasional",
    "rojo pasion": "rojo_pasional",
    "violeta_onirico": "purpura_onirico",
    "violeta onirico": "purpura_onirico",
    "turquesa_retro": "cian_melancolico",
    "turquesa retro": "cian_melancolico",
    "rosa_melancolico": "magenta_pop",
    "rosa melancolico": "magenta_pop",
    "naranja_vibrante": "naranja_apocaliptico",
    "naranja vibrante": "naranja_apocaliptico",
    "gris_industrial": "titanio_mecanico",
    "gris industrial": "titanio_mecanico",
    "sepia_nostalgico": "ambar_desertico",
    "sepia nostalgico": "ambar_desertico",
    "cyan_clinico": "cian_melancolico",
    "cyan clinico": "cian_melancolico",
    "verde_acido": "verde_lima",
    "verde acido": "verde_lima",
}


def normalize_key(value: str) -> str:
    """Lowercase and strip for fuzzy display-name matching."""
    return value.strip().lower()


def resolve_color_id(value: str) -> tuple[str | None, bool]:
    """
    Try to resolve a value to a canonical v1.3 ID.

    Returns:
        (canonical_id, is_already_valid)
        - If already valid: (value, True)
        - If fixable display name: (canonical_id, False)
        - If unknown/unfixable: (None, False)
    """
    if value in ALL_VALID_IDS:
        return value, True

    key = normalize_key(value)
    if key in DISPLAY_NAME_MAP:
        return DISPLAY_NAME_MAP[key], False

    return None, False


# ─── Violation record ─────────────────────────────────────────────────────────

class Violation:
    def __init__(self, file_path: str, field: str, found: str, expected: str | None):
        self.file_path = file_path
        self.field = field
        self.found = found
        self.expected = expected  # None if unfixable

    def is_fixable(self) -> bool:
        return self.expected is not None

    def __str__(self) -> str:
        if self.is_fixable():
            return (
                f"  ⚠  {self.file_path}\n"
                f"      field: {self.field}\n"
                f"      found: '{self.found}'\n"
                f"      fix:   '{self.expected}'"
            )
        else:
            return (
                f"  ✗  {self.file_path}\n"
                f"      field: {self.field}\n"
                f"      found: '{self.found}'\n"
                f"      fix:   (unknown — manual review required)"
            )


# ─── Validation logic ─────────────────────────────────────────────────────────

def validate_work_file(file_path: Path) -> list[Violation]:
    """Check a normalized work JSON file for color ID violations."""
    violations: list[Violation] = []

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ✗  Cannot parse JSON: {file_path}: {e}", file=sys.stderr)
        return violations

    prisma = data.get("prisma_palette", {})
    if not prisma:
        # No prisma_palette field — not a violation, just skip
        return violations

    # Check primary
    primary = prisma.get("primary")
    if primary is not None:
        canonical, already_valid = resolve_color_id(str(primary))
        if not already_valid:
            violations.append(Violation(
                file_path=str(file_path),
                field="prisma_palette.primary",
                found=str(primary),
                expected=canonical,
            ))

    # Check secondary colors
    secondary = prisma.get("secondary", [])
    if isinstance(secondary, list):
        for i, color in enumerate(secondary):
            canonical, already_valid = resolve_color_id(str(color))
            if not already_valid:
                violations.append(Violation(
                    file_path=str(file_path),
                    field=f"prisma_palette.secondary[{i}]",
                    found=str(color),
                    expected=canonical,
                ))

    # Also check color_identity block if present (schema field)
    color_identity = data.get("color_identity", {})
    if color_identity:
        primary_ci = color_identity.get("primary_color")
        if primary_ci is not None:
            canonical, already_valid = resolve_color_id(str(primary_ci))
            if not already_valid:
                violations.append(Violation(
                    file_path=str(file_path),
                    field="color_identity.primary_color",
                    found=str(primary_ci),
                    expected=canonical,
                ))

        secondary_ci = color_identity.get("secondary_colors", [])
        if isinstance(secondary_ci, list):
            for i, color in enumerate(secondary_ci):
                canonical, already_valid = resolve_color_id(str(color))
                if not already_valid:
                    violations.append(Violation(
                        file_path=str(file_path),
                        field=f"color_identity.secondary_colors[{i}]",
                        found=str(color),
                        expected=canonical,
                    ))

    return violations


def validate_derived_file(file_path: Path) -> list[Violation]:
    """
    Check a derived color JSON file for color ID violations.
    Derived files currently contain only oklab metrics — no color IDs.
    This function future-proofs against derived files that may grow color fields.
    """
    violations: list[Violation] = []

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ✗  Cannot parse JSON: {file_path}: {e}", file=sys.stderr)
        return violations

    # Check color_distribution if present
    color_dist = data.get("color_distribution", {})
    if isinstance(color_dist, dict):
        for color_id in color_dist:
            canonical, already_valid = resolve_color_id(str(color_id))
            if not already_valid:
                violations.append(Violation(
                    file_path=str(file_path),
                    field=f"color_distribution.{color_id}",
                    found=str(color_id),
                    expected=canonical,
                ))

    # Check primary_color if present
    primary = data.get("primary_color")
    if primary is not None:
        canonical, already_valid = resolve_color_id(str(primary))
        if not already_valid:
            violations.append(Violation(
                file_path=str(file_path),
                field="primary_color",
                found=str(primary),
                expected=canonical,
            ))

    return violations


def apply_fix_to_work_file(file_path: Path, violations: list[Violation]) -> bool:
    """Apply fixable violations to a work JSON file. Returns True if file was modified."""
    if not any(v.is_fixable() for v in violations):
        return False

    with open(file_path) as f:
        data = json.load(f)

    modified = False

    for v in violations:
        if not v.is_fixable():
            continue

        # prisma_palette.primary
        if v.field == "prisma_palette.primary":
            if data.get("prisma_palette", {}).get("primary") == v.found:
                data["prisma_palette"]["primary"] = v.expected
                modified = True

        # prisma_palette.secondary[i]
        elif v.field.startswith("prisma_palette.secondary["):
            idx_str = v.field[len("prisma_palette.secondary["):-1]
            try:
                idx = int(idx_str)
                sec = data.get("prisma_palette", {}).get("secondary", [])
                if isinstance(sec, list) and idx < len(sec) and sec[idx] == v.found:
                    sec[idx] = v.expected
                    modified = True
            except ValueError:
                pass

        # color_identity.primary_color
        elif v.field == "color_identity.primary_color":
            if data.get("color_identity", {}).get("primary_color") == v.found:
                data["color_identity"]["primary_color"] = v.expected
                modified = True

        # color_identity.secondary_colors[i]
        elif v.field.startswith("color_identity.secondary_colors["):
            idx_str = v.field[len("color_identity.secondary_colors["):-1]
            try:
                idx = int(idx_str)
                sec = data.get("color_identity", {}).get("secondary_colors", [])
                if isinstance(sec, list) and idx < len(sec) and sec[idx] == v.found:
                    sec[idx] = v.expected
                    modified = True
            except ValueError:
                pass

    if modified:
        with open(file_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")  # trailing newline

    return modified


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate (and optionally fix) Prisma color IDs in pipeline files."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-correct unambiguous display names to canonical v1.3 IDs.",
    )
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Project root directory (default: current directory)",
    )
    args = parser.parse_args()

    base = Path(args.base_dir)
    works_dir = base / "pipeline" / "normalized" / "works"
    derived_color_dir = base / "pipeline" / "derived" / "color"

    all_violations: list[Violation] = []
    files_checked = 0

    # ── Validate normalized work files ────────────────────────────────────────
    if works_dir.exists():
        work_files = sorted(works_dir.glob("*.json"))
        for work_file in work_files:
            violations = validate_work_file(work_file)
            if violations:
                all_violations.extend(violations)
                if args.fix:
                    fixable = [v for v in violations if v.is_fixable()]
                    unfixable = [v for v in violations if not v.is_fixable()]
                    if fixable:
                        if apply_fix_to_work_file(work_file, fixable):
                            print(f"  ✅ Fixed {len(fixable)} violation(s) in {work_file.name}")
                    if unfixable:
                        print(f"  ❌ {len(unfixable)} unfixable violation(s) in {work_file.name} — manual review required")
            files_checked += 1
    else:
        print(f"  ⚠  Works directory not found: {works_dir}")

    # ── Validate derived color files ──────────────────────────────────────────
    if derived_color_dir.exists():
        derived_files = sorted(derived_color_dir.glob("*.json"))
        for derived_file in derived_files:
            violations = validate_derived_file(derived_file)
            if violations:
                all_violations.extend(violations)
                if args.fix:
                    print(f"  ⚠  Violations in derived file {derived_file.name} — manual fix required")
            files_checked += 1
    else:
        print(f"  ⚠  Derived color directory not found: {derived_color_dir}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print(f"  Files checked:    {files_checked}")
    print(f"  Violations found: {len(all_violations)}")

    if not all_violations:
        print("  ✅ All color IDs are valid Prisma palette v1.3 canonical IDs.")
        return 0

    fixable_count = sum(1 for v in all_violations if v.is_fixable())
    unfixable_count = len(all_violations) - fixable_count

    if not args.fix:
        print("\n  Violations:")
        for v in all_violations:
            print(v)
        print()
        if fixable_count:
            print(f"  {fixable_count} violation(s) can be auto-fixed. Run with --fix to apply.")
        if unfixable_count:
            print(f"  {unfixable_count} violation(s) require manual review.")
        return 1

    # --fix was specified — report remaining unfixable violations
    remaining = [v for v in all_violations if not v.is_fixable()]
    if remaining:
        print("\n  Remaining violations (manual review required):")
        for v in remaining:
            print(v)
        return 1

    print("  ✅ All fixable violations have been corrected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
