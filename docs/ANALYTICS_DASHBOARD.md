# Analytics Dashboard Documentation

## Overview

The Analytics Dashboard provides comprehensive insights into blog post generation with interactive Plotly visualizations, KPIs, and performance metrics.

---

## Dashboard Layout

### **Top-Level KPI Cards**

Five key metrics displayed prominently at the top:

1. **Total Tokens** - Total tokens used across all models
2. **Word Count** - Total words in final blog post
3. **Sections** - Number of sections generated
4. **Research Sources** - Total research results collected
5. **Avg Originality** - Average plagiarism check score with delta indicator

---

## Four Main Tabs

### 📈 **Token Usage Tab**

#### Visualizations:
1. **Donut Chart** - Token distribution by model
2. **Progress Bars** - Per-model breakdown with percentages
3. **Bar Chart** - Token usage comparison

#### Metrics:
- Total tokens used
- Estimated cost ($0.001 per 1K tokens)
- Per-model token counts
- Percentage distribution

#### Example Output:
```
Total Tokens: 12,450
Est. Cost: $0.0125

Writer Model: 8,200 tokens (65.9%)
Researcher Model: 3,150 tokens (25.3%)
Structuring Model: 1,100 tokens (8.8%)
```

---

### 🔬 **Research Insights Tab**

#### Visualizations:
1. **Colored Bar Chart** - Research results by source (Viridis colorscale)
2. **Progress Bars** - Source breakdown

#### Metrics:
- Total research results
- Results per source (arXiv, Web, GitHub, Substack)
- Synthesis type (academic, repository, newsletter, web)
- Introduction status (generated or missing)
- Key insights count

#### Example Output:
```
Total Results: 15

Web: 8 results (53.3%)
arXiv: 4 results (26.7%)
GitHub: 3 results (20.0%)

Synthesis Type: Academic
Introduction: ✅ Generated
Key Insights: 5
```

---

### 📝 **Content Metrics Tab**

#### Visualizations:
1. **Bar Chart** - Word count per section (Blues colorscale)
2. **Data Table** - Section details with status indicators

#### Metrics:
- Total sections
- Drafted sections
- Total citations
- Revised sections
- Total word count
- Average words per section
- Estimated reading time (200 words/min)

#### Section Details Table:
| Section | Words | Citations | Revised | Status |
|---------|-------|-----------|---------|--------|
| Introduction | 450 | ✅ | ❌ | ✅ Complete |
| Implementation | 920 | ✅ | ✅ | ✅ Complete |
| Best Practices | 745 | ✅ | ❌ | ✅ Complete |

#### Example Output:
```
Total Sections: 5
Drafted: 5
Citations: 12
Revised: 2

Total Words: 3,245
Avg Words/Section: 649
Est. Reading Time: 16.2 min
```

---

### ⚡ **Performance Tab**

#### Visualizations:
1. **Gauge Chart** - Average originality score with color zones
   - Red zone: 0-60% (Poor)
   - Yellow zone: 60-80% (Fair)
   - Green zone: 80-100% (Good)
   - Threshold line at 80%

2. **Bar Chart** - Originality score by section (RdYlGn colorscale)
   - Red = low originality
   - Yellow = medium originality
   - Green = high originality

#### Workflow Metrics:
- Total sections
- Plagiarism checked
- Revised sections
- First-pass success rate (% without revision)

#### Resource Usage:
- Total tokens
- Credits used
- Credits remaining
- Progress bar for credits

#### Example Output:
```
Workflow Metrics:
- Total Sections: 5
- Plagiarism Checked: 5
- Revised Sections: 2
- First-Pass Success: 60.0%

Resource Usage:
- Total Tokens: 12,450
- Credits Used: 25
- Credits Remaining: 75
[████████████████████████░░░░░░░░] 75%

Average Originality Score: 87.3%
↑ +7.3% from threshold
```

---

## Interactive Features

### **Plotly Charts**

All charts are interactive with:
- **Hover tooltips** - Show exact values on hover
- **Zoom/Pan** - Click and drag to zoom, double-click to reset
- **Legend toggle** - Click legend items to show/hide
- **Download** - Camera icon to save as PNG

### **Color Scales**

- **Token Usage**: Set3 qualitative palette (distinct colors)
- **Research**: Viridis (blue to yellow gradient)
- **Content**: Blues (light to dark blue)
- **Originality**: RdYlGn (red-yellow-green traffic light)

### **Responsive Design**

- Charts adapt to container width
- Mobile-friendly layouts
- Collapsible sections
- Scrollable tables

---

## KPI Calculations

### **Token Usage**
```python
total_tokens = sum(token_usage.values())
est_cost = (total_tokens / 1000) * 0.001  # $0.001 per 1K tokens
```

### **Word Count**
```python
final_content = completion_summary.get("final_content", "")
word_count = len(final_content.split())
```

### **Research Sources**
```python
by_source = research_context.get("by_source", {})
total_sources = sum(len(v) if isinstance(v, list) else 1 for v in by_source.values())
```

### **Average Originality**
```python
scores = [check.get("originality_score", 0) for check in plagiarism_checks.values()]
avg_originality = sum(scores) / len(scores) if scores else 0
```

### **Reading Time**
```python
reading_time = total_words / 200  # 200 words per minute average
```

### **First-Pass Success**
```python
efficiency = ((total_sections - revised_sections) / total_sections) * 100
```

---

## Color Coding

### **Originality Scores**

- **🔴 Red (0-60%)**: Poor originality, likely plagiarism
- **🟡 Yellow (60-80%)**: Fair originality, needs improvement
- **🟢 Green (80-100%)**: Good originality, acceptable

