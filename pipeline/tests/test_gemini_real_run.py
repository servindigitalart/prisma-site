#!/usr/bin/env python3
"""
Real Gemini Research Integration Test

This test makes ACTUAL API calls to Gemini.
It verifies the complete Phase 2D pipeline end-to-end.

REQUIREMENTS:
- GEMINI_API_KEY must be set in environment
- google-generativeai SDK must be installed
- Internet connection required
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_result(label: str, value: Any, indent: int = 0):
    """Print formatted result."""
    spacing = "  " * indent
    if isinstance(value, (dict, list)):
        print(f"{spacing}{label}:")
        print(f"{spacing}  {json.dumps(value, indent=2)}")
    else:
        print(f"{spacing}{label}: {value}")


def create_test_research_request() -> Dict[str, Any]:
    """
    Create a test research request for a well-documented film.
    
    Using "Blade Runner" (1982) - plenty of primary sources available.
    """
    return {
        "request_metadata": {
            "work_id": "test_blade_runner_1982",
            "trigger_reason": "evidence_gap",
            "requested_at": datetime.utcnow().isoformat() + "Z"
        },
        "film_to_research": {
            "title": "Blade Runner",
            "year": 1982,
            "director": "Ridley Scott",
            "cinematographer": "Jordan Cronenweth",
            "countries": ["United States"],
            "languages": ["English"],
            "genres": ["Science Fiction", "Neo-noir", "Thriller"]
        },
        "research_goals": {
            "cinematographer_context": [
                "What did Jordan Cronenweth say about the visual approach?",
                "What lighting techniques were documented in production?"
            ],
            "film_aesthetic_discourse": [
                "How did critics describe the film's visual style?",
                "What scholarly analyses exist of the color palette?"
            ],
            "cultural_genre_context": [
                "What are the visual conventions of neo-noir?",
                "How does this fit into 1980s sci-fi aesthetics?"
            ]
        },
        "internal_evidence_status": "No internal evidence available for this film.",
        "doctrine_ambiguity": "Uncertain whether azul_nocturno or cian_melancolico better fits the documented noir-future aesthetic."
    }


def validate_research_output(output: Dict[str, Any]) -> bool:
    """
    Validate research output structure.
    
    Args:
        output: Research output from execute_external_research
    
    Returns:
        True if valid, False otherwise
    """
    required_top_level = ["work_id", "trigger_reason", "conducted_at"]
    
    for field in required_top_level:
        if field not in output:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check for either valid research OR error
    has_sources = "sources" in output
    has_findings = "findings" in output
    has_error = "error" in output
    
    if has_error:
        print("⚠️  Response contains error (may be expected)")
        return True  # Errors are valid responses
    
    if not has_sources or not has_findings:
        print("❌ Missing sources or findings (and no error)")
        return False
    
    print("✅ Output structure is valid")
    return True


def run_test():
    """Run the complete integration test."""
    print_section("GEMINI REAL RUN TEST - STARTING")
    
    # Step 1: Check API key
    print_section("Step 1: Environment Check")
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("\nTo fix this, run:")
        print('export GEMINI_API_KEY="your-api-key-here"')
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Step 2: Import the module
    print_section("Step 2: Module Import")
    try:
        from pipeline.phase_2d_external_research import execute_external_research
        print("✅ Successfully imported execute_external_research")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        print("\nMake sure you're running from the prisma-site directory:")
        print("python pipeline/tests/test_gemini_real_run.py")
        return False
    
    # Step 3: Create test request
    print_section("Step 3: Create Test Request")
    test_request = create_test_research_request()
    print("✅ Created test request for Blade Runner (1982)")
    print_result("Film", test_request["film_to_research"]["title"])
    print_result("Director", test_request["film_to_research"]["director"])
    print_result("Cinematographer", test_request["film_to_research"]["cinematographer"])
    
    # Step 4: Execute research
    print_section("Step 4: Execute External Research")
    print("⏳ Calling Gemini API (this may take 15-30 seconds)...")
    print()
    
    start_time = datetime.utcnow()
    
    try:
        result = execute_external_research(
            research_request=test_request,
            gemini_api_key=api_key,  # Explicit pass (tests resolution)
            model="gemini-2.0-flash",
            timeout=90
        )
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ API call completed in {duration:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Exception during execution: {e}")
        return False
    
    # Step 5: Validate output
    print_section("Step 5: Validate Output")
    
    if not validate_research_output(result):
        print("\n❌ Output validation failed")
        print("\nFull output:")
        print(json.dumps(result, indent=2))
        return False
    
    # Step 6: Display results
    print_section("Step 6: Results Summary")
    
    print_result("Work ID", result.get("work_id"))
    print_result("Trigger Reason", result.get("trigger_reason"))
    print_result("Conducted At", result.get("conducted_at"))
    
    if "error" in result:
        print("\n⚠️  RESEARCH FAILED WITH ERROR:")
        print_result("Error Type", result["error"].get("type"), indent=1)
        print_result("Error Message", result["error"].get("message"), indent=1)
        return False
    
    sources = result.get("sources", [])
    findings = result.get("findings", {})
    conflicts = result.get("conflicts", [])
    uncertainty_flags = result.get("uncertainty_flags", [])
    research_quality = result.get("research_quality", "UNKNOWN")
    promotion_eligible = result.get("promotion_eligible", False)
    
    print(f"\n📚 Sources Found: {len(sources)}")
    
    if sources:
        print("\nTop 3 sources:")
        for i, source in enumerate(sources[:3], 1):
            print(f"\n  {i}. {source.get('title', 'Untitled')}")
            print(f"     Author: {source.get('author', 'Unknown')}")
            print(f"     Type: {source.get('source_type', 'Unknown')}")
            print(f"     Authority: {source.get('authority_score', 0.0):.2f}")
            print(f"     URL: {source.get('url', 'N/A')}")
    
    print(f"\n🔍 Research Quality: {research_quality}")
    print(f"✨ Promotion Eligible: {promotion_eligible}")
    
    if uncertainty_flags:
        print(f"\n⚠️  Uncertainty Flags: {len(uncertainty_flags)}")
        for flag in uncertainty_flags:
            print(f"   - {flag}")
    
    if conflicts:
        print(f"\n⚡ Conflicts Found: {len(conflicts)}")
        for conflict in conflicts:
            print(f"   - {conflict.get('topic', 'Unknown topic')}")
    
    # Step 7: Save output
    print_section("Step 7: Save Output")
    
    output_file = "/home/claude/gemini_test_output.json"
    
    try:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"✅ Saved complete output to: {output_file}")
    except Exception as e:
        print(f"⚠️  Could not save output: {e}")
    
    # Final summary
    print_section("TEST COMPLETE - SUCCESS ✅")
    
    print("Summary:")
    print(f"  • Film researched: Blade Runner (1982)")
    print(f"  • Sources found: {len(sources)}")
    print(f"  • Research quality: {research_quality}")
    print(f"  • Execution time: {duration:.2f}s")
    print(f"  • Output saved: {output_file}")
    
    return True


def main():
    """Main entry point."""
    try:
        success = run_test()
        exit_code = 0 if success else 1
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()