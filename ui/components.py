import streamlit as st
import streamlit_shadcn_ui as ui
from typing import List, Tuple

# Colors now drive from CSS variables defined in theme (improved dark mode)
ACCENT = "var(--accent)"
ACCENT_LIGHT = "var(--muted-foreground)"
BORDER = "var(--border)"
BORDER_STRONG = "var(--border)"
BG_SUBTLE = "var(--secondary)"
BG_CARD = "var(--card)"
TEXT = "var(--foreground)"
TEXT_SECONDARY = "var(--muted-foreground)"
TEXT_TERTIARY = "var(--muted-foreground)"
SUBTEXT = "var(--muted-foreground)"


def section_header(title: str, icon: str = "", key: str = "section_header", nested: bool = False, subtitle: str | None = None) -> None:
    """Render a dark, outline-style section header.
    If nested=True, apply slight left indent to imply hierarchy under a parent section.
    """
    icon_html = f"<span style='margin-right: 8px;'>{icon}</span>" if icon else ""
    margin_left = "0.5rem" if nested else "0"
    subtitle_html = f"<div style='font-size: 0.75rem; color: {SUBTEXT}; margin-top: 2px;'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div style="
            margin-left: {margin_left};
            display: flex; align-items: center; justify-content: space-between;
            border-left: 4px solid {ACCENT};
            border: 1px solid {BORDER};
            background: {BG_SUBTLE};
            color: {TEXT};
            padding: 0.55rem 0.85rem; border-radius: var(--radius); margin: 0 0 0.6rem 0;">
            <div style="font-weight: 600; letter-spacing: 0.01em;">
                {icon_html}{title}
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(content: str, title: str = None, padding: str = "1.5rem", border_radius: str = "12px"):
    """Render a card component with optional title"""
    title_html = f"<h4 style='margin: 0 0 1rem 0; color: {TEXT}; font-weight: 600;'>{title}</h4>" if title else ""
    
    st.markdown(f"""
    <div style='
        background: {BG_CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: var(--radius); 
        padding: {padding}; 
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    '>
        {title_html}
        <div style='color: {TEXT}; line-height: 1.6;'>{content}</div>
    </div>
    """, unsafe_allow_html=True)


def badges(items: List[Tuple[str, str]] | None = None, key: str = "badges", gap: int = 8):
    """Render a row of shadcn badges. items: list of (label, variant)."""
    items = items or []
    ui.badges(badge_list=items, class_name=f"flex gap-2", key=key)


def pill_row(labels: List[str], key: str = "pill_row"):
    """Render a row of subtle pill badges using shadcn badges with 'secondary' variant."""
    badge_list = [(lbl, "secondary") for lbl in labels]
    badges(badge_list, key)


def panel(title: str | None = None, subtle_title: str | None = None):
    """Render a panel component with optional title"""
    c = st.container(border=True)
    with c:
        if title or subtle_title:
            title_html = title or ""
            subtle_html = f"<div style='font-size: 0.85rem; color: {TEXT_SECONDARY};'>{subtle_title}</div>" if subtle_title else ""
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; justify-content: space-between; margin-bottom: 0.75rem;">
                    <div style="font-weight:650; color: {TEXT};">{title_html}</div>
                    {subtle_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
    return c


def card_panel(content: str, title: str = None, padding: str = "1.5rem"):
    """Render a card-style panel component with optional title"""
    title_html = f"<h3 style='margin: 0 0 1rem 0; color: {TEXT}; font-weight: 600; font-size: 1.25rem;'>{title}</h3>" if title else ""
    
    st.markdown(f"""
    <div style='
        background: {BG_CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: var(--radius); 
        padding: {padding}; 
        margin: 1.5rem 0;
        box-shadow: var(--shadow-md);
    '>
        {title_html}
        <div style='color: {TEXT}; line-height: 1.6;'>{content}</div>
    </div>
    """, unsafe_allow_html=True)


def status_pills(items: List[Tuple[str, bool, str]] , key: str = "status_pills"):
    """Render compact status pills using shadcn badges to avoid raw HTML issues.
    items: list of (label, active_bool, icon_char)
    """
    labels = [
        f"{icon} {label}" if active else f"{icon} {label}"
        for (label, active, icon) in items
    ]
    # Use 'secondary' variant to keep subtle, add small text via class_name
    badge_list = [(lbl, "secondary") for lbl in labels]
    ui.badges(badge_list=badge_list, class_name="flex flex-wrap gap-1 text-[0.8rem]", key=key)


def icon_button(icon: str, help: str, key: str) -> bool:
    return st.button(icon, key=key, help=help)


def list_row(left_html: str, right_button_key: str, right_label: str = "✗", right_help: str = "") -> bool:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(left_html, unsafe_allow_html=True)
    with col2:
        return st.button(right_label, key=right_button_key, help=right_help)
