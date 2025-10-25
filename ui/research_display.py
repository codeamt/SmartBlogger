import streamlit as st


def render_research_details(result_state: dict):
    """Render research details"""
    st.header("Research Details")

    research_context = result_state.get("research_context", {})
    if not research_context:
        st.info("No research data available.")
        return

    # Prefer organized format if available
    source_map = research_context.get("by_source") if isinstance(research_context, dict) else None
    if not source_map or not isinstance(source_map, dict):
        source_map = research_context if isinstance(research_context, dict) else {}

    # Optional debug view
    with st.expander("🔎 Debug: Raw research context", expanded=False):
        st.json(research_context)

    # Get non-empty research sources
    sources = get_non_empty_sources(source_map)
    if not sources:
        st.info("Research conducted but no results found.")
        with st.expander("🔎 Debug: Source map (empty)", expanded=False):
            st.json(source_map)
        return

    # Create tabs for each research source
    render_research_tabs(sources, source_map)


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
            source_data = research_context.get(source_name, [])
            render_source_data(source_name, source_data)


def render_source_data(source_name: str, source_data):
    """Render data for a specific research source. Accepts list|dict|str and normalizes to list[dict]."""
    if not source_data:
        st.info(f"No {source_name} results.")
        return

    # Normalize input to list
    if isinstance(source_data, dict):
        items = [source_data]
    elif isinstance(source_data, list):
        items = source_data
    else:
        items = [source_data]

    # Normalize each item to dict
    normalized = []
    for it in items:
        if isinstance(it, dict):
            normalized.append(it)
        elif isinstance(it, str):
            text = it.strip()
            normalized.append({
                "title": (text[:60] + ("…" if len(text) > 60 else "")) or f"{source_name} result",
                "content": text
            })
        else:
            s = str(it)
            normalized.append({
                "title": (s[:60] + ("…" if len(s) > 60 else "")) or f"{source_name} result",
                "content": s
            })

    # Dispatch to specific renderers based on source type
    renderers = {
        "arxiv": render_arxiv_results,
        "web": render_web_results,
        "github": render_github_results,
        "substack": render_substack_results
    }

    renderer = renderers.get(source_name, render_generic_results)
    renderer(normalized)


def render_arxiv_results(results: list):
    """Render arXiv research results"""
    for item in results:
        with st.expander(item.get("title", "arXiv result")):
            st.markdown(item.get("summary") or item.get("content", ""))
            meta = []
            if item.get("authors"): meta.append(f"Authors: {', '.join(item.get('authors')) if isinstance(item.get('authors'), list) else item.get('authors')}")
            if item.get("published"): meta.append(f"Published: {item.get('published')}")
            if meta:
                st.caption(" • ".join(meta))
            if item.get("url"):
                st.markdown(f"[View paper]({item['url']})")


def render_web_results(results: list):
    """Render generic web search results"""
    for item in results:
        title = item.get("title") or (item.get("url") or "Web result")
        with st.expander(title):
            st.markdown(item.get("content", ""))
            if item.get("url"):
                st.markdown(f"[Open link]({item['url']})")


def render_github_results(results: list):
    """Render GitHub repository results"""
    for repo in results:
        title = repo.get("title", "Repository")
        with st.expander(title):
            desc = repo.get("content", "")
            if desc:
                st.markdown(desc)
            cols = st.columns(3)
            cols[0].metric("Stars", repo.get("stars", "N/A"))
            cols[1].metric("Lang", repo.get("language", ""))
            cols[2].caption(f"Updated: {repo.get('updated', '')}")
            if repo.get("topics"):
                st.caption("Topics: " + ", ".join(repo.get("topics", [])))
            if repo.get("url"):
                st.markdown(f"[Open repo]({repo['url']})")


def render_substack_results(results: list):
    """Render Substack posts"""
    for post in results:
        title = post.get("title", "Substack post")
        with st.expander(title):
            st.markdown(post.get("content", ""))
            meta = []
            if post.get("author"): meta.append(f"Author: {post.get('author')}")
            if post.get("published"): meta.append(f"Published: {post.get('published')}")
            if meta:
                st.caption(" • ".join(meta))
            if post.get("url"):
                st.markdown(f"[Read post]({post['url']})")


def render_generic_results(results: list):
    """Fallback renderer for unknown sources"""
    for item in results:
        if isinstance(item, str):
            title = (item[:60] + ("…" if len(item) > 60 else "")) or "Result"
            content = item
            url = None
        elif isinstance(item, dict):
            title = item.get("title", "Result")
            content = item.get("content", "")
            url = item.get("url")
        else:
            s = str(item)
            title = (s[:60] + ("…" if len(s) > 60 else "")) or "Result"
            content = s
            url = None

        with st.expander(title):
            st.markdown(content)
            if url:
                st.markdown(f"[Open link]({url})")