### **Status Indicators**

- **✅ Complete**: Section drafted successfully
- **⏳ Pending**: Section not yet drafted
- **❌ Missing**: Feature not present

### **Delta Colors**

- **Green arrow ↑**: Above threshold (good)
- **Red arrow ↓**: Below threshold (needs attention)

---

## Usage Examples

### **Scenario 1: High Token Usage**

If you see high token usage in one model:
1. Check the Token Usage tab
2. Identify which model is using most tokens
3. Review section word counts in Content Metrics
4. Consider reducing section length or research depth

### **Scenario 2: Low Originality**

If average originality is below 80%:
1. Check the Performance tab
2. View the gauge chart for overall score
3. Check the bar chart to identify problematic sections
4. Review those sections in the Plagiarism tab
5. Rewrite flagged sections

### **Scenario 3: Unbalanced Sections**

If sections have very different word counts:
1. Check the Content Metrics tab
2. View the word count bar chart
3. Identify outliers (too short or too long)
4. Adjust prompts or regenerate specific sections

---

## Data Sources

### **Token Usage**
- Source: `state.token_usage` (dict)
- Updated by: `track_token_usage()` in each node
- Format: `{"model_name": token_count}`

### **Research Context**
- Source: `state.research_context` (dict)
- Updated by: Research nodes
- Format: `{"by_source": {"arxiv": [...], "web": [...]}}`

### **Content Stats**
- Source: `state.sections`, `state.section_drafts`
- Updated by: Drafting and completion nodes
- Format: Lists and dicts with section data

### **Plagiarism Checks**
- Source: `state.plagiarism_checks` (dict)
- Updated by: Plagiarism check node
- Format: `{"section_id": {"originality_score": 85, ...}}`

### **Completion Summary**
- Source: `state.research_context.completion_summary`
- Updated by: Completion node
- Format: Dict with aggregated metrics

---

## Customization

### **Change Color Schemes**

In `analytics_display.py`:
```python
# Token usage colors
marker=dict(colors=px.colors.qualitative.Set3)

# Research colors
colorscale='Viridis'

# Content colors
colorscale='Blues'

# Originality colors
colorscale='RdYlGn'
```

Available Plotly color scales:
- Qualitative: Set1, Set2, Set3, Pastel, Dark2
- Sequential: Blues, Greens, Reds, Viridis, Plasma
- Diverging: RdYlGn, RdBu, Spectral

### **Adjust Thresholds**

```python
# Originality threshold (default: 80%)
fig_bar.add_hline(y=80, line_dash="dash", line_color="red")

# Gauge color zones
'steps': [
    {'range': [0, 60], 'color': "lightcoral"},   # Poor
    {'range': [60, 80], 'color': "lightyellow"}, # Fair
    {'range': [80, 100], 'color': "lightgreen"}  # Good
]
```

### **Change Cost Estimation**

```python
# Default: $0.001 per 1K tokens
est_cost = (total / 1000) * 0.001

# For different pricing:
est_cost = (total / 1000) * 0.002  # $0.002 per 1K tokens
```

---

## Performance Considerations

### **Chart Rendering**

- Plotly charts are rendered client-side
- Large datasets (>1000 points) may slow rendering
- Use `use_container_width=True` for responsive sizing

### **Data Processing**

- Calculations are performed on each render
- For large states, consider caching with `@st.cache_data`
- Token usage and word counts are lightweight

### **Memory Usage**

- Plotly charts are memory-efficient
- State data is already in memory
- No additional API calls required

---

## Troubleshooting

### **Charts Not Displaying**

1. Verify plotly is installed: `pip install plotly>=5.18.0`
2. Check browser console for JavaScript errors
3. Try clearing Streamlit cache: Menu → Settings → Clear cache

### **Incorrect Metrics**

1. Verify state data is populated
2. Check completion_summary exists
3. Ensure plagiarism checks ran
4. Review token tracking in nodes

### **Layout Issues**

1. Adjust column ratios: `st.columns([2, 1])`
2. Modify chart heights: `fig.update_layout(height=400)`
3. Use `st.divider()` for spacing

---

## Future Enhancements

### **Planned Features**

1. **Time Series** - Track metrics across multiple generations
2. **Export Reports** - Download analytics as PDF/CSV
3. **Comparison Mode** - Compare multiple blog posts
4. **Cost Tracking** - Detailed cost breakdown by operation
5. **Quality Score** - Composite score from multiple metrics
6. **Recommendations** - AI-powered suggestions for improvement

### **Advanced Visualizations**

1. **Sankey Diagram** - Token flow through workflow
2. **Heatmap** - Section quality matrix
3. **Radar Chart** - Multi-dimensional quality assessment
4. **Timeline** - Generation progress over time

---

## Dependencies

```toml
[dependencies]
plotly = ">=5.18.0"
streamlit = ">=1.28.0"
```

---

## API Reference

### **Main Function**

```python
def render_analytics(result_state: dict) -> None:
    """
    Render comprehensive analytics dashboard.
    
    Args:
        result_state: Complete workflow state dict
    """
```

### **Sub-Functions**

```python
def render_kpi_cards(result_state: dict) -> None:
    """Render top-level KPI cards"""

def render_token_analytics(result_state: dict) -> None:
    """Display token usage with visualizations"""

def render_research_analytics(result_state: dict) -> None:
    """Display research insights with visualizations"""

def render_content_analytics(result_state: dict) -> None:
    """Display content metrics with visualizations"""

def render_performance_analytics(result_state: dict) -> None:
    """Display workflow performance with visualizations"""
```

---

**Version**: 2.3  
**Last Updated**: October 2025  
**Status**: ✅ Production Ready
