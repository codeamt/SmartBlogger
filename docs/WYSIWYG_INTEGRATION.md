# WYSIWYG Editor Integration Guide

## Overview

Integrate a WYSIWYG (What You See Is What You Get) editor into SmartBlogger to allow users to make final edits, formatting adjustments, and content refinements directly in the UI before downloading.

---

## Editor Options Comparison

### 1. **streamlit-jodit** (Recommended)
- **Pros**:
  - Full-featured WYSIWYG editor
  - Markdown support
  - Image upload
  - Toolbar customization
  - Mobile-friendly
  - Active maintenance
- **Cons**:
  - Larger bundle size
  - Requires custom component
- **Best for**: Full editing capabilities

### 2. **streamlit-quill**
- **Pros**:
  - Lightweight
  - Clean interface
  - Good Streamlit integration
  - Delta format support
- **Cons**:
  - Limited markdown support
  - Fewer features than Jodit
- **Best for**: Simple text editing

### 3. **streamlit-ace**
- **Pros**:
  - Code editor (great for markdown)
  - Syntax highlighting
  - Multiple themes
  - Fast
- **Cons**:
  - Not WYSIWYG (shows raw markdown)
  - More technical
- **Best for**: Power users who prefer markdown

### 4. **Custom HTML Editor (TinyMCE/CKEditor)**
- **Pros**:
  - Industry-standard editors
  - Extensive plugins
  - Full control
- **Cons**:
  - Requires custom Streamlit component
  - More complex integration
- **Best for**: Advanced customization needs

---

## Recommended Approach: streamlit-jodit

### Why Jodit?
1. **Full WYSIWYG** - True visual editing
2. **Markdown support** - Can import/export markdown
3. **Rich features** - Tables, images, links, code blocks
4. **Customizable** - Toolbar can be tailored
5. **Maintained** - Active development

---

## Implementation Plan

### **Phase 1: Basic Integration**

#### 1.1 Install Dependencies
```bash
pip install streamlit-jodit
```

#### 1.2 Create Editor Component
```python
# ui/editor_display.py
from streamlit_jodit import st_jodit
import streamlit as st

def render_wysiwyg_editor(result_state: dict):
    """Render WYSIWYG editor for final blog post"""
    
    completion_summary = result_state.get("research_context", {}).get("completion_summary", {})
    final_content = completion_summary.get("final_content", "")
    
    if not final_content:
        st.info("Generate a blog post first to enable editing.")
        return
    
    st.header("✏️ Edit Blog Post")
    
    # Convert markdown to HTML for better WYSIWYG experience
    html_content = markdown_to_html(final_content)
    
    # Jodit editor
    edited_content = st_jodit(
        value=html_content,
        height=600,
        buttons=[
            'bold', 'italic', 'underline', '|',
            'ul', 'ol', '|',
            'link', 'image', '|',
            'align', '|',
            'undo', 'redo', '|',
            'source'  # Toggle HTML/visual mode
        ],
        key="blog_editor"
    )
    
    # Save edited content
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            # Convert back to markdown
            markdown_content = html_to_markdown(edited_content)
            save_edited_content(result_state, markdown_content)
            st.success("Changes saved!")
    
    with col2:
        st.download_button(
            label="📥 Download Edited Version",
            data=html_to_markdown(edited_content),
            file_name="blog_post_edited.md",
            mime="text/markdown"
        )
```

#### 1.3 Add Conversion Utilities
```python
# utils/content_conversion.py
import markdown
from markdownify import markdownify as md

def markdown_to_html(markdown_text: str) -> str:
    """Convert markdown to HTML for WYSIWYG editing"""
    return markdown.markdown(
        markdown_text,
        extensions=['fenced_code', 'tables', 'nl2br']
    )

def html_to_markdown(html_text: str) -> str:
    """Convert HTML back to markdown"""
    return md(html_text, heading_style="ATX")
```

---

### **Phase 2: Enhanced Features**

#### 2.1 Side-by-Side Preview
```python
def render_split_editor(result_state: dict):
    """Render editor with live markdown preview"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✏️ Editor")
        edited_content = st_jodit(
            value=html_content,
            height=600,
            key="editor"
        )
    
    with col2:
        st.subheader("👁️ Preview")
        markdown_preview = html_to_markdown(edited_content)
        st.markdown(markdown_preview)
```

