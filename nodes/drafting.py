from state import EnhancedBlogState
from utils.formatting import format_research_for_drafting
from utils.token_tracking import track_token_usage
from models.llm_manager import local_llm_manager
from models.summarizer import summarizer
from typing import Dict, List
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
    """Generate content for the current section with iterative self-correction and research integration"""
    if not state.current_section:
        return state.update(next_action="completion")

    section = state.current_section
    writer_llm = local_llm_manager.get_writer()
    researcher_llm = local_llm_manager.get_researcher()

    # Create optimized prompt with research context
    research_context = state.research_context or {}
    
    # Select best 1-2 research snippets for intentional integration
    selected_research = select_best_research_snippets(research_context, section, researcher_llm)
    formatted_research = format_research_with_integration_instructions(selected_research, section)

    # Build style context
    tone = state.tone or "Professional"
    audience = state.target_audience or "Developers"
    style_prefs = state.writing_style or []
    custom_qs = state.custom_questions or []
    sections = state.sections or []
    
    # Add SEO constraints if available
    seo_instructions = ""
    if state.seo_constraints:
        seo_instructions = f"\n\nSEO INSTRUCTIONS:\n{state.seo_constraints.get('instructions', '')}"
    
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
    
    # Build narrative context from previous sections with context window management
    current_idx = next((i for i, s in enumerate(sections) if s.get("id") == section.get("id")), 0)
    narrative_context = ""
    
    if current_idx > 0:
        # Handle context window overflow
        narrative_context = build_narrative_context_with_summarization(sections[:current_idx], state)
        narrative_context += f"\n\nBuild on these topics naturally. Reference previous concepts where relevant."
    
    if current_idx < len(sections) - 1:
        next_section = sections[current_idx + 1]
        narrative_context += f"\n\nNEXT SECTION: {next_section.get('title', '')}\nSet up a smooth transition to this topic."

    # Initial draft prompt
    prompt = f"""
Write a cohesive blog section that fits into the larger narrative.

SECTION: {section['title']}
PURPOSE: {section['description']}{narrative_context}

CONTENT CONTEXT:
{state.content_summary[:1500] if state.content_summary else 'No content summary available'}

{formatted_research}{questions_context}{seo_instructions}

STYLE: {style_guidance}

Write 1000-1500 words that flow naturally from previous sections. Integrate 1-3 citations using [^n] notation. Use proper markdown formatting.

DO NOT:
- Repeat content from previous sections
- Start with generic phrases like "In this section" or "Let's explore"
- Include numbered lists of the same points across sections
- Echo these instructions

OUTPUT ONLY THE SECTION CONTENT.
    """

    # Generate initial draft
    response = writer_llm.invoke([
        ("system", f"You are a technical writer creating a cohesive blog post for {audience.lower()}. Write in a {tone.lower()} tone. Each section should build on previous ones naturally. Avoid repetition. Output markdown-formatted content only."),
        ("human", prompt)
    ])

    updated_state = track_token_usage(state, response)
    initial_draft = (response.content or "").strip()
    
    if not initial_draft:
        initial_draft = f"### {section['title']}\n\n_The writer model returned no content. Please try again or adjust your research focus._"

    # Iterative Self-Correction Loop (Critic Node)
    refined_draft = apply_self_correction_loop(initial_draft, section, formatted_research, writer_llm, researcher_llm, updated_state)

    # Update section drafts
    section_id = section["id"]
    updated_drafts = state.section_drafts.copy()
    updated_drafts[section_id] = refined_draft

    return updated_state.update(
        section_drafts=updated_drafts,
        next_action="plagiarism_check"
    )


def select_best_research_snippets(research_context: Dict, section: Dict, researcher_llm) -> List[Dict]:
    """Select the best 1-2 research snippets for the current section"""
    all_snippets = []
    
    # Collect all research snippets
    for source_type, results in research_context.get('by_source', {}).items():
        for result in results:
            if isinstance(result, dict):
                snippet = result.copy()
                snippet['source_type'] = source_type
                all_snippets.append(snippet)
    
    if not all_snippets:
        return []
    
    # If we have few snippets, return all
    if len(all_snippets) <= 2:
        return all_snippets
    
    # Use LLM to rank snippets by relevance to the current section
    section_title = section.get('title', '')
    section_description = section.get('description', '')
    
    ranking_prompt = f"""
Rank the following research snippets by relevance to this section:

SECTION TITLE: {section_title}
SECTION PURPOSE: {section_description}

SNIPPETS:
"""
    
    for i, snippet in enumerate(all_snippets):
        content = snippet.get('content', '')[:200] + "..." if len(snippet.get('content', '')) > 200 else snippet.get('content', '')
        ranking_prompt += f"{i+1}. {content}\n"
    
    ranking_prompt += "\nReturn ONLY a JSON array with the indices (1-based) of the 2 most relevant snippets, e.g., [1, 3]"
    
    try:
        response = researcher_llm.invoke([
            ("system", "You are a research analyst. Rank research snippets by relevance. Return ONLY a JSON array with indices."),
            ("human", ranking_prompt)
        ])
        
        # Try to parse the response
        content = response.content.strip()
        if content.startswith('[') and content.endswith(']'):
            indices = json.loads(content)
            # Convert to 0-based indices and get snippets
            selected = [all_snippets[i-1] for i in indices if 1 <= i <= len(all_snippets)][:2]
            return selected
    except Exception as e:
        print(f"Research snippet ranking failed: {e}")
    
    # Fallback: return first 2 snippets
    return all_snippets[:2]


