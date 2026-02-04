# Phase 2D: External Research Execution

**Status:** Implementation Complete  
**Version:** 1.0  
**Last Updated:** 2026-02-04

---

## PURPOSE

Phase 2D executes external research requests via Gemini API to gather contextual information when Prisma's internal Evidence layer has gaps.

**This phase does NOT:**
- Assign colors
- Make aesthetic judgments
- Interpret research findings
- Persist data (Phase 2C handles persistence)
- Retry with modified prompts
- Validate outputs (Phase 2C validator handles this)

**This phase ONLY:**
- Accepts structured research requests from Phase 2C
- Calls Gemini API with fixed prompts
- Returns raw JSON response

---

## AUTHENTICATION

**Method:** API Key Only

**Resolution Order:**
1. Explicit function argument (`gemini_api_key`)
2. Environment variable `GEMINI_API_KEY`
3. If missing → structured error response (NOT exception)

**Configuration:**
```bash
export GEMINI_API_KEY="<YOUR_API_KEY>"
export GEMINI_PROJECT_NUMBER="868141683596"  # Optional, for quota tracking
```

**SDK Choice:** `google-generativeai` Python SDK

This is the official, stable SDK for Gemini API interaction with full API key support.

Authentication is ONLY via environment variable or function argument.

---

## INPUTS

### Required Input Structure
```json
{
  "request_metadata": {
    "work_id": "work_tropical_malady_2004",
    "trigger_reason": "cultural_context",
    "requested_at": "2026-02-04T02:59:16Z",
    "doctrine_version_context": "1.1",
    "evidence_version_context": "2.1"
  },
  "film_to_research": {
    "title": "Tropical Malady",
    "year": 2004,
    "director": "person_apichatpong_weerasethakul",
    "cinematographer": "person_jean_marc_selva",
    "countries": ["TH", "FR", "DE"],
    "languages": ["th"],
    "genres": ["Drama", "Fantasy", "Romance"]
  },
  "research_goals": {
    "cinematographer_context": [...],
    "film_aesthetic_discourse": [...],
    "cultural_genre_context": [...]
  },
  "internal_evidence_status": "Film not found in Evidence...",
  "doctrine_ambiguity": null
}
```

---

## OUTPUTS

### Required Output Structure
```json
{
  "work_id": "work_tropical_malady_2004",
  "trigger_reason": "cultural_context",
  "conducted_at": "2026-02-04T03:15:42Z",
  "sources": [...],
  "findings": {...},
  "conflicts": [...],
  "uncertainty_flags": [...],
  "research_quality": "HIGH | MODERATE | LOW",
  "promotion_eligible": true | false
}
```

**Consumed by:** `pipeline.lib.external_research.external_research_validator`

---

## USAGE
```python
from pipeline.lib.external_research_execution import execute_external_research

research_request = {...}  # From Phase 2C request builder

result = execute_external_research(
    research_request=research_request,
    gemini_api_key="<YOUR_API_KEY>"  # Optional, reads from env
)

# result is ALWAYS valid JSON (never raises)
```

---

## ERROR HANDLING

All errors return structured JSON:
```json
{
  "work_id": "...",
  "trigger_reason": "...",
  "conducted_at": "...",
  "sources": [],
  "findings": {},
  "conflicts": [],
  "uncertainty_flags": ["api_failure"],
  "research_quality": "LOW",
  "promotion_eligible": false,
  "error": {
    "type": "APIError",
    "message": "...",
    "timestamp": "..."
  }
}
```

---

## DEPENDENCIES
```bash
pip install google-generativeai --break-system-packages
```

---

## CONFIGURATION

Default values (can be overridden):
```python
GEMINI_MODEL = "gemini-1.5-pro"
GEMINI_TIMEOUT = 60  # seconds
GEMINI_MAX_RETRIES = 3  # for network errors only
```