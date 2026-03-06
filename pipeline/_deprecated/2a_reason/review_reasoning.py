"""
Reasoning Chain Review Tool

Human-readable validation of epistemic integrity for AI color reasoning.
Checks compliance with doctrine principles and Evidence Framework requirements.

This tool flags violations of:
- Doctrine principles (no pixel dominance, cultural memory priority)
- Evidence Framework rules (proper citation, conflict acknowledgment)
- Reasoning chain completeness (traceable logic, source attribution)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple


def review_reasoning_chain(reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Review AI reasoning chain for epistemic integrity and compliance.
    
    Args:
        reasoning_result: Output from ai_color_agent.reason_about_color()
    
    Returns:
        {
            "compliance_summary": dict,
            "violations": list[dict],
            "recommendations": list[str],
            "overall_status": "compliant" | "needs_review" | "non_compliant"
        }
    """
    
    violations = []
    recommendations = []
    compliance_checks = {
        "doctrine_compliance": False,
        "evidence_framework_compliance": False,
        "reasoning_chain_completeness": False,
        "confidence_explanation": False,
        "conflict_acknowledgment": False,
        "source_attribution": False
    }
    
    # Check 1: Doctrine Compliance
    doctrine_violations = _check_doctrine_compliance(reasoning_result)
    violations.extend(doctrine_violations)
    compliance_checks["doctrine_compliance"] = len(doctrine_violations) == 0
    
    # Check 2: Evidence Framework Compliance
    framework_violations = _check_evidence_framework_compliance(reasoning_result)
    violations.extend(framework_violations)
    compliance_checks["evidence_framework_compliance"] = len(framework_violations) == 0
    
    # Check 3: Reasoning Chain Completeness
    chain_violations = _check_reasoning_chain_completeness(reasoning_result)
    violations.extend(chain_violations)
    compliance_checks["reasoning_chain_completeness"] = len(chain_violations) == 0
    
    # Check 4: Confidence Explanation
    confidence_violations = _check_confidence_explanation(reasoning_result)
    violations.extend(confidence_violations)
    compliance_checks["confidence_explanation"] = len(confidence_violations) == 0
    
    # Check 5: Conflict Acknowledgment
    conflict_violations = _check_conflict_acknowledgment(reasoning_result)
    violations.extend(conflict_violations)
    compliance_checks["conflict_acknowledgment"] = len(conflict_violations) == 0
    
    # Check 6: Source Attribution
    source_violations = _check_source_attribution(reasoning_result)
    violations.extend(source_violations)
    compliance_checks["source_attribution"] = len(source_violations) == 0
    
    # Generate recommendations
    recommendations = _generate_recommendations(violations, reasoning_result)
    
    # Determine overall status
    critical_violations = [v for v in violations if v.get("severity") == "critical"]
    warning_violations = [v for v in violations if v.get("severity") == "warning"]
    
    if critical_violations:
        overall_status = "non_compliant"
    elif warning_violations:
        overall_status = "needs_review"
    else:
        overall_status = "compliant"
    
    return {
        "work_id": reasoning_result.get("work_id"),
        "compliance_summary": compliance_checks,
        "violations": violations,
        "recommendations": recommendations,
        "overall_status": overall_status,
        "total_violations": len(violations),
        "critical_violations": len(critical_violations),
        "warning_violations": len(warning_violations)
    }


