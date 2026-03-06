#!/usr/bin/env python3
"""
Phase 2D: External Research Execution

Exposes a single public function: execute_external_research
"""

from .gemini_executor import execute_external_research

__all__ = ["execute_external_research"]