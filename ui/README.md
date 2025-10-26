# SmartBlogger UI Components

## Overview
This directory contains all UI components for the SmartBlogger application, designed with a Medium/Substack-inspired aesthetic for an optimal writing experience.

## Components

### `theme.py`
Custom CSS theme with Medium/Substack color palette.

**Key Features:**
- Serif typography (Source Serif 4) for content
- Sans-serif typography (Inter) for UI elements
- Medium green (#1A8917) and Substack orange (#FF6719) accents
- Comprehensive component styling

**Usage:**
```python
from ui.theme import apply_custom_theme
apply_custom_theme()  # Call in main app
```

### `dashboard.py`
Main content area with welcome screen and results display.

**Components:**
- `render_main_content()` - Routes to welcome or results
- `render_welcome_screen()` - Elegant landing page with feature cards
- `render_results_tabs()` - Tabbed interface for generated content

**Design Highlights:**
- Hero section with centered typography
- Gradient feature cards
- Clean getting started guide
- Tag-style example topics

### `sidebar.py`
Left sidebar for user inputs and configuration.

**Components:**
- `render_sidebar()` - Main sidebar rendering function
- `process_uploaded_files()` - File upload handling

**Sections:**
- Research sources selection
- Source content input
- Document upload
- Research focus topics
- Writing style preferences
- Custom questions
- Model information
- Generate/Reset buttons

**Design Highlights:**
- Centered branding header
- Minimal section labels
- Collapsed input labels for clean look
- Styled model info box

### `content_display.py`
Display generated blog content with sections.

**Components:**
- `render_blog_content()` - Main content display
- `render_section_compact()` - Individual section rendering
- `render_revision_history()` - Version history display

**Design Highlights:**
- Gradient metrics card
- Pro tip call-to-action box
- Prominent download button
- Collapsible section breakdown

### `editor_display.py`
Writing-focused editor with live preview.

**Components:**
- `render_editor()` - Main editor interface
- `render_markdown_editor()` - Split-view editor with preview
- `render_preview_only()` - Read-only preview mode
- `render_action_buttons()` - Export and save actions
- `render_version_history()` - Version management

**Design Highlights:**
- Elegant empty state
- Word/character count stats
- Side-by-side editor and preview
- Multiple export formats
- Clean action buttons

### `research_display.py`
Display research findings and sources.

**Components:**
- Research results from various sources
- Source attribution and links

### `plagiarism_display.py`
Plagiarism detection results.

**Components:**
- Similarity scores
- Flagged content
- Rewrite suggestions

### `analytics_display.py`
Content analytics and metrics.

**Components:**
- Readability scores
- Word frequency
- Content statistics

## Design System

### Typography
- **Content**: Source Serif 4 (serif)
- **UI**: Inter (sans-serif)
- **Code**: SF Mono, Monaco (monospace)

### Colors
- **Primary**: #1A8917 (Medium green)
- **Secondary**: #FF6719 (Substack orange)
- **Text**: #242424, #6B6B6B, #8B8B8B
- **Background**: #FFFFFF, #F7F7F7, #FAFAFA
- **Borders**: #E6E6E6, #D4D4D4

### Spacing
- Small: 0.5rem
- Medium: 1rem
- Large: 2rem
- XLarge: 4rem

### Components
- **Buttons**: Rounded (24px), shadows, hover effects
- **Cards**: 8-12px radius, subtle shadows
- **Inputs**: 6px radius, focus states
- **Containers**: Consistent padding

## Best Practices

1. **Consistency**: Use the theme system for all styling
2. **Accessibility**: Maintain color contrast ratios
3. **Responsiveness**: Test on different screen sizes
4. **Performance**: Minimize custom CSS where possible
5. **Maintainability**: Document custom styling decisions

## Adding New Components

When creating new UI components:

1. Import the theme: `from ui.theme import apply_custom_theme`
2. Use semantic HTML in markdown for custom styling
3. Follow the established color palette
4. Maintain typography hierarchy
5. Add component documentation here

## Testing

Test UI components with:
- Different content lengths
- Various screen sizes
- Light/dark system preferences
- Different browsers

## Future Improvements

- [ ] Dark mode support
- [ ] More streamlit-shadcn-ui components
- [ ] Animation and transitions
- [ ] Component library
- [ ] Theme customization options
