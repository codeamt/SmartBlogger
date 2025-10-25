from state import EnhancedBlogState
import os
import concurrent.futures
from .arxiv import execute_arxiv_search
from .github import execute_github_search
from .substack import execute_substack_search
from .perplexity import execute_perplexity_search
from utils.research_organizer import organize_research_results


def research_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Enhanced parallel research execution"""
    if not state.research_queries:
        return state.update(next_action="blog_structuring")

    research_plan = state.research_plan or {}
    all_results = {}

    # Execute high priority research first
    high_priority_queries = research_plan.get("high_priority", [])

    for query_plan in high_priority_queries:
        query = query_plan["query"]
        sources = query_plan["sources"]

        query_results = execute_parallel_research(query, sources, state)
        all_results[query] = query_results

        # Check token usage after each high-priority query
        if should_stop_research(state):
            break

    # Only proceed with medium priority if we have capacity
    if not should_stop_research(state):
        medium_priority_queries = research_plan.get("medium_priority", [])
        for query_plan in medium_priority_queries[:2]:  # Limit to 2 medium priority
            query = query_plan["query"]
            sources = query_plan["sources"]

            query_results = execute_parallel_research(query, sources, state)
            all_results[query] = query_results

            if should_stop_research(state):
                break

    # Organize results by source for easier consumption
    organized_results = organize_research_results(all_results)

    # Merge with existing research context
    existing_context = state.research_context or {}
    merged_context = {**existing_context, **organized_results}

    return state.update(
        research_context=merged_context,
        next_action="blog_structuring"
    )


def execute_parallel_research(query: str, sources: list, state: EnhancedBlogState) -> dict:
    """Execute research across multiple sources in parallel"""
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_source = {}

        for source in sources:
            if source == "web":
                future = executor.submit(execute_web_search, query, state)
                future_to_source[future] = "web"
            elif source == "arxiv":
                future = executor.submit(execute_arxiv_search, query, state)
                future_to_source[future] = "arxiv"
            elif source == "github":
                future = executor.submit(execute_github_search, query, state)
                future_to_source[future] = "github"
            elif source == "substack":
                future = executor.submit(execute_substack_search, query, state)
                future_to_source[future] = "substack"
            elif source == "perplexity" and os.environ.get("PERPLEXITY_API_KEY"):
                future = executor.submit(execute_perplexity_search, query, state)
                future_to_source[future] = "perplexity"

        # Collect results with per-future timeout to avoid dropping remaining futures
        for future, source in list(future_to_source.items()):
            try:
                results[source] = future.result(timeout=30)
            except Exception as e:
                print(f"Research failed for {source}: {e}")
                results[source] = []

    return results


def should_stop_research(state: EnhancedBlogState) -> bool:
    """Check if we should stop research due to token limits"""
    total_tokens = sum(state.token_usage.values())
    return total_tokens > 950000  # Stop before hitting limits


# Web search function (you'll need to implement this based on your preferred API)
def execute_web_search(query: str, state: EnhancedBlogState) -> list:
    """Execute web search via Perplexity (minimal proxy)."""
    if not os.environ.get("PERPLEXITY_API_KEY"):
        return []
    try:
        return execute_perplexity_search(query, state)
    except Exception as e:
        print(f"Web search (Perplexity) failed: {e}")
        return []