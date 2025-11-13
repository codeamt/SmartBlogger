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
            # Show enhanced loading screen
            from ui.loading_screen import show_loading_screen
            show_loading_screen()
            # Execute workflow in background
            execute_workflow_with_status(user_inputs)
        else:
            # Show results
            render_results_tabs()
    else:
        # Show welcome screen
        render_welcome_screen()
    
    # Show footer on all pages
    from ui.footer import render_footer
    render_footer()


def render_results_tabs():
    """Render results using enhanced shadcn tabs with improved visual design."""
    # Enhanced header with back button and result summary
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Back", help="Return to welcome screen"):
            st.session_state.generate_clicked = False
            st.session_state.result = None
            st.rerun()
    with col2:
        # Show a quick summary of the generated content
        rs = st.session_state.result or {}
        title = rs.get("title", "Untitled Blog Post")
        st.markdown(f"<h3 style='margin: 0; padding: 0;'>{title}</h3>", unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Compute counts from result for tab labels
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
    token_label = f" ({token_total/1000:.1f}k tokens)" if token_total else ""

    # Build enhanced tab labels (no emojis)
    tab_blog = "Blog Content"
    tab_editor = "Editor"
    tab_research = f"Research ({research_total})" if research_total else "Research"
    tab_plag = (
        f"Plagiarism ({flagged_sections} flagged)" if flagged_sections else "Plagiarism"
    )
    tab_analytics = f"Analytics{token_label}"

    # Enhanced tabs using proper shadcn UI pattern
    options = [tab_blog, tab_editor, tab_research, tab_plag, tab_analytics]
    selected = ui.tabs(options=options, default_value=tab_blog, key="results_tabs")

    # Add content area styling
    st.markdown("""
    <div style='border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; background: var(--bg-surface); margin-top: 1rem;'>
    """, unsafe_allow_html=True)
    
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
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show footer on results page
    from ui.footer import render_footer
    render_footer()


def render_welcome_screen():
    """Render welcome screen with instructions"""
    
    # Content Input panel with improved layout
    with st.expander("Content Configuration Prompt", expanded=True):
        st.markdown("### Research Configuration")
         
        # Research sources with better explanation
        st.session_state.research_sources = st.multiselect(
            "Choose which sources to research from",
            ["Arxiv", "Web", "GitHub", "Substack"],
            default=st.session_state.get("research_sources", ["Arxiv", "Web"]),
            help="Select one or more sources for AI research. Each source provides different types of information.",
        )

        # Research focus with better placeholder and help
        st.session_state.research_focus = st.text_input(
            "Enter comma-separated topics to focus research on",
            value=st.session_state.get("research_focus", ""),
            placeholder="e.g., machine learning, python, API design, cloud computing",
            help="Specify topics to guide the AI research. Use commas to separate multiple topics.",
        )

        # Dynamic inputs by source
        selected_sources = set(st.session_state.get("research_sources", []))

        if "GitHub" in selected_sources:
            gh_prefill = "\n".join(st.session_state.get("github_urls", []))
            gh_text = st.text_area("GitHub URL(s)", value=gh_prefill, help="One URL per line (repo, file, or issue)", key="gh_urls_input")
            st.session_state.github_urls = [u.strip() for u in gh_text.splitlines() if u.strip()]
        if "Substack" in selected_sources:
            sub_post = st.text_input("Substack post URL (optional)", value=st.session_state.get("substack_post_url", ""), key="substack_post_url")
            sub_pubs_prefill = ", ".join(st.session_state.get("substack_publications", []))
            sub_pubs = st.text_input("Substack publication(s) (comma-separated, optional)", value=sub_pubs_prefill, key="substack_pubs_input")
            st.session_state.substack_publications = [p.strip() for p in sub_pubs.split(",") if p.strip()]
        if "Web" in selected_sources:
            web_sites_prefill = ", ".join(st.session_state.get("web_sites", []))
            web_sites = st.text_input("Target domain(s) (comma-separated, optional)", value=web_sites_prefill, key="web_sites_input")
            web_urls_prefill = "\n".join(st.session_state.get("web_urls", []))
            web_urls = st.text_area("Specific URL(s) (one per line, optional)", value=web_urls_prefill, key="web_urls_input")
            st.session_state.web_sites = [d.strip() for d in web_sites.split(",") if d.strip()]
            st.session_state.web_urls = [u.strip() for u in web_urls.splitlines() if u.strip()]
        if "Arxiv" in selected_sources:
            st.session_state.arxiv_query = st.text_input("arXiv query or IDs (optional)", value=st.session_state.get("arxiv_query", ""), key="arxiv_query_input")
    
        st.markdown("### Main Topic")
        # Paste area with better instructions
        st.session_state.code_input = st.text_area(
            "Paste your source code or text",
            value=st.session_state.get("code_input", ""),
                height=180,
                placeholder="Paste your code, documentation, or any text content here...",
                label_visibility="visible",
                help="Paste your source code, documentation, or any text content you want to use as a basis for your blog post."
            )

        # Custom Questions with improved UI
        st.markdown("##### Ask Specific Questions")
        st.markdown("Add questions you want the AI to address in your blog post:")
        if "custom_questions" not in st.session_state:
            st.session_state.custom_questions = []
        col1, col2 = st.columns([4, 1])
        with col1:
            new_q = st.text_input("Enter your question", placeholder="e.g., How does this compare to alternatives?", label_visibility="collapsed", key="main_new_question_input")
        with col2:
            if st.button("Add", key="main_add_question_btn", use_container_width=True):
                if new_q and new_q.strip():
                    st.session_state.custom_questions.append(new_q.strip())
                    st.rerun()
                
            if st.session_state.custom_questions:
                st.markdown("#### Added Questions:")
                for idx, q in enumerate(st.session_state.custom_questions):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"<div style='padding: 0.5rem; background: var(--bg-subtle); border-radius: var(--radius); margin: 0.25rem 0;'>{q}</div>", unsafe_allow_html=True)
                    with col2:
                        if st.button("Delete", key=f"main_del_q_{idx}", help="Remove this question"):
                            st.session_state.custom_questions.pop(idx)
                            st.rerun()
                
        # Uploads with clearer instructions
        st.markdown("### Upload Files")
        uploaded_files_main = st.file_uploader(
            "Upload documents (PDF, TXT, MD) or images (PNG, JPEG - processed with OCR)",
            accept_multiple_files=True,
            type=["pdf", "txt", "md", "png", "jpeg"],
            label_visibility="visible",
            key="main_uploader",
            help="Upload documents or images. Images will be processed with OCR to extract text."
        )

        if uploaded_files_main is not None:
            st.session_state.file_paths = process_uploaded_files(uploaded_files_main)
            # Show uploaded files count
            if st.session_state.get("file_paths"):
                st.success(f"{len(st.session_state.file_paths)} file(s) uploaded successfully")  
        
    # Writing Style with improved organization
    with st.expander("Writing Style & Preferences", expanded=False):
        st.markdown("##### Tone & Audience")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.tone = st.selectbox(
                "Tone",
                ["Professional", "Conversational", "Academic", "Tutorial", "Enthusiastic"],
                index=["Professional", "Conversational", "Academic", "Tutorial", "Enthusiastic"].index(st.session_state.get("tone", "Professional"))
            )
        with col2:
            st.session_state.target_audience = st.selectbox(
                "Target Audience",
                ["Developers", "Technical Leaders", "Beginners", "General Tech Audience", "Researchers"],
                index=["Developers", "Technical Leaders", "Beginners", "General Tech Audience", "Researchers"].index(st.session_state.get("target_audience", "Developers"))
            )
        
        st.markdown("##### Style Preferences")
        st.session_state.writing_style = st.multiselect(
            "Select writing style preferences",
            ["Include code examples", "Add diagrams/visuals", "Step-by-step guides", "Real-world examples", "Comparative analysis"],
            default=st.session_state.get("writing_style", ["Include code examples"]) or ["Include code examples"],
            help="Choose how you want your content to be structured and presented."
        )

    # Model Settings moved from sidebar
    with st.expander("Model Settings", expanded=True):
        ollama_up = local_llm_manager.is_ollama_up()
        current_writer = local_llm_manager.selected_writer_model or ModelConfig.LOCAL_WRITER_MODEL
        current_researcher = local_llm_manager.selected_researcher_model or ModelConfig.LOCAL_RESEARCHER_MODEL
        models_list = local_llm_manager.available_models or []
        writer_available = current_writer in models_list
        researcher_available = current_researcher in models_list

        st.markdown("#### Ollama Service Status")
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                status_label = "Running" if ollama_up else "Idle"
                status_color = "var(--success)" if ollama_up else "var(--warning)"
                st.markdown(
                    f"<div style='display: flex; align-items: center; gap: 8px;'>"
                    f"<div style='font-size: 1rem; color: var(--muted-foreground);'>Service Status:</div>"
                    f"<div style='font-weight: 600; color: {status_color};'>{status_label}</div>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
            with col2:
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
                if switch_value != ollama_up:
                    if switch_value:
                        with st.spinner("Starting Ollama service..."):
                            success = local_llm_manager.start_ollama()
                        if success:
                            st.success("Ollama service started successfully")
                            st.toast("Ollama service is now running")
                        else:
                            st.error("Failed to start Ollama service")
                            st.toast("Failed to start Ollama service")
                    else:
                        with st.spinner("Stopping Ollama service..."):
                            success = local_llm_manager.stop_ollama()
                        if success:
                            st.success("Ollama service stopped successfully")
                            st.toast("Ollama service has been stopped")
                        else:
                            st.error("Failed to stop Ollama service")
                            st.toast("Failed to stop Ollama service")
                    st.rerun()

        st.markdown("#### Model Selection")
        writer_status = "Available" if writer_available else "Not Installed"
        researcher_status = "Available" if researcher_available else "Not Installed"
        writer_status_color = "var(--success)" if writer_available else "var(--muted-foreground)"
        researcher_status_color = "var(--success)" if researcher_available else "var(--muted-foreground)"

        st.markdown("**Writer Model**")
        writer_col1, writer_col2 = st.columns([0.45, 0.55])
        with writer_col1:
            st.markdown(f"<div style='font-weight: 600; color: {writer_status_color}; font-size: 0.9rem; margin-top: 0.2rem;'>{writer_status}</div>", unsafe_allow_html=True)
        with writer_col2:
            writer_options = models_list if models_list else [current_writer]
            writer_index = writer_options.index(current_writer) if current_writer in writer_options else 0
            sb_writer = st.selectbox(
                "Select writer model",
                options=writer_options,
                index=writer_index,
                key="sb_writer_select",
                help="Select the model used for generating blog content"
            )

        st.markdown("**Researcher Model**")
        researcher_col1, researcher_col2 = st.columns([0.45, 0.55])
        with researcher_col1:
            st.markdown(f"<div style='font-weight: 600; color: {researcher_status_color}; font-size: 0.9rem; margin-top: 0.2rem;'>{researcher_status}</div>", unsafe_allow_html=True)
        with researcher_col2:
            researcher_options = models_list if models_list else [current_researcher]
            researcher_index = researcher_options.index(current_researcher) if current_researcher in researcher_options else 0
            sb_researcher = st.selectbox(
                "Select researcher model",
                options=researcher_options,
                index=researcher_index,
                key="sb_researcher_select",
                help="Select the model used for research and information gathering"
            )

        if sb_writer != current_writer or sb_researcher != current_researcher:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Apply Selected Models", key="sb_apply_models", type="primary", use_container_width=True, help="Apply the selected models for content generation and research"):
                with st.spinner("Updating model configuration..."):
                    local_llm_manager.set_default_models(writer=sb_writer, researcher=sb_researcher)
                st.success("Models updated successfully")
                st.toast("Model configuration updated")
                st.rerun()
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("Current model configuration is active")

        st.markdown("### Model Temperature Settings")
        writer_temp = st.slider("Writer Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, key="writer_temp")
        researcher_temp = st.slider("Researcher Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.1, key="researcher_temp")

        st.markdown("### Install/Remove Models")
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
        all_models = list(set(popular_models + models_list))
        all_models.sort()
        st.markdown("#### Select Model to Install or Remove")
        st.markdown(
            """
            <div style='font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;'>
            Choose from popular models optimized for your system or enter a custom model identifier.
            For Apple Silicon users, 8b models are recommended for best performance.
            </div>
            """,
            unsafe_allow_html=True,
        )
        model_selection_type = st.radio(
            "Model Selection Type",
            ["Popular Models", "Custom Model"],
            horizontal=True,
            key="model_selection_type",
            label_visibility="visible",
            help="Choose between popular pre-selected models or enter a custom model identifier",
        )
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        if model_selection_type == "Popular Models":
            st.markdown("**Select from popular models:**")
            target_model = ui.select(options=all_models, key="model_dropdown_select")
        else:
            st.markdown("**Enter custom model identifier:**")
            target_model = st.text_input(
                "Custom model identifier",
                value="",
                placeholder="e.g., llama3.1:8b, mistral:7b",
                key="model_custom_input",
                help="Enter a model identifier in the format 'model_name:version' (e.g., llama3.1:8b)",
            )
        mg1, mg2 = st.columns(2)
        with mg1:
            if st.button("Install Model", key="sb_pull_model", use_container_width=True, type="primary", help="Download and install the selected model"):
                if not target_model:
                    st.warning("Please select or enter a model identifier")
                    st.toast("Please select a model to install")
                elif not local_llm_manager.is_ollama_up():
                    st.warning("Ollama service is not running. Please start Ollama first.")
                    st.toast("Ollama service is not running")
                else:
                    with st.spinner(f"Installing {target_model}... This may take several minutes."):
                        ok = local_llm_manager.pull_model(target_model)
                    if ok:
                        st.success(f"Model {target_model} installed successfully")
                        st.toast(f"Model {target_model} installed")
                        local_llm_manager.available_models = local_llm_manager._get_available_models()
                        st.rerun()
                    else:
                        st.error(f"Failed to install model {target_model}")
                        st.toast(f"Failed to install {target_model}")
        with mg2:
            if st.button("Remove Model", key="sb_remove_model", use_container_width=True, type="secondary", help="Remove the selected model from your system"):
                if not target_model:
                    st.warning("Please select or enter a model identifier")
                    st.toast("Please select a model to remove")
                elif not local_llm_manager.is_ollama_up():
                    st.warning("Ollama service is not running. Please start Ollama first.")
                    st.toast("Ollama service is not running")
                else:
                    with st.spinner(f"Removing {target_model}..."):
                        ok = local_llm_manager.delete_model(target_model)
                    if ok:
                        st.success(f"Model {target_model} removed successfully")
                        st.toast(f"Model {target_model} removed")
                        local_llm_manager.available_models = local_llm_manager._get_available_models()
                        st.rerun()
                    else:
                        st.error(f"Failed to remove model {target_model}")
                        st.toast(f"Failed to remove {target_model}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh Model List", key="sb_refresh_models", use_container_width=True, help="Refresh the list of installed models"):
            with st.spinner("Refreshing model list..."):
                local_llm_manager.available_models = local_llm_manager._get_available_models()
            st.success("Model list refreshed successfully")
            st.toast("Model list updated")
            st.rerun()
        if models_list:
            st.markdown("#### Installed Models")
            with st.container():
                st.markdown(
                    "<div style='max-height: 250px; overflow-y: auto; border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem; background: var(--bg-subtle);'>",
                    unsafe_allow_html=True,
                )
                for model in models_list:
                    st.markdown(
                        f"<div style='padding: 0.5rem; background: var(--bg-card); border-radius: var(--radius); margin: 0.25rem 0; font-family: monospace; display: flex; align-items: center;'>"
                        f"<span>{model}</span></div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No models installed yet. Install a model to get started.")

    # Research configuration and Generate with improved UI
    # Generate button with improved styling and validation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_help = "Generate a blog post based on your content and research configuration"
        if st.button("Generate Blog Post", type="primary", use_container_width=True, key="main_generate_btn", help=generate_help):
            if not st.session_state.get("code_input") and not st.session_state.get("file_paths"):
                st.warning("Please provide source code or upload documents to generate content from")
                st.toast("Please provide content to generate from")
            else:
                st.session_state.generate_clicked = True
                st.rerun()
    with col2:
        if st.button("Reset", use_container_width=True, key="main_reset_btn", help="Clear all inputs and start over"):
            st.session_state.code_input = ""
            st.session_state.file_paths = []
            st.session_state.research_focus = ""
            st.session_state.custom_questions = []
            st.rerun()
