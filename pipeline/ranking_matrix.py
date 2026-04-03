"""
pipeline/ranking_matrix.py
───────────────────────────
Defines how each award category contributes to each person role's ranking score.

The AWARD_ROLE_WEIGHTS dict maps award category patterns (matched against award_id)
to a dict of {role: weight}. Weights are multiplied by FESTIVAL_TIER_MULTIPLIERS
and by a win/nomination multiplier (1.0 for win, 0.3 for nomination).

Usage as a module:
  from ranking_matrix import get_award_weight, FESTIVAL_TIER_MULTIPLIERS

Self-test when run directly:
  python3 pipeline/ranking_matrix.py
"""

from __future__ import annotations

# ─── Festival tier multipliers ────────────────────────────────────────────────
# Tier A: Big three + Oscar (Cannes, Berlin, Venice, Academy Awards)
# Tier B: BAFTA, César, Goya, Golden Globe, Sundance, TIFF, San Sebastián, Locarno
# Tier C: FIPRESCI, regional, genre festivals

FESTIVAL_TIER_MULTIPLIERS: dict[str, float] = {
    "A": 1.0,
    "B": 0.6,
    "C": 0.35,
}

# ─── Award → role weights ────────────────────────────────────────────────────
# Keys are patterns matched (case-insensitive, substring) against award_id.
# Patterns are checked in ORDER — first match wins.
# Roles match the 'role' field in work_people and ranking_scores.context.

AWARD_ROLE_WEIGHTS: dict[str, dict[str, float]] = {

    # ── Grand prizes (festival best film equivalent) ─────────────────────────
    # Benefits director most; slight credit to writer and DP
    "palme-dor": {
        "director": 1.0, "writer": 0.2, "cinematography": 0.15,
    },
    "golden-bear": {
        "director": 1.0, "writer": 0.2, "cinematography": 0.15,
    },
    "golden-lion": {
        "director": 1.0, "writer": 0.2, "cinematography": 0.15,
    },
    "golden-leopard": {
        "director": 1.0, "writer": 0.2, "cinematography": 0.15,
    },
    "golden-shell": {
        "director": 1.0, "writer": 0.2, "cinematography": 0.15,
    },
    "peoples-choice": {
        "director": 0.8, "writer": 0.15,
    },

    # ── Oscar / Academy best picture ─────────────────────────────────────────
    "oscar-best-picture": {
        "director": 1.0, "writer": 0.4, "cinematography": 0.3,
        "editor": 0.3, "composer": 0.1, "actor": 0.05, "actress": 0.05,
    },
    "best-picture": {
        "director": 1.0, "writer": 0.3, "cinematography": 0.2,
        "editor": 0.2, "composer": 0.1, "actor": 0.05, "actress": 0.05,
    },

    # ── Best film (non-picture naming) ──────────────────────────────────────
    "bafta-best-film": {
        "director": 1.0, "writer": 0.3, "cinematography": 0.2, "editor": 0.2,
    },
    "cesar-best-film": {
        "director": 1.0, "writer": 0.3, "cinematography": 0.15,
    },
    "goya-best-film": {
        "director": 1.0, "writer": 0.3, "cinematography": 0.15,
    },
    "ariel-best-film": {
        "director": 1.0, "writer": 0.3,
    },
    "gg-best-film-drama": {
        "director": 0.9, "writer": 0.25,
    },
    "grand-jury": {
        "director": 0.9, "writer": 0.2, "cinematography": 0.1,
    },
    "grand-prix": {
        "director": 0.9, "writer": 0.2, "cinematography": 0.1,
    },
    "jury-prize": {
        "director": 0.7, "writer": 0.15, "cinematography": 0.1,
    },
    "special-jury": {
        "director": 0.6, "writer": 0.1,
    },

    # ── Best director ─────────────────────────────────────────────────────────
    "best-director": {
        "director": 1.0,
    },
    "silver-bear-director": {
        "director": 1.0,
    },
    "silver-lion-director": {
        "director": 1.0,
    },
    "silver-shell": {  # San Sebastián directing awards
        "director": 0.8,
    },

    # ── Cinematography ────────────────────────────────────────────────────────
    "best-cinematography": {
        "cinematography": 1.0,
    },
    "asc-award": {
        "cinematography": 1.0,
    },

    # ── Screenplay ────────────────────────────────────────────────────────────
    "best-original-screenplay": {
        "writer": 1.0,
    },
    "best-adapted-screenplay": {
        "writer": 0.9,
    },
    "best-screenplay": {
        "writer": 1.0,
    },

    # ── Acting — lead ─────────────────────────────────────────────────────────
    "best-actress": {
        "actress": 1.0,
    },
    "best-actor": {
        "actor": 1.0,
    },
    "volpi-cup-actress": {
        "actress": 1.0,
    },
    "volpi-cup-actor": {
        "actor": 1.0,
    },
    "silver-bear-actress": {
        "actress": 1.0,
    },
    "silver-bear-actor": {
        "actor": 1.0,
    },
    "silver-shell-actress": {
        "actress": 0.9,
    },
    "silver-shell-actor": {
        "actor": 0.9,
    },

    # ── Acting — supporting ───────────────────────────────────────────────────
    "best-supporting-actor": {
        "actor": 0.8,
    },
    "best-supporting-actress": {
        "actress": 0.8,
    },

    # ── Technical ────────────────────────────────────────────────────────────
    "best-film-editing": {
        "editor": 1.0,
    },
    "best-original-score": {
        "composer": 1.0,
    },
    "best-sound": {
        "editor": 0.3, "composer": 0.3,
    },
    "best-production-design": {
        "director": 0.1,
    },

    # ── International / foreign ───────────────────────────────────────────────
    "best-intl-film": {
        "director": 0.8, "writer": 0.2,
    },
    "best-international-film": {
        "director": 0.8, "writer": 0.2,
    },
    "best-foreign-language": {
        "director": 0.8, "writer": 0.2,
    },

    # ── FIPRESCI ──────────────────────────────────────────────────────────────
    "fipresci": {
        "director": 0.5, "writer": 0.1, "cinematography": 0.1,
    },

    # ── Camera d'Or (debut film) ──────────────────────────────────────────────
    "camera-dor": {
        "director": 0.9,
    },

    # ── Audience / popularity awards ─────────────────────────────────────────
    "audience": {
        "director": 0.4, "writer": 0.1,
    },
    "world-cinema-drama": {
        "director": 0.8, "writer": 0.2,
    },
    "directing-drama": {
        "director": 1.0,
    },
    "grand-jury-doc": {
        "director": 0.9, "writer": 0.2,
    },

    # ── Tiger Award (Rotterdam) ───────────────────────────────────────────────
    "tiger": {
        "director": 0.9, "writer": 0.15,
    },

    # ── Platform (TIFF) ───────────────────────────────────────────────────────
    "platform": {
        "director": 0.8, "writer": 0.15,
    },

    # ── Genre-specific best director awards ──────────────────────────────────
    "ariel-best-director": {
        "director": 1.0,
    },
    "goya-best-director": {
        "director": 1.0,
    },
    "cesar-best-director": {
        "director": 1.0,
    },
    "bafta-best-director": {
        "director": 1.0,
    },
    "gg-best-director": {
        "director": 0.9,
    },
}


