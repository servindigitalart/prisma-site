def calculate_color_score(ai_reasoning: dict, cultural_weight: dict, authorship: float = 0.0, popularity: float = 0.0) -> dict:
    """
    Calculate doctrine-bound color score for a film using Phase 2A and 2B outputs.
    Inputs:
        ai_reasoning: dict (must include color_assignment.primary.confidence [0–1])
        cultural_weight: dict (must include cultural_weight_score [0–100])
        authorship: float (optional, normalized 0–100)
        popularity: float (optional, normalized 0–100)
    Output:
        {
            "work_id": str,
            "numeric_score": float (0–100),
            "breakdown": list[str],
            "doctrine_version": str
        }
    """
    import json
    import os

    # Load doctrine
    doctrine_path = os.path.join(
        os.path.dirname(__file__),
        "../doctrine/current/score_doctrine.json"
    )
    with open(doctrine_path, "r") as f:
        doctrine = json.load(f)
    formula = doctrine.get("formula", {})

    # Read weights from flat keys
    w_ai = formula.get("ai_confidence_weight", 0.0)
    w_auth = formula.get("authorship_weight", 0.0)
    w_cult = formula.get("cultural_recognition_weight", 0.0)
    w_pop = formula.get("popularity_weight", 0.0)

    # Defensive extraction
    ai_conf = 0.0
    color_assignment = ai_reasoning.get("color_assignment", {})
    primary = color_assignment.get("primary", {})
    confidence = primary.get("confidence", None)
    if confidence is not None:
        try:
            ai_conf = float(confidence) * 100.0
        except Exception:
            ai_conf = 0.0
    else:
        ai_conf = 0.0
    authorship = float(authorship)
    popularity = float(popularity)
    cultural_recognition = float(cultural_weight.get("cultural_weight_score", 0.0))

    # Weighted sum
    score = (
        ai_conf * w_ai +
        authorship * w_auth +
        cultural_recognition * w_cult +
        popularity * w_pop
    )
    score = min(score, 100)

    breakdown = [
        f"AI confidence × {w_ai}: {ai_conf} × {w_ai} = {ai_conf * w_ai}",
        f"Authorship × {w_auth}: {authorship} × {w_auth} = {authorship * w_auth}",
        f"Cultural recognition × {w_cult}: {cultural_recognition} × {w_cult} = {cultural_recognition * w_cult}",
        f"Popularity × {w_pop}: {popularity} × {w_pop} = {popularity * w_pop}",
        f"Total (capped at 100): {score}"
    ]

    work_id = ai_reasoning.get("work_id", cultural_weight.get("work_id", ""))
    return {
        "work_id": work_id,
        "numeric_score": score,
        "breakdown": breakdown,
        "doctrine_version": doctrine.get("version", "")
    }