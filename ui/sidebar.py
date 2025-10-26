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

        with st.expander("Getting Started", expanded=False):
            st.markdown(
                "- Add your content — paste code or upload PDF/TXT/MD\n"
                "- Choose research sources — ArXiv, Web, GitHub, Substack\n"
                "- Define research focus — comma-separated topics\n"
                "- Click Generate"
            )
        
        
        user_inputs = {}

        # Model Studio (playground-style controls)
        with st.expander("Model Settings", expanded=True):
            # State probes
            ollama_up = local_llm_manager.is_ollama_up()
            current_writer = local_llm_manager.selected_writer_model or ModelConfig.LOCAL_WRITER_MODEL
            current_researcher = local_llm_manager.selected_researcher_model or ModelConfig.LOCAL_RESEARCHER_MODEL
            models_list = local_llm_manager.available_models or []
            writer_available = current_writer in models_list
            researcher_available = current_researcher in models_list
            has_pplx = bool(getattr(local_llm_manager, "perplexity_api_key", None))

            # Ollama Service with inline switch
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    status_label = "Running" if ollama_up else "Stopped"
                    status_color = "var(--success)" if ollama_up else "var(--destructive)"  # Use theme variables
                    st.markdown(
                        f"<div style='display: flex; align-items: center; gap: 8px;'>"
                        f"<div style='font-size: 1rem; color: var(--muted-foreground);'>Ollama Service:</div>"
                        f"<div style='font-weight: 600; color: {status_color};'>{status_label}</div>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                with col2:
                    # Simple switch for Ollama service
                    # Add custom styling to match theme
                    st.markdown(
                        "<style>"
                        ".shadcn-ui-switch { background: var(--secondary) !important; border: 1px solid var(--border) !important; }"
                        ".shadcn-ui-switch[data-state='checked'] { background: var(--primary) !important; }"
                        ".shadcn-ui-switch-thumb { background: var(--primary-foreground) !important; }"
                        ".shadcn-ui-switch[data-state='checked'] .shadcn-ui-switch-thumb { background: var(--primary-foreground) !important; }"
                        "</style>", 
                        unsafe_allow_html=True
                    )
                    switch_value = ui.switch(default_checked=ollama_up, label="", key="ollama_switch")
                    # Handle switch toggle
                    if switch_value != ollama_up:
                        if switch_value:  # Turn on
                            with st.spinner("Starting Ollama..."):
                                success = local_llm_manager.start_ollama()
                            if success:
                                st.success("Ollama started")
                            else:
                                st.error("Failed to start")
                        else:  # Turn off
                            with st.spinner("Stopping Ollama..."):
                                success = local_llm_manager.stop_ollama()
                            if success:
                                st.success("Ollama stopped")
                            else:
                                st.error("Failed to stop")
                        st.rerun()

            # Model Selection with improved layout
            
            
            # Writer model selection
            writer_col1, writer_col2 = st.columns([0.40, 0.60])
            # Model status summary under Ollama Service
            writer_status = "Available" if writer_available else "Not Installed"
            researcher_status = "Available" if researcher_available else "Not Installed"
            
            writer_status_color = "var(--success)" if writer_available else "var(--destructive)"
            researcher_status_color = "var(--success)" if researcher_available else "var(--destructive)"
            with writer_col1:
                st.markdown("**Writer:**")
                st.markdown("<div style='font-weight: 600; color: {writer_status_color}; font-size: 0.8rem; margin-top: 0.2rem;'>{writer_status}</div>", unsafe_allow_html=True)
            with writer_col2:
                writer_options = models_list if models_list else [current_writer]
                writer_index = writer_options.index(current_writer) if current_writer in writer_options else 0
                sb_writer = st.selectbox(
                    "Select writer model",
                    options=writer_options,
                    index=writer_index,
                    key="sb_writer_select",
                    label_visibility="collapsed"
                )
            
            # Researcher model selection
            researcher_col1, researcher_col2 = st.columns([0.40, 0.60])
            with researcher_col1:
                st.markdown("**Researcher:**")
                st.markdown("<div style='font-weight: 600; color: {researcher_status_color}; font-size: 0.8rem; margin-top: 0.2rem;'>{researcher_status}</div>", unsafe_allow_html=True)
            with researcher_col2:
                researcher_options = models_list if models_list else [current_researcher]
                researcher_index = researcher_options.index(current_researcher) if current_researcher in researcher_options else 0
                sb_researcher = st.selectbox(
                    "Select researcher model",
                    options=researcher_options,
                    index=researcher_index,
                    key="sb_researcher_select",
                    label_visibility="collapsed"
                )
            
            # Apply button with better styling
            if sb_writer != current_writer or sb_researcher != current_researcher:
                if st.button("Apply Selected Models", key="sb_apply_models", type="primary", use_container_width=True):
                    local_llm_manager.set_default_models(writer=sb_writer, researcher=sb_researcher)
                    st.success("Models updated successfully")
                    st.rerun()

            # Temperature Controls (playground controls style)
            with st.expander("Temperature Controls", expanded=False):
                st.markdown("### Model Temperature Settings")
                writer_temp = st.slider("Writer Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, key="writer_temp")
                researcher_temp = st.slider("Researcher Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.1, key="researcher_temp")
            
            # Model Management (playground controls style)
            with st.expander("Model Management", expanded=False):
                st.markdown("### Install/Remove Models")
                
                # Popular models suitable for Mac M2 Ultra 64GB
                popular_models = [
                    "llama3.1:8b",
                    "llama3.1:70b",
                    "llama3:8b",
                    "llama3:70b",
                    "mistral:7b",
                    "mixtral:8x7b",
                    "mixtral:8x22b",
                    "codellama:7b",
                    "codellama:34b",
                    "codellama:70b",
                    "phi3:3.8b",
                    "phi3:14b",
                    "gemma2:9b",
                    "gemma2:27b",
                    "qwen2:7b",
                    "qwen2:72b",
                    "dolphin-llama3:8b",
                    "dolphin-mistral:7b",
                    "deepseek-coder:6.7b",
                    "deepseek-coder:33b",
                    "command-r:35b",
                    "command-r-plus:104b"
                ]
                
                # Combine with already installed models to avoid duplicates
                all_models = list(set(popular_models + models_list))
                all_models.sort()
                
                # Dropdown for model selection with custom input option
                st.markdown("**Select from popular models or enter custom model:**")
                model_selection_type = st.radio("Model Selection", ["Popular Models", "Custom Model"], horizontal=True, key="model_selection_type", label_visibility="collapsed")
                
                # Add some spacing after the radio buttons
                st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                
                if model_selection_type == "Popular Models":
                    # Use shadcn UI select component
                    # Note: The select component has limited parameter support
                    # It will automatically scroll when there are many options
                    target_model = ui.select(
                        options=all_models,
                        key="model_dropdown_select"
                    )
                else:
                    target_model = st.text_input(
                        "Custom model identifier", 
                        value="", 
                        placeholder="e.g., llama3.1:8b, mistral:7b", 
                        key="model_custom_input",
                        label_visibility="collapsed"
                    )
                
                mg1, mg2 = st.columns(2)
                with mg1:
                    if st.button("Pull Model", key="sb_pull_model", use_container_width=True, type="secondary"):
                        if not target_model:
                            st.warning("Please select or enter a model identifier")
                        elif not local_llm_manager.is_ollama_up():
                            st.error("Ollama service is not running")
                        else:
                            with st.spinner(f"Pulling {target_model}... This may take several minutes."):
                                ok = local_llm_manager.pull_model(target_model)
                            if ok:
                                st.success(f"Model {target_model} installed successfully")
                                local_llm_manager.available_models = local_llm_manager._get_available_models()
                                st.rerun()
                            else:
                                st.error(f"Failed to pull model {target_model}")
                with mg2:
                    if st.button("Remove Model", key="sb_remove_model", use_container_width=True, type="secondary"):
                        if not target_model:
                            st.warning("Please select or enter a model identifier")
                        elif not local_llm_manager.is_ollama_up():
                            st.error("Ollama service is not running")
                        else:
                            with st.spinner(f"Removing {target_model}..."):
                                ok = local_llm_manager.delete_model(target_model)
                            if ok:
                                st.success(f"Model {target_model} removed successfully")
                                local_llm_manager.available_models = local_llm_manager._get_available_models()
                                st.rerun()
                            else:
                                st.error(f"Failed to remove model {target_model}")
                
                # Refresh models button
                if st.button("🔄 Refresh Model List", key="sb_refresh_models", use_container_width=True):
                    with st.spinner("Refreshing models..."):
                        local_llm_manager.available_models = local_llm_manager._get_available_models()
                    st.success("Model list refreshed")
                    st.rerun()

                # Display available models
                if models_list:
                    st.markdown("**Installed Models**")
                    # Create a scrollable container for the model list
                    with st.container():
                        st.markdown(
                            "<div style='max-height: 200px; overflow-y: auto; border: 1px solid var(--border); border-radius: 6px; padding: 0.5rem;'>", 
                            unsafe_allow_html=True
                        )
                        for model in models_list:
                            st.markdown(f"<div style='padding: 0.25rem 0.5rem; background: var(--bg-card); border-radius: 6px; margin: 0.25rem 0; font-family: monospace;'>{model}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

        # Research controls moved to main; read from session state
        user_inputs["research_sources"] = st.session_state.get("research_sources", ["Arxiv", "Web"])
        user_inputs["research_focus"] = st.session_state.get("research_focus", "")
        user_inputs["research_queries"] = [q.strip() for q in user_inputs["research_focus"].split(",") if q.strip()]

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