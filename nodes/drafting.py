from state import EnhancedBlogState
from utils.formatting import format_research_for_drafting
from utils.token_tracking import track_token_usage
from models.llm_manager import local_llm_manager
import json
import re


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

    # Build context for structuring
    tone = state.tone or "Professional"
    audience = state.target_audience or "Developers"
    custom_qs = state.custom_questions or []
    
    questions_context = ""
    if custom_qs:
        questions_context = "\n\nKEY QUESTIONS TO ADDRESS:\n" + "\n".join(f"- {q}" for q in custom_qs)
    
    prompt = f"""
    Create a cohesive blog structure that tells a complete story for {audience.lower()}.

    CONTENT SUMMARY:
    {state.content_summary[:2000]}

    RESEARCH INSIGHTS:
    {research_insights}{questions_context}

    TONE: {tone}

    Create 4-6 sections that build on each other logically. Each section should:
    - Have a clear, specific title (not generic like "Introduction" or "Implementation")
    - Flow naturally from the previous section
    - Contribute to answering the key questions
    - Build toward a practical conclusion

    Return ONLY valid JSON with this exact shape. No prose, no backticks:
    {{
        "title": "Compelling blog post title",
        "sections": [
            {{
                "id": "1",
                "title": "Specific, descriptive section title",
                "description": "What this section covers and how it connects to the overall narrative"
            }}
        ]
    }}
    """

    try:
        response = writer_llm.invoke([
            ("system",
             "You are a technical content strategist. Return ONLY a JSON object with key 'sections'. No prose, no code fences."),
            ("human", prompt)
        ])

        updated_state = track_token_usage(state, response)
        raw = response.content or ""
        try:
            structure = json.loads(raw)
        except Exception:
            # Try to extract JSON block from free-form text
            json_block = None
            if "```" in raw:
                # Prefer fenced code blocks first
                parts = re.findall(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw)
                if parts:
                    json_block = parts[0]
            if not json_block:
                # Fallback: take substring between first '{' and last '}'
                start = raw.find('{')
                end = raw.rfind('}')
                if start != -1 and end != -1 and end > start:
                    json_block = raw[start:end+1]
            if json_block:
                structure = json.loads(json_block)
            else:
                raise

        sections = structure.get("sections", [])
        blog_title = structure.get("title", "")
        
        return updated_state.update(
            sections=sections,
            current_section=sections[0] if sections else None,
            next_action="draft_section",
            research_context={**(state.research_context or {}), "blog_title": blog_title}
        )
    except Exception as e:
        print(f"Blog structuring failed: {e}")
        # Fallback structure
        # Create a more specific fallback based on content
        focus = state.research_focus or "technical concepts"
        sections = [
            {"id": "1", "title": f"Understanding {focus.split(',')[0].strip().title()}", "description": "Core concepts and context"},
            {"id": "2", "title": "Practical Implementation", "description": "Step-by-step approach with examples"},
            {"id": "3", "title": "Common Challenges and Solutions", "description": "Real-world issues and how to address them"},
            {"id": "4", "title": "Best Practices and Optimization", "description": "Professional recommendations"},
            {"id": "5", "title": "Key Takeaways", "description": "Summary and next steps"}
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

    # Build style context
    tone = state.tone or "Professional"
    audience = state.target_audience or "Developers"
    style_prefs = state.writing_style or []
    custom_qs = state.custom_questions or []
    sections = state.sections or []
    
    style_guidance = f"Write in a {tone.lower()} tone for {audience.lower()}."
    if "Include code examples" in style_prefs:
        style_guidance += " Include practical code examples with explanations."
    if "Step-by-step guides" in style_prefs:
        style_guidance += " Use step-by-step instructions where applicable."
    if "Real-world examples" in style_prefs:
        style_guidance += " Incorporate real-world use cases and scenarios."
    if "Comparative analysis" in style_prefs:
        style_guidance += " Compare different approaches or alternatives."
    
    questions_context = ""
    if custom_qs:
        questions_context = f"\n\nKEY QUESTIONS TO ADDRESS:\n" + "\n".join(f"- {q}" for q in custom_qs)
    
    # Build narrative context from previous sections
    current_idx = next((i for i, s in enumerate(sections) if s.get("id") == section.get("id")), 0)
    narrative_context = ""
    
    if current_idx > 0:
        prev_titles = [s.get("title", "") for s in sections[:current_idx]]
        narrative_context = f"\n\nPREVIOUS SECTIONS COVERED:\n" + "\n".join(f"- {t}" for t in prev_titles if t)
        narrative_context += f"\n\nBuild on these topics naturally. Reference previous concepts where relevant."
    
    if current_idx < len(sections) - 1:
        next_section = sections[current_idx + 1]
        narrative_context += f"\n\nNEXT SECTION: {next_section.get('title', '')}\nSet up a smooth transition to this topic."

    prompt = f"""
Write a cohesive blog section that fits into the larger narrative.

SECTION: {section['title']}
PURPOSE: {section['description']}{narrative_context}

CONTENT CONTEXT:
{state.content_summary[:1500] if state.content_summary else 'No content summary available'}

{formatted_research}{questions_context}

STYLE: {style_guidance}

Write 1000-1500 words that flow naturally from previous sections. Integrate 1-3 citations using [^n] notation. Use proper markdown formatting.

DO NOT:
- Repeat content from previous sections
- Start with generic phrases like "In this section" or "Let's explore"
- Include numbered lists of the same points across sections
- Echo these instructions

OUTPUT ONLY THE SECTION CONTENT.
    """

    response = writer_llm.invoke([
        ("system", f"You are a technical writer creating a cohesive blog post for {audience.lower()}. Write in a {tone.lower()} tone. Each section should build on previous ones naturally. Avoid repetition. Output markdown-formatted content only."),
        ("human", prompt)
    ])

    updated_state = track_token_usage(state, response)

    # Update section drafts
    section_id = section["id"]
    updated_drafts = state.section_drafts.copy()
    content = (response.content or "").strip()
    if not content:
        content = f"### {section['title']}\n\n_The writer model returned no content. Please try again or adjust your research focus._"
    updated_drafts[section_id] = content

    return updated_state.update(
        section_drafts=updated_drafts,
        next_action="plagiarism_check"
    )