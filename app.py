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
        initial_sidebar_state="expanded",
    )

    apply_custom_theme()
    ensure_defaults()

    # Add a custom header
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: var(--card); border-bottom: 1px solid var(--border); margin-bottom: 1rem; border-radius: var(--radius);'>
        <h1 style='margin: 0; color: var(--foreground);'>SmartBlogger</h1>
        <p style='margin: 0.5rem 0 0 0; color: var(--muted-foreground);'>Transform your ideas into polished technical content with AI-powered research, 
                intelligent writing assistance, and built-in originality protection.</p>
    </div>
    """, unsafe_allow_html=True)

    # Render sidebar and collect user inputs
    user_inputs = render_sidebar()

    # Render dashboard/studio main area
    render_main_content(user_inputs)


if __name__ == "__main__":
    main()