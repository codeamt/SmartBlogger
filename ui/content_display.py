import streamlit as st


def render_blog_content(result_state: dict):
    """Render generated blog content"""
    st.header("Generated Blog Content")

    if not result_state.get("section_drafts"):
        st.info("No content generated yet.")
        return

    sections = result_state.get("sections", [])
    section_drafts = result_state.get("section_drafts", {})

    if not sections:
        # Fallback: display all drafts
        render_fallback_content(section_drafts)
        return

    # Display sections in order
    for section in sections:
        render_section(section, section_drafts, result_state)


def render_section(section: dict, section_drafts: dict, result_state: dict):
    """Render a single section with revisions"""
    section_id = section["id"]
    content = section_drafts.get(section_id, "")

    if not content:
        return

    with st.expander(f"### {section['title']}", expanded=True):
        st.markdown(content)
        render_revision_history(section_id, result_state)


def render_revision_history(section_id: str, result_state: dict):
    """Render revision history for a section"""
    revision_history = result_state.get("revision_history", {}).get(section_id, [])
    if revision_history:
        with st.expander(f"📝 Revision History ({len(revision_history)} versions)", expanded=False):
            for i, revision in enumerate(revision_history):
                st.caption(f"**Version {i + 1}:**")
                st.markdown(revision[:500] + "..." if len(revision) > 500 else revision)
                if i < len(revision_history) - 1:
                    st.divider()


def render_fallback_content(section_drafts: dict):
    """Fallback content display when no section structure exists"""
    st.warning("No sections structure found. Displaying all content:")
    for section_id, content in section_drafts.items():
        with st.expander(f"Section {section_id}"):
            st.markdown(content)