#!/usr/bin/env python3
"""
External Research Registry

WHAT THIS MODULE DOES:
- Maintains an append-only registry of External Research actions
- Tracks metadata for audit purposes
- Provides basic query interface for registry entries
- Ensures chronological ordering

WHAT THIS MODULE DOES NOT DO:
- Does NOT make promotion decisions
- Does NOT delete entries
- Does NOT mutate existing entries
- Does NOT validate research outputs (that's external_research_validator.py)
- Does NOT persist research outputs (that's external_research_persistence.py)
- Does NOT interpret research findings
- Does NOT filter or rank by business logic

EPISTEMIC POSITION:
This module is a write-only audit trail with NO decision-making authority.
It records actions. It does not judge, promote, filter, or rank.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import fcntl


class ExternalResearchRegistry:
    """
    Append-only registry of External Research actions.
    
    This is a stateless recorder: action → registry entry.
    No decisions. No deletions. No mutations. No filtering.
    """
    
    def __init__(self, registry_path: str = "pipeline/derived/external_research_registry.jsonl"):
        """
        Initialize registry.
        
        Args:
            registry_path: Path to registry file (JSONL format)
        """
        self.registry_path = Path(registry_path)
    
    def register(
        self,
        work_id: str,
        trigger_reason: str,
        research_quality: str,
        promotion_eligible: bool,
        doctrine_version: str,
        evidence_version: str,
        file_path: str,
        conducted_at: Optional[str] = None
    ) -> None:
        """
        Register an external research action.
        
        Args:
            work_id: Work identifier
            trigger_reason: Why research was triggered
            research_quality: Research quality (HIGH/MODERATE/LOW)
            promotion_eligible: Whether eligible for evidence promotion
            doctrine_version: Doctrine version used
            evidence_version: Evidence version used
            file_path: Path to saved research output
            conducted_at: ISO timestamp (defaults to now if not provided)
        
        Raises:
            OSError: If registry write fails
        """
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "work_id": work_id,
            "trigger_reason": trigger_reason,
            "conducted_at": conducted_at or datetime.utcnow().isoformat() + "Z",
            "research_quality": research_quality,
            "promotion_eligible": promotion_eligible,
            "doctrine_version": doctrine_version,
            "evidence_version": evidence_version,
            "file_path": file_path,
            "registered_at": datetime.utcnow().isoformat() + "Z"
        }
        
        self._append_entry(entry)
    
    def _append_entry(self, entry: Dict[str, Any]) -> None:
        """
        Append entry to registry file with file locking.
        
        Args:
            entry: Registry entry dict
        
        Raises:
            OSError: If write fails
        """
        with open(self.registry_path, 'a', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            
            try:
                json.dump(entry, f, ensure_ascii=False)
                f.write('\n')
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def get_all_entries(self) -> List[Dict[str, Any]]:
        """
        Get all registry entries (for audit purposes).
        
        Returns:
            List of all registry entries in chronological order
        """
        if not self.registry_path.exists():
            return []
        
        entries = []
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return entries
    
    def get_entry_by_work_id(self, work_id: str) -> Optional[Dict[str, Any]]:
        """
        Get most recent registry entry for a work_id.
        
        Args:
            work_id: Work identifier
        
        Returns:
            Most recent entry for work_id, or None if not found
        """
        entries = self.get_all_entries()
        
        matching = [e for e in entries if e.get('work_id') == work_id]
        
        if not matching:
            return None
        
        return matching[-1]


def register_external_research(
    work_id: str,
    trigger_reason: str,
    research_quality: str,
    promotion_eligible: bool,
    doctrine_version: str,
    evidence_version: str,
    file_path: str,
    registry_path: str = "pipeline/derived/external_research_registry.jsonl"
) -> None:
    """
    Convenience function for registering external research action.
    
    Args:
        work_id: Work identifier
        trigger_reason: Research trigger reason
        research_quality: Research quality (HIGH/MODERATE/LOW)
        promotion_eligible: Whether eligible for promotion
        doctrine_version: Doctrine version used
        evidence_version: Evidence version used
        file_path: Path to saved research output
        registry_path: Path to registry file
    """
    registry = ExternalResearchRegistry(registry_path=registry_path)
    registry.register(
        work_id=work_id,
        trigger_reason=trigger_reason,
        research_quality=research_quality,
        promotion_eligible=promotion_eligible,
        doctrine_version=doctrine_version,
        evidence_version=evidence_version,
        file_path=file_path
    )