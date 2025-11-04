"""
Introduction synthesis node - Creates a compelling, context-aware introduction
that sets the tone and direction for the entire blog post.
"""

from state import EnhancedBlogState
from models.llm_manager import local_llm_manager
from utils.token_tracking import track_token_usage


def introduction_synthesis_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """
    Synthesize a compelling introduction that:
    1. Hooks the reader with the problem/question
    2. Establishes context from research
    3. Previews what the post will cover
    4. Sets the tone for the entire piece
    """
    
    writer_llm = local_llm_manager.get_writer()
    
    # Gather context
    tone = state.tone or "Professional"
    audience = state.target_audience or "Developers"
    custom_qs = state.custom_questions or []
    research_focus = state.research_focus or ""
    content_summary = state.content_summary or ""
    sections = state.sections or []
    research_context = state.research_context or {}
    blog_title = research_context.get("blog_title", "")
    
    # Build research insights summary
    research_insights = _summarize_research_insights(research_context)
    
    # Build section preview
    section_preview = ""
    if sections:
        section_titles = [s.get("title", "") for s in sections if s.get("title")]
        if len(section_titles) > 2:
            section_preview = f"We'll explore {', '.join(section_titles[:-1])}, and {section_titles[-1]}."
        elif len(section_titles) == 2:
            section_preview = f"We'll cover {section_titles[0]} and {section_titles[1]}."
    
    # Build the prompt
    prompt = f"""
Write a compelling introduction for a technical blog post titled "{blog_title}".

TARGET AUDIENCE: {audience}
TONE: {tone}
RESEARCH FOCUS: {research_focus}

CONTENT CONTEXT:
{content_summary[:800]}

KEY RESEARCH INSIGHTS:
{research_insights}

CUSTOM QUESTIONS TO ADDRESS:
{chr(10).join(f"- {q}" for q in custom_qs) if custom_qs else "None"}

WHAT THE POST WILL COVER:
{section_preview}

Write a 200-300 word introduction that:
1. Opens with a hook that captures attention (question, statistic, scenario, or problem statement)
2. Establishes why this topic matters to {audience.lower()}
3. References the key question(s) naturally
4. Previews what readers will learn
5. Sets expectations for the {tone.lower()} tone

DO NOT:
- Start with "In this post" or "This article will"
- Include generic phrases like "Let's dive in"
- Echo these instructions
- Use placeholder text

OUTPUT ONLY THE INTRODUCTION TEXT in markdown format.
"""

    system_message = f"""You are a technical writer crafting an engaging introduction for {audience.lower()}.
Write in a {tone.lower()} tone. Hook the reader immediately with a compelling opening.
Avoid clichés and generic phrases. Make every sentence count."""

    response = writer_llm.invoke([
        ("system", system_message),
        ("human", prompt)
    ])
    
    updated_state = track_token_usage(state, response)
    
    intro_content = (response.content or "").strip()
    
    # Store introduction in research_context for later assembly
    updated_research_context = updated_state.research_context or {}
    updated_research_context["introduction"] = intro_content
    
    return updated_state.update(
        research_context=updated_research_context,
        next_action="draft_section"  # Continue to section drafting
    )


def _summarize_research_insights(research_context: dict) -> str:
    """Extract and summarize key research insights."""
    insights = []
    
    # Check for key insights
    if "key_insights" in research_context:
        key_insights = research_context["key_insights"]
        if isinstance(key_insights, list):
            insights.extend(key_insights[:3])
    
    # Check for research by source
    by_source = research_context.get("by_source", {})
    for source_name, source_data in by_source.items():
        if isinstance(source_data, list) and source_data:
            # Get first result from each source
            first_result = source_data[0]
            if isinstance(first_result, dict):
                title = first_result.get("title", "")
                if title:
                    insights.append(f"{source_name.title()}: {title}")
    
    if not insights:
        return "Research conducted across multiple sources."
    
    return "\n".join(f"- {insight}" for insight in insights[:5])


def conditional_research_synthesis_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """
    Conditional node that performs specialized synthesis based on research sources.
    Routes to specialized handlers for arxiv, github, etc.
    """
    
    research_sources = state.research_sources or []
    research_context = state.research_context or {}
    
    # Determine which specialized synthesis to perform
    if "arxiv" in research_sources:
        return _synthesize_arxiv_context(state)
    elif "github" in research_sources:
        return _synthesize_github_context(state)
    elif "substack" in research_sources:
        return _synthesize_substack_context(state)
    else:
        # Default: web-based synthesis
        return _synthesize_web_context(state)


