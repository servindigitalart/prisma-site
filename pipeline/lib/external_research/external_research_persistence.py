#!/usr/bin/env python3
"""
External Research Persistence

WHAT THIS MODULE DOES:
- Writes External Research JSON to disk
- Creates directory structure if needed
- Ensures atomic writes (temp file + rename)
- Provides deterministic file paths

WHAT THIS MODULE DOES NOT DO:
- Does NOT validate data (that's external_research_validator.py)
- Does NOT read data
- Does NOT interpret data
- Does NOT make decisions
- Does NOT modify content
- Does NOT handle promotion logic
- Does NOT maintain indexes (that's external_research_registry.py)

EPISTEMIC POSITION:
This module is a write-only persistence layer with NO logic beyond file I/O.
It writes what it's given. It does not question, validate, or transform.
"""

import json
from pathlib import Path
from typing import Dict, Any
import tempfile
import os


class ExternalResearchPersistence:
    """
    Write-only persistence layer for External Research outputs.
    
    This is a stateless writer: data → disk.
    No side effects beyond file creation. No decisions.
    """
    
    def __init__(self, base_dir: str = "pipeline/derived/external_research"):
        """
        Initialize persistence layer.
        
        Args:
            base_dir: Base directory for external research outputs
        """
        self.base_dir = Path(base_dir)
    
    def save(self, work_id: str, research_output: Dict[str, Any]) -> Path:
        """
        Save external research output to disk.
        
        Args:
            work_id: Work identifier (e.g., "work_blade_runner_1982")
            research_output: Complete external research JSON output
        
        Returns:
            Path to saved file
        
        Raises:
            OSError: If file write fails
            ValueError: If work_id is invalid
        """
        if not work_id or not isinstance(work_id, str):
            raise ValueError(f"Invalid work_id: {work_id}")
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = self.base_dir / f"{work_id}.json"
        
        self._atomic_write_json(file_path, research_output)
        
        return file_path
    
    def _atomic_write_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """
        Write JSON file atomically using temp file + rename.
        
        Args:
            file_path: Destination file path
            data: Data to write
        
        Raises:
            OSError: If write fails
        """
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix='.tmp_',
            suffix='.json'
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            os.replace(temp_path, file_path)
            
        except Exception as e:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise OSError(f"Failed to write {file_path}: {e}") from e
    
    def get_file_path(self, work_id: str) -> Path:
        """
        Get file path for a work_id without writing.
        
        Args:
            work_id: Work identifier
        
        Returns:
            Path where file would be/is saved
        """
        return self.base_dir / f"{work_id}.json"
    
    def exists(self, work_id: str) -> bool:
        """
        Check if external research file exists for work_id.
        
        Args:
            work_id: Work identifier
        
        Returns:
            True if file exists, False otherwise
        """
        return self.get_file_path(work_id).exists()


def save_external_research(
    work_id: str, 
    research_output: Dict[str, Any],
    base_dir: str = "pipeline/derived/external_research"
) -> Path:
    """
    Convenience function for saving external research output.
    
    Args:
        work_id: Work identifier
        research_output: External research JSON output
        base_dir: Base directory for outputs
    
    Returns:
        Path to saved file
    """
    persistence = ExternalResearchPersistence(base_dir=base_dir)
    return persistence.save(work_id, research_output)