#### 2.2 Version History
```python
def render_editor_with_versions(result_state: dict):
    """Editor with version history tracking"""
    
    # Initialize version history in session state
    if "edit_versions" not in st.session_state:
        st.session_state.edit_versions = []
    
    # Editor
    edited_content = st_jodit(value=html_content, height=600)
    
    # Save version
    if st.button("💾 Save Version"):
        version = {
            "timestamp": datetime.now().isoformat(),
            "content": edited_content
        }
        st.session_state.edit_versions.append(version)
        st.success(f"Version {len(st.session_state.edit_versions)} saved!")
    
    # Version selector
    if st.session_state.edit_versions:
        st.subheader("📚 Version History")
        version_idx = st.selectbox(
            "Load version",
            range(len(st.session_state.edit_versions)),
            format_func=lambda i: f"Version {i+1} - {st.session_state.edit_versions[i]['timestamp']}"
        )
        
        if st.button("⏮️ Restore Version"):
            # Reload editor with selected version
            st.rerun()
```

#### 2.3 Collaborative Comments
```python
def render_editor_with_comments(result_state: dict):
    """Editor with inline commenting"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        edited_content = st_jodit(value=html_content, height=600)
    
    with col2:
        st.subheader("💬 Comments")
        
        # Add comment
        comment = st.text_area("Add comment", key="new_comment")
        if st.button("Add"):
            if "comments" not in st.session_state:
                st.session_state.comments = []
            st.session_state.comments.append({
                "text": comment,
                "timestamp": datetime.now()
            })
            st.rerun()
        
        # Display comments
        for idx, c in enumerate(st.session_state.get("comments", [])):
            with st.expander(f"Comment {idx+1}"):
                st.write(c["text"])
                st.caption(c["timestamp"].strftime("%Y-%m-%d %H:%M"))
```

---

### **Phase 3: Advanced Integration**

#### 3.1 AI-Assisted Editing
```python
def render_ai_assisted_editor(result_state: dict):
    """Editor with AI suggestions"""
    
    edited_content = st_jodit(value=html_content, height=600)
    
    st.divider()
    st.subheader("🤖 AI Suggestions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✨ Improve Grammar"):
            improved = improve_grammar_with_llm(edited_content)
            st.session_state.suggested_content = improved
            st.success("Grammar improvements ready!")
    
    with col2:
        if st.button("📝 Simplify Language"):
            simplified = simplify_with_llm(edited_content)
            st.session_state.suggested_content = simplified
            st.success("Simplified version ready!")
    
    with col3:
        if st.button("🎯 Enhance SEO"):
            seo_enhanced = enhance_seo_with_llm(edited_content)
            st.session_state.suggested_content = seo_enhanced
            st.success("SEO enhancements ready!")
    
    # Show suggestion
    if "suggested_content" in st.session_state:
        with st.expander("📋 View Suggestion"):
            st.markdown(st.session_state.suggested_content)
            if st.button("✅ Apply Suggestion"):
                # Update editor content
                st.rerun()
```

#### 3.2 Export Options
```python
def render_export_options(edited_content: str):
    """Multiple export format options"""
    
    st.subheader("📤 Export Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Markdown
        markdown_content = html_to_markdown(edited_content)
        st.download_button(
            "📝 Markdown",
            data=markdown_content,
            file_name="blog_post.md",
            mime="text/markdown"
        )
    
    with col2:
        # HTML
        st.download_button(
            "🌐 HTML",
            data=edited_content,
            file_name="blog_post.html",
            mime="text/html"
        )
    
    with col3:
        # PDF (requires additional library)
        pdf_content = convert_to_pdf(edited_content)
        st.download_button(
            "📄 PDF",
            data=pdf_content,
            file_name="blog_post.pdf",
            mime="application/pdf"
        )
    
    with col4:
        # Medium-ready format
        medium_content = format_for_medium(markdown_content)
        st.download_button(
            "📰 Medium",
            data=medium_content,
            file_name="blog_post_medium.md",
            mime="text/markdown"
        )
```

#### 3.3 Real-time Collaboration
```python
def render_collaborative_editor(result_state: dict):
    """Editor with real-time collaboration (requires backend)"""
    
    # This would require:
    # 1. WebSocket connection
    # 2. Operational Transform (OT) or CRDT
    # 3. Backend server for coordination
    
    st.warning("⚠️ Collaborative editing requires additional backend setup")
    
    # Simplified version: Lock-based editing
    if "editor_lock" not in st.session_state:
        st.session_state.editor_lock = None
    
    if st.session_state.editor_lock is None:
        if st.button("🔓 Start Editing"):
            st.session_state.editor_lock = st.session_state.get("user_id", "user1")
            st.rerun()
    else:
        if st.session_state.editor_lock == st.session_state.get("user_id"):
            edited_content = st_jodit(value=html_content, height=600)
            
            if st.button("🔒 Release Lock"):
                st.session_state.editor_lock = None
                st.rerun()
        else:
            st.info(f"🔒 Currently being edited by {st.session_state.editor_lock}")
```

---

## Alternative: Streamlit-Ace (Markdown Editor)

### For users who prefer markdown:

