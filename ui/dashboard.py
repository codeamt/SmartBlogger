import streamlit as st
from ui.content_display import render_blog_content
from ui.research_display import render_research_details
from ui.plagiarism_display import render_plagiarism_report
from ui.analytics_display import render_analytics
from ui.editor_display import render_editor
from workflow_runner import execute_workflow_with_status
# from state_management import get_initial_state
from models.llm_manager import local_llm_manager
from config import ModelConfig
from ui.components import section_header, card, panel, status_pills, icon_button, list_row
from ui.sidebar import process_uploaded_files
import streamlit_shadcn_ui as ui


def render_main_content(user_inputs: dict):
    """Render the main content area based on application state"""
    if st.session_state.get("generate_clicked"):
        if st.session_state.result is None:
            # Show generation in progress
            execute_workflow_with_status(user_inputs)
        else:
            # Show results
            render_results_tabs()
    else:
        # Show welcome screen
        render_welcome_screen()


def render_results_tabs():
    """Render results using shadcn tabs (emoji-free, with counts)."""
    # Back to Welcome
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("Back to Welcome", help="Return to welcome screen"):
            st.session_state.generate_clicked = False
            st.session_state.result = None
            st.rerun()

    # Compute counts from result
    rs = st.session_state.result or {}
    research_ctx = (rs.get("research_context") or {})
    by_source = research_ctx.get("by_source", {}) if isinstance(research_ctx, dict) else {}
    research_total = 0
    for v in by_source.values():
        if isinstance(v, list):
            research_total += len(v)
        elif v:
            research_total += 1

    plagiarism_checks = rs.get("plagiarism_checks", {}) or {}
    flagged_sections = 0
    for _sid, checks in plagiarism_checks.items():
        api_score = (checks.get("api", {}) or {}).get("score")
        ai_score = (checks.get("ai", {}) or {}).get("risk_score")
        if (isinstance(api_score, (int, float)) and api_score > 15) or (
            isinstance(ai_score, (int, float)) and ai_score > 70
        ):
            flagged_sections += 1

    token_usage = rs.get("token_usage", {}) or {}
    token_total = sum(token_usage.values()) if isinstance(token_usage, dict) else 0
    token_label = f" ({token_total/1000:.1f}k)" if token_total else ""

    # Build labels
    tab_blog = "Blog Content"
    tab_editor = "Editor"
    tab_research = f"Research ({research_total})" if research_total else "Research"
    tab_plag = (
        f"Plagiarism ({flagged_sections} flagged)" if flagged_sections else "Plagiarism"
    )
    tab_analytics = f"Analytics{token_label}"

    options = [tab_blog, tab_editor, tab_research, tab_plag, tab_analytics]
    selected = ui.tabs(options=options, default_value=tab_blog, key="results_tabs")

    if selected == tab_blog:
        render_blog_content(st.session_state.result)
    elif selected == tab_editor:
        render_editor(st.session_state.result)
    elif selected == tab_research:
        render_research_details(st.session_state.result)
    elif selected == tab_plag:
        render_plagiarism_report(st.session_state.result)
    elif selected == tab_analytics:
        render_analytics(st.session_state.result)


def render_welcome_screen():
    """Render welcome screen with instructions"""
    
    # Hero section in a panel matching collapsible header surface
    with panel():
        st.markdown("# Welcome to SmartBlogger")
        st.markdown(
            "Transform your ideas into polished technical content with AI-powered research, "
            "intelligent writing assistance, and built-in originality protection."
        )
    
    # Getting Started moved to sidebar; keep hero compact
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Content Input panel (moved from sidebar)
    with panel():
        st.markdown("### Content Input")
        # Paste area
        st.session_state.code_input = st.text_area(
            "Paste your source code or text",
            value=st.session_state.get("code_input", ""),
            height=180,
            placeholder="Paste code or text...",
            label_visibility="collapsed"
        )
        # Uploads
        uploaded_files_main = st.file_uploader(
            "Upload files",
            accept_multiple_files=True,
            type=["pdf", "txt", "md", "png", "jpeg"],
            label_visibility="collapsed",
            key="main_uploader"
        )
        if uploaded_files_main is not None:
            st.session_state.file_paths = process_uploaded_files(uploaded_files_main)
        # Writing Style (collapsed)
        with st.expander("Writing Style", expanded=False):
            st.session_state.tone = st.selectbox(
                "Tone",
                ["Professional", "Conversational", "Academic", "Tutorial", "Enthusiastic"],
                index=["Professional", "Conversational", "Academic", "Tutorial", "Enthusiastic"].index(st.session_state.get("tone", "Professional"))
            )
            st.session_state.target_audience = st.selectbox(
                "Target Audience",
                ["Developers", "Technical Leaders", "Beginners", "General Tech Audience", "Researchers"],
                index=["Developers", "Technical Leaders", "Beginners", "General Tech Audience", "Researchers"].index(st.session_state.get("target_audience", "Developers"))
            )
            st.session_state.writing_style = st.multiselect(
                "Style Preferences",
                ["Include code examples", "Add diagrams/visuals", "Step-by-step guides", "Real-world examples", "Comparative analysis"],
                default=st.session_state.get("writing_style", ["Include code examples"]) or ["Include code examples"]
            )
        # Custom Questions (collapsed)
        with st.expander("Custom Questions", expanded=False):
            if "custom_questions" not in st.session_state:
                st.session_state.custom_questions = []
            new_q = st.text_input("Add a question", placeholder="e.g., How does this compare to alternatives?", key="main_new_question_input")
            if st.button("Add Question", key="main_add_question_btn"):
                if new_q and new_q.strip():
                    st.session_state.custom_questions.append(new_q.strip())
                    st.rerun()
            if st.session_state.custom_questions:
                for idx, q in enumerate(st.session_state.custom_questions):
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.text(f"{idx+1}. {q}")
                    with col2:
                        if st.button("Delete", key=f"main_del_q_{idx}"):
                            st.session_state.custom_questions.pop(idx)
                            st.rerun()

    # Research configuration and Generate
    with panel():
        st.markdown("### Research")
        st.session_state.research_sources = st.multiselect(
            "Select sources",
            ["Arxiv", "Web", "GitHub", "Substack"],
            default=st.session_state.get("research_sources", ["Arxiv", "Web"]),
            label_visibility="collapsed",
            key="main_research_sources"
        )
        st.session_state.research_focus = st.text_input(
            "Topics",
            value=st.session_state.get("research_focus", ""),
            placeholder="e.g., machine learning, python",
            label_visibility="collapsed",
            key="main_research_focus"
        )
        if st.button("Generate Blog Post", type="primary", width='stretch', key="main_generate_btn"):
            if not st.session_state.get("code_input") and not st.session_state.get("file_paths"):
                st.error("Please provide source code or upload documents")
            else:
                st.session_state.generate_clicked = True
                st.rerun()