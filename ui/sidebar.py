import streamlit as st
import os
import tempfile


def render_sidebar() -> dict:
    """Render sidebar and return user inputs"""
    with st.sidebar:
        st.header("📝 Input Options")

        user_inputs = {}

        # Research sources
        user_inputs["research_sources"] = st.multiselect(
            "Research Sources",
            ["Arxiv", "Web", "GitHub", "Substack"],
            default=["Arxiv", "Web"]
        )

        # Code input
        user_inputs["code_input"] = st.text_area(
            "Paste source code",
            height=200,
            placeholder="// Paste your code here..."
        )

        # Document upload
        uploaded_files = st.file_uploader(
            "Upload files",
            accept_multiple_files=True,
            type=["pdf", "txt", "md", "png", "jpeg"]
        )
        user_inputs["uploaded_files"] = uploaded_files
        user_inputs["file_paths"] = process_uploaded_files(uploaded_files)

        # Research focus
        user_inputs["research_focus"] = st.text_input(
            "Research Focus",
            "best practices, technical documentation",
            placeholder="comma-separated topics"
        )
        user_inputs["research_queries"] = [
            q.strip() for q in user_inputs["research_focus"].split(",")
        ]

        # Model info
        st.divider()
        from config import ModelConfig
        st.caption(f"🤖 Writer: {ModelConfig.LOCAL_WRITER_MODEL}")
        st.caption(f"🔬 Researcher: {ModelConfig.LOCAL_RESEARCHER_MODEL}")

        # Generate button
        if st.button("🚀 Generate Blog Post", type="primary", use_container_width=True):
            if not user_inputs["code_input"] and not user_inputs["file_paths"]:
                st.error("❌ Please provide source code or upload documents")
            else:
                st.session_state.generate_clicked = True
                st.rerun()

        # Reset button
        if st.session_state.get("generate_clicked"):
            if st.button("🔄 Reset", use_container_width=True):
                from state_management import clear_session_state
                clear_session_state()
                st.rerun()

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