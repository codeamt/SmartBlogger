from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel, Field


class EnhancedBlogState(BaseModel):
    # Inputs
    source_code: Optional[str] = None
    uploaded_files: Optional[List[str]] = None

    # Content pipeline
    documents: Optional[List[str]] = None
    content_summary: Optional[str] = None
    research_queries: Optional[List[str]] = None
    research_context: Optional[Dict] = None
    research_plan: Optional[Dict] = None
    research_sources: Optional[List[str]] = Field(default_factory=list)

    # Drafting
    sections: Optional[List[Dict]] = None
    current_section: Optional[Dict] = None
    section_drafts: Dict[str, str] = Field(default_factory=dict)
    citations: Dict[str, List[Dict]] = Field(default_factory=dict)
    next_action: str = "process_inputs"

    # Resources
    token_usage: Dict[str, int] = Field(default_factory=dict)
    free_tier_credits: int = 100
    content_fingerprints: Set[str] = Field(default_factory=set)

    # Plagiarism
    plagiarism_checks: Dict[str, Dict] = Field(default_factory=dict)
    revision_history: Dict[str, List[str]] = Field(default_factory=dict)
    plagiarism_feedback: Optional[str] = None
    needs_rewrite: bool = False

    def update(self, **updates) -> 'EnhancedBlogState':
        """Update state and return new instance"""
        return self.copy(update=updates)

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override dict to include all fields"""
        return super().dict(**kwargs)