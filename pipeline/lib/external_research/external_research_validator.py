#!/usr/local/bin/python3
"""
External Research Validator

WHAT THIS MODULE DOES:
- Validates External Research outputs against canonical schema
- Enforces External Research Policy compliance
- Validates required field presence and types
- Validates enum values
- Validates source authority classifications

WHAT THIS MODULE DOES NOT DO:
- Does NOT mutate data
- Does NOT enrich data
- Does NOT make inferences
- Does NOT assign colors
- Does NOT interpret research findings
- Does NOT persist data
- Does NOT make promotion decisions
- Does NOT perform natural language analysis

EPISTEMIC POSITION:
This module is a pure validator with NO decision-making authority.
It enforces rules defined in External Research Policy and JSON Schema.
"""

from typing import Dict, Any, List, Literal


SourceType = Literal["PRIMARY", "SECONDARY", "TERTIARY", "PROHIBITED"]
ResearchQuality = Literal["HIGH", "MODERATE", "LOW"]
TriggerReason = Literal["evidence_gap", "cultural_context", "doctrine_ambiguity", "editorial_request"]


class ValidationResult:
    """Validation result container."""
    
    def __init__(self):
        self.valid = True
        self.errors: List[str] = []
    
    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.valid = False
        self.errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {
            "valid": self.valid,
            "errors": self.errors
        }


class ExternalResearchValidator:
    """
    Validates External Research outputs for schema and policy compliance.
    
    This is a stateless validator: input → validation result.
    No side effects. No decisions. No mutations.
    """
    
    def __init__(self):
        """Initialize validator with no state."""
        pass
    
    def validate(self, research_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate external research output.
        
        Args:
            research_output: External research JSON output
        
        Returns:
            Validation result dict: {"valid": bool, "errors": list[str]}
        """
        result = ValidationResult()
        
        self._validate_required_fields(research_output, result)
        self._validate_trigger_reason(research_output, result)
        self._validate_sources(research_output, result)
        self._validate_findings(research_output, result)
        self._validate_research_quality(research_output, result)
        self._validate_forbidden_fields(research_output, result)
        self._validate_promotion_eligible(research_output, result)
        
        return result.to_dict()
    
    def _validate_required_fields(
        self, 
        research_output: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate required top-level fields exist."""
        required_fields = [
            'work_id',
            'trigger_reason',
            'research_date',
            'sources',
            'findings',
            'conflicts',
            'uncertainty_flags',
            'research_quality',
            'promotion_eligible'
        ]
        
        for field in required_fields:
            if field not in research_output:
                result.add_error(f"Missing required field: {field}")
    
    def _validate_trigger_reason(
        self, 
        research_output: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate trigger reason is valid enum value."""
        if 'trigger_reason' not in research_output:
            return
        
        valid_triggers = ["evidence_gap", "cultural_context", "doctrine_ambiguity", "editorial_request"]
        trigger = research_output['trigger_reason']
        
        if trigger not in valid_triggers:
            result.add_error(
                f"Invalid trigger_reason: '{trigger}'. Must be one of {valid_triggers}"
            )
    
    def _validate_sources(
        self, 
        research_output: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate sources structure and authority classifications."""
        if 'sources' not in research_output:
            return
        
        sources = research_output['sources']
        
        if not isinstance(sources, list):
            result.add_error("sources must be a list")
            return
        
        valid_source_types = ["PRIMARY", "SECONDARY", "TERTIARY", "PROHIBITED"]
        
        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                result.add_error(f"Source {i} is not a dict")
                continue
            
            required_source_fields = [
                'url', 'title', 'author', 'publication', 
                'date', 'source_type', 'authority_score', 'excerpt', 'relevance'
            ]
            
            for field in required_source_fields:
                if field not in source:
                    result.add_error(f"Source {i} missing field: {field}")
            
            if 'source_type' in source and source['source_type'] not in valid_source_types:
                result.add_error(
                    f"Source {i} has invalid source_type: '{source['source_type']}'. "
                    f"Must be one of {valid_source_types}"
                )
            
            if 'authority_score' in source:
                score = source['authority_score']
                if not isinstance(score, (int, float)):
                    result.add_error(f"Source {i} authority_score must be numeric")
                elif not (0.0 <= score <= 1.0):
                    result.add_error(
                        f"Source {i} authority_score {score} out of range (must be 0.0-1.0)"
                    )
            
            if source.get('source_type') == 'PROHIBITED' and source.get('authority_score', 0) != 0.0:
                result.add_error(
                    f"Source {i} marked PROHIBITED but authority_score is not 0.0"
                )
    
    def _validate_findings(
        self, 
        research_output: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate findings structure."""
        if 'findings' not in research_output:
            return
        
        findings = research_output['findings']
        
        if not isinstance(findings, dict):
            result.add_error("findings must be a dict")
            return
        
        expected_keys = [
            'cinematographer_context',
            'aesthetic_discourse',
            'cultural_context'
        ]
        
        for key in expected_keys:
            if key in findings and not isinstance(findings[key], dict):
                result.add_error(f"findings.{key} must be a dict")
    
    def _validate_research_quality(
        self, 
        research_output: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate research quality enum."""
        if 'research_quality' not in research_output:
            return
        
        valid_qualities = ["HIGH", "MODERATE", "LOW"]
        quality = research_output['research_quality']
        
        if quality not in valid_qualities:
            result.add_error(
                f"Invalid research_quality: '{quality}'. Must be one of {valid_qualities}"
            )
    
    def _validate_forbidden_fields(
        self, 
        research_output: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """
        Validate that research output does not contain forbidden fields.
        
        Forbidden fields are explicit schema violations that indicate
        prescriptive behavior (e.g., assigning colors directly).
        """
        forbidden_top_level_fields = [
            'assigned_color',
            'recommended_color',
            'primary_color',
            'color_assignment'
        ]
        
        for field in forbidden_top_level_fields:
            if field in research_output:
                result.add_error(
                    f"Forbidden field '{field}' found in output. "
                    "External research must not assign colors."
                )
        
        if 'findings' in research_output and isinstance(research_output['findings'], dict):
            findings = research_output['findings']
            
            forbidden_findings_fields = [
                'assigned_color',
                'recommended_color',
                'color_decision'
            ]
            
            for field in forbidden_findings_fields:
                if field in findings:
                    result.add_error(
                        f"Forbidden field 'findings.{field}' found. "
                        "External research must not assign colors."
                    )
    
    def _validate_promotion_eligible(
        self, 
        research_output: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate promotion_eligible is boolean."""
        if 'promotion_eligible' not in research_output:
            return
        
        promotion_eligible = research_output['promotion_eligible']
        
        if not isinstance(promotion_eligible, bool):
            result.add_error(
                f"promotion_eligible must be boolean, got {type(promotion_eligible).__name__}"
            )


def validate_external_research(research_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for validating external research output.
    
    Args:
        research_output: External research JSON output
    
    Returns:
        Validation result: {"valid": bool, "errors": list[str]}
    """
    validator = ExternalResearchValidator()
    return validator.validate(research_output)