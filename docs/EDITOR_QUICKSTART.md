# Editor Quick Start Guide

## What's New: Built-in Editor! ✏️

You can now edit your generated blog posts directly in the UI with a new **Editor** tab!

---

## Current Features (Basic Editor)

### ✅ **Available Now** (No additional installation)

1. **📝 Markdown Editor**
   - Edit markdown directly in a text area
   - Live preview side-by-side
   - Word/character count
   - Syntax highlighting

2. **💾 Version History**
   - Save multiple versions
   - Restore previous versions
   - Timestamp tracking

3. **📤 Multiple Export Formats**
   - Markdown (.md)
   - HTML (.html)
   - Plain text (.txt)
   - Medium-ready format

4. **👁️ Preview Mode**
   - Read-only preview
   - Scrollable container
   - Formatted display

---

## How to Use

### **Step 1: Generate Blog Post**
1. Fill in sidebar inputs
2. Click "Generate Blog Post"
3. Wait for completion

### **Step 2: Open Editor Tab**
1. Click the **"✏️ Editor"** tab
2. Choose editor mode:
   - **📝 Markdown Editor** - Edit and preview
   - **👁️ Preview Only** - Read-only view

### **Step 3: Edit Content**
1. Edit markdown in left pane
2. See live preview in right pane
3. Word count updates automatically

### **Step 4: Save & Export**
1. Click **"💾 Save Version"** to save
2. Choose export format:
   - **📥 Download Markdown** - Standard .md file
   - **🌐 Download HTML** - Styled HTML page
   - **📋 Copy Text** - Plain text version
   - **📰 Medium Format** - Ready for Medium

---

## Editor Interface

### **Markdown Editor Mode**

```
┌─────────────────────────────────────────────────────────┐
│ 📝 Editor                    👁️ Live Preview           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  # Blog Title                 Blog Title                │
│                                                         │
│  Introduction text...         Introduction text...     │
│                                                         │
│  ## Section 1                 Section 1                 │
│                                                         │
│  Content here...              Content here...           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **Action Buttons**

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 📥 Download  │ 🌐 Download  │ 📋 Copy Text │ 📰 Medium    │
│   Markdown   │    HTML      │              │   Format     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Keyboard Shortcuts

### **In Text Area:**
- `Cmd/Ctrl + A` - Select all
- `Cmd/Ctrl + C` - Copy
- `Cmd/Ctrl + V` - Paste
- `Cmd/Ctrl + Z` - Undo
- `Cmd/Ctrl + Shift + Z` - Redo

### **Markdown Shortcuts:**
- `**text**` - Bold
- `*text*` - Italic
- `# text` - Heading 1
- `## text` - Heading 2
- `- text` - Bullet list
- `1. text` - Numbered list
- `` `code` `` - Inline code
- ` ```code``` ` - Code block

---

## Version History

### **Save a Version**
1. Make your edits
2. Click **"💾 Save Version"**
3. Version saved with timestamp

### **Restore a Version**
1. Scroll to "📚 Version History"
2. Expand version to view
3. Click **"⏮️ Restore"**
4. Content restored to editor

### **Version Info**
Each version shows:
- Version number
- Timestamp
- Content preview
- Word count

---

## Export Formats

### **1. Markdown (.md)**
- Standard markdown format
- Compatible with GitHub, GitLab, etc.
- Preserves all formatting

### **2. HTML (.html)**
- Styled HTML page
- Ready to host
- Includes CSS styling
- Mobile-responsive

### **3. Plain Text (.txt)**
- No formatting
- Good for copying
- Universal compatibility

### **4. Medium Format (.md)**
- Optimized for Medium
- Includes formatting tips
- Subset of markdown
- Paste directly into Medium editor

---

## Advanced Features (Coming Soon)

### **🚀 Full WYSIWYG Editor** (Optional)

Install enhanced editor:
```bash
pip install streamlit-jodit markdown markdownify
```

Or install all editor features:
```bash
uv pip install -e ".[editor]"
```

#### **Features with streamlit-jodit:**
- ✨ True WYSIWYG editing
- 🎨 Rich text toolbar
- 🖼️ Image upload
- 📊 Table editor
- 🔗 Link manager
- 🎨 Color picker
- ⚡ Faster editing

#### **Toolbar Buttons:**
```
Bold | Italic | Underline | Strikethrough
List | Ordered List | Indent | Outdent
Font | Size | Color | Background
Link | Image | Table | Code
Align | Undo | Redo | Source
```

---

## Tips & Tricks

### **Editing Tips:**