def format_research_with_integration_instructions(research_snippets: List[Dict], section: Dict) -> str:
    """Format research snippets with explicit integration instructions"""
    if not research_snippets:
        return "No research context available"
    
    formatted = "## Research Insights for Section\n\n"
    formatted += "### Selected Sources with Integration Instructions:\n\n"
    
    for i, snippet in enumerate(research_snippets, 1):
        content = snippet.get('content', '')
        title = snippet.get('title', f'Source {i}')
        source_type = snippet.get('source_type', 'web')
        url = snippet.get('url', '')
        
        # Determine integration instruction based on content type
        instruction = determine_integration_instruction(content, section)
        
        formatted += f"{i}. **{title}** ({source_type})\n"
        formatted += f"   **Integration:** {instruction}\n"
        formatted += f"   **Content:** {content[:300]}...\n"
        if url:
            formatted += f"   [Read more]({url})\n"
        formatted += "\n"
    
    return formatted


def determine_integration_instruction(content: str, section: Dict) -> str:
    """Determine how to integrate a research snippet based on its content"""
    content_lower = content.lower()
    
    # Check for different content patterns
    if '"' in content or '\'' in content:
        return "Use this as a supporting quote with proper attribution"
    elif any(keyword in content_lower for keyword in ['study', 'research', 'experiment', 'data']):
        return "Rephrase this finding to support the section's main points"
    elif any(keyword in content_lower for keyword in ['code', 'function', 'class', 'method']):
        return "Include this as a code example with explanation"
    elif any(keyword in content_lower for keyword in ['steps', 'process', 'procedure']):
        return "Use this to structure a step-by-step explanation"
    else:
        return "Incorporate this information to support key concepts"


def build_narrative_context_with_summarization(previous_sections: List[Dict], state: EnhancedBlogState) -> str:
    """Build narrative context with summarization to handle context window overflow"""
    if not previous_sections:
        return ""
    
    # Calculate total length of previous sections
    total_length = 0
    for section in previous_sections:
        section_id = section.get("id", "")
        draft_content = state.section_drafts.get(section_id, "")
        total_length += len(draft_content)
    
    # If total length is reasonable, include full content
    if total_length < 3000:  # Roughly 750 tokens
        prev_titles = [s.get("title", "") for s in previous_sections]
        context = f"\n\nPREVIOUS SECTIONS COVERED:\n" + "\n".join(f"- {t}" for t in prev_titles if t)
        context += "\n\nFull content of previous sections:\n"
        
        for section in previous_sections:
            section_id = section.get("id", "")
            draft_content = state.section_drafts.get(section_id, "")
            if draft_content:
                context += f"\n--- {section.get('title', '')} ---\n{draft_content[:500]}...\n"
        
        return context
    
    # If too long, use summarization
    summary_prompt = "Summarize the key points from the previous sections of this blog post:\n\n"
    for section in previous_sections:
        section_id = section.get("id", "")
        draft_content = state.section_drafts.get(section_id, "")
        if draft_content:
            summary_prompt += f"\n{section.get('title', '')}:\n{draft_content[:800]}...\n"
    
    try:
        # Use the HybridSummarizer to create a condensed summary
        summary = summarizer.summarize(summary_prompt, "blog post context", state.dict())
        return f"\n\nSUMMARY OF PREVIOUS SECTIONS:\n{summary}"
    except Exception as e:
        print(f"Summarization failed: {e}")
        # Fallback to simple title listing
        prev_titles = [s.get("title", "") for s in previous_sections]
        return f"\n\nPREVIOUS SECTIONS COVERED:\n" + "\n".join(f"- {t}" for t in prev_titles if t)


