from ..state import EnhancedBlogState
from ..utils.token_tracking import track_token_usage
from models.llm_manager import local_llm_manager
import json


def research_coordinator_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Smart research coordination with query optimization"""
    # Skip research if approaching token limit
    total_tokens = sum(state.token_usage.values())
    if total_tokens > 900000:  # Approaching 1M token free tier
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

    prompt = f"""
    Analyze this technical content and generate 2-3 focused research queries:

    CONTENT:
    {content_preview}

    USER RESEARCH FOCUS: {state.research_focus or 'technical documentation'}

    Generate JSON output:
    {{
        "queries": [
            "specific technical concept to research",
            "related tools or frameworks", 
            "best practices or implementation examples"
        ],
        "priority": ["high", "medium", "low"]
    }}
    """

    try:
        researcher_llm = local_llm_manager.get_researcher()
        response = researcher_llm.invoke([
            ("system",
             "You are a research strategist. Create focused, actionable research queries. Output valid JSON only."),
            ("human", prompt)
        ])

        result = json.loads(response.content)
        return result.get("queries", ["technical documentation", "best practices"])

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

        # Assign sources based on query type and priority
        if "github" in research_sources and any(
                keyword in query.lower() for keyword in ["library", "framework", "package", "implementation"]):
            plan[priority].append({"query": query, "sources": ["github", "web"]})
        elif "arxiv" in research_sources and any(
                keyword in query.lower() for keyword in ["paper", "research", "study", "algorithm"]):
            plan[priority].append({"query": query, "sources": ["arxiv", "web"]})
        else:
            plan[priority].append({"query": query, "sources": research_sources})

    return plan