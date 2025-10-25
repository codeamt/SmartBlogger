import streamlit as st
from state import EnhancedBlogState
from config import FREE_TIER_CREDITS
import os
import shutil


def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        "generate_clicked": False,
        "result": None,
        "generation_status": "ready",
        "workflow": None,
        "current_tab": "welcome"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_initial_state(user_inputs: dict) -> EnhancedBlogState:
    """Create initial workflow state from user inputs"""
    # Normalize research queries to list[str]
    rq_raw = user_inputs.get("research_queries", []) or []
    if isinstance(rq_raw, list):
        normalized_rq = []
        for it in rq_raw:
            if isinstance(it, str):
                s = it.strip()
                if s:
                    normalized_rq.append(s)
            elif isinstance(it, dict):
                q = (it.get("query") or "").strip()
                if q:
                    normalized_rq.append(q)
    else:
        normalized_rq = []

    return EnhancedBlogState(
        source_code=user_inputs.get("code_input"),
        uploaded_files=user_inputs.get("file_paths", []),
        research_focus=user_inputs.get("research_focus"),
        research_queries=normalized_rq,
        research_sources=[s.lower() for s in user_inputs.get("research_sources", [])],
        tone=user_inputs.get("tone", "Professional"),
        target_audience=user_inputs.get("target_audience", "Developers"),
        writing_style=user_inputs.get("writing_style", []),
        custom_questions=user_inputs.get("custom_questions", []),
        sections=None,
        current_section=None,
        section_drafts={},
        citations={},
        token_usage={},
        free_tier_credits=FREE_TIER_CREDITS,
        content_fingerprints=set(),
        plagiarism_checks={},
        revision_history={},
        next_action="process_inputs",
    )


def clear_session_state():
    """Clear all session state"""
    # Clean up session-scoped upload directory if present
    upload_dir = st.session_state.get("upload_dir")
    if upload_dir and os.path.isdir(upload_dir):
        try:
            shutil.rmtree(upload_dir)
        except Exception:
            pass

    st.session_state.clear()
    initialize_session_state()