def apply_self_correction_loop(initial_draft: str, section: Dict, formatted_research: str, writer_llm, researcher_llm, state: EnhancedBlogState) -> str:
    """Apply iterative self-correction loop to refine the draft"""
    current_draft = initial_draft
    
    # Check keyword density if SEO targets are available
    seo_feedback = ""
    if state.seo_targets:
        primary_keywords = [kw.get("keyword", "") for kw in state.seo_targets.get("primary_keywords", [])]
        secondary_keywords = [kw.get("keyword", "") for kw in state.seo_targets.get("secondary_keywords", [])]
        
        density_analysis = analyze_keyword_density(current_draft, primary_keywords, secondary_keywords)
        
        # Check if density meets targets (1.5-2.5% for primary, 0.5-1.0% for secondary)
        primary_density = density_analysis.get("primary_density", 0)
        secondary_density = density_analysis.get("secondary_density", 0)
        
        if primary_density < 1.5 or primary_density > 2.5:
            seo_feedback += f"\nSEO FEEDBACK: Primary keyword density is {primary_density}%. Target range is 1.5-2.5%. "
        
        if secondary_density < 0.5 or secondary_density > 1.0:
            seo_feedback += f"\nSEO FEEDBACK: Secondary keyword density is {secondary_density}%. Target range is 0.5-1.0%. "
    
    # Critic Node - Review the draft
    critic_prompt = f"""
Review this blog section draft and provide constructive feedback:

SECTION TITLE: {section.get('title', '')}
SECTION PURPOSE: {section.get('description', '')}

DRAFT:
{current_draft[:2000]}...

RESEARCH CONTEXT:
{formatted_research}{seo_feedback}

Provide feedback on:
1. How well the draft addresses the section's purpose
2. Integration of research insights
3. Clarity and flow
4. Technical accuracy
5. Overall quality (score 1-10)
6. SEO optimization (keyword usage, natural integration)

Return ONLY a JSON object with this structure:
{{
  "score": 7,
  "strengths": ["list of strengths"],
  "weaknesses": ["list of weaknesses"],
  "suggestions": ["specific improvement suggestions"]
}}
"""
    
    try:
        critic_response = researcher_llm.invoke([
            ("system", "You are a critical reviewer of technical content. Provide detailed, actionable feedback."),
            ("human", critic_prompt)
        ])
        
        # Parse critic feedback
        feedback_content = critic_response.content.strip()
        feedback = None
        
        # Try to extract JSON from the response
        if feedback_content.startswith('{') and feedback_content.endswith('}'):
            try:
                feedback = json.loads(feedback_content)
            except:
                # Try to find JSON block
                json_match = re.search(r'\{[^}]+\}', feedback_content)
                if json_match:
                    try:
                        feedback = json.loads(json_match.group())
                    except:
                        pass
        
        if feedback and isinstance(feedback, dict):
            score = feedback.get('score', 5)
            
            # If score is low or there's SEO feedback, apply refinement
            if score < 8 or seo_feedback:
                refinement_prompt = f"""
Improve this blog section based on the feedback provided:

ORIGINAL DRAFT:
{current_draft}

FEEDBACK:
Score: {feedback.get('score', 5)}/10
Strengths: {', '.join(feedback.get('strengths', []))}
Weaknesses: {', '.join(feedback.get('weaknesses', []))}
Suggestions: {', '.join(feedback.get('suggestions', []))}{seo_feedback}

RESEARCH CONTEXT:
{formatted_research}

SECTION TITLE: {section.get('title', '')}
SECTION PURPOSE: {section.get('description', '')}

Write an improved version that addresses the feedback while maintaining the core content.
Include better integration of SEO keywords naturally throughout the content.
"""
                
                refinement_response = writer_llm.invoke([
                    ("system", "You are a technical writer improving content based on feedback. Maintain the core message while addressing issues. Naturally integrate SEO keywords without keyword stuffing."),
                    ("human", refinement_prompt)
                ])
                
                refined_draft = (refinement_response.content or "").strip()
                if refined_draft:
                    return refined_draft
    except Exception as e:
        print(f"Self-correction loop failed: {e}")
    
    # Return original draft if refinement failed
    return current_draft


def analyze_keyword_density(content: str, primary_keywords: list, secondary_keywords: list) -> dict:
    """Analyze keyword density in content"""
    if not content:
        return {"primary_density": 0, "secondary_density": 0}
    
    # Simple word count
    words = content.lower().split()
    total_words = len(words)
    
    if total_words == 0:
        return {"primary_density": 0, "secondary_density": 0}
    
    # Count primary keyword occurrences
    primary_count = 0
    for keyword in primary_keywords:
        keyword_words = keyword.lower().split()
        if len(keyword_words) == 1:
            primary_count += words.count(keyword_words[0])
        else:
            # For phrases, count occurrences
            primary_count += content.lower().count(keyword.lower())
    
    # Count secondary keyword occurrences
    secondary_count = 0
    for keyword in secondary_keywords:
        keyword_words = keyword.lower().split()
        if len(keyword_words) == 1:
            secondary_count += words.count(keyword_words[0])
        else:
            secondary_count += content.lower().count(keyword.lower())
    
    primary_density = (primary_count / total_words) * 100 if total_words > 0 else 0
    secondary_density = (secondary_count / total_words) * 100 if total_words > 0 else 0
    
    return {
        "primary_density": round(primary_density, 2),
        "secondary_density": round(secondary_density, 2),
        "primary_count": primary_count,
        "secondary_count": secondary_count,
        "total_words": total_words
    }