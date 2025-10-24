import streamlit as st
# from config import PLAGIARISM_THRESHOLD


def render_plagiarism_report(result_state: dict):
    """Render plagiarism analysis results"""
    st.header("Plagiarism Analysis")

    plagiarism_checks = result_state.get("plagiarism_checks", {})
    if not plagiarism_checks:
        st.info("No plagiarism checks performed.")
        return

    render_plagiarism_summary(plagiarism_checks)
    render_detailed_checks(plagiarism_checks, result_state)