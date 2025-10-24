from ..state import EnhancedBlogState
from ..utils.token_tracking import track_token_usage
from models.llm_manager import llm_manager


def process_code_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Analyze source code with local LLM"""
    if not state.source_code:
        return state.update(next_action="research_coordinator")

    content = state.source_code[:10000]
    writer_llm = llm_manager.get_writer()

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
    researcher_llm = llm_manager.get_researcher()

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

    combined = f"""## SOURCE CODE
{state.source_code[:5000]}

### DOCUMENTS
{"\n\n".join(state.documents)[:5000]}"""

    researcher_llm = llm_manager.get_researcher()
    response = researcher_llm.invoke([
        ("system", "You're a technical integrator. Find connections between code and docs."),
        ("human", f"Create unified technical overview:\n{combined}")
    ])

    updated_state = track_token_usage(state, response)

    return updated_state.update(
        content_summary=response.content,
        next_action="research_coordinator"
    )