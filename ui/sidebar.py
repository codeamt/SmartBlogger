import streamlit as st
import os
import tempfile
from ui.components import pill_row, badges
from models.llm_manager import local_llm_manager
import streamlit_shadcn_ui as ui
try:
    from config import ModelConfig  # preferred
except Exception:  # fallback guard to prevent runtime crash
    class _ModelDefaults:
        LOCAL_WRITER_MODEL = "llama3.1:8b"
        LOCAL_RESEARCHER_MODEL = "llama3.1:8b"
    ModelConfig = _ModelDefaults()  # type: ignore


def render_sidebar() -> dict:
    """Render sidebar and return user inputs"""
    with st.sidebar:
        ICON_SVG = r"""
<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 64 64" role="img" aria-label="SmartBlogger">
  <circle cx="32" cy="32" r="30" fill="#64748B"/>
  <text x="26" y="38" text-anchor="end"
        font-family="Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto"
        font-size="22" font-weight="700" fill="#9CA3AF">S</text>
  <text x="38" y="38" text-anchor="start"
        font-family="Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto"
        font-size="22" font-weight="700" fill="#9CA3AF">B</text>
  <g transform="translate(32,32) rotate(-18)">
    <rect x="-1.3" y="-14" width="2.6" height="18" rx="1.3" fill="#9CA3AF"/>
    <polygon points="0,6 4.5,14 -4.5,14" fill="#9CA3AF"/>
    <circle cx="0" cy="9.7" r="0.9" fill="#0B0F14" opacity="0.7"/>
  </g>
</svg>
"""
        st.markdown(f"<div style='text-align:center; margin-bottom: 1rem;'>{ICON_SVG}</div>", unsafe_allow_html=True)

        with st.expander("Post Idea Feed From Notion", expanded=False):
            st.markdown("""
            <div style='padding: 0.75rem; border-radius: var(--radius); background: var(--bg-subtle); margin-bottom: 0.5rem;'>
                <h3 style='margin: 0 0 0.25rem 0;'>Configure Writing Direction</h3>
                <p style='color: var(--text-secondary); font-size: 0.9rem; margin: 0;'> Paste code, upload files, and configure Arxiv, Web, GitHub, and Substack nodes.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style='padding: 0.75rem; border-radius: var(--radius); background: var(--bg-subtle); margin-bottom: 0.5rem;'>
                <h3 style='margin: 0 0 0.25rem 0;'>Set Preferences and Models</h3>
                <p style='color: var(--text-secondary); font-size: 0.9rem; margin: 0;'> Adjust tone, audience, and writing style and select research/writer llms in sidebar.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style='padding: 0.75rem; border-radius: var(--radius); background: var(--bg-subtle);'>
                <h3 style='margin: 0 0 0.25rem 0;'>Generate Posts</h3>
                <p style='color: var(--text-secondary); font-size: 0.9rem; margin: 0;'>Click Generate Blog Post to create posts with plagiarism detection and originality analysis.</p>
            </div>
            """, unsafe_allow_html=True)

        user_inputs = {}

        # Research controls moved to main; read from session state
        user_inputs["research_sources"] = st.session_state.get("research_sources", ["Arxiv", "Web"])
        user_inputs["research_focus"] = st.session_state.get("research_focus", "")
        user_inputs["research_queries"] = [q.strip() for q in user_inputs["research_focus"].split(",") if q.strip()]
        user_inputs["github_urls"] = st.session_state.get("github_urls", [])
        user_inputs["substack_post_url"] = st.session_state.get("substack_post_url", "")
        user_inputs["substack_publications"] = st.session_state.get("substack_publications", [])
        user_inputs["web_sites"] = st.session_state.get("web_sites", [])
        user_inputs["web_urls"] = st.session_state.get("web_urls", [])
        user_inputs["arxiv_query"] = st.session_state.get("arxiv_query", "")

        # Bridge main panel state into user_inputs for backend
        user_inputs["code_input"] = st.session_state.get("code_input", "")
        user_inputs["file_paths"] = st.session_state.get("file_paths", [])
        user_inputs["tone"] = st.session_state.get("tone", "Professional")
        user_inputs["target_audience"] = st.session_state.get("target_audience", "Developers")
        user_inputs["writing_style"] = st.session_state.get("writing_style", ["Include code examples"]) or ["Include code examples"]
        user_inputs["custom_questions"] = st.session_state.get("custom_questions", [])

        # Model info
        # st.divider()
        # st.caption(f"Writer: {ModelConfig.LOCAL_WRITER_MODEL.split(':')[0]}  ·  "
        #           f"Researcher: {ModelConfig.LOCAL_RESEARCHER_MODEL.split(':')[0]}")

        # Generate button moved to main

        # Reset button with enhanced styling
        if st.session_state.get("generate_clicked"):
            st.markdown("<div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);'>", unsafe_allow_html=True)
            if st.button("Start Over", use_container_width=True, type="secondary"):
                from state_management import clear_session_state
                clear_session_state()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    return user_inputs


def _get_upload_dir():
    """Return a session-scoped upload directory path."""
    if "upload_dir" not in st.session_state:
        st.session_state["upload_dir"] = tempfile.mkdtemp(prefix="smartblogger_uploads_")
    return st.session_state["upload_dir"]


def process_uploaded_files(uploaded_files):
    """Process uploaded files and return file paths"""
    if not uploaded_files:
        return []

    file_paths = []
    with st.spinner("Processing uploads..."):
        upload_dir = _get_upload_dir()
        os.makedirs(upload_dir, exist_ok=True)
        for file in uploaded_files:
            path = os.path.join(upload_dir, file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            file_paths.append(path)

    return file_paths