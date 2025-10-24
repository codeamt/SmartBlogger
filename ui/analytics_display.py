import streamlit as st


def render_analytics(result_state: dict):
    """Render generation analytics"""
    st.header("Generation Analytics")

    col1, col2 = st.columns(2)

    with col1:
        render_token_usage(result_state)

    with col2:
        render_research_stats(result_state)

    render_content_stats(result_state)