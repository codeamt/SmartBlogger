from state import EnhancedBlogState
from utils import memory_management
from models.llm_manager import local_llm_manager


def completion_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Final node to handle workflow completion and cleanup"""
    # Optimize memory before completion
    optimized_state = memory_management.optimize_memory(state)

    # Assemble final blog post with polish
    final_content = assemble_final_blog(optimized_state)

    # Generate completion summary
    total_sections = len(optimized_state.section_drafts)
    checked_sections = len(optimized_state.plagiarism_checks)
    total_tokens = sum(optimized_state.token_usage.values())

    completion_summary = {
        "total_sections": total_sections,
        "checked_sections": checked_sections,
        "total_tokens": total_tokens,
        "remaining_credits": optimized_state.free_tier_credits,
        "sections_with_revisions": len([h for h in optimized_state.revision_history.values() if h]),
        "final_content": final_content
    }

    # Add completion summary to research context
    research_context = optimized_state.research_context or {}
    research_context["completion_summary"] = completion_summary

    return optimized_state.update(
        research_context=research_context,
        next_action="end"
    )


def assemble_final_blog(state: EnhancedBlogState) -> str:
    """Assemble sections into a polished blog post with intro, transitions, and conclusion."""
    sections = state.sections or []
    section_drafts = state.section_drafts or {}
    
    if not sections or not section_drafts:
        return "# Blog Post\n\n_No content generated._"
    
    # Build the blog structure
    parts = []
    
    # Generate title from first section or content summary
    title = _generate_title(state)
    parts.append(f"# {title}\n")
    
    # Use synthesized introduction if available
    research_context = state.research_context or {}
    intro_content = research_context.get("introduction", "")
    
    if intro_content:
        # Use the synthesized introduction
        parts.append(intro_content + "\n")
    else:
        # Fallback: Add a brief intro hook if first section isn't already "Introduction"
        first_section = sections[0] if sections else None
        if first_section and "intro" not in first_section.get("title", "").lower():
            intro_hook = _generate_intro_hook(state)
            if intro_hook:
                parts.append(intro_hook + "\n")
    
    # Assemble sections with transitions
    for idx, section in enumerate(sections):
        section_id = section.get("id")
        content = section_drafts.get(section_id, "")
        
        if not content:
            continue
        
        # Add section with proper heading
        section_title = section.get("title", f"Section {idx+1}")
        parts.append(f"## {section_title}\n")
        parts.append(content.strip() + "\n")
    
    # Add conclusion if not already present
    last_section = sections[-1] if sections else None
    if last_section and "conclusion" not in last_section.get("title", "").lower():
        conclusion = _generate_conclusion(state)
        if conclusion:
            parts.append("\n## Conclusion\n")
            parts.append(conclusion + "\n")
    
    # Add citations section if any citations exist
    if state.citations:
        parts.append("\n## References\n")
        all_citations = []
        for cites in state.citations.values():
            all_citations.extend(cites)
        for idx, cite in enumerate(all_citations, 1):
            title = cite.get("title", "Source")
            url = cite.get("url", "")
            if url:
                parts.append(f"[^{idx}]: [{title}]({url})\n")
            else:
                parts.append(f"[^{idx}]: {title}\n")
    
    return "\n".join(parts)


def _generate_title(state: EnhancedBlogState) -> str:
    """Generate a compelling title for the blog post."""
    # Use the title from blog structuring if available
    research_context = state.research_context or {}
    blog_title = research_context.get("blog_title", "")
    
    if blog_title and blog_title.strip():
        return blog_title.strip()
    
    # Fallback: create from research focus and custom questions
    focus = state.research_focus or "Technical Guide"
    custom_qs = state.custom_questions or []
    
    if custom_qs:
        # Use first question to create engaging title
        first_q = custom_qs[0].strip("?")
        return first_q if len(first_q) < 80 else f"{focus.split(',')[0].strip().title()}: A Practical Guide"
    
    return f"Mastering {focus.split(',')[0].strip().title()}: A Developer's Guide"


def _generate_intro_hook(state: EnhancedBlogState) -> str:
    """Generate a brief intro hook (1-2 sentences)."""
    custom_qs = state.custom_questions or []
    focus = state.research_focus or ""
    
    # If there are custom questions, use them to create an engaging hook
    if custom_qs:
        return f"When working with {focus.split(',')[0].strip() if focus else 'technical implementations'}, developers often ask: {custom_qs[0]} This guide explores practical approaches and best practices to help you master this concept.\n"
    
    # Fallback to content summary
    summary = (state.content_summary or "")[:300]
    if not summary:
        return ""
    
    sentences = summary.split(". ")
    hook = ". ".join(sentences[:2])
    if hook and not hook.endswith("."):
        hook += "."
    return hook + "\n"


def _generate_conclusion(state: EnhancedBlogState) -> str:
    """Generate a brief conclusion summarizing key points."""
    sections = state.sections or []
    custom_qs = state.custom_questions or []
    focus = state.research_focus or "these concepts"
    
    if not sections:
        return ""
    
    # Create a conclusion that ties back to the questions and focus
    section_titles = [s.get("title", "") for s in sections if s.get("title")]
    
    conclusion_parts = []
    
    # Summary of what was covered
    if len(section_titles) > 2:
        conclusion_parts.append(f"Throughout this guide, we've explored {', '.join(section_titles[:-1])}, and {section_titles[-1]}.")
    elif len(section_titles) == 2:
        conclusion_parts.append(f"In this guide, we covered {section_titles[0]} and {section_titles[1]}.")
    
    # Tie back to custom questions if present
    if custom_qs:
        conclusion_parts.append(f"By understanding these concepts, you're now equipped to {custom_qs[0].lower().strip('?')}.")
    else:
        conclusion_parts.append(f"With these insights into {focus.split(',')[0].strip()}, you can build more robust and efficient solutions.")
    
    # Call to action
    conclusion_parts.append("\nAs you apply these techniques in your projects, remember that practice and experimentation are key to mastery. Happy coding!")
    
    return "\n\n".join(conclusion_parts)