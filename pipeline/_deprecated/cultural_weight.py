"""
PHASE 2B — CULTURAL WEIGHT CALCULATION
====================================

PURPOSE
-------
Calculate the editorial cultural weight of a film STRICTLY following
pipeline/doctrine/current/score_doctrine.json.

This module is QUANTITATIVE and DOCTRINE-BOUND.

WHAT THIS MODULE DOES
---------------------
- Reads score_doctrine.json
- Calculates cultural weight signals exactly as defined
- Sums signals into a 0–100 score
- Returns transparent breakdown for editorial inspection

WHAT THIS MODULE MUST NOT DO
----------------------------
- Must NOT consult evidence
- Must NOT infer prestige heuristically
- Must NOT invent new signals
- Must NOT normalize beyond doctrine rules
- Must NOT exceed doctrine maximums

INPUT
-----
work: dict
Normalized work object from pipeline/normalized/works/

OUTPUT
------
{
    "work_id": str,
    "cultural_weight_score": float (0–100),
    "signals": {
        "festival_prestige": float,
        "critical_canon": float,
        "cinematography_awards": float,
        "arthouse_distribution": float,
        "non_english_bonus": float,
        "editorial_boost": float
    },
    "breakdown": list[str],
    "doctrine_version": str
}

IMPORTANT RULES
---------------
- If required data is missing → score = 0 for that signal
- Editorial override ALWAYS applies if present
- Final score is capped at 100
- No external lists, APIs, or assumptions

IMPLEMENTATION STATUS
---------------------
Only ONE function should be implemented in this file for now:
- calculate_cultural_weight(work)

All helpers may be added if strictly necessary and doctrine-bound.
"""

def calculate_cultural_weight(work: dict) -> dict:
    import json
    import os

    # Doctrine loader: use local loader if available, else fallback to file
    try:
        from pipeline.lib.doctrine import load_doctrine
        doctrine = load_doctrine("score_doctrine")
    except Exception:
        doctrine_path = os.path.join(
            os.path.dirname(__file__),
            "../doctrine/current/score_doctrine.json"
        )
        with open(doctrine_path, "r") as f:
            doctrine = json.load(f)

    signals = {
        "festival_prestige": 0.0,
        "critical_canon": 0.0,
        "cinematography_awards": 0.0,
        "arthouse_distribution": 0.0,
        "non_english_bonus": 0.0,
        "editorial_boost": 0.0
    }
    breakdown = []

    # Defensive doctrine access
    cw_signals = doctrine.get("cultural_weight_signals", {})

    # FESTIVAL PRESTIGE
    fest_signal = 0.0
    fest_info = work.get("festival_awards", [])
    fest_doctrine = cw_signals.get("festivals", {}).get("criteria", {})
    if fest_info and fest_doctrine:
        for award in fest_info:
            for tier, tier_data in fest_doctrine.items():
                if isinstance(tier_data, dict) and "festivals" in tier_data and "points" in tier_data:
                    if award in tier_data["festivals"]:
                        fest_signal = max(fest_signal, tier_data["points"])
                        breakdown.append(f"Festival: {award} → {tier_data['points']} points")
    else:
        breakdown.append("No festival data → 0 points")
    signals["festival_prestige"] = fest_signal

    # CRITICAL CANON (MVP: only if doctrine and work both provide explicit keys)
    canon_signal = 0.0
    canon_doctrine = cw_signals.get("critical_canon", {}).get("criteria", {})
    canon_info = work.get("critical_canon", {})
    if canon_doctrine and canon_info:
        for key, value in canon_doctrine.items():
            if canon_info.get(key):
                points = value["points"] if isinstance(value, dict) and "points" in value else value if isinstance(value, (int, float)) else 0
                canon_signal = max(canon_signal, points)
                breakdown.append(f"Critical Canon: {key} → {points} points")
    else:
        breakdown.append("No critical canon data → 0 points")
    signals["critical_canon"] = canon_signal

    # CINEMATOGRAPHY AWARDS
    cine_signal = 0.0
    cine_doctrine = cw_signals.get("cinematography_awards", {}).get("criteria", {})
    cine_info = work.get("cinematography_awards", [])
    if cine_info and cine_doctrine:
        for award in cine_info:
            for key, value in cine_doctrine.items():
                points = value["points"] if isinstance(value, dict) and "points" in value else value if isinstance(value, (int, float)) else 0
                if award == key:
                    cine_signal = max(cine_signal, points)
                    breakdown.append(f"Cinematography Award: {award} → {points} points")
    else:
        breakdown.append("No cinematography award data → 0 points")
    signals["cinematography_awards"] = cine_signal

    # ARTHOUSE DISTRIBUTION
    arthouse_signal = 0.0
    arthouse_doctrine = cw_signals.get("arthouse_distribution", {}).get("criteria", {})
    arthouse_info = work.get("arthouse_distribution", [])
    if arthouse_info and arthouse_doctrine:
        for dist in arthouse_info:
            if dist in arthouse_doctrine:
                points = arthouse_doctrine[dist] if isinstance(arthouse_doctrine[dist], (int, float)) else 0
                arthouse_signal = max(arthouse_signal, points)
                breakdown.append(f"Arthouse Distribution: {dist} → {points} points")
    else:
        breakdown.append("No arthouse distribution data → 0 points")
    signals["arthouse_distribution"] = arthouse_signal

    # NON-ENGLISH BONUS (doctrine conditions only)
    lang_signal = 0.0
    lang_doctrine = cw_signals.get("language_bonus", {}).get("criteria", {})
    language = work.get("language", None)
    non_english_points = lang_doctrine.get("non_english", 0)
    if language and language != "English" and non_english_points:
        lang_signal = non_english_points
        breakdown.append(f"Non-English language → {lang_signal} points")
    else:
        breakdown.append("No non-English bonus → 0 points")
    signals["non_english_bonus"] = lang_signal

    # EDITORIAL BOOST
    editorial_signal = 0.0
    editorial_boost = work.get("editorial_boost", 0.0)
    max_boost = cw_signals.get("editorial_boost", {}).get("max_points", 0)
    if editorial_boost and max_boost:
        editorial_signal = min(editorial_boost, max_boost)
        breakdown.append(f"Editorial boost applied → {editorial_signal} points")
    else:
        breakdown.append("No editorial boost → 0 points")
    signals["editorial_boost"] = editorial_signal

    # SUM AND CAP
    total_score = sum(signals.values())
    total_score = min(total_score, 100)

    return {
        "work_id": work.get("work_id", ""),
        "cultural_weight_score": total_score,
        "signals": signals,
        "breakdown": breakdown,
        "doctrine_version": doctrine.get("version", "")
    }
