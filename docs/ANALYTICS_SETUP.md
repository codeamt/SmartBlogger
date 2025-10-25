# Analytics Dashboard Setup Guide

## Quick Start

### 1. Install Plotly

```bash
# Option 1: Using uv (recommended)
uv pip install plotly>=5.18.0

# Option 2: Using pip
pip install plotly>=5.18.0

# Option 3: Sync from pyproject.toml
uv sync
```

### 2. Clear Cache

```bash
./clear_cache.sh
```

### 3. Restart App

```bash
uv run streamlit run app.py
```

### 4. Navigate to Analytics Tab

Once the app is running:
1. Generate a blog post (or use existing results)
2. Click the "Analytics" tab
3. Explore the four sub-tabs:
   - 📈 Token Usage
   - 🔬 Research Insights
   - 📝 Content Metrics
   - ⚡ Performance

---

## What's New

### **Enhanced Analytics Dashboard**

#### Top-Level KPIs (5 Cards)
- Total Tokens
- Word Count
- Sections
- Research Sources
- Avg Originality (with delta indicator)

#### Token Usage Tab
- 🍩 Donut chart of token distribution
- 📊 Bar chart comparison
- 💰 Cost estimation
- 📈 Progress bars per model

#### Research Insights Tab
- 📊 Colored bar chart by source
- 📈 Progress bars
- 🔍 Synthesis type indicator
- ✅ Introduction status
- 💡 Key insights count

#### Content Metrics Tab
- 📊 Word count bar chart per section
- 📋 Section details table
- 📖 Reading time estimate
- ✅ Status indicators (Complete/Pending)
- 📚 Citation tracking

#### Performance Tab
- 🎯 Gauge chart for avg originality
- 📊 Originality by section (color-coded)
- ⚡ First-pass success rate
- 💳 Credits tracking
- 🔄 Revision statistics

---

## Visual Examples

### Token Usage Donut Chart
```
         Writer (65.9%)
       /                \
      /                  \
Researcher (25.3%)    Structuring (8.8%)
```

### Originality Gauge
```
    100%
     |
  ✅ 87.3%  (Green zone)
     |
    80% ← Threshold
     |
    60%
     |
     0%
```

### Section Word Count
```
Introduction    ████████░░ 450 words
Implementation  ████████████████ 920 words
Best Practices  █████████████ 745 words
```

---

## Interactive Features

### All Charts Support:
- **Hover** - See exact values
- **Zoom** - Click and drag
- **Pan** - Shift + drag
- **Reset** - Double-click
- **Download** - Camera icon (PNG)
- **Legend** - Click to toggle

### Color Coding:
- **🔴 Red (0-60%)** - Poor originality
- **🟡 Yellow (60-80%)** - Fair originality
- **🟢 Green (80-100%)** - Good originality

---

## Troubleshooting

### Charts Not Showing?

**Solution 1: Install Plotly**
```bash
uv pip install plotly>=5.18.0
```

**Solution 2: Clear Cache**
```bash
./clear_cache.sh
# Or manually:
rm -rf ~/.streamlit/cache
find . -type d -name "__pycache__" -exec rm -rf {} +
```

**Solution 3: Restart App**
```bash
# Stop current app (Ctrl+C)
uv run streamlit run app.py
```

### "No Data Available" Messages?

This is normal if:
- No blog post has been generated yet
- Workflow didn't complete
- State wasn't saved properly

**Solution**: Generate a new blog post and check again.

### Layout Issues?

**Browser zoom**: Reset to 100% (Cmd+0 or Ctrl+0)
**Window size**: Expand browser window
**Mobile**: Some charts work better on desktop

---

## Performance Tips

### For Large Blog Posts (>10 sections):

1. **Token charts** may take 1-2s to render
2. **Section tables** are scrollable
3. **Originality charts** scale automatically

### Optimization:

- Charts render client-side (no server load)
- Data is already in memory (no extra queries)
- Caching is automatic (Streamlit handles it)

---

## Customization

### Change Colors

Edit `ui/analytics_display.py`:

```python
# Token usage
marker=dict(colors=px.colors.qualitative.Pastel)  # Softer colors

# Research
colorscale='Plasma'  # Purple-orange gradient

# Content
colorscale='Greens'  # Green gradient

# Originality
colorscale='RdBu'  # Red-blue diverging
```

### Adjust Thresholds

```python
# Change originality threshold from 80% to 85%
fig_bar.add_hline(y=85, line_dash="dash", line_color="red")

# Adjust gauge zones
'steps': [
    {'range': [0, 70], 'color': "lightcoral"},   # Poor
    {'range': [70, 85], 'color': "lightyellow"}, # Fair
    {'range': [85, 100], 'color': "lightgreen"}  # Good
]
```

### Change Cost Rate

```python
# Default: $0.001 per 1K tokens
est_cost = (total / 1000) * 0.001

# For GPT-4: $0.03 per 1K tokens
est_cost = (total / 1000) * 0.03
```

---

## Data Flow

```
Workflow Execution
    ↓
State Updates (token_usage, sections, etc.)
    ↓
Completion Node (aggregates metrics)
    ↓
Analytics Dashboard (visualizes data)
    ↓
Interactive Charts (Plotly)
```

---

## Dependencies

### Required:
- `plotly>=5.18.0` - Interactive charts
- `streamlit>=1.28.0` - Dashboard framework

### Optional:
- `pandas` - For advanced data manipulation (not currently used)

---

## Next Steps

1. ✅ Install plotly
2. ✅ Restart app
3. ✅ Generate a blog post
4. ✅ Explore analytics tabs
5. 📖 Read ANALYTICS_DASHBOARD.md for details
6. 🎨 Customize colors/thresholds if desired

---

## Support

### Documentation:
- `ANALYTICS_DASHBOARD.md` - Complete feature guide
- `WORKFLOW_GUIDE.md` - Overall workflow
- `CONTENT_QUALITY_IMPROVEMENTS.md` - Content improvements

### Issues:
- Check browser console for errors
- Verify plotly installation: `pip show plotly`
- Clear cache and restart
- Check state data in debug mode

---

**Version**: 2.3  
**Last Updated**: October 2025  
**Status**: ✅ Ready to Use
