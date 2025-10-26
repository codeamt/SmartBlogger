"""
WYSIWYG Editor for blog post editing
"""

import streamlit as st
from datetime import datetime


def render_editor(result_state: dict):
    """
    Render editor interface for final blog post editing with writing-focused design.
    """
    
    # Get final content
    completion_summary = result_state.get("research_context", {}).get("completion_summary", {})
    final_content = completion_summary.get("final_content", "")
    
    if not final_content:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <h2 style="color: #6B6B6B; font-weight: 400;">No content to edit yet</h2>
            <p style="color: #8B8B8B; font-size: 1.125rem; margin-top: 1rem;">
                Generate a blog post first, then return here to refine and polish your content.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Editor mode selector with cleaner design
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h2 style="font-size: 2rem; margin-bottom: 0.5rem;">Edit Your Post</h2>
        <p style="color: #6B6B6B; font-size: 1.125rem;">Refine and perfect your content</p>
    </div>
    """, unsafe_allow_html=True)
    
    editor_mode = st.radio(
        "Editor Mode",
        ["📝 Edit", "👁️ Preview"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if editor_mode == "📝 Edit":
        render_markdown_editor(final_content, result_state)
    else:
        render_preview_only(final_content, result_state)


def render_markdown_editor(final_content: str, result_state: dict):
    """Render markdown editor with live preview and writing-focused design"""
    
    # Initialize edited content in session state
    if "edited_content" not in st.session_state:
        st.session_state.edited_content = final_content
    
    # Action buttons with cleaner design
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        # Calculate stats
        word_count = len(st.session_state.edited_content.split())
        char_count = len(st.session_state.edited_content)
        st.markdown(f"""
        <div style="padding: 0.5rem 0;">
            <span style="color: #6B6B6B; font-size: 0.875rem;">
                {word_count:,} words · {char_count:,} characters
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("↻ Reset", width='stretch'):
            st.session_state.edited_content = final_content
            st.rerun()
    with col3:
        if st.button("💾 Save", width='stretch'):
            save_version(st.session_state.edited_content)
            st.success("Saved!")
    with col4:
        st.download_button(
            label="⬇ Export",
            data=st.session_state.edited_content,
            file_name="blog_post.md",
            mime="text/markdown",
            width='stretch'
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Split view: Editor + Preview with writing-focused styling
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("**Editor**")
        
        # Text area for editing with custom styling
        edited = st.text_area(
            "Markdown Content",
            value=st.session_state.edited_content,
            height=650,
            key="markdown_editor",
            label_visibility="collapsed",
            help="Write in Markdown format"
        )
        
        # Update session state
        st.session_state.edited_content = edited
    
    with col2:
        st.markdown("**Live Preview**")
        
        # Preview with scrollable container and custom styling
        st.markdown("""
        <style>
        .preview-container {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            border: 1px solid #E6E6E6;
            height: 650px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container(height=650):
            st.markdown(st.session_state.edited_content)
    
    st.divider()
    
    # Action buttons
    render_action_buttons(st.session_state.edited_content)
    
    # Version history
    render_version_history()


def render_preview_only(final_content: str, result_state: dict):
    """Render preview-only mode with download option and elegant design"""
    
    # Stats with cleaner design
    sections = result_state.get("sections", [])
    word_count = len(final_content.split())
    char_count = len(final_content)
    
    st.markdown("""
    <div style="display: flex; gap: 2rem; padding: 1.5rem; background: #F7F7F7; 
                border-radius: 8px; margin-bottom: 2rem;">
        <div>
            <div style="font-size: 0.875rem; color: #8B8B8B; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 0.25rem;">Sections</div>
            <div style="font-size: 1.75rem; font-weight: 600; color: #242424;">{}</div>
        </div>
        <div>
            <div style="font-size: 0.875rem; color: #8B8B8B; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 0.25rem;">Words</div>
            <div style="font-size: 1.75rem; font-weight: 600; color: #242424;">{:,}</div>
        </div>
        <div>
            <div style="font-size: 0.875rem; color: #8B8B8B; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 0.25rem;">Characters</div>
            <div style="font-size: 1.75rem; font-weight: 600; color: #242424;">{:,}</div>
        </div>
    </div>
    """.format(len(sections), word_count, char_count), unsafe_allow_html=True)
    
    # Download options
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="⬇ Download Markdown",
            data=final_content,
            file_name="blog_post.md",
            mime="text/markdown",
            type="primary",
            width='stretch'
        )
    with col2:
        html_content = markdown_to_html_simple(final_content)
        st.download_button(
            label="⬇ Download HTML",
            data=html_content,
            file_name="blog_post.html",
            mime="text/html",
            width='stretch'
        )
    with col3:
        medium_content = format_for_medium(final_content)
        st.download_button(
            label="⬇ Medium Format",
            data=medium_content,
            file_name="blog_post_medium.md",
            mime="text/markdown",
            width='stretch'
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Preview with reading-focused design
    st.markdown("**Preview**")
    st.markdown("""
    <style>
    .reading-container {
        background: white;
        padding: 3rem 4rem;
        border-radius: 8px;
        border: 1px solid #E6E6E6;
        max-width: 800px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container(height=650):
        st.markdown(final_content)


def render_action_buttons(edited_content: str):
    """Render action buttons for save/download/export"""
    
    st.subheader("📤 Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.download_button(
            label="📥 Download Markdown",
            data=edited_content,
            file_name="blog_post_edited.md",
            mime="text/markdown",
            width='stretch'
        )
    
    with col2:
        # HTML export
        html_content = markdown_to_html_simple(edited_content)
        st.download_button(
            label="🌐 Download HTML",
            data=html_content,
            file_name="blog_post.html",
            mime="text/html",
            width='stretch'
        )
    
    with col3:
        # Copy to clipboard (via download with .txt)
        st.download_button(
            label="📋 Copy Text",
            data=edited_content,
            file_name="blog_post.txt",
            mime="text/plain",
            width='stretch'
        )
    
    with col4:
        # Medium-ready format
        medium_content = format_for_medium(edited_content)
        st.download_button(
            label="📰 Medium Format",
            data=medium_content,
            file_name="blog_post_medium.md",
            mime="text/markdown",
            width='stretch'
        )
    
    
def render_version_history():
    """Render version history section"""
    
    if "edit_versions" not in st.session_state:
        st.session_state.edit_versions = []
    
    if not st.session_state.edit_versions:
        return
    
    st.divider()
    st.subheader("📚 Version History")
    
    st.caption(f"{len(st.session_state.edit_versions)} version(s) saved")
    
    for idx, version in enumerate(reversed(st.session_state.edit_versions)):
        with st.expander(f"Version {len(st.session_state.edit_versions) - idx} - {version['timestamp']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                preview = version['content'][:200] + "..." if len(version['content']) > 200 else version['content']
                st.text(preview)
            
            with col2:
                if st.button("⏮️ Restore", key=f"restore_{idx}"):
                    st.session_state.edited_content = version['content']
                    st.success("Version restored!")
                    st.rerun()


def save_version(content: str):
    """Save current version to history"""
    
    if "edit_versions" not in st.session_state:
        st.session_state.edit_versions = []
    
    version = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": content,
        "word_count": len(content.split())
    }
    
    st.session_state.edit_versions.append(version)


def markdown_to_html_simple(markdown_text: str) -> str:
    """
    Simple markdown to HTML conversion.
    For better conversion, install markdown library:
        pip install markdown
    """
    
    # Basic HTML wrapper
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Post</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #7f8c8d;
        }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div id="content">
        {markdown_text.replace('\n', '<br>\n')}
    </div>
</body>
</html>"""
    
    return html


def format_for_medium(markdown_text: str) -> str:
    """
    Format markdown for Medium publication.
    Medium supports a subset of markdown.
    """
    
    # Medium-specific formatting tips
    header = """<!-- 
Medium Formatting Tips:
- Use # for titles, ## for subtitles
- Bold with **text**
- Italic with *text*
- Code with `code`
- Code blocks with ```language
- Lists with - or 1.
- Images: ![alt](url)
- Quotes with >

Paste this content into Medium's editor.
-->

"""
    
    return header + markdown_text


# ============================================================================
# ADVANCED WYSIWYG IMPLEMENTATION (Requires streamlit-jodit)
# ============================================================================
# 
# Uncomment this section after installing: pip install streamlit-jodit
#
# from streamlit_jodit import st_jodit
# 
# def render_wysiwyg_editor(final_content: str, result_state: dict):
#     """Render full WYSIWYG editor using Jodit"""
#     
#     st.subheader("✏️ WYSIWYG Editor")
#     st.caption("Edit your blog post with a visual editor")
#     
#     # Convert markdown to HTML for better WYSIWYG experience
#     try:
#         import markdown
#         html_content = markdown.markdown(
#             final_content,
#             extensions=['fenced_code', 'tables', 'nl2br']
#         )
#     except ImportError:
#         html_content = final_content
#     
#     # Jodit editor
#     edited_html = st_jodit(
#         value=html_content,
#         height=600,
#         buttons=[
#             'bold', 'italic', 'underline', 'strikethrough', '|',
#             'ul', 'ol', '|',
#             'outdent', 'indent', '|',
#             'font', 'fontsize', 'brush', '|',
#             'link', 'image', 'table', '|',
#             'align', 'undo', 'redo', '|',
#             'hr', 'eraser', 'copyformat', '|',
#             'symbol', 'fullsize', 'print', 'source'
#         ],
#         key="jodit_editor"
#     )
#     
#     # Convert back to markdown
#     try:
#         from markdownify import markdownify as md
#         markdown_content = md(edited_html, heading_style="ATX")
#     except ImportError:
#         markdown_content = edited_html
#     
#     # Action buttons
#     col1, col2 = st.columns(2)
#     
#     with col1:
#         if st.button("💾 Save Changes", type="primary"):
#             st.session_state.edited_content = markdown_content
#             save_version(markdown_content)
#             st.success("Changes saved!")
#     
#     with col2:
#         st.download_button(
#             label="📥 Download",
#             data=markdown_content,
#             file_name="blog_post_edited.md",
#             mime="text/markdown"
#         )
