import streamlit as st
from ui.components import section_header, panel


def render_blog_content(result_state: dict):
    """Render generated blog content with elegant design"""
    
    if not result_state.get("section_drafts"):
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <h2 style="color: #6B6B6B; font-weight: 400;">No content generated yet</h2>
            <p style="color: #8B8B8B; font-size: 1.125rem; margin-top: 1rem;">
                Configure your inputs in the sidebar and generate your first blog post.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Check if we have a final assembled blog post
    completion_summary = result_state.get("research_context", {}).get("completion_summary", {})
    final_content = completion_summary.get("final_content")
    
    if final_content:
        # Header
        section_header("Your Blog Post", icon="📝", subtitle="Review and refine your generated content")
        
        # Metrics in a neutral dark panel
        sections = result_state.get("sections", [])
        total_sections = len(sections)
        total_words = len(final_content.split())

        st.markdown(
            f"""
        <div style="display:flex; gap:1.5rem; padding:1rem; background: var(--bg-subtle); border:1px solid var(--border); border-radius: 10px; margin-bottom:1rem; color: var(--text-primary);">
            <div>
                <div style="font-size:0.8rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">Sections</div>
                <div style="font-size:1.5rem; font-weight:650;">{total_sections}</div>
            </div>
            <div>
                <div style="font-size:0.8rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">Total Words</div>
                <div style="font-size:1.5rem; font-weight:650;">{total_words:,}</div>
            </div>
            <div>
                <div style="font-size:0.8rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">Status</div>
                <div style="font-size:1.5rem; font-weight:650; color: #10B981;">✓ Complete</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Call to action (legible on dark)
        st.markdown(
            """
        <div style="background: var(--bg-subtle); padding: 1rem; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 1rem;">
            <span style="color: var(--text-primary); font-size: 0.98rem;">
                <strong>💡 Pro Tip:</strong> Head to the <strong>✏️ Editor</strong> tab for a distraction-free
                writing experience with live preview and export options.
            </span>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Download button
        st.download_button(
            label="⬇ Download Complete Blog Post",
            data=final_content,
            file_name="blog_post.md",
            mime="text/markdown",
            type="primary",
            width='stretch'
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Individual sections in collapsible expanders
        st.markdown("**Section Breakdown**")
        st.caption("Review individual sections below")
        
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

        # Plagiarism feedback & quick rewrites
        plagiarism = (result_state.get("plagiarism_checks", {}) or {}).get(section_id, {})
        ai = plagiarism.get("ai", {}) if plagiarism else {}
        flagged = ai.get("flagged_phrases") or []
        recs = ai.get("recommendations") or []
        risk = ai.get("risk_score")

        if flagged or recs or risk is not None:
            with panel(subtle_title="Plagiarism feedback"):
                cols = st.columns(3)
                with cols[0]:
                    st.metric("AI Risk", f"{risk:.1f}" if isinstance(risk, (int, float)) else "-")
                with cols[1]:
                    st.metric("Flagged", len(flagged))
                with cols[2]:
                    st.metric("Suggestions", len(recs))

                if flagged:
                    st.caption("Flagged phrases and quick fixes:")
                    for i, phrase in enumerate(flagged[:10]):
                        suggestion = recs[i] if i < len(recs) else None
                        row = st.columns([4, 3, 1])
                        with row[0]:
                            st.code(phrase)
                        with row[1]:
                            st.text(suggestion or "—")
                        with row[2]:
                            if suggestion and phrase in content:
                                if st.button("Replace", key=f"rw_{section_id}_{i}"):
                                    # Update the section text in session state result
                                    try:
                                        new_text = content.replace(phrase, suggestion)
                                        st.session_state.result["section_drafts"][section_id] = new_text
                                        st.success("Applied")
                                        st.rerun()
                                    except Exception:
                                        st.warning("Could not apply rewrite")


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