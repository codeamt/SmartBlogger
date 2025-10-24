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
    return EnhancedBlogState(
        source_code=user_inputs.get("code_input"),
        uploaded_files=user_inputs.get("file_paths", []),
        research_queries=user_inputs.get("research_queries", []),
        research_sources=user_inputs.get("research_sources", []),
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