# ─── Public API ───────────────────────────────────────────────────────────────

def get_award_weight(award_id: str, role: str, tier: str = "A") -> float:
    """
    Returns the contribution weight of an award to a person's ranking score.

    award_id: PRISMA award ID e.g. 'award_cannes-palme-dor'
    role: person role e.g. 'director', 'cinematography', 'writer', 'actor', etc.
    tier: festival tier 'A', 'B', or 'C'

    Final weight = pattern_role_weight × tier_multiplier
    Win multiplier (1.0) and nomination multiplier (0.3) are applied by the caller.
    """
    tier_mult = FESTIVAL_TIER_MULTIPLIERS.get(tier, 0.35)

    # Strip the 'award_' prefix for cleaner pattern matching
    stripped = award_id.removeprefix("award_")

    # Try each pattern in definition order — first match wins
    for pattern, role_weights in AWARD_ROLE_WEIGHTS.items():
        if pattern in stripped:
            return role_weights.get(role, 0.0) * tier_mult

    return 0.0


def get_all_roles() -> list[str]:
    """Return all role names referenced in AWARD_ROLE_WEIGHTS."""
    roles: set[str] = set()
    for weights in AWARD_ROLE_WEIGHTS.values():
        roles.update(weights.keys())
    return sorted(roles)


# ─── Self-test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("PRISMA Ranking Matrix — Self-Test")
    print("=" * 60)

    test_cases = [
        # (award_id, role, tier, expected_min)
        ("award_cannes-palme-dor",          "director",      "A", 0.9),
        ("award_cannes-palme-dor",          "writer",        "A", 0.1),
        ("award_cannes-palme-dor",          "actor",         "A", 0.0),
        ("award_oscar-best-picture",        "director",      "A", 0.9),
        ("award_oscar-best-picture",        "cinematography","A", 0.2),
        ("award_oscar-best-director",       "director",      "A", 0.9),
        ("award_oscar-best-cinematography", "cinematography","A", 0.9),
        ("award_oscar-best-original-screenplay", "writer",   "A", 0.9),
        ("award_oscar-best-actress",        "actress",       "A", 0.9),
        ("award_bafta-best-film",           "director",      "A", 0.9),
        ("award_bafta-best-film",           "editor",        "A", 0.1),
        ("award_bafta-best-cinematography", "cinematography","A", 0.9),
        ("award_berlin-golden-bear",        "director",      "A", 0.9),
        ("award_cesar-best-film",           "director",      "B", 0.55),  # 1.0 × 0.6
        ("award_goya-best-film",            "director",      "B", 0.55),
        ("award_ariel-best-film",           "director",      "B", 0.55),
        ("award_fipresci-cannes",           "director",      "C", 0.1),
        ("award_unknown-xyz",               "director",      "A", 0.0),
    ]

    all_pass = True
    for award_id, role, tier, expected_min in test_cases:
        weight = get_award_weight(award_id, role, tier)
        status = "✅" if weight >= expected_min else "❌"
        if weight < expected_min:
            all_pass = False
        print(f"  {status} {award_id:45s} {role:15s} tier={tier} → {weight:.3f} (expected ≥ {expected_min})")

    print()
    print(f"Tier multipliers: {FESTIVAL_TIER_MULTIPLIERS}")
    print(f"Award patterns defined: {len(AWARD_ROLE_WEIGHTS)}")
    print(f"Roles covered: {', '.join(get_all_roles())}")
    print()
    print("Matrix check example — Cannes Palme d'Or, all roles:")
    for role in get_all_roles():
        w = get_award_weight("award_cannes-palme-dor", role, "A")
        if w > 0:
            print(f"  {role:15s} → {w:.2f}")

    print()
    if all_pass:
        print("✅ All self-tests passed")
    else:
        print("❌ Some self-tests failed — review AWARD_ROLE_WEIGHTS")
