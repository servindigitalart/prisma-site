#!/usr/local/bin/python3
"""
Prisma External Research Dry-Run Integration Test

PURPOSE:
This is NOT a unit test suite.
This is a deterministic integration test that exercises the External Research
trigger pipeline (Phase 2C.5 → Phase 2C) without external API calls.

WHAT THIS DOES:
- Constructs deterministic test inputs
- Calls real pipeline functions
- Prints structured outputs for human inspection

WHAT THIS DOES NOT DO:
- Does NOT execute Gemini API calls
- Does NOT write to filesystem
- Does NOT use mocking libraries
- Does NOT perform assertions
- Does NOT assign colors
- Does NOT reason about aesthetics

USAGE:
    python pipeline/tests/test_external_research_dry_run.py

EXPECTED OUTPUT:
Human-readable structured output showing:
- Evidence snapshots
- Trigger decisions
- Research request payloads (if triggered)
"""

import pprint
from typing import Dict, Any, Set

from pipeline.lib.external_research_trigger import (
    check_evidence_snapshot,
    should_trigger_external_research
)

from pipeline.lib.external_research.external_research_request_builder import (
    build_external_research_request
)


def run_test_case(
    case_name: str,
    work: Dict[str, Any],
    evidence_films: Set[str],
    evidence_cinematographers: Set[str],
    evidence_national_cinemas: Dict[str, int],
    editorial_override: bool = False,
    doctrine_ambiguity: bool = False,
    doctrine_ambiguity_description: str = None
):
    """
    Run a single dry-run test case.
    
    Args:
        case_name: Test case name
        work: Normalized work dict
        evidence_films: Set of work IDs in Evidence
        evidence_cinematographers: Set of cinematographer IDs in Evidence
        evidence_national_cinemas: Dict mapping country codes to film counts
        editorial_override: Whether work has editorial override
        doctrine_ambiguity: Whether doctrine presents ambiguous assignment
        doctrine_ambiguity_description: Optional ambiguity description
    """
    print("=" * 60)
    print(f"CASE: {case_name}")
    print("=" * 60)
    print()
    
    print("WORK:")
    pprint.pprint(work)
    print()
    
    evidence_snapshot = check_evidence_snapshot(
        work=work,
        evidence_films=evidence_films,
        evidence_cinematographers=evidence_cinematographers,
        evidence_national_cinemas=evidence_national_cinemas
    )
    
    print("EVIDENCE SNAPSHOT:")
    pprint.pprint(evidence_snapshot)
    print()
    
    trigger_decision = should_trigger_external_research(
        work=work,
        evidence_snapshot=evidence_snapshot,
        doctrine_version="1.1",
        editorial_override=editorial_override,
        doctrine_ambiguity=doctrine_ambiguity,
        doctrine_ambiguity_description=doctrine_ambiguity_description
    )
    
    print("TRIGGER DECISION:")
    pprint.pprint(trigger_decision)
    print()
    
    if trigger_decision["should_trigger"]:
        research_request = build_external_research_request(
            work=work,
            trigger_reason=trigger_decision["trigger_reason"],
            doctrine_version="1.1",
            evidence_version="2.1",
            evidence_gap_description=trigger_decision.get("evidence_gap_description"),
            doctrine_ambiguity_description=trigger_decision.get("doctrine_ambiguity_description")
        )
        
        print("RESEARCH REQUEST:")
        pprint.pprint(research_request)
    else:
        print("RESEARCH REQUEST:")
        print("NOT TRIGGERED")
    
    print()
    print()


def main():
    """Run all dry-run test cases."""
    
    evidence_films = {
        "work_moonlight_2016"
    }
    
    evidence_cinematographers = {
        "person_james_laxton"
    }
    
    evidence_national_cinemas = {
        "US": 150,
        "GB": 85,
        "FR": 120,
        "IT": 60
    }
    
    work_tropical_malady = {
        "id": "work_tropical_malady_2004",
        "title": "Tropical Malady",
        "year": 2004,
        "countries": ["TH", "FR", "DE"],
        "languages": ["th"],
        "genres": ["Drama", "Fantasy", "Romance"],
        "people": {
            "director": ["person_apichatpong_weerasethakul"],
            "cinematography": ["person_jean_marc_selva"],
            "writer": ["person_apichatpong_weerasethakul"],
            "cast": []
        }
    }
    
    run_test_case(
        case_name="Tropical Malady (2004)",
        work=work_tropical_malady,
        evidence_films=evidence_films,
        evidence_cinematographers=evidence_cinematographers,
        evidence_national_cinemas=evidence_national_cinemas
    )
    
    work_blade_runner = {
        "id": "work_blade_runner_1982",
        "title": "Blade Runner",
        "year": 1982,
        "countries": ["US"],
        "languages": ["en"],
        "genres": ["Science Fiction", "Thriller"],
        "people": {
            "director": ["person_ridley_scott"],
            "cinematography": ["person_jordan_cronenweth"],
            "writer": ["person_hampton_fancher", "person_david_peoples"],
            "cast": ["person_harrison_ford", "person_rutger_hauer"]
        }
    }
    
    run_test_case(
        case_name="Blade Runner (1982)",
        work=work_blade_runner,
        evidence_films=evidence_films,
        evidence_cinematographers=evidence_cinematographers,
        evidence_national_cinemas=evidence_national_cinemas
    )
    
    work_moonlight = {
        "id": "work_moonlight_2016",
        "title": "Moonlight",
        "year": 2016,
        "countries": ["US"],
        "languages": ["en"],
        "genres": ["Drama"],
        "people": {
            "director": ["person_barry_jenkins"],
            "cinematography": ["person_james_laxton"],
            "writer": ["person_barry_jenkins"],
            "cast": ["person_trevante_rhodes", "person_ashton_sanders"]
        }
    }
    
    run_test_case(
        case_name="Moonlight (2016)",
        work=work_moonlight,
        evidence_films=evidence_films,
        evidence_cinematographers=evidence_cinematographers,
        evidence_national_cinemas=evidence_national_cinemas
    )
    
    work_chungking_express = {
        "id": "work_chungking_express_1994",
        "title": "Chungking Express",
        "year": 1994,
        "countries": ["HK"],
        "languages": ["cn", "en"],
        "genres": ["Drama", "Romance"],
        "people": {
            "director": ["person_wong_kar_wai"],
            "cinematography": ["person_christopher_doyle", "person_andrew_lau"],
            "writer": ["person_wong_kar_wai"],
            "cast": ["person_brigitte_lin", "person_tony_leung"]
        }
    }
    
    run_test_case(
        case_name="Chungking Express (1994)",
        work=work_chungking_express,
        evidence_films=evidence_films,
        evidence_cinematographers=evidence_cinematographers,
        evidence_national_cinemas=evidence_national_cinemas
    )


if __name__ == "__main__":
    main()