from state import EnhancedBlogState
from utils.token_tracking import track_token_usage
from models.llm_manager import local_llm_manager
from config import RESEARCH_QUERY_COUNT, RESEARCH_MAX_TOKENS
import json
import re


def research_coordinator_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Smart research coordination with query optimization"""
    # Skip research if approaching token limit
    total_tokens = sum(state.token_usage.values())
    if total_tokens > RESEARCH_MAX_TOKENS:  # Approaching 1M token free tier
        return state.update(next_action="blog_structuring")

    if not state.content_summary:
        return state.update(next_action="blog_structuring")

    # Generate optimized research queries
    research_queries = optimize_research_queries(state, total_tokens)

    return state.update(
        research_queries=research_queries,
        research_plan=generate_research_plan(research_queries, state),
        next_action="conduct_research"
    )


def optimize_research_queries(state: EnhancedBlogState, total_tokens: int) -> list:
    """Generate focused research queries based on content"""
    content_preview = state.content_summary[:1500] if state.content_summary else ""

    # Determine input type to prioritize appropriate sources
    input_type = _determine_input_type(state)
    
    # Generate dynamic prompt based on input type and configurable query count
    prompt = _generate_dynamic_prompt(content_preview, state, input_type, RESEARCH_QUERY_COUNT)

    # Proactive state management for dependencies
    if not _check_research_dependencies():
        raise Exception("Required research dependencies are not properly initialized. Please check your configuration.")
    
    try:
        researcher_llm = local_llm_manager.get_researcher()
        response = researcher_llm.invoke([
            ("system",
             "You are a research strategist. Create focused, actionable research queries. Output valid JSON only."),
            ("human", prompt)
        ])
        
        # Track token usage (now handled by LLM manager)
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            state.token_usage = _update_token_usage(state.token_usage, response.response_metadata['token_usage'])

        raw = response.content or ""
        try:
            result = json.loads(raw)
        except Exception:
            json_block = None
            if "```" in raw:
                parts = re.findall(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw)
                if parts:
                    json_block = parts[0]
            if not json_block:
                start = raw.find('{')
                end = raw.rfind('}')
                if start != -1 and end != -1 and end > start:
                    json_block = raw[start:end+1]
            if json_block:
                result = json.loads(json_block)
            else:
                raise
        # Extract both research queries and competitor queries
        research_queries = result.get("research_queries", []) or []
        competitor_queries = result.get("competitor_queries", []) or []
        
        # Combine all queries for processing
        queries = research_queries + competitor_queries
        
        # Store competitor queries in state for later processing
        if competitor_queries:
            research_context = state.research_context or {}
            research_context["competitor_queries"] = competitor_queries
            state.research_context = research_context
        # Normalize to list[str]
        normalized = []
        for q in queries:
            if isinstance(q, str):
                s = q.strip()
                if s:
                    normalized.append(s)
            elif isinstance(q, dict):
                s = str(q.get("query", "")).strip()
                if s:
                    normalized.append(s)
        if not normalized:
            normalized = ["technical documentation", "best practices"]
        return normalized

    except Exception as e:
        print(f"Query optimization failed: {e}")
        return ["technical documentation", "best practices"]


def generate_research_plan(queries: list, state: EnhancedBlogState) -> dict:
    """Create optimized research execution plan"""
    research_sources = state.research_sources or ["arxiv", "web"]

    plan = {
        "high_priority": [],
        "medium_priority": [],
        "low_priority": []
    }

    for i, query in enumerate(queries):
        priority = "high" if i == 0 else "medium" if i == 1 else "low"
        bucket = f"{priority}_priority"

        # Assign sources based on query type, priority, and input type
        sources = _determine_sources_for_query(query, research_sources, input_type)
        plan[bucket].append({"query": query, "sources": sources})

    return plan


def _determine_input_type(state: EnhancedBlogState) -> str:
    """Determine the input type to prioritize appropriate research sources"""
    content = state.source_code or ""
    
    # Check if content contains code-like patterns
    code_indicators = ["def ", "class ", "import ", "function", "var ", "let ", "const ",
                      "public ", "private ", "static ", "void ", "int ", "string ", "fn",
                      "<?php", "<html", "<script", "#include"]
    
    if any(indicator in content.lower() for indicator in code_indicators):
        return "code"
    
    # Check for scientific/academic content
    scientific_indicators = ["theorem", "proof", "lemma", "corollary", "hypothesis",
                           "experiment", "data", "analysis", "research", "study",
                           "algorithm", "methodology"]
    
    if any(indicator in content.lower() for indicator in scientific_indicators):
        return "scientific"
    
    # Default to general
    return "general"


def _generate_dynamic_prompt(content_preview: str, state: EnhancedBlogState, input_type: str, query_count: int) -> str:
    """Generate dynamic prompt based on input type and content preview"""
    # Determine source priorities based on input type
    if input_type == "code":
        source_priorities = "Prioritize GitHub and web search sources for code-related queries."
    elif input_type == "scientific":
        source_priorities = "Prioritize Arxiv and web search sources for scientific queries."
    else:
        source_priorities = "Use appropriate sources for each query type."
    
    prompt = f"""
Analyze the following content and generate {query_count} research queries that will help create a comprehensive blog post.
Also generate 2 competitor search queries to find high-performing blog posts on this topic.

CONTENT PREVIEW:
{content_preview}

INPUT TYPE: {input_type}
{source_priorities}

Generate diverse queries that cover different aspects of the topic. Focus on technical accuracy and recent information.
For competitor search queries, focus on finding high-authority blog posts and articles about this topic.

Return ONLY a JSON object with this structure:
{{
  "research_queries": ["query1", "query2", ...],
  "competitor_queries": ["competitor query 1", "competitor query 2"]
}}
"""
    
    return prompt


def _check_research_dependencies() -> bool:
    """Check if required research dependencies are properly initialized"""
    # Check if local LLM manager is available
    if not local_llm_manager:
        return False
    
    # Check if Perplexity API key is available (if needed)
    # For now, we'll just check if the local LLM manager is functional
    return True


def _update_token_usage(current_usage: dict, new_usage: dict) -> dict:
    """Update token usage with new values"""
    updated = current_usage.copy()
    for model, tokens in new_usage.items():
        if model in updated:
            updated[model] += tokens
        else:
            updated[model] = tokens
    return updated


def _determine_sources_for_query(query: str, available_sources: list, input_type: str) -> list:
    """Determine appropriate sources for a given query based on input type and content"""
    # If specific sources are mentioned in the query, prioritize those
    query_lower = query.lower()
    
    if "github" in available_sources and any(keyword in query_lower for keyword in 
        ["library", "framework", "package", "implementation", "code", "repository", "repo"]):
        return ["github", "web"]
    
    if "arxiv" in available_sources and any(keyword in query_lower for keyword in 
        ["paper", "research", "study", "algorithm", "theorem", "proof", "experiment"]):
        return ["arxiv", "web"]
    
    # For content about newsletters, blogging, or content creation, prioritize Substack
    if "substack" in available_sources and any(keyword in query_lower for keyword in 
        ["newsletter", "blog", "content", "writing", "audience", "subscribers", "engagement"]):
        return ["substack", "web"]
    
    # For code input type, prioritize GitHub and web
    if input_type == "code" and "github" in available_sources:
        return ["github", "web"]
    
    # For scientific input type, prioritize Arxiv and web
    if input_type == "scientific" and "arxiv" in available_sources:
        return ["arxiv", "web"]
    
    # Default to available sources
    return available_sources