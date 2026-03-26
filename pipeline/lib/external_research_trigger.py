#!/usr/local/bin/python3
"""
External Research Trigger Decision Logic

WHAT THIS MODULE DOES:
- Deterministically decides whether External Research should be triggered
- Applies External Research Policy rules
- Returns structured trigger decision with audit metadata

WHAT THIS MODULE DOES NOT DO:
- Does NOT execute research
- Does NOT assign colors
- Does NOT reason about aesthetics
- Does NOT call AI or external APIs
- Does NOT persist data
- Does NOT mutate inputs
- Does NOT use heuristics or randomness

EPISTEMIC POSITION:
This module is a policy gate with NO decision-making authority beyond policy application.
It enforces rules defined in External Research Policy.
"""

from typing import Dict, Any, Optional, Literal, Set


TriggerReason = Literal["evidence_gap", "cultural_context", "doctrine_ambiguity"]


WESTERN_CANON_COUNTRIES = {"US", "GB", "FR", "IT"}
WESTERN_CANON_YEAR_START = 1960
WESTERN_CANON_YEAR_END = 2010

UNDER_DOCUMENTED_YEAR_EARLY = 1960
UNDER_DOCUMENTED_YEAR_RECENT = 2020


class TriggerDecision:
    """Container for trigger decision result."""
    
    def __init__(self):
        self.should_trigger: bool = False
        self.trigger_reason: Optional[TriggerReason] = None
        self.evidence_gap_description: Optional[str] = None
        self.doctrine_ambiguity_description: Optional[str] = None
        self.decision_metadata: Dict[str, bool] = {
            "evidence_consulted": False,
            "editorial_override_exists": False,
            "film_in_evidence": False,
            "cinematographer_in_evidence": False,
            "national_cinema_in_evidence": False,
            "is_western_canon": False
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "should_trigger": self.should_trigger,
            "trigger_reason": self.trigger_reason,
            "evidence_gap_description": self.evidence_gap_description,
            "doctrine_ambiguity_description": self.doctrine_ambiguity_description,
            "decision_metadata": self.decision_metadata
        }


