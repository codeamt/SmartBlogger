import streamlit as st
from ui.sidebar import render_sidebar
from ui.dashboard import render_main_content
from state_management import initialize_session_state, get_initial_state
from workflow_runner import execute_workflow
# import config


def main():
    """Minimal main application entry point"""
    st.set_page_config(
        page_title="Research-Powered Blog Assistant",
        layout="wide",
        page_icon="📝"
    )

    st.title("📝 Research-Powered Blog Assistant")
    st.caption("Generate technical content with integrated research and plagiarism protection")

    # Initialize session state
    initialize_session_state()

    # Render sidebar and get user inputs
    user_inputs = render_sidebar()

    # Render main content area
    render_main_content(user_inputs)


if __name__ == "__main__":
    main()