1. **Use Preview** - Check formatting as you type
2. **Save Often** - Create versions at milestones
3. **Test Links** - Verify all links work
4. **Check Code Blocks** - Ensure proper syntax
5. **Review Citations** - Verify reference numbers

### **Formatting Tips:**

1. **Headings** - Use # for hierarchy
2. **Lists** - Use - or 1. for clarity
3. **Code** - Use ``` for code blocks
4. **Quotes** - Use > for blockquotes
5. **Links** - Use [text](url) format

### **Export Tips:**

1. **Markdown** - Best for version control
2. **HTML** - Best for hosting
3. **Medium** - Best for publishing
4. **Text** - Best for email/chat

---

## Troubleshooting

### **Editor Not Showing?**

**Check**: Did you generate a blog post?
- Editor only appears after content is generated
- Go to sidebar and click "Generate Blog Post"

### **Preview Not Updating?**

**Solution**: Streamlit auto-updates on text change
- If stuck, click outside text area
- Or press Tab to trigger update

### **Version Not Saving?**

**Check**: Click "💾 Save Version" button
- Versions are stored in session state
- They persist until you refresh the page

### **Download Not Working?**

**Try**: Right-click → "Save Link As"
- Or use different browser
- Check browser download settings

---

## Comparison: Basic vs Advanced

| Feature | Basic Editor | Advanced (Jodit) |
|---------|-------------|------------------|
| Edit markdown | ✅ | ✅ |
| Live preview | ✅ | ✅ |
| Version history | ✅ | ✅ |
| Export formats | ✅ | ✅ |
| WYSIWYG editing | ❌ | ✅ |
| Rich toolbar | ❌ | ✅ |
| Image upload | ❌ | ✅ |
| Table editor | ❌ | ✅ |
| Color picker | ❌ | ✅ |
| Installation | None | `pip install` |

---

## Workflow Example

### **Typical Editing Session:**

```
1. Generate blog post
   ↓
2. Review in "Blog Content" tab
   ↓
3. Switch to "Editor" tab
   ↓
4. Choose "Markdown Editor" mode
   ↓
5. Make edits in left pane
   ↓
6. Check preview in right pane
   ↓
7. Click "Save Version"
   ↓
8. Continue editing or export
   ↓
9. Download in preferred format
```

---

## Integration with Other Tabs

### **Content Tab** → **Editor Tab**
- Review generated content
- Identify areas to improve
- Switch to editor to make changes

### **Editor Tab** → **Analytics Tab**
- Edit content
- Check word count in analytics
- Verify section balance

### **Plagiarism Tab** → **Editor Tab**
- Review plagiarism results
- Switch to editor to rewrite
- Re-check after edits

---

## Future Enhancements

### **Planned Features:**

1. **AI-Assisted Editing**
   - Grammar improvements
   - Style suggestions
   - SEO optimization

2. **Collaborative Features**
   - Inline comments
   - Change tracking
   - Multi-user editing

3. **Advanced Export**
   - PDF generation
   - DOCX format
   - WordPress ready

4. **Smart Tools**
   - Readability score
   - Keyword density
   - Link checker

---

## FAQ

### **Q: Can I edit sections individually?**
A: Currently, you edit the full blog post. Section-by-section editing coming soon.

### **Q: Are my edits saved permanently?**
A: Edits are saved in session state. Download to save permanently.

### **Q: Can I undo changes?**
A: Yes, use Cmd/Ctrl+Z in the text area, or restore a previous version.

### **Q: Does the editor work on mobile?**
A: Yes, but desktop is recommended for better experience.

### **Q: Can I paste from Word?**
A: Yes, but formatting may need adjustment. Markdown is recommended.

---

## Support & Documentation

### **Related Docs:**
- `WYSIWYG_INTEGRATION.md` - Technical implementation details
- `CONTENT_QUALITY_IMPROVEMENTS.md` - Content generation improvements
- `ANALYTICS_DASHBOARD.md` - Analytics features

### **Get Help:**
- Check browser console for errors
- Verify blog post was generated
- Try refreshing the page
- Clear cache if issues persist

---

## Quick Reference

### **Editor Modes:**
- 📝 **Markdown Editor** - Edit with live preview
- 👁️ **Preview Only** - Read-only view

### **Actions:**
- 🔄 **Reset** - Restore original content
- 💾 **Save Version** - Create version snapshot
- 📥 **Download** - Export in various formats

### **Formats:**
- `.md` - Markdown
- `.html` - HTML
- `.txt` - Plain text
- `_medium.md` - Medium-ready

---

**Version**: 2.4  
**Last Updated**: October 2025  
**Status**: ✅ Ready to Use

**Next**: Install `streamlit-jodit` for full WYSIWYG features!
