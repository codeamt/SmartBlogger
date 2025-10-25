# SmartBlogger Workflow Guide

## Overview
SmartBlogger generates research-backed technical blog posts with customizable tone, style, and structure.

---

## Workflow Steps

### 1. **Input Phase**
**Sidebar Controls:**
- **Research Sources**: Select from Arxiv, Web, GitHub, Substack
- **Code Input**: Paste source code to analyze
- **File Upload**: Upload PDFs, markdown, text files
- **Research Focus**: Comma-separated topics to research

### 2. **Writing Style Configuration**
**Tone Options:**
- Professional
- Conversational
- Academic
- Tutorial
- Enthusiastic

**Target Audience:**
- Developers
- Technical Leaders
- Beginners
- General Tech Audience
- Researchers

**Style Preferences** (multi-select):
- Include code examples
- Add diagrams/visuals
- Step-by-step guides
- Real-world examples
- Comparative analysis

**Custom Questions:**
- Add specific questions you want answered
- Use ➕ button to add, 🗑️ to remove
- Questions are integrated into section drafts

### 3. **Generation Process**
**Automated Steps:**
1. **Input Processing**: Analyzes code/documents
2. **Research Coordination**: Plans research queries
3. **Research Execution**: Searches selected sources
4. **Blog Structuring**: Creates section outline
5. **Section Drafting**: Writes each section with citations
6. **Plagiarism Check**: Validates originality
7. **Completion**: Assembles final polished post

### 4. **Output Structure**
**Final Blog Post Includes:**
- Auto-generated title
- Intro hook (if needed)
- All sections with proper headings
- Code examples (if requested)
- Citations with [^n] notation
- Auto-generated conclusion (if needed)
- References section

---

## UI Panels

### **Generated Blog Content Tab**
**Metrics:**
- Total sections count
- Total word count
- Completion status

**Features:**
- 📥 Download button (markdown format)
- 📄 Full blog preview (collapsible)
- 📑 Sections breakdown with:
  - Section number and title
  - Word count per section
  - Section description
  - Revision history (if any)

### **Research Details Tab**
**Organized by Source:**
- Arxiv papers (with authors, publication date)
- Web results (with URLs)
- GitHub repos (with stars, language)
- Substack posts (with author, date)

**Debug Tools:**
- Raw research context JSON
- Source-by-source breakdown

### **Analytics Tab**
- Token usage tracking
- Performance metrics
- Resource utilization

### **Plagiarism Tab**
- Originality scores
- Flagged phrases
- Revision suggestions

---

## Tips for Best Results

### Research Focus
- Be specific: "React hooks best practices, performance optimization"
- Include technical terms relevant to your code
- Add 2-4 topics for comprehensive coverage

### Custom Questions
- Ask specific technical questions
- Example: "How does this compare to Redux?"
- Example: "What are the performance implications?"

### Tone Selection
- **Professional**: Technical documentation, enterprise blogs
- **Conversational**: Developer blogs, tutorials
- **Academic**: Research papers, deep dives
- **Tutorial**: Step-by-step guides, how-tos
- **Enthusiastic**: Community posts, announcements

### Style Preferences
- Select multiple for richer content
- "Code examples" + "Real-world examples" = practical posts
- "Step-by-step" + "Comparative analysis" = comprehensive guides

---

## Troubleshooting

### Cache Issues
If you see old errors or stale content:
```bash
./clear_cache.sh
uv run streamlit run app.py
```

Or manually:
- Menu → Settings → Clear cache
- Restart the app

### Research Returns Empty
- Check Health panel: Perplexity API should show "Detected"
- Verify .env has PERPLEXITY_API_KEY
- Try different research sources
- Broaden research focus topics

### Sections Echo Requirements
- Already fixed in latest version
- Clear cache and restart if you see this

### Model Errors
- Check Health panel for Ollama status
- Verify selected models are available
- Use "Refresh Models" button

---

## File Structure

```
SmartBlogger/
├── app.py                    # Main entry point
├── workflow.py               # LangGraph workflow definition
├── state.py                  # State model with all fields
├── state_management.py       # Session state handling
├── config.py                 # Configuration & env loading
├── nodes/
│   ├── input_processing.py   # Code/doc analysis
│   ├── research/
│   │   ├── coordinator.py    # Research planning
│   │   ├── perplexity.py     # Web search
│   │   ├── arxiv.py          # Academic papers
│   │   ├── github.py         # Repo search
│   │   └── substack.py       # Newsletter search
│   ├── drafting.py           # Section writing
│   ├── plagiarism.py         # Originality checks
│   └── completion.py         # Final assembly
├── ui/
│   ├── sidebar.py            # Input controls
│   ├── content_display.py    # Blog output
│   ├── research_display.py   # Research results
│   ├── analytics_display.py  # Metrics
│   └── dashboard.py          # Main layout
└── utils/
    ├── formatting.py         # Research formatting
    ├── token_tracking.py     # Usage tracking
    └── memory_management.py  # Optimization
```

---

## Recent Improvements

### ✅ Enhanced Sidebar
- Tone selector with 5 options
- Target audience selector
- Multi-select style preferences
- Dynamic custom questions with add/remove

### ✅ Improved Prompts
- No more echoed requirements
- Tone and audience integrated
- Custom questions addressed
- Clearer output instructions

### ✅ Polished Output
- Auto-generated title
- Intro hook
- Section flow
- Auto-generated conclusion
- Formatted references

### ✅ Better UI
- Metrics at top
- Prominent download button
- Collapsible sections
- Word counts per section
- Compact, readable layout

### ✅ Fixed Workflow
- draft_section routing corrected
- Multi-section loop works
- Perplexity model fallback
- arXiv package migration

---

## Environment Variables

Required in `.env`:
```bash
PERPLEXITY_API_KEY=sk-xxxxx
```

Optional:
```bash
PERPLEXITY_MODEL=sonar          # Default model
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Next Steps

### Planned Enhancements
- Progressive status indicators
- AI-generated section transitions
- LLM-powered title generation
- SEO metadata generation
- Export to multiple formats (HTML, PDF)
- Diagram generation support

### Feedback Welcome
- Report issues via GitHub
- Suggest features
- Share example outputs

---

**Version**: 2.0  
**Last Updated**: October 2025
