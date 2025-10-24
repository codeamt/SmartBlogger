import streamlit as st
from ui.content_display import render_blog_content
from ui.research_display import render_research_details
from ui.plagiarism_display import render_plagiarism_report
from ui.analytics_display import render_analytics
from workflow_runner import execute_workflow_with_status
# from state_management import get_initial_state


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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Blog Content",
        "🔍 Research Details",
        "⚖️ Plagiarism Report",
        "📊 Analytics"
    ])

    with tab1:
        render_blog_content(st.session_state.result)

    with tab2:
        render_research_details(st.session_state.result)

    with tab3:
        render_plagiarism_report(st.session_state.result)

    with tab4:
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