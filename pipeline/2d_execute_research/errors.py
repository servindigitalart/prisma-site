#!/usr/bin/env python3
"""
Error Response Builders

WHAT THIS MODULE DOES:
- Creates structured error responses
- Ensures all errors are valid research JSON
- Provides consistent error formatting

WHAT THIS MODULE DOES NOT DO:
- Does NOT raise exceptions
- Does NOT log (logging is a side effect)
- Does NOT interpret errors

EPISTEMIC POSITION:
This module creates error DATA, not control flow.
"""

from typing import Dict, Any, Optional
from datetime import datetime


def create_error_response(
    work_id: str,
    trigger_reason: str,
    error_type: str,
    error_message: str,
    raw_response: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create structured error response matching research schema.
    
    Args:
        work_id: Work identifier
        trigger_reason: Research trigger reason
        error_type: Error type (e.g., "APIError", "TimeoutError")
        error_message: Human-readable error message
        raw_response: Optional raw response for debugging
    
    Returns:
        Valid research output dict with error embedded
    """
    error_obj = {
        "type": error_type,
        "message": error_message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if raw_response:
        error_obj["raw_response"] = raw_response
    
    return {
        "work_id": work_id,
        "trigger_reason": trigger_reason,
        "conducted_at": datetime.utcnow().isoformat() + "Z",
        "sources": [],
        "findings": {
            "cinematographer_context": {},
            "aesthetic_discourse": {},
            "cultural_context": {}
        },
        "conflicts": [],
        "uncertainty_flags": [error_type.lower()],
        "research_quality": "LOW",
        "promotion_eligible": False,
        "error": error_obj
    }