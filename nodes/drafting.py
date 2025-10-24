from ..state import EnhancedBlogState
from ..utils.formatting import format_research_for_drafting
from ..utils.token_tracking import track_token_usage
from models.llm_manager import local_llm_manager
import json


def blog_structuring_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Generate blog structure based on content and research"""
    if not state.content_summary:
        # Fallback structure
        sections = [
            {"id": "1", "title": "Introduction", "description": "Overview and context"},
            {"id": "2", "title": "Technical Analysis", "description": "Detailed examination"},
            {"id": "3", "title": "Implementation", "description": "Code examples and explanations"},
            {"id": "4", "title": "Conclusion", "description": "Summary and takeaways"}
        ]
        return state.update(
            sections=sections,
            current_section=sections[0],
            next_action="draft_section"
        )

    writer_llm = local_llm_manager.get_writer()

    # Include research context if available
    research_context = state.research_context or {}
    research_insights = research_context.get('key_insights', [])[:3] if research_context else []

    prompt = f"""
    Based on this content summary, create an appropriate blog structure:

    CONTENT SUMMARY:
    {state.content_summary[:2000]}

    RESEARCH CONTEXT:
    {research_insights}

    Create a logical blog structure with 4-6 sections. Output JSON:
    {{
        "sections": [
            {{
                "id": "1",
                "title": "Section Title", 
                "description": "What this section will cover"
            }}
        ]
    }}
    """

    try:
        response = writer_llm.invoke([
            ("system",
             "You are a technical content strategist. Create logical blog structures. Output valid JSON only."),
            ("human", prompt)
        ])

        updated_state = track_token_usage(state, response)
        structure = json.loads(response.content)

        return updated_state.update(
            sections=structure["sections"],
            current_section=structure["sections"][0] if structure["sections"] else None,
            next_action="draft_section"
        )
    except Exception as e:
        print(f"Blog structuring failed: {e}")
        # Fallback structure
        sections = [
            {"id": "1", "title": "Introduction", "description": "Overview and context"},
            {"id": "2", "title": "Technical Background", "description": "Foundational concepts"},
            {"id": "3", "title": "Implementation", "description": "Practical examples"},
            {"id": "4", "title": "Best Practices", "description": "Recommendations and tips"},
            {"id": "5", "title": "Conclusion", "description": "Summary and next steps"}
        ]
        return state.update(
            sections=sections,
            current_section=sections[0],
            next_action="draft_section"
        )


def section_drafting_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Generate content for the current section"""
    if not state.current_section:
        return state.update(next_action="completion")

    section = state.current_section
    writer_llm = local_llm_manager.get_writer()

    # Create optimized prompt with research context
    research_context = state.research_context or {}
    formatted_research = format_research_for_drafting(research_context, section)

    prompt = f"""
    ## Technical Writing Task
    **Section Title:** {section['title']}
    **Purpose:** {section['description']}

    ## Content Summary
    {state.content_summary[:1500] if state.content_summary else 'No content summary available'}

    {formatted_research}

    ## Requirements:
    1. Integrate 1-3 relevant citations using [^n] notation
    2. Include code snippets if applicable
    3. Use markdown formatting
    4. Maintain technical accuracy
    5. Write in clear, engaging style
    6. Target length: 500-1000 words
    """

    response = writer_llm.invoke([
        ("system", "You're a technical writer. Create comprehensive, cited content with proper markdown formatting."),
        ("human", prompt)
    ])

    updated_state = track_token_usage(state, response)

    # Update section drafts
    section_id = section["id"]
    updated_drafts = state.section_drafts.copy()
    updated_drafts[section_id] = response.content

    return updated_state.update(
        section_drafts=updated_drafts,
        next_action="plagiarism_check"
    )