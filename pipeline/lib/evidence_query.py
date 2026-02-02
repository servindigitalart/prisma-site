"""
Evidence Query Layer - Non-Prescriptive Evidence Access

This module provides strictly non-prescriptive query functions for accessing
Prisma's evidence layer. All functions return descriptive context only.

CRITICAL RULES:
- Evidence returns context, not decisions
- Always return plural perspectives when available
- Preserve contradictions and debates
- Quote sources; never collapse into assertions
- Empty results are valid
- NEVER assign colors or make recommendations

Compliance with pipeline/evidence/FRAMEWORK.md is mandatory.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


# Evidence directory paths
EVIDENCE_V1_DIR = Path(__file__).parent.parent / "evidence" / "v1.0"
EVIDENCE_V2_DIR = Path(__file__).parent.parent / "evidence" / "v2.0"


def _load_evidence_file(version: str, filename: str) -> Dict[str, Any]:
    """Load evidence JSON file from specified version."""
    if version == "v1.0":
        evidence_dir = EVIDENCE_V1_DIR
    elif version == "v2.0":
        evidence_dir = EVIDENCE_V2_DIR
    else:
        raise ValueError(f"Unknown evidence version: {version}")
    
    file_path = evidence_dir / filename
    if not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_cinematographer_context(cinematographer_name: str, version: str = "v2.0") -> Dict[str, Any]:
    """
    Query evidence for cinematographer's documented perspectives.
    
    Args:
        cinematographer_name: Name of cinematographer to query
        version: Evidence version to query (default: v2.0)
    
    Returns:
        {
            "name": str,
            "documented_perspectives": list[dict],  # Quoted statements with sources
            "critical_assessments": list[dict],     # What critics say about their work
            "collaborations": list[dict],           # Films discussed with context
            "sources": list[str]
        }
    
    MUST NOT return:
    - color_signatures
    - recommended_colors
    - numeric scores
    """
    cinematographers_data = _load_evidence_file(version, "cinematographers.json")
    
    if not cinematographers_data or "cinematographers" not in cinematographers_data:
        return {
            "name": cinematographer_name,
            "documented_perspectives": [],
            "critical_assessments": [],
            "collaborations": [],
            "sources": [],
            "note": "No evidence found for this cinematographer"
        }
    
    # Find cinematographer (case-insensitive search)
    cinematographer = None
    for dp in cinematographers_data["cinematographers"]:
        if dp["name"].lower() == cinematographer_name.lower():
            cinematographer = dp
            break
    
    if not cinematographer:
        return {
            "name": cinematographer_name,
            "documented_perspectives": [],
            "critical_assessments": [],
            "collaborations": [],
            "sources": [],
            "note": f"No evidence found for cinematographer: {cinematographer_name}"
        }
    
    # Structure response preserving evidence nature
    documented_perspectives = []
    if "documented_color_philosophy" in cinematographer:
        for philosophy in cinematographer["documented_color_philosophy"]:
            documented_perspectives.append({
                "statement": philosophy,
                "type": "philosophy",
                "source_attribution": "Documented in evidence layer"
            })
    
    if "key_concepts" in cinematographer:
        for concept in cinematographer["key_concepts"]:
            documented_perspectives.append({
                "statement": concept,
                "type": "concept",
                "source_attribution": "Documented in evidence layer"
            })
    
    # Critical assessments from evidence
    critical_assessments = []
    if "philosophy_summary" in cinematographer:
        critical_assessments.append({
            "assessment": cinematographer["philosophy_summary"],
            "type": "summary",
            "source": "Evidence layer synthesis"
        })
    
    if "color_approach_summary" in cinematographer:
        critical_assessments.append({
            "assessment": cinematographer["color_approach_summary"],
            "type": "approach_analysis",
            "source": "Evidence layer synthesis"
        })
    
    # Collaborations (films mentioned in context)
    collaborations = []
    if "referenced_films" in cinematographer:
        for film in cinematographer["referenced_films"]:
            collaborations.append({
                "film": film,
                "context": "Referenced in cinematographer evidence",
                "note": "Illustrative example only - not color assignment"
            })
    
    if "cited_films" in cinematographer:
        for film in cinematographer["cited_films"]:
            collaborations.append({
                "film": film,
                "context": "Cited in evidence analysis",
                "note": "Illustrative example only - not color assignment"
            })
    
    # Sources
    sources = []
    if "sources" in cinematographer:
        for source in cinematographer["sources"]:
            if isinstance(source, dict):
                sources.append(source.get("description", str(source)))
            else:
                sources.append(str(source))
    
    if "source_citations" in cinematographer:
        sources.extend(cinematographer["source_citations"])
    
    return {
        "name": cinematographer["name"],
        "documented_perspectives": documented_perspectives,
        "critical_assessments": critical_assessments,
        "collaborations": collaborations,
        "sources": sources,
        "evidence_version": version,
        "note": "All content is descriptive evidence, not prescriptive guidance"
    }


def get_film_critical_discourse(work_title: str, year: int, version: str = "v2.0") -> Dict[str, Any]:
    """
    Query evidence for critical discourse about a film's aesthetics.
    
    Args:
        work_title: Title of film to query
        year: Year of film
        version: Evidence version to query
    
    Returns:
        {
            "film": str,
            "perspectives": list[dict],
            "debates": list[dict], 
            "theoretical_readings": list[dict],
            "sources": list[str]
        }
    
    MUST NOT return:
    - assigned_color
    - dominant_color
    - color_mapping
    """
    case_studies = _load_evidence_file(version, "film_case_studies.json")
    
    if not case_studies or "films" not in case_studies:
        return {
            "film": f"{work_title} ({year})",
            "perspectives": [],
            "debates": [],
            "theoretical_readings": [],
            "sources": [],
            "note": "No critical discourse found in evidence"
        }
    
    # Find film (flexible matching)
    film_data = None
    for film in case_studies["films"]:
        if (film.get("title", "").lower() == work_title.lower() and 
            film.get("year") == year):
            film_data = film
            break
    
    if not film_data:
        # Try title-only match if year doesn't match exactly
        for film in case_studies["films"]:
            if film.get("title", "").lower() == work_title.lower():
                film_data = film
                break
    
    if not film_data:
        return {
            "film": f"{work_title} ({year})",
            "perspectives": [],
            "debates": [],
            "theoretical_readings": [],
            "sources": [],
            "note": f"No critical discourse found for {work_title} ({year})"
        }
    
    # Extract perspectives
    perspectives = []
    if "color_discussion_summary" in film_data:
        perspectives.append({
            "perspective": film_data["color_discussion_summary"],
            "type": "critical_analysis",
            "source": "Evidence layer synthesis"
        })
    
    if "described_color_strategy" in film_data:
        perspectives.append({
            "perspective": film_data["described_color_strategy"],
            "type": "strategy_analysis", 
            "source": "Evidence layer documentation"
        })
    
    # Theoretical readings
    theoretical_readings = []
    if "themes" in film_data:
        for theme in film_data["themes"]:
            theoretical_readings.append({
                "reading": theme,
                "type": "thematic_analysis",
                "source": "Evidence layer categorization"
            })
    
    if "color_approach" in film_data:
        theoretical_readings.append({
            "reading": film_data["color_approach"],
            "type": "approach_categorization",
            "source": "Evidence layer analysis"
        })
    
    # Key insights as debates/discussions
    debates = []
    if "key_insight" in film_data:
        debates.append({
            "debate": film_data["key_insight"],
            "type": "analytical_insight",
            "source": "Evidence layer synthesis"
        })
    
    if "narrative_function_of_color" in film_data:
        debates.append({
            "debate": film_data["narrative_function_of_color"],
            "type": "narrative_analysis",
            "source": "Evidence layer documentation"
        })
    
    # Sources
    sources = []
    if "sources" in film_data:
        for source in film_data["sources"]:
            if isinstance(source, dict):
                sources.append(source.get("description", str(source)))
            else:
                sources.append(str(source))
    
    if "source_citations" in film_data:
        sources.extend(film_data["source_citations"])
    
    return {
        "film": f"{film_data.get('title', work_title)} ({film_data.get('year', year)})",
        "director": film_data.get("director"),
        "cinematographer": film_data.get("cinematographer"),
        "perspectives": perspectives,
        "debates": debates,
        "theoretical_readings": theoretical_readings,
        "sources": sources,
        "evidence_version": version,
        "note": "All content is descriptive evidence, not color assignments"
    }


def get_genre_aesthetic_discourse(genres: List[str], version: str = "v2.0") -> Dict[str, Any]:
    """
    Query evidence for documented genre aesthetics.
    
    Args:
        genres: List of genre strings to query
        version: Evidence version to query
    
    Returns:
        {
            "genres": list[str],
            "documented_conventions": list[dict],
            "debates": list[dict],
            "canonical_references": list[dict],
            "theoretical_frameworks": list[str],
            "sources": list[str]
        }
    
    NOTE:
    - Do NOT assume genre priority by list order
    - Do NOT map genres to colors
    """
    color_themes = _load_evidence_file(version, "color_themes.json")
    movements = _load_evidence_file(version, "movements_and_periods.json")
    
    documented_conventions = []
    debates = []
    canonical_references = []
    theoretical_frameworks = []
    sources = []
    
    # Query color themes for genre-related patterns
    if color_themes and "color_themes" in color_themes:
        for theme in color_themes["color_themes"]:
            theme_examples = theme.get("examples", [])
            theme_contradictions = theme.get("contradictions", [])
            
            # Check if any examples mention our genres
            relevant_examples = []
            for example in theme_examples:
                for genre in genres:
                    if genre.lower() in example.lower():
                        relevant_examples.append(example)
            
            if relevant_examples:
                documented_conventions.append({
                    "theme": theme.get("theme_id"),
                    "description": theme.get("description"),
                    "relevant_examples": relevant_examples,
                    "type": "color_theme"
                })
                
                # Add contradictions as debates
                for contradiction in theme_contradictions:
                    debates.append({
                        "debate": contradiction,
                        "context": theme.get("theme_id"),
                        "type": "contradiction"
                    })
    
    # Query movements for genre-related periods
    if movements and "movements_and_periods" in movements:
        for movement in movements["movements_and_periods"]:
            movement_genres = movement.get("genre_associations", [])
            
            # Check for genre overlap
            genre_overlap = any(genre.lower() in [g.lower() for g in movement_genres] 
                             for genre in genres)
            
            if genre_overlap:
                documented_conventions.append({
                    "movement": movement.get("period"),
                    "characteristics": movement.get("defining_color_characteristics", []),
                    "context": movement.get("ideological_context"),
                    "type": "historical_movement"
                })
                
                if "key_films" in movement:
                    for film in movement["key_films"]:
                        canonical_references.append({
                            "reference": film,
                            "context": movement.get("period"),
                            "type": "movement_example"
                        })
    
    # Collect theoretical frameworks mentioned
    theoretical_frameworks = list(set(theoretical_frameworks))
    
    # Collect all sources
    all_sources = set()
    if color_themes and "color_themes" in color_themes:
        for theme in color_themes["color_themes"]:
            all_sources.update(theme.get("sources", []))
    
    if movements and "movements_and_periods" in movements:
        for movement in movements["movements_and_periods"]:
            all_sources.update(movement.get("sources", []))
    
    sources = list(all_sources)
    
    return {
        "genres": genres,
        "documented_conventions": documented_conventions,
        "debates": debates,
        "canonical_references": canonical_references,
        "theoretical_frameworks": theoretical_frameworks,
        "sources": sources,
        "evidence_version": version,
        "note": "All content is descriptive evidence. Do NOT assume genre priority by list order. Do NOT map genres to colors."
    }


def get_color_theory_discourse(color_concept: str, version: str = "v2.0") -> Dict[str, Any]:
    """
    Query evidence for theoretical color frameworks.
    
    Args:
        color_concept: Color concept to query (e.g., "red", "monochromatic", "artificial")
        version: Evidence version to query
    
    Returns:
        {
            "concept": str,
            "psychological_frameworks": list[dict],
            "cultural_frameworks": list[dict],
            "semiotic_frameworks": list[dict], 
            "historical_contexts": list[dict],
            "sources": list[str]
        }
    
    MUST NOT return prescriptive guidance.
    """
    frameworks = _load_evidence_file(version, "theoretical_frameworks.json")
    color_themes = _load_evidence_file(version, "color_themes.json")
    
    psychological_frameworks = []
    cultural_frameworks = []
    semiotic_frameworks = []
    historical_contexts = []
    sources = []
    
    # Query theoretical frameworks
    if frameworks and "frameworks" in frameworks:
        for framework in frameworks["frameworks"]:
            framework_concepts = framework.get("key_concepts", [])
            framework_description = framework.get("description", "")
            
            # Check if concept appears in framework
            concept_relevant = (
                color_concept.lower() in framework_description.lower() or
                any(color_concept.lower() in concept.lower() for concept in framework_concepts)
            )
            
            if concept_relevant:
                framework_entry = {
                    "framework_name": framework.get("name"),
                    "originator": framework.get("originator"),
                    "description": framework.get("description"),
                    "key_concepts": framework_concepts,
                    "application_context": framework.get("application_context")
                }
                
                # Categorize by type
                if "psychological" in framework.get("name", "").lower():
                    psychological_frameworks.append(framework_entry)
                elif "cultural" in framework.get("name", "").lower():
                    cultural_frameworks.append(framework_entry)
                else:
                    semiotic_frameworks.append(framework_entry)
                
                # Add sources
                framework_sources = framework.get("sources", [])
                for source in framework_sources:
                    if isinstance(source, dict):
                        sources.append(source.get("description", str(source)))
                    else:
                        sources.append(str(source))
    
    # Query color themes
    if color_themes and "color_themes" in color_themes:
        for theme in color_themes["color_themes"]:
            theme_id = theme.get("theme_id", "")
            theme_description = theme.get("description", "")
            
            # Check if concept appears in theme
            concept_relevant = (
                color_concept.lower() in theme_id.lower() or
                color_concept.lower() in theme_description.lower()
            )
            
            if concept_relevant:
                historical_contexts.append({
                    "theme": theme_id,
                    "description": theme_description,
                    "examples": theme.get("examples", []),
                    "contradictions": theme.get("contradictions", []),
                    "cultural_variations": theme.get("cultural_variations", [])
                })
                
                sources.extend(theme.get("sources", []))
    
    return {
        "concept": color_concept,
        "psychological_frameworks": psychological_frameworks,
        "cultural_frameworks": cultural_frameworks,
        "semiotic_frameworks": semiotic_frameworks,
        "historical_contexts": historical_contexts,
        "sources": list(set(sources)),
        "evidence_version": version,
        "note": "All content is descriptive evidence. MUST NOT return prescriptive guidance."
    }


def get_movement_context(period: str, version: str = "v2.0") -> Dict[str, Any]:
    """
    Query evidence for cinematic movement color characteristics.
    
    Args:
        period: Period or movement name to query
        version: Evidence version to query
        
    Returns:
        {
            "period": str,
            "color_characteristics": list[str],
            "technological_basis": list[str],
            "ideological_context": str,
            "key_films": list[str],
            "cultural_impact": str,
            "sources": list[str]
        }
    """
    movements = _load_evidence_file(version, "movements_and_periods.json")
    
    if not movements or "movements_and_periods" not in movements:
        return {
            "period": period,
            "color_characteristics": [],
            "technological_basis": [],
            "ideological_context": "",
            "key_films": [],
            "cultural_impact": "",
            "sources": [],
            "note": "No movement context found in evidence"
        }
    
    # Find movement (flexible matching)
    movement_data = None
    for movement in movements["movements_and_periods"]:
        movement_period = movement.get("period", "")
        if period.lower() in movement_period.lower() or movement_period.lower() in period.lower():
            movement_data = movement
            break
    
    if not movement_data:
        return {
            "period": period,
            "color_characteristics": [],
            "technological_basis": [],
            "ideological_context": "",
            "key_films": [],
            "cultural_impact": "",
            "sources": [],
            "note": f"No movement context found for: {period}"
        }
    
    return {
        "period": movement_data.get("period", period),
        "timeframe": movement_data.get("timeframe"),
        "color_characteristics": movement_data.get("defining_color_characteristics", []),
        "technological_basis": movement_data.get("technological_basis", []),
        "ideological_context": movement_data.get("ideological_context", ""),
        "key_films": movement_data.get("key_films", []),
        "cultural_impact": movement_data.get("cultural_impact", ""),
        "sources": movement_data.get("sources", []),
        "evidence_version": version,
        "note": "All examples are illustrative only, not assignments or rankings"
    }


def query_evidence_for_work(work_title: str, year: int, director: str = None, 
                           cinematographer: str = None, genres: List[str] = None) -> Dict[str, Any]:
    """
    Comprehensive evidence query for a specific work.
    
    Args:
        work_title: Title of work
        year: Year of work
        director: Director name (optional)
        cinematographer: Cinematographer name (optional)
        genres: List of genres (optional)
    
    Returns:
        Comprehensive evidence context without prescriptive guidance
    """
    evidence_context = {
        "work": f"{work_title} ({year})",
        "director": director,
        "cinematographer": cinematographer,
        "genres": genres or [],
        "film_discourse": {},
        "cinematographer_context": {},
        "director_context": {},
        "genre_discourse": {},
        "note": "Comprehensive evidence query - all content descriptive only"
    }
    
    # Query film-specific discourse
    evidence_context["film_discourse"] = get_film_critical_discourse(work_title, year)
    
    # Query cinematographer context if provided
    if cinematographer:
        evidence_context["cinematographer_context"] = get_cinematographer_context(cinematographer)
    
    # Query genre discourse if provided
    if genres:
        evidence_context["genre_discourse"] = get_genre_aesthetic_discourse(genres)
    
    return evidence_context


# Utility functions for evidence validation
def validate_evidence_response(response: Dict[str, Any]) -> List[str]:
    """
    Validate that evidence response follows non-prescriptive rules.
    
    Returns list of compliance issues (empty list = compliant)
    """
    issues = []
    
    # Check for prohibited content
    prohibited_keys = [
        "color_assignment", "assigned_color", "dominant_color", "primary_color",
        "recommended_color", "color_mapping", "color_signatures", "scores"
    ]
    
    def check_dict_recursively(d: Dict[str, Any], path: str = ""):
        for key, value in d.items():
            full_key = f"{path}.{key}" if path else key
            
            if key in prohibited_keys:
                issues.append(f"Prohibited key found: {full_key}")
            
            if isinstance(value, dict):
                check_dict_recursively(value, full_key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        check_dict_recursively(item, f"{full_key}[{i}]")
    
    check_dict_recursively(response)
    
    # Check for prescriptive language
    response_str = json.dumps(response).lower()
    prohibited_phrases = [
        "should be", "must be", "is definitely", "assigns", "maps to",
        "dominant color", "primary color is", "best color"
    ]
    
    for phrase in prohibited_phrases:
        if phrase in response_str:
            issues.append(f"Prescriptive language found: '{phrase}'")
    
    return issues


if __name__ == "__main__":
    # Test evidence query functions
    print("Testing Evidence Query Layer...")
    
    # Test cinematographer query
    print("\n1. Testing cinematographer context...")
    dp_context = get_cinematographer_context("Roger Deakins")
    print(f"✓ Found {len(dp_context['documented_perspectives'])} perspectives")
    print(f"✓ Found {len(dp_context['collaborations'])} collaborations")
    
    # Test film discourse query
    print("\n2. Testing film critical discourse...")
    film_discourse = get_film_critical_discourse("Blade Runner", 1982)
    print(f"✓ Found {len(film_discourse['perspectives'])} perspectives")
    print(f"✓ Found {len(film_discourse['debates'])} debates")
    
    # Test genre discourse query
    print("\n3. Testing genre aesthetic discourse...")
    genre_discourse = get_genre_aesthetic_discourse(["sci_fi", "neo_noir"])
    print(f"✓ Found {len(genre_discourse['documented_conventions'])} conventions")
    print(f"✓ Found {len(genre_discourse['debates'])} debates")
    
    # Test color theory query
    print("\n4. Testing color theory discourse...")
    color_theory = get_color_theory_discourse("blue")
    print(f"✓ Found {len(color_theory['psychological_frameworks'])} psychological frameworks")
    print(f"✓ Found {len(color_theory['historical_contexts'])} historical contexts")
    
    # Test comprehensive query
    print("\n5. Testing comprehensive work query...")
    work_context = query_evidence_for_work(
        "Blade Runner", 1982, 
        director="Ridley Scott",
        cinematographer="Jordan Cronenweth",
        genres=["sci_fi", "neo_noir"]
    )
    print(f"✓ Comprehensive context generated")
    
    # Test validation
    print("\n6. Testing evidence validation...")
    issues = validate_evidence_response(dp_context)
    if issues:
        print(f"✗ Validation issues: {issues}")
    else:
        print("✓ Evidence response compliant")
    
    print("\n✅ Evidence Query Layer tests completed!")