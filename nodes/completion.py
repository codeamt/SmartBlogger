from ..state import EnhancedBlogState
from ..utils import memory_management


def completion_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Final node to handle workflow completion and cleanup"""
    # Optimize memory before completion
    optimized_state = memory_management.optimize_memory(state)

    # Generate completion summary
    total_sections = len(optimized_state.section_drafts)
    checked_sections = len(optimized_state.plagiarism_checks)
    total_tokens = sum(optimized_state.token_usage.values())

    completion_summary = {
        "total_sections": total_sections,
        "checked_sections": checked_sections,
        "total_tokens": total_tokens,
        "remaining_credits": optimized_state.free_tier_credits,
        "sections_with_revisions": len([h for h in optimized_state.revision_history.values() if h])
    }

    # Add completion summary to research context
    research_context = optimized_state.research_context or {}
    research_context["completion_summary"] = completion_summary

    return optimized_state.update(
        research_context=research_context,
        next_action="end"
    )