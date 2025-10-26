import streamlit as st
from ui.sidebar import render_sidebar
from ui.dashboard import render_main_content
from ui.theme import apply_custom_theme
from ui.state import ensure_defaults


def main():
    """Main entry: classic studio with original theme and unified sidebar+dashboard flow."""
    st.set_page_config(
        page_title="SmartBlogger",
        layout="wide",
        page_icon="✍️",
        initial_sidebar_state="expanded",
    )

    apply_custom_theme()
    ensure_defaults()

    # Render sidebar and collect user inputs
    user_inputs = render_sidebar()

    # Render dashboard/studio main area
    render_main_content(user_inputs)


if __name__ == "__main__":
    main()