#!/usr/local/bin/python3
"""
External Research Request Builder

WHAT THIS MODULE DOES:
- Constructs the exact request payload for Gemini External Research Agent
- Translates internal system state into a structured research request
- Validates that required input fields exist
- Produces deterministic, serializable output

WHAT THIS MODULE DOES NOT DO:
- Does NOT perform research
- Does NOT assign colors
- Does NOT interpret evidence
- Does NOT make inferences about film aesthetics
- Does NOT fetch external data
- Does NOT validate outputs (that's external_research_validator.py)
- Does NOT persist data (that's external_research_persistence.py)
- Does NOT infer, format, or humanize person names

EPISTEMIC POSITION:
This module is a pure data transformer with NO decision-making authority.
It prepares input for an external system (Gemini) following a fixed template.
"""

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime


TriggerReason = Literal[
    "evidence_gap",
    "cultural_context", 
    "doctrine_ambiguity",
    "editorial_request"
]


class ExternalResearchRequestBuilder:
    """
    Builds structured research requests for Gemini External Research Agent.
    
    This is a stateless transformer: inputs → structured request.
    No side effects. No decisions. No color assignment. No inference.
    """
    
    def __init__(self):
        """Initialize builder with no state."""
        pass
    
    def build_request(
        self,
        work: Dict[str, Any],
        trigger_reason: TriggerReason,
        doctrine_version: str,
        evidence_version: str,
        evidence_gap_description: Optional[str] = None,
        doctrine_ambiguity_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build research request payload.
        
        Args:
            work: Normalized work dict from pipeline/normalized/works/
            trigger_reason: Why external research is being triggered
            doctrine_version: Current doctrine version (e.g., "1.1")
            evidence_version: Current evidence version (e.g., "2.1")
            evidence_gap_description: Optional description of evidence gaps
            doctrine_ambiguity_description: Optional description of doctrine ambiguities
        
        Returns:
            Dict matching Gemini External Research USER PROMPT structure
        
        Raises:
            ValueError: If required fields are missing from work
        """
        self._validate_work_structure(work)
        
        work_id = work['id']
        title = work.get('title')
        year = work.get('year')
        countries = work.get('countries', [])
        languages = work.get('languages', [])
        genres = work.get('genres', [])
        
        people = work.get('people', {})
        director_ids = people.get('director', [])
        cinematographer_ids = people.get('cinematography', [])
        
        director = director_ids[0] if director_ids else None
        cinematographer = cinematographer_ids[0] if cinematographer_ids else None
        
        decade = f"{(year // 10) * 10}s" if year and year > 0 else None
        primary_genre = genres[0] if genres else None
        
        request = {
            "request_metadata": {
                "work_id": work_id,
                "trigger_reason": trigger_reason,
                "requested_at": datetime.utcnow().isoformat() + "Z",
                "doctrine_version_context": doctrine_version,
                "evidence_version_context": evidence_version
            },
            "film_to_research": {
                "title": title,
                "year": year,
                "director": director,
                "cinematographer": cinematographer,
                "countries": countries,
                "languages": languages,
                "genres": genres
            },
            "research_goals": {
                "cinematographer_context": self._build_cinematographer_goals(cinematographer),
                "film_aesthetic_discourse": self._build_film_discourse_goals(title, year),
                "cultural_genre_context": self._build_cultural_context_goals(
                    countries, decade, primary_genre
                )
            },
            "internal_evidence_status": evidence_gap_description,
            "doctrine_ambiguity": doctrine_ambiguity_description
        }
        
        return request
    
    def _validate_work_structure(self, work: Dict[str, Any]) -> None:
        """
        Validate that work dict has required fields.
        
        Args:
            work: Work dictionary
        
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['id']
        
        for field in required_fields:
            if field not in work:
                raise ValueError(f"Work dict missing required field: {field}")
    
    def _build_cinematographer_goals(self, cinematographer: Optional[str]) -> List[str]:
        """
        Build cinematographer research goals.
        
        Args:
            cinematographer: Cinematographer ID or None
        
        Returns:
            List of research goal strings
        """
        if cinematographer is None:
            return [
                "Find information about this film's cinematographer",
                "Find critical assessments of this film's cinematography",
                "Find documentation of cinematographic approach"
            ]
        
        return [
            f"Find statements by {cinematographer} about this film's visual approach",
            f"Find critical assessments of {cinematographer}'s work on this film",
            f"Find documentation of {cinematographer}'s aesthetic philosophy"
        ]
    
    def _build_film_discourse_goals(self, title: Optional[str], year: Optional[int]) -> List[str]:
        """
        Build film aesthetic discourse research goals.
        
        Args:
            title: Film title or None
            year: Film year or None
        
        Returns:
            List of research goal strings
        """
        if title is None:
            return [
                "Find critical reviews discussing visual/color aesthetics",
                "Find scholarly analyses of cinematography",
                "Find director statements about visual intent"
            ]
        
        title_year = f"{title} ({year})" if year else title
        
        return [
            f"Find contemporary critical reviews of {title_year} discussing visual/color aesthetics",
            f"Find scholarly analyses of {title}'s cinematography",
            f"Find director statements about {title}'s visual intent"
        ]
    
    def _build_cultural_context_goals(
        self, 
        countries: List[str], 
        decade: Optional[str], 
        primary_genre: Optional[str]
    ) -> List[str]:
        """
        Build cultural/genre context research goals.
        
        Args:
            countries: Country codes
            decade: Decade string (e.g., "2000s") or None
            primary_genre: Primary genre or None
        
        Returns:
            List of research goal strings
        """
        country_str = ', '.join(countries) if countries else None
        
        goals = []
        
        if country_str and decade:
            goals.append(f"Find information about {country_str} cinema aesthetics in {decade}")
        elif country_str:
            goals.append(f"Find information about {country_str} cinema aesthetics")
        
        if primary_genre and decade:
            goals.append(f"Find documentation of {primary_genre} visual conventions in {decade}")
        elif primary_genre:
            goals.append(f"Find documentation of {primary_genre} visual conventions")
        
        if country_str and decade:
            goals.append(f"Find historical context affecting production design in {country_str} during {decade}")
        
        if not goals:
            goals.append("Find historical and cultural context affecting production design")
        
        return goals


def build_external_research_request(
    work: Dict[str, Any],
    trigger_reason: TriggerReason,
    doctrine_version: str,
    evidence_version: str,
    evidence_gap_description: Optional[str] = None,
    doctrine_ambiguity_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for building research requests.
    
    Args:
        work: Normalized work dict
        trigger_reason: Research trigger reason
        doctrine_version: Current doctrine version
        evidence_version: Current evidence version
        evidence_gap_description: Optional evidence gap description
        doctrine_ambiguity_description: Optional doctrine ambiguity description
    
    Returns:
        Structured research request dict
    """
    builder = ExternalResearchRequestBuilder()
    return builder.build_request(
        work=work,
        trigger_reason=trigger_reason,
        doctrine_version=doctrine_version,
        evidence_version=evidence_version,
        evidence_gap_description=evidence_gap_description,
        doctrine_ambiguity_description=doctrine_ambiguity_description
    )