def _check_doctrine_compliance(reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check compliance with doctrine principles."""
    violations = []
    
    reasoning_chain = reasoning_result.get("reasoning_chain", {})
    final_reasoning = reasoning_chain.get("final_reasoning", "")
    
    # Check for pixel dominance language (PROHIBITED)
    pixel_dominance_patterns = [
        r"pixel.{0,20}dominance",
        r"frame.{0,20}percentage",
        r"color.{0,20}frequency",
        r"dominant.{0,20}pixel",
        r"frame.{0,20}analysis.{0,20}shows",
        r"most.{0,20}frequent.{0,20}color"
    ]
    
    for pattern in pixel_dominance_patterns:
        if re.search(pattern, final_reasoning, re.IGNORECASE):
            violations.append({
                "type": "doctrine_violation",
                "severity": "critical",
                "issue": "Pixel dominance language detected",
                "pattern": pattern,
                "location": "final_reasoning",
                "doctrine_rule": "ai_must_not_use: pixel_dominance"
            })
    
    # Check for frame frequency language (PROHIBITED)
    frame_frequency_patterns = [
        r"frame.{0,20}frequency",
        r"appears.{0,20}\d+.{0,20}percent",
        r"color.{0,20}appears.{0,20}most",
        r"statistically.{0,20}dominant"
    ]
    
    for pattern in frame_frequency_patterns:
        if re.search(pattern, final_reasoning, re.IGNORECASE):
            violations.append({
                "type": "doctrine_violation",
                "severity": "critical", 
                "issue": "Frame frequency language detected",
                "pattern": pattern,
                "location": "final_reasoning",
                "doctrine_rule": "ai_must_not_use: frame_frequency"
            })
    
    # Check for numeric thresholds (PROHIBITED)
    numeric_threshold_patterns = [
        r"threshold.{0,20}\d+",
        r"above.{0,20}\d+.{0,20}percent",
        r"minimum.{0,20}\d+",
        r"cutoff.{0,20}\d+"
    ]
    
    for pattern in numeric_threshold_patterns:
        if re.search(pattern, final_reasoning, re.IGNORECASE):
            violations.append({
                "type": "doctrine_violation",
                "severity": "critical",
                "issue": "Numeric threshold language detected", 
                "pattern": pattern,
                "location": "final_reasoning",
                "doctrine_rule": "ai_must_not_use: numeric_thresholds"
            })
    
    # Check for cultural memory priority
    doctrine_app = reasoning_chain.get("doctrine_application", {})
    if "cultural_memory_assessment" not in doctrine_app:
        violations.append({
            "type": "doctrine_violation",
            "severity": "warning",
            "issue": "Missing cultural memory assessment",
            "location": "doctrine_application",
            "doctrine_rule": "primary_color_basis: cultural_memory_and_cinematographic_intent"
        })
    
    return violations


def _check_evidence_framework_compliance(reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check compliance with Evidence Framework requirements."""
    violations = []
    
    reasoning_chain = reasoning_result.get("reasoning_chain", {})
    evidence_interpretation = reasoning_chain.get("evidence_interpretation", "")
    
    # Check for "evidence assigns" phrasing (PROHIBITED)
    evidence_assignment_patterns = [
        r"evidence.{0,20}assigns",
        r"evidence.{0,20}shows.{0,20}[a-z_]+.{0,20}is.{0,20}[a-z_]+",
        r"evidence.{0,20}indicates.{0,20}[a-z_]+.{0,20}color",
        r"according.{0,20}to.{0,20}evidence.{0,20}[a-z_]+.{0,20}is"
    ]
    
    for pattern in evidence_assignment_patterns:
        if re.search(pattern, evidence_interpretation, re.IGNORECASE):
            violations.append({
                "type": "framework_violation",
                "severity": "critical",
                "issue": "Evidence assignment language detected",
                "pattern": pattern,
                "location": "evidence_interpretation",
                "framework_rule": "Evidence never assigns colors, never dictates decisions"
            })
    
    # Check for missing source citations
    evidence_context = reasoning_chain.get("evidence_context", {})
    
    has_sources = False
    for context_type in ["film_discourse", "cinematographer_context", "genre_discourse"]:
        context_data = evidence_context.get(context_type, {})
        if context_data.get("sources"):
            has_sources = True
            break
    
    if not has_sources and "Limited evidence available" not in evidence_interpretation:
        violations.append({
            "type": "framework_violation",
            "severity": "warning",
            "issue": "Missing source citations",
            "location": "evidence_context",
            "framework_rule": "Every evidence reference must include source attribution"
        })
    
    # Check for evidence contextualization
    if "evidence provides context" not in evidence_interpretation.lower():
        violations.append({
            "type": "framework_violation",
            "severity": "warning",
            "issue": "Missing evidence contextualization statement",
            "location": "evidence_interpretation",
            "framework_rule": "Evidence must be cited and contextualized as descriptive"
        })
    
    return violations


def _check_reasoning_chain_completeness(reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check reasoning chain completeness."""
    violations = []
    
    reasoning_chain = reasoning_result.get("reasoning_chain", {})
    required_components = [
        "doctrine_application",
        "evidence_context", 
        "evidence_interpretation",
        "final_reasoning"
    ]
    
    for component in required_components:
        if component not in reasoning_chain:
            violations.append({
                "type": "completeness_violation",
                "severity": "critical",
                "issue": f"Missing reasoning chain component: {component}",
                "location": "reasoning_chain",
                "requirement": "AI reasoning chain requirements"
            })
        elif not reasoning_chain[component]:
            violations.append({
                "type": "completeness_violation",
                "severity": "warning",
                "issue": f"Empty reasoning chain component: {component}",
                "location": "reasoning_chain",
                "requirement": "AI reasoning chain requirements"
            })
    
    return violations


def _check_confidence_explanation(reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check confidence explanation quality."""
    violations = []
    
    primary = reasoning_result.get("color_assignment", {}).get("primary", {})
    confidence = primary.get("confidence", 0)
    explanation = primary.get("confidence_explanation", "")
    
    if not explanation:
        violations.append({
            "type": "confidence_violation",
            "severity": "critical",
            "issue": "Missing confidence explanation",
            "location": "color_assignment.primary",
            "requirement": "Confidence must be explained qualitatively"
        })
    
    # Check confidence bands alignment
    if confidence >= 0.85 and "strong" not in explanation.lower():
        violations.append({
            "type": "confidence_violation",
            "severity": "warning",
            "issue": "High confidence not explained as 'strong'",
            "location": "confidence_explanation",
            "requirement": "Confidence bands: 0.85-1.00 = Strong"
        })
    elif confidence < 0.50 and "editorial review" not in explanation.lower():
        violations.append({
            "type": "confidence_violation",
            "severity": "warning",
            "issue": "Low confidence should recommend editorial review",
            "location": "confidence_explanation", 
            "requirement": "Confidence bands: <0.50 = Editorial review recommended"
        })
    
    return violations


def _check_conflict_acknowledgment(reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check conflict acknowledgment."""
    violations = []
    
    reasoning_chain = reasoning_result.get("reasoning_chain", {})
    conflicts_acknowledged = reasoning_chain.get("conflicts_acknowledged")
    evidence_context = reasoning_chain.get("evidence_context", {})
    
    # Check if there are potential conflicts that should be acknowledged
    has_debates = False
    for context_type in ["film_discourse", "genre_discourse"]:
        context_data = evidence_context.get(context_type, {})
        if context_data.get("debates"):
            has_debates = True
            break
    
    if has_debates and not conflicts_acknowledged:
        violations.append({
            "type": "conflict_violation",
            "severity": "warning",
            "issue": "Evidence contains debates but no conflicts acknowledged",
            "location": "conflicts_acknowledged",
            "requirement": "Evidence ambiguity must be preserved and reported"
        })
    
    return violations


def _check_source_attribution(reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check source attribution compliance."""
    violations = []
    
    reasoning_chain = reasoning_result.get("reasoning_chain", {})
    evidence_context = reasoning_chain.get("evidence_context", {})
    evidence_interpretation = reasoning_chain.get("evidence_interpretation", "")
    
    # Check if evidence is used but not attributed
    uses_evidence = "evidence" in evidence_interpretation.lower()
    
    has_attribution = False
    for context_type in ["film_discourse", "cinematographer_context", "genre_discourse"]:
        context_data = evidence_context.get(context_type, {})
        if context_data.get("sources"):
            has_attribution = True
            break
    
    if uses_evidence and not has_attribution:
        violations.append({
            "type": "attribution_violation",
            "severity": "warning",
            "issue": "Evidence used but sources not properly attributed",
            "location": "evidence_context",
            "requirement": "Every evidence reference must include source attribution"
        })
    
    return violations


def _generate_recommendations(violations: List[Dict], reasoning_result: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on violations."""
    recommendations = []
    
    critical_violations = [v for v in violations if v.get("severity") == "critical"]
    warning_violations = [v for v in violations if v.get("severity") == "warning"]
    
    if critical_violations:
        recommendations.append("CRITICAL: This reasoning chain violates core doctrine principles and must be revised")
        
        doctrine_violations = [v for v in critical_violations if v["type"] == "doctrine_violation"]
        if doctrine_violations:
            recommendations.append("Remove all pixel dominance, frame frequency, and numeric threshold language")
        
        framework_violations = [v for v in critical_violations if v["type"] == "framework_violation"]
        if framework_violations:
            recommendations.append("Revise evidence interpretation to be descriptive, not prescriptive")
        
        completeness_violations = [v for v in critical_violations if v["type"] == "completeness_violation"]
        if completeness_violations:
            recommendations.append("Complete all required reasoning chain components")
    
    if warning_violations:
        recommendations.append("Address warning-level issues to improve reasoning quality")
        
        confidence_issues = [v for v in warning_violations if v["type"] == "confidence_violation"]
        if confidence_issues:
            recommendations.append("Improve confidence explanation alignment with confidence bands")
        
        conflict_issues = [v for v in warning_violations if v["type"] == "conflict_violation"]
        if conflict_issues:
            recommendations.append("Acknowledge evidence debates and ambiguity where present")
    
    # Confidence-specific recommendations
    confidence = reasoning_result.get("color_assignment", {}).get("primary", {}).get("confidence", 0)
    if confidence < 0.50:
        recommendations.append("Low confidence detected - recommend editorial review before publication")
    elif confidence < 0.70:
        recommendations.append("Moderate confidence - consider additional evidence research")
    
    if not recommendations:
        recommendations.append("Reasoning chain appears compliant - ready for editorial review")
    
    return recommendations


def review_reasoning_file(file_path: str) -> Dict[str, Any]:
    """Review reasoning chain from saved JSON file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reasoning_result = json.load(f)
    
    return review_reasoning_chain(reasoning_result)


def generate_human_readable_report(review_result: Dict[str, Any]) -> str:
    """Generate human-readable compliance report."""
    
    work_id = review_result.get("work_id", "Unknown")
    status = review_result.get("overall_status", "unknown")
    
    report_lines = [
        f"REASONING CHAIN REVIEW: {work_id}",
        f"Overall Status: {status.upper()}",
        f"Total Violations: {review_result.get('total_violations', 0)}",
        f"Critical: {review_result.get('critical_violations', 0)}, "
        f"Warnings: {review_result.get('warning_violations', 0)}",
        ""
    ]
    
    # Compliance summary
    compliance = review_result.get("compliance_summary", {})
    report_lines.append("COMPLIANCE SUMMARY:")
    for check, passed in compliance.items():
        status_icon = "✓" if passed else "✗"
        report_lines.append(f"  {status_icon} {check.replace('_', ' ').title()}")
    
    # Violations
    violations = review_result.get("violations", [])
    if violations:
        report_lines.extend(["", "VIOLATIONS:"])
        for violation in violations:
            severity_icon = "🚨" if violation.get("severity") == "critical" else "⚠️"
            report_lines.append(
                f"  {severity_icon} {violation.get('issue', 'Unknown issue')} "
                f"({violation.get('type', 'unknown')})"
            )
            if violation.get("doctrine_rule"):
                report_lines.append(f"     Doctrine: {violation['doctrine_rule']}")
            if violation.get("framework_rule"):
                report_lines.append(f"     Framework: {violation['framework_rule']}")
    
    # Recommendations
    recommendations = review_result.get("recommendations", [])
    if recommendations:
        report_lines.extend(["", "RECOMMENDATIONS:"])
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"  {i}. {rec}")
    
    return "\n".join(report_lines)


def batch_review_reasoning_files(results_dir: str) -> Dict[str, Any]:
    """Review all reasoning files in a directory."""
    
    results_path = Path(results_dir)
    if not results_path.exists():
        return {"error": f"Results directory not found: {results_dir}"}
    
    reasoning_files = list(results_path.glob("*_reasoning.json"))
    
    if not reasoning_files:
        return {"error": f"No reasoning files found in: {results_dir}"}
    
    batch_results = {
        "total_files": len(reasoning_files),
        "compliant": 0,
        "needs_review": 0,
        "non_compliant": 0,
        "file_results": {}
    }
    
    for file_path in reasoning_files:
        try:
            review_result = review_reasoning_file(str(file_path))
            status = review_result["overall_status"]
            
            batch_results["file_results"][file_path.name] = review_result
            batch_results[status] += 1
            
        except Exception as e:
            batch_results["file_results"][file_path.name] = {
                "error": str(e),
                "overall_status": "error"
            }
    
    return batch_results


if __name__ == "__main__":
    # Test reasoning chain review
    print("Testing Reasoning Chain Review Tool...")
    
    # Find test reasoning file
    results_dir = Path(__file__).parent / "results"
    reasoning_files = list(results_dir.glob("*_reasoning.json"))
    
    if not reasoning_files:
        print("No reasoning files found for testing")
        sys.exit(1)
    
    test_file = reasoning_files[0]
    print(f"Testing with: {test_file.name}")
    
    try:
        # Review single file
        review_result = review_reasoning_file(str(test_file))
        
        # Generate human-readable report
        report = generate_human_readable_report(review_result)
        print("\n" + "="*60)
        print(report)
        print("="*60)
        
        # Test batch review
        batch_result = batch_review_reasoning_files(str(results_dir))
        print(f"\nBatch Review Summary:")
        print(f"  Total files: {batch_result['total_files']}")
        print(f"  Compliant: {batch_result['compliant']}")
        print(f"  Needs review: {batch_result['needs_review']}")
        print(f"  Non-compliant: {batch_result['non_compliant']}")
        
        print("\n✅ Reasoning Chain Review Tool test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise