"""
AI Color Reasoning Agent - Doctrine-First Implementation

This module implements AI color reasoning that strictly follows Prisma doctrine
and consults evidence per the Evidence Framework requirements.

CRITICAL CONSTRAINTS:
- Cultural memory over pixel dominance
- Evidence informs, doctrine constrains
- Evidence never assigns colors
- Conflicting evidence must be acknowledged
- Confidence must be explained qualitatively

Compliance with pipeline/evidence/FRAMEWORK.md is mandatory.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from lib.doctrine import load_doctrine, get_color_palette, get_monochromatic_modes, get_assignment_rules
from lib.evidence_query import (
    get_cinematographer_context, 
    get_film_critical_discourse,
    get_genre_aesthetic_discourse,
    query_evidence_for_work
)


def reason_about_color(work: Dict[str, Any]) -> Dict[str, Any]:
    """
    Doctrine-first color reasoning for a film work.
    
    Args:
        work: Work dictionary with title, year, director, cinematographer, genres, etc.
    
    Returns:
        {
            "work_id": str,
            "color_assignment": {
                "primary": {
                    "color_id": str,
                    "confidence": float,
                    "confidence_explanation": str
                },
                "secondary": [
                    {"color_id": str, "confidence": float},
                    ...
                ],
                "monochromatic": {
                    "is_monochromatic": bool,
                    "mode": str | None
                }
            },
            "reasoning_chain": {
                "doctrine_application": {...},
                "evidence_context": {...},
                "evidence_interpretation": str,
                "conflicts_acknowledged": str | None,
                "final_reasoning": str
            },
            "metadata": {
                "model": "doctrine-based-reasoning",
                "doctrine_version": "1.1",
                "evidence_version": "v2.0",
                "processed_at": str
            }
        }
    """
    
    # Load doctrine
    color_doctrine = load_doctrine("color_doctrine")
    colors = get_color_palette()
    monochromatic_modes = get_monochromatic_modes()
    assignment_rules = get_assignment_rules()
    
    # Extract work information
    work_id = work.get("id", f"work_{work.get('title', 'unknown').lower().replace(' ', '_')}_{work.get('year', 0)}")
    title = work.get("title", "Unknown")
    year = work.get("year", 0)
    director = work.get("people", {}).get("director", [None])[0] if work.get("people", {}).get("director") else None
    cinematographer = work.get("people", {}).get("cinematography", [None])[0] if work.get("people", {}).get("cinematography") else None
    genres = work.get("genres", [])
    
    # Query evidence comprehensively
    evidence_context = query_evidence_for_work(
        work_title=title,
        year=year,
        director=director,
        cinematographer=cinematographer,
        genres=genres
    )
    
    # Apply doctrine principles
    doctrine_application = _apply_doctrine_principles(work, colors, assignment_rules)
    
    # Interpret evidence within doctrine constraints
    evidence_interpretation = _interpret_evidence_within_doctrine(evidence_context, colors, assignment_rules)
    
    # Synthesize reasoning
    reasoning_synthesis = _synthesize_color_reasoning(
        work, doctrine_application, evidence_interpretation, colors, monochromatic_modes
    )
    
    # Detect conflicts and ambiguity
    conflicts_acknowledged = _acknowledge_conflicts(evidence_context, reasoning_synthesis)
    
    # Generate final reasoning explanation
    final_reasoning = _generate_final_reasoning(
        work, doctrine_application, evidence_interpretation, reasoning_synthesis, conflicts_acknowledged
    )
    
    # Determine confidence
    confidence_assessment = _assess_confidence(
        doctrine_application, evidence_interpretation, conflicts_acknowledged
    )
    
    # Structure response
    return {
        "work_id": work_id,
        "color_assignment": {
            "primary": {
                "color_id": reasoning_synthesis["primary_color"],
                "confidence": confidence_assessment["primary_confidence"],
                "confidence_explanation": confidence_assessment["primary_explanation"]
            },
            "secondary": reasoning_synthesis["secondary_colors"],
            "monochromatic": {
                "is_monochromatic": reasoning_synthesis["is_monochromatic"],
                "mode": reasoning_synthesis.get("monochromatic_mode")
            }
        },
        "reasoning_chain": {
            "doctrine_application": doctrine_application,
            "evidence_context": evidence_context,
            "evidence_interpretation": evidence_interpretation,
            "conflicts_acknowledged": conflicts_acknowledged,
            "final_reasoning": final_reasoning
        },
        "metadata": {
            "model": "doctrine-based-reasoning",
            "doctrine_version": color_doctrine["version"],
            "evidence_version": "v2.0",
            "processed_at": datetime.now().isoformat()
        }
    }


def _apply_doctrine_principles(work: Dict[str, Any], colors: List[Dict], assignment_rules: Dict) -> Dict[str, Any]:
    """Apply doctrine principles to work analysis."""
    
    # Extract work metadata
    title = work.get("title", "Unknown")
    year = work.get("year", 0)
    genres = work.get("genres", [])
    
    # Apply decision hierarchy from doctrine
    decision_hierarchy = assignment_rules["decision_hierarchy"]
    
    doctrine_analysis = {
        "decision_hierarchy_applied": decision_hierarchy,
        "cultural_memory_assessment": f"Analyzing {title} ({year}) for collective cultural memory associations",
        "genre_context": {
            "genres": genres,
            "note": "Genre associations are contextual, not deterministic per doctrine"
        },
        "available_colors": [
            {
                "id": color["id"],
                "name": color["name"],
                "moods": color["moods"],
                "genre_associations": color["genre_associations"],
                "cultural_context": color["cultural_context"]
            }
            for color in colors
        ],
        "monochromatic_detection": {
            "criteria": assignment_rules["monochromatic_detection"]["criteria"],
            "assignment_logic": assignment_rules["monochromatic_detection"]["assignment_logic"],
            "note": "Monochromatic assignment is editorial decision based on cinematographic style"
        },
        "constraints": {
            "ai_must_not_use": assignment_rules["ai_must_not_use"],
            "primary_color_basis": assignment_rules["primary_color_basis"],
            "editorial_override": assignment_rules["editorial_override_always_wins"]
        }
    }
    
    return doctrine_analysis


def _interpret_evidence_within_doctrine(evidence_context: Dict, colors: List[Dict], assignment_rules: Dict) -> str:
    """Interpret evidence within doctrine constraints."""
    
    interpretation_parts = []
    
    # Film-specific evidence
    film_discourse = evidence_context.get("film_discourse", {})
    if film_discourse.get("perspectives"):
        interpretation_parts.append(
            f"Critical discourse on {film_discourse.get('film', 'this work')} "
            f"includes {len(film_discourse['perspectives'])} documented perspectives. "
            f"These provide cultural context but do not assign colors per doctrine."
        )
    
    # Cinematographer evidence
    dp_context = evidence_context.get("cinematographer_context", {})
    if dp_context.get("documented_perspectives"):
        dp_name = dp_context.get("name", "cinematographer")
        interpretation_parts.append(
            f"Evidence documents {dp_name}'s color philosophy through "
            f"{len(dp_context['documented_perspectives'])} documented perspectives. "
            f"This informs understanding of cinematographic intent per doctrine hierarchy."
        )
    
    # Genre evidence
    genre_discourse = evidence_context.get("genre_discourse", {})
    if genre_discourse.get("documented_conventions"):
        interpretation_parts.append(
            f"Genre aesthetic discourse provides {len(genre_discourse['documented_conventions'])} "
            f"documented conventions. Per doctrine, these are contextual reference points, "
            f"not deterministic rules."
        )
    
    if not interpretation_parts:
        interpretation_parts.append(
            "Limited evidence available for this work. Reasoning will rely primarily "
            "on doctrine principles and available metadata."
        )
    
    # Add evidence framework compliance note
    interpretation_parts.append(
        "All evidence interpretation follows pipeline/evidence/FRAMEWORK.md requirements: "
        "evidence provides context, doctrine provides constraints, editorial provides authority."
    )
    
    return " ".join(interpretation_parts)


def _synthesize_color_reasoning(work: Dict, doctrine_app: Dict, evidence_interp: str, 
                               colors: List[Dict], mono_modes: List[Dict]) -> Dict[str, Any]:
    """Synthesize color reasoning from doctrine and evidence."""
    
    title = work.get("title", "Unknown")
    year = work.get("year", 0)
    genres = work.get("genres", [])
    
    # Check for monochromatic indicators first
    is_monochromatic = False
    monochromatic_mode = None
    
    # Simple heuristics for monochromatic detection (to be refined)
    if any(keyword in title.lower() for keyword in ["noir", "shadow", "light"]):
        # This is a placeholder - real implementation would need more sophisticated detection
        pass
    
    # Primary color reasoning (simplified for Phase 2A)
    primary_color = None
    primary_reasoning = []
    
    # Apply doctrine decision hierarchy
    # 1. Collective cultural memory
    cultural_memory_candidates = []
    for color in colors:
        if any(example.lower() in title.lower() for example in color.get("reference_examples", [])):
            cultural_memory_candidates.append({
                "color_id": color["id"],
                "reason": f"Cultural memory association via reference examples",
                "strength": "strong"
            })
    
    # 2. Genre associations (contextual, not deterministic)
    genre_candidates = []
    for color in colors:
        color_genres = color.get("genre_associations", [])
        genre_overlap = set(genres).intersection(set(color_genres))
        if genre_overlap:
            genre_candidates.append({
                "color_id": color["id"],
                "reason": f"Genre association overlap: {list(genre_overlap)}",
                "strength": "contextual"
            })
    
    # Select primary color (simplified logic for Phase 2A)
    if cultural_memory_candidates:
        primary_color = cultural_memory_candidates[0]["color_id"]
        primary_reasoning.append("Selected based on cultural memory association per doctrine hierarchy")
    elif genre_candidates:
        primary_color = genre_candidates[0]["color_id"]
        primary_reasoning.append("Selected based on genre context (contextual reference only)")
    else:
        # Default to first color for testing (to be improved)
        primary_color = colors[0]["id"]
        primary_reasoning.append("Default assignment for testing - requires editorial review")
    
    # Secondary colors (simplified)
    secondary_colors = []
    remaining_candidates = [c for c in cultural_memory_candidates + genre_candidates 
                          if c["color_id"] != primary_color]
    
    for candidate in remaining_candidates[:3]:  # Max 3 per doctrine
        secondary_colors.append({
            "color_id": candidate["color_id"],
            "confidence": 0.6,  # Moderate confidence for secondary
            "reasoning": candidate["reason"]
        })
    
    return {
        "primary_color": primary_color,
        "primary_reasoning": primary_reasoning,
        "secondary_colors": secondary_colors,
        "is_monochromatic": is_monochromatic,
        "monochromatic_mode": monochromatic_mode,
        "cultural_memory_candidates": cultural_memory_candidates,
        "genre_candidates": genre_candidates
    }


def _acknowledge_conflicts(evidence_context: Dict, reasoning_synthesis: Dict) -> Optional[str]:
    """Identify and acknowledge conflicts in evidence or reasoning."""
    
    conflicts = []
    
    # Check for evidence debates
    film_discourse = evidence_context.get("film_discourse", {})
    if film_discourse.get("debates"):
        conflicts.append(
            f"Evidence contains {len(film_discourse['debates'])} documented debates "
            f"about this film's color characteristics"
        )
    
    # Check for genre discourse conflicts
    genre_discourse = evidence_context.get("genre_discourse", {})
    if genre_discourse.get("debates"):
        conflicts.append(
            f"Genre aesthetic evidence contains {len(genre_discourse['debates'])} "
            f"documented contradictions"
        )
    
    # Check for reasoning ambiguity
    if len(reasoning_synthesis.get("cultural_memory_candidates", [])) > 1:
        conflicts.append(
            "Multiple cultural memory candidates identified - requires editorial consideration"
        )
    
    if not conflicts:
        return None
    
    return "; ".join(conflicts)


def _assess_confidence(doctrine_app: Dict, evidence_interp: str, conflicts: Optional[str]) -> Dict[str, Any]:
    """Assess confidence in color assignment with qualitative explanation."""
    
    # Confidence bands per requirements:
    # 0.85–1.00 → Strong doctrine alignment + evidence consensus
    # 0.70–0.84 → Good fit with plurality  
    # 0.50–0.69 → Ambiguous, flag-worthy
    # <0.50 → Editorial review recommended
    
    base_confidence = 0.70  # Start with moderate confidence
    confidence_factors = []
    
    # Adjust based on cultural memory evidence
    cultural_candidates = len(doctrine_app.get("cultural_memory_candidates", []))
    if cultural_candidates > 0:
        base_confidence += 0.10
        confidence_factors.append(f"Cultural memory evidence available ({cultural_candidates} candidates)")
    
    # Adjust based on conflicts
    if conflicts:
        base_confidence -= 0.15
        confidence_factors.append("Conflicts in evidence reduce confidence")
    
    # Adjust based on evidence availability
    if "Limited evidence available" in evidence_interp:
        base_confidence -= 0.20
        confidence_factors.append("Limited evidence available")
    
    # Cap confidence
    primary_confidence = max(0.1, min(1.0, base_confidence))
    
    # Generate explanation
    if primary_confidence >= 0.85:
        confidence_band = "Strong"
        explanation = "Strong doctrine alignment with evidence consensus"
    elif primary_confidence >= 0.70:
        confidence_band = "Good"
        explanation = "Good fit with evidence plurality"
    elif primary_confidence >= 0.50:
        confidence_band = "Ambiguous"
        explanation = "Ambiguous assignment - flag for editorial review"
    else:
        confidence_band = "Low"
        explanation = "Editorial review recommended"
    
    detailed_explanation = f"{confidence_band} confidence ({primary_confidence:.2f}): {explanation}. " + \
                          f"Factors: {'; '.join(confidence_factors) if confidence_factors else 'Standard doctrine application'}"
    
    return {
        "primary_confidence": primary_confidence,
        "primary_explanation": detailed_explanation,
        "confidence_band": confidence_band
    }


def _generate_final_reasoning(work: Dict, doctrine_app: Dict, evidence_interp: str, 
                            reasoning_synthesis: Dict, conflicts: Optional[str]) -> str:
    """Generate comprehensive final reasoning explanation."""
    
    title = work.get("title", "Unknown")
    year = work.get("year", 0)
    
    reasoning_parts = [
        f"Color reasoning for {title} ({year}):",
        "",
        "DOCTRINE APPLICATION:",
        f"- Decision hierarchy: {' → '.join(doctrine_app['decision_hierarchy_applied'])}",
        f"- Primary color basis: {doctrine_app['constraints']['primary_color_basis']}",
        f"- AI follows doctrine constraints (no pixel analysis, no frame counting, no numeric thresholds)",
        "",
        "EVIDENCE CONSULTATION:",
        f"- {evidence_interp}",
        "",
        "REASONING SYNTHESIS:",
        f"- Primary color: {reasoning_synthesis['primary_color']}",
        f"- Reasoning: {'; '.join(reasoning_synthesis['primary_reasoning'])}",
        f"- Secondary colors: {len(reasoning_synthesis['secondary_colors'])} identified",
        f"- Monochromatic: {reasoning_synthesis['is_monochromatic']}"
    ]
    
    if conflicts:
        reasoning_parts.extend([
            "",
            "CONFLICTS ACKNOWLEDGED:",
            f"- {conflicts}"
        ])
    
    reasoning_parts.extend([
        "",
        "FRAMEWORK COMPLIANCE:",
        "- Evidence used for context only, not assignment",
        "- Doctrine principles applied throughout",
        "- Editorial authority acknowledged",
        "- Reasoning chain fully traceable"
    ])
    
    return "\n".join(reasoning_parts)


def process_single_work(work_file_path: str) -> Dict[str, Any]:
    """Process a single work file for color reasoning."""
    
    work_path = Path(work_file_path)
    if not work_path.exists():
        raise FileNotFoundError(f"Work file not found: {work_file_path}")
    
    with open(work_path, 'r', encoding='utf-8') as f:
        work_data = json.load(f)
    
    return reason_about_color(work_data)


def save_reasoning_result(reasoning_result: Dict[str, Any], output_dir: str = None) -> str:
    """Save reasoning result to file."""
    
    if output_dir is None:
        output_dir = Path(__file__).parent / "results"
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    work_id = reasoning_result["work_id"]
    result_file = output_path / f"{work_id}_reasoning.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(reasoning_result, f, indent=2, ensure_ascii=False)
    
    return str(result_file)


if __name__ == "__main__":
    # Test with a sample work (create minimal test data)
    test_work = {
        "id": "work_blade_runner_1982",
        "title": "Blade Runner",
        "year": 1982,
        "genres": ["sci_fi", "neo_noir"],
        "people": {
            "director": ["Ridley Scott"],
            "cinematography": ["Jordan Cronenweth"]
        }
    }
    
    print("Testing AI Color Reasoning Agent...")
    print(f"Test work: {test_work['title']} ({test_work['year']})")
    
    try:
        result = reason_about_color(test_work)
        
        print(f"\n✓ Primary assignment: {result['color_assignment']['primary']['color_id']}")
        print(f"✓ Confidence: {result['color_assignment']['primary']['confidence']:.2f}")
        print(f"✓ Secondary colors: {len(result['color_assignment']['secondary'])}")
        print(f"✓ Monochromatic: {result['color_assignment']['monochromatic']['is_monochromatic']}")
        
        # Save result for inspection
        result_file = save_reasoning_result(result)
        print(f"✓ Reasoning saved to: {result_file}")
        
        print("\n✅ AI Color Reasoning Agent test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise