"""
WYSIWYG Editor for blog post editing
"""

import streamlit as st
from datetime import datetime


def render_editor(result_state: dict):
    """
    Render editor interface for final blog post editing.
    
    Note: This is a basic implementation using st.text_area.
    For full WYSIWYG, install streamlit-jodit:
        pip install streamlit-jodit
    Then uncomment the advanced implementation below.
    """
    
    st.header("✏️ Edit Blog Post")
    
    # Get final content
    completion_summary = result_state.get("research_context", {}).get("completion_summary", {})
    final_content = completion_summary.get("final_content", "")
    
    if not final_content:
        st.info("📝 Generate a blog post first to enable editing.")
        st.caption("Go to the sidebar, fill in your inputs, and click 'Generate Blog Post'")
        return
    
    # Editor mode selector
    editor_mode = st.radio(
        "Editor Mode",
        ["📝 Markdown Editor", "👁️ Preview Only"],
        horizontal=True,
        help="Choose between editing markdown directly or viewing the preview"
    )
    
    if editor_mode == "📝 Markdown Editor":
        render_markdown_editor(final_content, result_state)
    else:
        render_preview_only(final_content, result_state)


def render_markdown_editor(final_content: str, result_state: dict):
    """Render markdown editor with live preview"""
    
    # Initialize edited content in session state
    if "edited_content" not in st.session_state:
        st.session_state.edited_content = final_content
    
    # Reset button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("💡 Tip: Edit the markdown on the left, see the preview on the right")
    with col2:
        if st.button("🔄 Reset to Original"):
            st.session_state.edited_content = final_content
            st.rerun()
    with col3:
        if st.button("💾 Save Version"):
            save_version(st.session_state.edited_content)
            st.success("Version saved!")
    
    st.divider()
    
    # Split view: Editor + Preview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Editor")
        
        # Calculate stats
        word_count = len(st.session_state.edited_content.split())
        char_count = len(st.session_state.edited_content)
        
        st.caption(f"Words: {word_count:,} | Characters: {char_count:,}")
        
        # Text area for editing
        edited = st.text_area(
            "Markdown Content",
            value=st.session_state.edited_content,
            height=600,
            key="markdown_editor",
            label_visibility="collapsed"
        )
        
        # Update session state
        st.session_state.edited_content = edited
    
    with col2:
        st.subheader("👁️ Live Preview")
        
        # Preview with scrollable container
        with st.container(height=650):
            st.markdown(st.session_state.edited_content)
    
    st.divider()
    
    # Action buttons
    render_action_buttons(st.session_state.edited_content)
    
    # Version history
    render_version_history()


def render_preview_only(final_content: str, result_state: dict):
    """Render preview-only mode with download option"""
    
    # Stats
    sections = result_state.get("sections", [])
    word_count = len(final_content.split())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Sections", len(sections))
    col2.metric("Words", f"{word_count:,}")
    col3.metric("Status", "✅ Complete")
    
    st.divider()
    
    # Download button
    st.download_button(
        label="📥 Download Blog Post",
        data=final_content,
        file_name="blog_post.md",
        mime="text/markdown",
        type="primary",
        use_container_width=True
    )
    
    st.divider()
    
    # Preview
    st.subheader("📄 Preview")
    with st.container(height=600):
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
            use_container_width=True
        )
    
    with col2:
        # HTML export
        html_content = markdown_to_html_simple(edited_content)
        st.download_button(
            label="🌐 Download HTML",
            data=html_content,
            file_name="blog_post.html",
            mime="text/html",
            use_container_width=True
        )
    
    with col3:
        # Copy to clipboard (via download with .txt)
        st.download_button(
            label="📋 Copy Text",
            data=edited_content,
            file_name="blog_post.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col4:
        # Medium-ready format
        medium_content = format_for_medium(edited_content)
        st.download_button(
            label="📰 Medium Format",
            data=medium_content,
            file_name="blog_post_medium.md",
            mime="text/markdown",
            use_container_width=True
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
