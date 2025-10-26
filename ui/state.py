import streamlit as st
from typing import Any, Dict, Optional

# Optionally expose the existing EnhancedBlogState if needed by callers
try:
    from state import EnhancedBlogState  # root-level state.py
except Exception:
    EnhancedBlogState = None  # type: ignore

DEFAULTS: Dict[str, Any] = {
    "current_page": "overview",
    "user_inputs": {},
    "active_article_id": None,
    # Dashboard/session flags
    "result": None,
    "generate_clicked": False,
}


def ensure_defaults() -> None:
    """Initialize common session keys if missing."""
    for key, val in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val


# --- Page routing helpers ---

def get_current_page() -> str:
    return st.session_state.get("current_page", DEFAULTS["current_page"])  # type: ignore


def set_current_page(page: str) -> None:
    st.session_state["current_page"] = page


# --- Article focus helpers ---

def get_active_article_id() -> Optional[str]:
    return st.session_state.get("active_article_id")


def set_active_article_id(article_id: Optional[str]) -> None:
    st.session_state["active_article_id"] = article_id


# --- User inputs helpers ---

def get_user_inputs() -> Dict[str, Any]:
    return st.session_state.get("user_inputs", {})


def set_user_inputs(data: Dict[str, Any]) -> None:
    st.session_state["user_inputs"] = data