def _synthesize_arxiv_context(state: EnhancedBlogState) -> EnhancedBlogState:
    """Synthesize academic paper insights for arxiv sources."""
    
    research_context = state.research_context or {}
    arxiv_results = research_context.get("by_source", {}).get("arxiv", [])
    
    if not arxiv_results:
        return state
    
    # Extract key academic insights with enhanced metadata
    papers = []
    high_quality_papers = []
    
    for result in arxiv_results[:5]:  # Process more papers for better selection
        if isinstance(result, dict):
            title = result.get("title", "")
            authors = result.get("authors", [])
            summary = result.get("summary", "")
            
            # Extract enhanced metadata if available
            paper_type = result.get("type", "unknown")
            quality_score = result.get("quality_score", 0)
            metadata = result.get("metadata", {})
            
            paper_info = {
                "title": title,
                "authors": authors if isinstance(authors, list) else [authors],
                "summary": summary[:300] if summary else "",
                "type": paper_type,
                "quality_score": quality_score,
                "citation_count": metadata.get("citation_count", 0),
                "year": metadata.get("year", 0),
                "venue": metadata.get("venue", ""),
                "topics": metadata.get("topics", [])
            }
            
            if title:
                papers.append(paper_info)
                # Track high-quality papers separately
                if quality_score >= 70:
                    high_quality_papers.append(paper_info)
    
    # Sort papers by quality score
    papers.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    high_quality_papers.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    
    # Add academic context to research_context
    updated_research_context = research_context.copy()
    updated_research_context["academic_papers"] = papers[:3]  # Top 3 papers
    updated_research_context["high_quality_papers"] = high_quality_papers[:2]  # Top 2 high-quality papers
    updated_research_context["synthesis_type"] = "academic"
    updated_research_context["paper_count"] = len(papers)
    
    return state.update(research_context=updated_research_context)


def _synthesize_github_context(state: EnhancedBlogState) -> EnhancedBlogState:
    """Synthesize repository insights for github sources."""
    
    research_context = state.research_context or {}
    github_results = research_context.get("by_source", {}).get("github", [])
    
    if not github_results:
        return state
    
    # Extract key repository insights
    repos = []
    for result in github_results[:3]:
        if isinstance(result, dict):
            title = result.get("title", "")
            stars = result.get("stars", 0)
            language = result.get("language", "")
            description = result.get("content", "")
            
            if title:
                repos.append({
                    "name": title,
                    "stars": stars,
                    "language": language,
                    "description": description[:200] if description else ""
                })
    
    # Add repository context to research_context
    updated_research_context = research_context.copy()
    updated_research_context["github_repos"] = repos
    updated_research_context["synthesis_type"] = "repository"
    
    return state.update(research_context=updated_research_context)


def _synthesize_substack_context(state: EnhancedBlogState) -> EnhancedBlogState:
    """Synthesize newsletter insights for substack sources."""
    
    research_context = state.research_context or {}
    substack_results = research_context.get("by_source", {}).get("substack", [])
    
    if not substack_results:
        return state
    
    # Extract key newsletter insights
    posts = []
    for result in substack_results[:3]:
        if isinstance(result, dict):
            title = result.get("title", "")
            author = result.get("author", "")
            content = result.get("content", "")
            
            if title:
                posts.append({
                    "title": title,
                    "author": author,
                    "excerpt": content[:200] if content else ""
                })
    
    # Add newsletter context to research_context
    updated_research_context = research_context.copy()
    updated_research_context["substack_posts"] = posts
    updated_research_context["synthesis_type"] = "newsletter"
    
    return state.update(research_context=updated_research_context)


def _synthesize_web_context(state: EnhancedBlogState) -> EnhancedBlogState:
    """Synthesize general web search insights."""
    
    research_context = state.research_context or {}
    web_results = research_context.get("by_source", {}).get("web", [])
    
    if not web_results:
        return state
    
    # Extract key web insights
    articles = []
    for result in web_results[:5]:
        if isinstance(result, dict):
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")
            
            if title:
                articles.append({
                    "title": title,
                    "url": url,
                    "excerpt": content[:200] if content else ""
                })
    
    # Add web context to research_context
    updated_research_context = research_context.copy()
    updated_research_context["web_articles"] = articles
    updated_research_context["synthesis_type"] = "web"
    
    return state.update(research_context=updated_research_context)
