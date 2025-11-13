"""
Loading screen for SmartBlogger
"""

import streamlit as st
import time

def show_loading_screen():
    """Show an enhanced loading screen with progress indicators"""
    # Create a container for the loading screen
    with st.container():
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: var(--card); border-radius: var(--radius); border: 1px solid var(--border);'>
            <h2 style='color: var(--foreground); margin-bottom: 1rem;'>Generating your content</h2>
            <p style='color: var(--muted-foreground); margin-bottom: 2rem;'>SmartBlogger is creating your draft...</p>
            <div style='display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;'>
                <div style='background: var(--secondary); padding: 1rem; border-radius: var(--radius); min-width: 150px;'>
                    <h3 style='color: var(--primary); margin: 0;'>Research</h3>
                    <p style='color: var(--muted-foreground); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Gathering information</p>
                </div>
                <div style='background: var(--secondary); padding: 1rem; border-radius: var(--radius); min-width: 150px;'>
                    <h3 style='color: var(--primary); margin: 0;'>Writing</h3>
                    <p style='color: var(--muted-foreground); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Crafting content</p>
                </div>
                <div style='background: var(--secondary); padding: 1rem; border-radius: var(--radius); min-width: 150px;'>
                    <h3 style='color: var(--primary); margin: 0;'>Protection</h3>
                    <p style='color: var(--muted-foreground); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Checking originality</p>
                </div>
            </div>
            <div style='margin-top: 2rem;'>
                <p style='color: var(--muted-foreground); font-size: 0.9rem;'>This may take a few minutes depending on the complexity of your content.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a subtle animation
        st.markdown("""
        <style>
        @keyframes pulse {
          0% { opacity: 0.6; }
          50% { opacity: 1; }
          100% { opacity: 0.6; }
        }
        .pulse {
          animation: pulse 2s infinite;
        }
        </style>
        <div class='pulse' style='text-align: center; margin-top: 1rem; color: var(--text-tertiary);'>
          <p>Processing... Please wait</p>
        </div>
        """, unsafe_allow_html=True)

def show_simple_loading(message="Processing..."):
    """Show a simple loading indicator with a message"""
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background: var(--card); border-radius: var(--radius); border: 1px solid var(--border);'>
        <p style='color: var(--foreground); margin: 0;'>{message}</p>
    </div>
    """, unsafe_allow_html=True)