```python
from streamlit_ace import st_ace

def render_markdown_editor(result_state: dict):
    """Markdown editor with syntax highlighting"""
    
    final_content = get_final_content(result_state)
    
    st.header("📝 Edit Markdown")
    
    # Ace editor
    edited_markdown = st_ace(
        value=final_content,
        language="markdown",
        theme="monokai",
        height=600,
        font_size=14,
        tab_size=2,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        key="markdown_editor"
    )
    
    # Live preview
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Markdown")
        st.code(edited_markdown, language="markdown")
    
    with col2:
        st.subheader("👁️ Preview")
        st.markdown(edited_markdown)
    
    # Download
    st.download_button(
        "📥 Download",
        data=edited_markdown,
        file_name="blog_post.md",
        mime="text/markdown"
    )
```

---

## Integration into Dashboard

### Update `ui/dashboard.py`:

```python
def render_dashboard(result_state: dict):
    """Main dashboard with editor tab"""
    
    tabs = st.tabs([
        "📊 Overview",
        "📝 Content",
        "✏️ Editor",  # NEW
        "🔬 Research",
        "🛡️ Plagiarism",
        "📊 Analytics"
    ])
    
    with tabs[0]:
        render_overview(result_state)
    
    with tabs[1]:
        render_blog_content(result_state)
    
    with tabs[2]:
        render_wysiwyg_editor(result_state)  # NEW
    
    with tabs[3]:
        render_research_results(result_state)
    
    with tabs[4]:
        render_plagiarism_results(result_state)
    
    with tabs[5]:
        render_analytics(result_state)
```

---

## Dependencies

### Required:
```toml
[dependencies]
streamlit-jodit = ">=0.1.0"
markdown = ">=3.4.0"
markdownify = ">=0.11.0"
```

### Optional (for advanced features):
```toml
weasyprint = ">=59.0"  # PDF export
pypandoc = ">=1.11"    # Format conversion
```

---

## User Experience Flow

### 1. **Generate Blog Post**
```
User inputs → Workflow → Final content generated
```

### 2. **Review in Content Tab**
```
Read-only preview → Identify areas for improvement
```

### 3. **Edit in Editor Tab**
```
WYSIWYG editor → Make changes → Preview live
```

### 4. **Save & Export**
```
Save version → Download in preferred format
```

---

## Benefits

### **For Users:**
1. ✅ **Visual editing** - See changes immediately
2. ✅ **No markdown knowledge needed** - WYSIWYG interface
3. ✅ **Quick fixes** - Correct typos, adjust formatting
4. ✅ **Version control** - Track changes over time
5. ✅ **Multiple formats** - Export to MD, HTML, PDF

### **For Power Users:**
1. ✅ **Markdown mode** - Direct markdown editing
2. ✅ **Syntax highlighting** - Better readability
3. ✅ **Keyboard shortcuts** - Faster editing
4. ✅ **Source view** - Toggle between visual/code

### **For Teams:**
1. ✅ **Comments** - Inline feedback
2. ✅ **Version history** - Track iterations
3. ✅ **Lock mechanism** - Prevent conflicts
4. ✅ **Export options** - Share in any format

---

## Limitations & Considerations

### **Streamlit Constraints:**
- No true real-time collaboration (requires backend)
- State resets on page refresh (use session state)
- Large documents may slow down editor

### **Workarounds:**
1. **Auto-save** - Save to session state every N seconds
2. **Chunked editing** - Edit sections individually
3. **Local storage** - Use browser localStorage via custom component

---

## Implementation Priority

### **Phase 1 (MVP)** - Week 1
- [ ] Install streamlit-jodit
- [ ] Create basic editor component
- [ ] Add markdown ↔ HTML conversion
- [ ] Implement save/download

### **Phase 2 (Enhanced)** - Week 2
- [ ] Add side-by-side preview
- [ ] Implement version history
- [ ] Add export options (HTML, PDF)

### **Phase 3 (Advanced)** - Week 3
- [ ] AI-assisted editing
- [ ] Inline comments
- [ ] SEO optimization tools

---

## Testing Checklist

- [ ] Editor loads with generated content
- [ ] Formatting preserved (bold, italic, lists)
- [ ] Code blocks render correctly
- [ ] Images display properly
- [ ] Links are clickable
- [ ] Save functionality works
- [ ] Download produces valid markdown
- [ ] Version history tracks changes
- [ ] Preview matches final output

---

## Next Steps

1. **Install dependencies**:
   ```bash
   pip install streamlit-jodit markdown markdownify
   ```

2. **Create editor component**:
   ```bash
   touch ui/editor_display.py
   touch utils/content_conversion.py
   ```

3. **Update dashboard**:
   - Add "Editor" tab
   - Import editor component

4. **Test with sample content**:
   - Generate blog post
   - Open editor tab
   - Make edits
   - Download

---

**Version**: 2.4  
**Last Updated**: October 2025  
**Status**: 📋 Design Complete - Ready for Implementation
