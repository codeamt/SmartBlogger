import streamlit as st


def render_plagiarism_report(result_state: dict):
    """Render plagiarism analysis results"""
    st.header("Plagiarism Analysis")

    plagiarism_checks = result_state.get("plagiarism_checks", {}) if isinstance(result_state, dict) else {}
    if not plagiarism_checks:
        st.info("No plagiarism checks performed.")
        return

    render_plagiarism_summary(plagiarism_checks)
    render_detailed_checks(plagiarism_checks, result_state)


def render_plagiarism_summary(plagiarism_checks: dict):
    total_sections = len(plagiarism_checks)
    flagged = 0
    avg_api = []
    avg_ai = []

    for sec, checks in plagiarism_checks.items():
        api_score = checks.get("api", {}).get("score")
        ai_score = (checks.get("ai", {}) or {}).get("risk_score")
        if isinstance(api_score, (int, float)):
            avg_api.append(api_score)
        if isinstance(ai_score, (int, float)):
            avg_ai.append(ai_score)
        if (api_score and api_score > 15) or (ai_score and ai_score > 70):
            flagged += 1

    col1, col2, col3 = st.columns(3)
    col1.metric("Sections Checked", total_sections)
    col2.metric("Flagged Sections", flagged)
    col3.metric("Avg AI Risk", f"{(sum(avg_ai)/len(avg_ai)):.1f}" if avg_ai else "-")


def render_detailed_checks(plagiarism_checks: dict, result_state: dict):
    st.subheader("Details")
    for section_id, checks in plagiarism_checks.items():
        with st.expander(f"Section {section_id}"):
            api = checks.get("api", {})
            ai = checks.get("ai", {})
            st.write("API Similarity:", api.get("score", "-"))
            st.write("AI Risk Score:", ai.get("risk_score", "-"))
            flagged = ai.get("flagged_phrases") or []
            if flagged:
                st.write("Flagged Phrases:")
                for p in flagged[:5]:
                    st.write(f"- {p}")
            recs = ai.get("recommendations") or []
            if recs:
                st.write("Recommendations:")
                for r in recs[:5]:
                    st.write(f"- {r}")