def should_trigger_external_research(
    work: Dict[str, Any],
    evidence_snapshot: Dict[str, Any],
    doctrine_version: str,
    editorial_override: bool = False,
    doctrine_ambiguity: bool = False,
    doctrine_ambiguity_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Decide whether External Research should be triggered for a work.
    
    Args:
        work: Normalized work dict from pipeline/normalized/works/
        evidence_snapshot: Evidence availability information:
            {
                "film_exists": bool,
                "cinematographer_exists": bool,
                "national_cinema_exists": bool,
                "national_cinema_count": int
            }
        doctrine_version: Current doctrine version (e.g., "1.1")
        editorial_override: Whether work has editorial color override
        doctrine_ambiguity: Whether doctrine presents ambiguous assignment
        doctrine_ambiguity_description: Optional description of ambiguity
    
    Returns:
        Trigger decision dict with structure defined in module docstring
    """
    decision = TriggerDecision()
    
    decision.decision_metadata["evidence_consulted"] = True
    decision.decision_metadata["editorial_override_exists"] = editorial_override
    
    if editorial_override:
        return decision.to_dict()
    
    decision.decision_metadata["film_in_evidence"] = evidence_snapshot.get("film_exists", False)
    if evidence_snapshot.get("film_exists", False):
        return decision.to_dict()
    
    decision.decision_metadata["cinematographer_in_evidence"] = evidence_snapshot.get("cinematographer_exists", False)
    if evidence_snapshot.get("cinematographer_exists", False):
        return decision.to_dict()
    
    national_cinema_exists = evidence_snapshot.get("national_cinema_exists", False)
    decision.decision_metadata["national_cinema_in_evidence"] = national_cinema_exists
    
    national_cinema_count = evidence_snapshot.get("national_cinema_count", 0)
    if national_cinema_exists and national_cinema_count >= 10:
        return decision.to_dict()
    
    is_western_canon = _is_western_canon(work)
    decision.decision_metadata["is_western_canon"] = is_western_canon
    if is_western_canon:
        return decision.to_dict()
    
    has_metadata = _has_sufficient_metadata(work)
    if not has_metadata:
        return decision.to_dict()
    
    if doctrine_ambiguity:
        decision.should_trigger = True
        decision.trigger_reason = "doctrine_ambiguity"
        decision.doctrine_ambiguity_description = doctrine_ambiguity_description
        return decision.to_dict()
    
    is_non_western = _is_non_western_cinema(work)
    is_under_documented_period = _is_under_documented_period(work)
    
    if is_non_western or is_under_documented_period:
        decision.should_trigger = True
        decision.trigger_reason = "cultural_context"
        decision.evidence_gap_description = _build_evidence_gap_description(
            work, 
            is_non_western, 
            is_under_documented_period,
            national_cinema_exists,
            national_cinema_count
        )
        return decision.to_dict()
    
    decision.should_trigger = True
    decision.trigger_reason = "evidence_gap"
    decision.evidence_gap_description = _build_evidence_gap_description(
        work,
        is_non_western,
        is_under_documented_period,
        national_cinema_exists,
        national_cinema_count
    )
    
    return decision.to_dict()


def _is_western_canon(work: Dict[str, Any]) -> bool:
    """
    Check if work is Western canon (US/UK/France/Italy, 1960-2010).
    
    Args:
        work: Normalized work dict
    
    Returns:
        True if work is Western canon, False otherwise
    """
    year = work.get("year")
    if not year:
        return False
    
    if not (WESTERN_CANON_YEAR_START <= year <= WESTERN_CANON_YEAR_END):
        return False
    
    countries = work.get("countries", [])
    if not countries:
        return False
    
    primary_country = countries[0]
    
    return primary_country in WESTERN_CANON_COUNTRIES


def _is_non_western_cinema(work: Dict[str, Any]) -> bool:
    """
    Check if work is from non-Western cinema.
    
    Args:
        work: Normalized work dict
    
    Returns:
        True if non-Western, False otherwise
    """
    countries = work.get("countries", [])
    if not countries:
        return False
    
    primary_country = countries[0]
    
    return primary_country not in WESTERN_CANON_COUNTRIES


def _is_under_documented_period(work: Dict[str, Any]) -> bool:
    """
    Check if work is from under-documented period (pre-1960 or post-2020).
    
    Args:
        work: Normalized work dict
    
    Returns:
        True if under-documented period, False otherwise
    """
    year = work.get("year")
    if not year:
        return False
    
    return year < UNDER_DOCUMENTED_YEAR_EARLY or year >= UNDER_DOCUMENTED_YEAR_RECENT


def _has_sufficient_metadata(work: Dict[str, Any]) -> bool:
    """
    Check if work has sufficient metadata for research trigger evaluation.
    
    Args:
        work: Normalized work dict
    
    Returns:
        True if sufficient metadata exists, False otherwise
    """
    required_fields = ["id", "title", "year", "countries"]
    
    for field in required_fields:
        if field not in work:
            return False
        
        value = work[field]
        
        if value is None:
            return False
        
        if field == "countries" and not value:
            return False
    
    return True


def _build_evidence_gap_description(
    work: Dict[str, Any],
    is_non_western: bool,
    is_under_documented_period: bool,
    national_cinema_exists: bool,
    national_cinema_count: int
) -> str:
    """
    Build human-readable evidence gap description.
    
    Args:
        work: Normalized work dict
        is_non_western: Whether film is non-Western
        is_under_documented_period: Whether from under-documented period
        national_cinema_exists: Whether national cinema has any Evidence
        national_cinema_count: Number of films from this cinema in Evidence
    
    Returns:
        Evidence gap description string
    """
    parts = []
    
    parts.append("Film not found in Evidence.")
    
    cinematographer = work.get("people", {}).get("cinematography", [])
    if cinematographer:
        parts.append("Cinematographer not found in Evidence.")
    else:
        parts.append("Cinematographer unknown.")
    
    countries = work.get("countries", [])
    if countries:
        country_str = ", ".join(countries)
        if national_cinema_exists:
            parts.append(
                f"National cinema ({country_str}) has limited Evidence coverage ({national_cinema_count} films)."
            )
        else:
            parts.append(f"National cinema ({country_str}) not documented in Evidence.")
    
    if is_under_documented_period:
        year = work.get("year")
        if year:
            if year < UNDER_DOCUMENTED_YEAR_EARLY:
                parts.append(f"Film from under-documented early period ({year}).")
            else:
                parts.append(f"Film from under-documented recent period ({year}).")
    
    return " ".join(parts)


def check_evidence_snapshot(
    work: Dict[str, Any],
    evidence_films: Set[str],
    evidence_cinematographers: Set[str],
    evidence_national_cinemas: Dict[str, int]
) -> Dict[str, Any]:
    """
    Check what evidence exists for a work.
    
    Args:
        work: Normalized work dict
        evidence_films: Set of work IDs in Evidence
        evidence_cinematographers: Set of cinematographer IDs in Evidence
        evidence_national_cinemas: Dict mapping country codes to film counts
    
    Returns:
        Evidence snapshot dict:
        {
            "film_exists": bool,
            "cinematographer_exists": bool,
            "national_cinema_exists": bool,
            "national_cinema_count": int
        }
    """
    work_id = work.get("id")
    film_exists = work_id in evidence_films if work_id else False
    
    cinematographer_ids = work.get("people", {}).get("cinematography", [])
    cinematographer_exists = False
    if cinematographer_ids:
        cinematographer_exists = cinematographer_ids[0] in evidence_cinematographers
    
    countries = work.get("countries", [])
    national_cinema_exists = False
    national_cinema_count = 0
    
    if countries:
        primary_country = countries[0]
        if primary_country in evidence_national_cinemas:
            national_cinema_exists = True
            national_cinema_count = evidence_national_cinemas[primary_country]
    
    return {
        "film_exists": film_exists,
        "cinematographer_exists": cinematographer_exists,
        "national_cinema_exists": national_cinema_exists,
        "national_cinema_count": national_cinema_count
    }