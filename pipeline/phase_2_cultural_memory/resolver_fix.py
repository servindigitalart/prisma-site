def _call_gemini_api(prompt: str) -> str:
    """
    Call Gemini API with perception-focused prompt.
    Updated to use new google-genai SDK.
    """
    try:
        from google import genai
        import os
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        client = genai.Client(api_key=api_key)
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Strip markdown code blocks if present
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return text.strip()
        
    except ImportError as e:
        raise Exception(f"google-genai package not installed: {e}")
    except Exception as e:
        raise Exception(f"Gemini API error: {e}")
