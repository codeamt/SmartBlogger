from state import EnhancedBlogState
from utils.token_tracking import track_token_usage
from models.llm_manager import local_llm_manager


def process_code_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Analyze source code with local LLM"""
    if not state.source_code:
        return state.update(next_action="research_coordinator")

    content = state.source_code[:10000]
    writer_llm = local_llm_manager.get_writer()

    response = writer_llm.invoke([
        ("system", "You're a senior developer. Provide technical analysis in 3-5 key points."),
        ("human", content)
    ])

    # Update token usage
    updated_state = track_token_usage(state, response)

    return updated_state.update(
        content_summary=response.content,
        next_action="research_coordinator"
    )


def process_docs_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Analyze documents with local LLM"""
    if not state.documents:
        return state.update(next_action="research_coordinator")

    docs_text = "\n\n".join(state.documents[:3])[:10000]
    researcher_llm = local_llm_manager.get_researcher()

    response = researcher_llm.invoke([
        ("system", "You're a research analyst. Extract core concepts."),
        ("human", f"Summarize key points:\n{docs_text}")
    ])

    updated_state = track_token_usage(state, response)

    return updated_state.update(
        content_summary=response.content,
        next_action="research_coordinator"
    )


def process_both_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Unify code and document content"""
    if not state.source_code or not state.documents:
        return state.update(next_action="research_coordinator")

    documents_content = "\n\n".join(state.documents)[:5000]
    combined = "## SOURCE CODE\n" + state.source_code[:5000] + "\n\n### DOCUMENTS\n" + documents_content

    researcher_llm = local_llm_manager.get_researcher()
    response = researcher_llm.invoke([
        ("system", "You're a technical integrator. Find connections between code and docs."),
        ("human", f"Create unified technical overview:\n{combined}")
    ])

    updated_state = track_token_usage(state, response)

    return updated_state.update(
        content_summary=response.content,
        next_action="research_coordinator"
    )


def route_outline_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Generate only an outline without full research and drafting"""
    # Create a minimal content summary for outline generation
    content_preview = ""
    
    if state.source_code:
        content_preview = state.source_code[:1000]
    elif state.documents:
        content_preview = "\n\n".join(state.documents[:2])[:1000]
    
    # Set a simple content summary to trigger blog structuring
    summary = f"Content for outline generation: {content_preview[:200]}..."
    
    return state.update(
        content_summary=summary,
        next_action="blog_structuring"
    )
