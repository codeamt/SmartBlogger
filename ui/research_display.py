import streamlit as st


def render_research_details(result_state: dict):
    """Render research details"""
    st.header("Research Details")

    research_context = result_state.get("research_context", {})
    if not research_context:
        st.info("No research data available.")
        return

    # Get non-empty research sources
    sources = get_non_empty_sources(research_context)
    if not sources:
        st.info("Research conducted but no results found.")
        return

    # Create tabs for each research source
    render_research_tabs(sources, research_context)


def get_non_empty_sources(research_context: dict) -> list:
    """Get list of research sources that have data"""
    return [source for source, data in research_context.items()
            if data and len(data) > 0]


def render_research_tabs(sources: list, research_context: dict):
    """Render research sources in tabs"""
    tab_names = [source.capitalize() for source in sources]
    tabs = st.tabs(tab_names)

    for i, source_name in enumerate(sources):
        with tabs[i]:
            source_data = research_context[source_name]
            render_source_data(source_name, source_data)


def render_source_data(source_name: str, source_data: list):
    """Render data for a specific research source"""
    if not source_data:
        st.info(f"No {source_name} results.")
        return

    # Dispatch to specific renderers based on source type
    renderers = {
        "arxiv": render_arxiv_results,
        "web": render_web_results,
        "github": render_github_results,
        "substack": render_substack_results
    }

    renderer = renderers.get(source_name, render_generic_results)
    renderer(source_data)