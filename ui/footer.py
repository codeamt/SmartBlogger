"""
Footer component for SmartBlogger
"""

import streamlit as st

def render_footer():
    """Render a professional footer"""
    st.markdown("""
    <div style='text-align: center; padding: 1rem; margin-top: 2rem; border-top: 1px solid var(--border); background: var(--card); border-radius: var(--radius);'>
        <p style='color: var(--muted-foreground); margin: 0; font-size: 0.9rem;'>
            ✍️ SmartBlogger - AI-Powered Technical Content Creation
        </p>
        <p style='color: var(--muted-foreground); margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
            Transform your ideas into polished technical content
        </p>
    </div>
    """, unsafe_allow_html=True)
