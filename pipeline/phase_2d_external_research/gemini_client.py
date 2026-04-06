#!/usr/local/bin/python3
"""
Gemini Client

WHAT THIS MODULE DOES:
- Low-level Gemini API interaction
- API key authentication
- Timeout handling
- Network error retry (with backoff)
- Returns raw API response

WHAT THIS MODULE DOES NOT DO:
- Does NOT build prompts (that's gemini_prompt_builder.py)
- Does NOT modify prompts
- Does NOT interpret responses
- Does NOT validate responses
- Does NOT persist data
- Does NOT raise exceptions (returns structured errors)

EPISTEMIC POSITION:
This module is a pure API client with NO decision-making authority.
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2


class GeminiClient:
    """
    Low-level Gemini API client.
    
    Handles authentication, retries, and raw response retrieval.
    Stateless: each call is independent.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key
            model: Model name (default: gemini-1.5-flash)
            timeout: Request timeout in seconds (default: 60)
        
        Raises:
            ValueError: If api_key is missing or SDK unavailable
        """
        if not api_key:
            raise ValueError("api_key is required")
        
        if not GEMINI_AVAILABLE:
            raise ValueError("google-generativeai SDK not installed")
        
        self.api_key = api_key
        self.model_name = model
        self.timeout = timeout
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate content via Gemini API.
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
        
        Returns:
            Dict with:
            {
                "success": bool,
                "response_text": str or None,
                "error": dict or None
            }
        """
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.model.generate_content(
                    combined_prompt,
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 8192
                    },
                    request_options={
                        "timeout": self.timeout
                    }
                )
                
                if not response or not response.text:
                    return {
                        "success": False,
                        "response_text": None,
                        "error": {
                            "type": "EmptyResponse",
                            "message": "Gemini returned empty response",
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                
                return {
                    "success": True,
                    "response_text": response.text,
                    "error": None
                }
            
            except Exception as e:
                error_type = type(e).__name__
                
                if "timeout" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_BACKOFF_BASE ** attempt)
                        continue
                    
                    return {
                        "success": False,
                        "response_text": None,
                        "error": {
                            "type": "TimeoutError",
                            "message": f"Request timeout after {self.timeout}s",
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                
                if "rate" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_BACKOFF_BASE ** (attempt + 2))
                        continue
                    
                    return {
                        "success": False,
                        "response_text": None,
                        "error": {
                            "type": "RateLimitError",
                            "message": str(e),
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                
                return {
                    "success": False,
                    "response_text": None,
                    "error": {
                        "type": error_type,
                        "message": str(e),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                }
        
        return {
            "success": False,
            "response_text": None,
            "error": {
                "type": "MaxRetriesExceeded",
                "message": f"Failed after {MAX_RETRIES} attempts",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }


def create_client(
    api_key: str,
    model: str = DEFAULT_MODEL,
    timeout: int = DEFAULT_TIMEOUT
) -> Optional[GeminiClient]:
    """
    Create Gemini client.
    
    Args:
        api_key: Gemini API key
        model: Model name
        timeout: Request timeout
    
    Returns:
        GeminiClient instance or None if creation fails
    """
    try:
        return GeminiClient(api_key=api_key, model=model, timeout=timeout)
    except Exception:
        return None