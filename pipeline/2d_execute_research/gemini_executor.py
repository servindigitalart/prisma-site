#!/usr/bin/env python3
"""
Gemini Executor

WHAT THIS MODULE DOES:
- Orchestrates external research execution
- Resolves API key from env or argument
- Calls Gemini client
- Parses response
- Returns structured output (ALWAYS, even on error)

WHAT THIS MODULE DOES NOT DO:
- Does NOT validate outputs (Phase 2C handles that)
- Does NOT persist data (Phase 2C handles that)
- Does NOT assign colors
- Does NOT interpret findings
- Does NOT raise exceptions

EPISTEMIC POSITION:
This module orchestrates execution but has NO decision-making authority.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .gemini_client import create_client
from .gemini_prompt_builder import build_prompts
from .errors import create_error_response


def resolve_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """
    Resolve Gemini API key.
    
    Resolution order:
    1. Explicit argument
    2. Environment variable GEMINI_API_KEY
    
    Args:
        explicit_key: Explicitly provided API key
    
    Returns:
        API key string or None if unavailable
    """
    if explicit_key:
        return explicit_key
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key
    return None


def parse_gemini_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse Gemini response text as JSON.
    
    Args:
        response_text: Raw response from Gemini
    
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    try:
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def execute_external_research(
    research_request: Dict[str, Any],
    gemini_api_key: Optional[str] = None,
    model: str = "gemini-1.5-pro",
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Execute external research via Gemini.
    
    Args:
        research_request: Research request from Phase 2C request builder
        gemini_api_key: Gemini API key (optional, reads from env)
        model: Gemini model name
        timeout: Request timeout in seconds
    
    Returns:
        Research output dict (ALWAYS valid JSON, never raises)
    """
    work_id = research_request.get("request_metadata", {}).get("work_id", "unknown")
    trigger_reason = research_request.get("request_metadata", {}).get("trigger_reason", "unknown")
    
    api_key = resolve_api_key(gemini_api_key)
    
    if not api_key:
        return create_error_response(
            work_id=work_id,
            trigger_reason=trigger_reason,
            error_type="AuthenticationError",
            error_message="No API key available (check GEMINI_API_KEY env var)"
        )
    
    client = create_client(api_key=api_key, model=model, timeout=timeout)
    
    if not client:
        return create_error_response(
            work_id=work_id,
            trigger_reason=trigger_reason,
            error_type="ClientCreationError",
            error_message="Failed to create Gemini client (check SDK installation)"
        )
    
    prompts = build_prompts(research_request)
    
    result = client.generate(
        system_prompt=prompts["system_prompt"],
        user_prompt=prompts["user_prompt"]
    )
    
    if not result["success"]:
        error = result.get("error", {})
        return create_error_response(
            work_id=work_id,
            trigger_reason=trigger_reason,
            error_type=error.get("type", "APIError"),
            error_message=error.get("message", "Unknown error")
        )
    
    response_text = result.get("response_text")
    
    if not response_text:
        return create_error_response(
            work_id=work_id,
            trigger_reason=trigger_reason,
            error_type="EmptyResponse",
            error_message="Gemini returned empty response"
        )
    
    parsed = parse_gemini_response(response_text)
    
    if not parsed:
        return create_error_response(
            work_id=work_id,
            trigger_reason=trigger_reason,
            error_type="ParseError",
            error_message="Failed to parse Gemini response as JSON",
            raw_response=response_text[:500]
        )
    
    # Strictly require required fields; do NOT mutate output
    required_fields = ["work_id", "trigger_reason", "conducted_at"]
    missing_fields = [f for f in required_fields if f not in parsed]
    if missing_fields:
        return create_error_response(
            work_id=work_id,
            trigger_reason=trigger_reason,
            error_type="MissingFieldError",
            error_message=f"Gemini output missing required fields: {', '.join(missing_fields)}",
            raw_response=response_text[:500]
        )
    
    return parsed