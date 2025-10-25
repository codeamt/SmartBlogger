import streamlit as st


def render_blog_content(result_state: dict):
    """Render generated blog content"""
    st.header("Generated Blog Content")

    if not result_state.get("section_drafts"):
        st.info("No content generated yet.")
        return

    # Check if we have a final assembled blog post
    completion_summary = result_state.get("research_context", {}).get("completion_summary", {})
    final_content = completion_summary.get("final_content")
    
    if final_content:
        # Metrics row
        sections = result_state.get("sections", [])
        total_sections = len(sections)
        total_words = len(final_content.split())
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Sections", total_sections)
        col2.metric("Total Words", f"{total_words:,}")
        col3.metric("Status", "✅ Complete")
        
        st.divider()
        
        # Info box directing to editor
        st.info("💡 **Tip**: Use the **✏️ Editor** tab to preview and edit the complete blog post!")
        
        # Download button prominently at top
        st.download_button(
            label="📥 Download Complete Blog Post",
            data=final_content,
            file_name="blog_post.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True
        )
        
        st.divider()
        
        # Individual sections in collapsible expanders
        st.subheader("📑 Sections Breakdown")
        st.caption("Review individual sections below. For full preview and editing, use the Editor tab.")
        
        section_drafts = result_state.get("section_drafts", {})
        for idx, section in enumerate(sections, 1):
            render_section_compact(idx, section, section_drafts, result_state)
    else:
        # Fallback to section-by-section display
        sections = result_state.get("sections", [])
        section_drafts = result_state.get("section_drafts", {})

        if not sections:
            render_fallback_content(section_drafts)
            return

        st.subheader("📑 Generated Sections")
        for idx, section in enumerate(sections, 1):
            render_section_compact(idx, section, section_drafts, result_state)


def render_section_compact(idx: int, section: dict, section_drafts: dict, result_state: dict):
    """Render a single section in compact expander format"""
    section_id = section["id"]
    content = section_drafts.get(section_id, "")

    if not content:
        return

    # Calculate word count for this section
    word_count = len(content.split())
    title = section.get('title', f'Section {idx}')
    description = section.get('description', '')
    
    # Expander label with metadata
    label = f"**{idx}. {title}** • {word_count} words"
    
    with st.expander(label, expanded=False):
        if description:
            st.caption(f"_{description}_")
            st.divider()
        st.markdown(content)
        render_revision_history(section_id, result_state)


def render_section(section: dict, section_drafts: dict, result_state: dict):
    """Legacy render for backward compatibility"""
    section_id = section["id"]
    content = section_drafts.get(section_id, "")

    if not content:
        return

    with st.expander(f"{section['title']}", expanded=False):
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