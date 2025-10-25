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
    """Render results in organized tabs"""
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Blog Content",
        "✏️ Editor",
        "🔍 Research Details",
        "⚖️ Plagiarism Report",
        "📊 Analytics"
    ])

    with tab1:
        render_blog_content(st.session_state.result)

    with tab2:
        render_editor(st.session_state.result)

    with tab3:
        render_research_details(st.session_state.result)

    with tab4:
        render_plagiarism_report(st.session_state.result)

    with tab5:
        render_analytics(st.session_state.result)


def render_welcome_screen():
    """Render welcome screen with instructions"""
    st.markdown("""
    ## Welcome to the Research-Powered Blog Assistant! 🎉

    This tool helps you create technical blog posts with:

    - **🤖 AI-Powered Writing** - Generate content using local LLMs
    - **🔍 Integrated Research** - Automatically research your topic
    - **⚖️ Plagiarism Protection** - Check and rewrite content
    - **📚 Multiple Sources** - Arxiv, GitHub, web search, and more

    ### Getting Started:
    1. **Paste source code** or **upload documents** (PDF, TXT, MD)
    2. **Select research sources** you want to use
    3. **Set research focus** (comma-separated topics)
    4. Click **"Generate Blog Post"** and watch the magic happen!

    ### Example Research Focus:
    - `machine learning, python, best practices`
    - `web development, react, performance optimization` 
    - `data science, pandas, visualization techniques`
    """)

    with st.expander("⚙️ LLM Health & Controls", expanded=False):
        ollama_up = local_llm_manager.is_ollama_up()
        current_writer = local_llm_manager.selected_writer_model or ModelConfig.LOCAL_WRITER_MODEL
        current_researcher = local_llm_manager.selected_researcher_model or ModelConfig.LOCAL_RESEARCHER_MODEL
        models_list = local_llm_manager.available_models or []
        writer_available = current_writer in models_list
        researcher_available = current_researcher in models_list

        # Status Overview
        st.subheader("📊 System Status")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_icon = "🟢" if ollama_up else "🔴"
            st.metric("Ollama", f"{status_icon} {'Running' if ollama_up else 'Stopped'}")
        with col2:
            writer_icon = "✅" if writer_available else "⚠️"
            st.metric("Writer", f"{writer_icon} {current_writer.split(':')[0]}")
        with col3:
            researcher_icon = "✅" if researcher_available else "⚠️"
            st.metric("Researcher", f"{researcher_icon} {current_researcher.split(':')[0]}")
        with col4:
            has_pplx = bool(getattr(local_llm_manager, "perplexity_api_key", None))
            api_icon = "✅" if has_pplx else "❌"
            st.metric("Perplexity API", f"{api_icon} {'Active' if has_pplx else 'Missing'}")
        
        if not has_pplx:
            st.caption("💡 Add PERPLEXITY_API_KEY to .env for enhanced research capabilities")

        st.divider()

        # Ollama Controls
        st.subheader("🔧 Ollama Controls")
        col1, col2 = st.columns(2)
        with col1:
            if ollama_up:
                if st.button("⏹️ Stop Ollama", use_container_width=True, type="secondary"):
                    ok = local_llm_manager.stop_ollama()
                    if ok:
                        st.success("✅ Ollama stopped")
                    else:
                        st.error("❌ Failed to stop Ollama")
                    st.rerun()
            else:
                if st.button("▶️ Start Ollama", use_container_width=True, type="primary"):
                    ok = local_llm_manager.start_ollama()
                    if ok:
                        st.success("✅ Ollama started")
                    else:
                        st.error("❌ Failed to start Ollama")
                    st.rerun()
        with col2:
            if st.button("🔄 Refresh Models", use_container_width=True):
                local_llm_manager.available_models = local_llm_manager._get_available_models()
                st.success("✅ Models refreshed")
                st.rerun()

        st.divider()

        # Model Selection
        st.subheader("🎯 Model Selection")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Writer Model**")
            selected_writer = st.selectbox(
                "Choose writer model",
                options=models_list if models_list else [current_writer],
                index=models_list.index(current_writer) if current_writer in models_list else 0,
                key="writer_select",
                label_visibility="collapsed"
            )
            if not writer_available:
                st.warning(f"⚠️ {current_writer} not installed")
        
        with col2:
            st.write("**Researcher Model**")
            selected_researcher = st.selectbox(
                "Choose researcher model",
                options=models_list if models_list else [current_researcher],
                index=models_list.index(current_researcher) if current_researcher in models_list else 0,
                key="researcher_select",
                label_visibility="collapsed"
            )
            if not researcher_available:
                st.warning(f"⚠️ {current_researcher} not installed")
        
        # Apply button
        if selected_writer != current_writer or selected_researcher != current_researcher:
            if st.button("✅ Apply Selected Models", use_container_width=True, type="primary"):
                local_llm_manager.set_default_models(writer=selected_writer, researcher=selected_researcher)
                st.success(f"✅ Models updated: Writer={selected_writer}, Researcher={selected_researcher}")
                st.rerun()

        st.divider()

        # Model Management
        st.subheader("📦 Model Management")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            target_model = st.text_input(
                "Model to pull/remove",
                value="",
                placeholder="e.g., llama3.1:8b, mistral:7b, qwen2.5:7b",
                help="Recommended models: llama3.1:8b (balanced), mistral:7b (fast), qwen2.5:7b (quality)"
            )
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            model_exists = target_model in models_list if target_model else False
        
        if target_model:
            col1, col2 = st.columns(2)
            with col1:
                if not model_exists:
                    if st.button(f"⬇️ Pull {target_model}", use_container_width=True, type="primary"):
                        if not ollama_up:
                            st.error("❌ Ollama is not running. Start it first.")
                        else:
                            with st.spinner(f"Pulling {target_model}... This may take a few minutes."):
                                ok = local_llm_manager.pull_model(target_model)
                            if ok:
                                st.success(f"✅ {target_model} installed successfully!")
                            else:
                                st.error(f"❌ Failed to pull {target_model}")
                            st.rerun()
                else:
                    st.info(f"✅ {target_model} already installed")
            
            with col2:
                if model_exists:
                    if st.button(f"🗑️ Remove {target_model}", use_container_width=True, type="secondary"):
                        if not ollama_up:
                            st.error("❌ Ollama is not running. Start it first.")
                        else:
                            ok = local_llm_manager.delete_model(target_model)
                            if ok:
                                st.success(f"✅ {target_model} removed")
                            else:
                                st.error(f"❌ Failed to remove {target_model}")
                            st.rerun()
        
        # Available models list
        if models_list:
            st.divider()
            st.subheader("📋 Installed Models")
            st.caption(f"{len(models_list)} model(s) available")
            
            for model in sorted(models_list):
                col1, col2 = st.columns([4, 1])
                with col1:
                    is_active = model == current_writer or model == current_researcher
                    icon = "🟢" if is_active else "⚪"
                    role = ""
                    if model == current_writer and model == current_researcher:
                        role = " (Writer & Researcher)"
                    elif model == current_writer:
                        role = " (Writer)"
                    elif model == current_researcher:
                        role = " (Researcher)"
                    st.text(f"{icon} {model}{role}")
                with col2:
                    if st.button("🗑️", key=f"remove_{model}", help=f"Remove {model}"):
                        if not ollama_up:
                            st.error("❌ Ollama is not running")
                        else:
                            ok = local_llm_manager.delete_model(model)
                            if ok:
                                st.success(f"✅ Removed {model}")
                            else:
                                st.error(f"❌ Failed to remove {model}")
                            st.rerun()