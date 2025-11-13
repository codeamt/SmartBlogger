"""
Custom theme configuration inspired by Medium and Substack
"""

import streamlit as st


def apply_custom_theme():
    """Apply custom CSS theme inspired by Medium/Substack"""
    
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@300;400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Root tokens: Dark theme with Indigo accent (comfortable density) */
    :root {
      /* Core surfaces */
      --background: hsl(224 14% 12%);     /* dark slate */
      --foreground: hsl(210 20% 98%);
      --card: hsl(220 12% 16%);
      --card-foreground: var(--foreground);
      --popover: hsl(220 12% 16%);
      --popover-foreground: var(--foreground);

      /* Indigo accent */
      --primary: hsl(239 84% 67%);        /* indigo-500 */
      --primary-foreground: hsl(240 10% 10%);
      --ring: hsl(239 84% 67%);

      /* Secondary/muted */
      --secondary: hsl(222 14% 20%);
      --secondary-foreground: var(--foreground);
      --muted: hsl(222 12% 24%);
      --muted-foreground: hsl(215 16% 75%);
      --accent: hsl(222 12% 28%);
      --accent-foreground: var(--foreground);

      /* Status colors */
      --success: hsl(158 64% 52%);        /* emerald-400 */
      --warning: hsl(43 96% 56%);         /* amber-400 */
      --error: hsl(0 84% 60%);            /* red-500 */
      --destructive: var(--error);
      --destructive-foreground: hsl(0 0% 98%);

      /* Borders / inputs */
      --border: hsl(222 12% 28%);
      --input: var(--border);

      /* Radii / shadows */
      --radius: 0.6rem;
      --shadow-sm: 0 1px 2px hsla(0,0%,0%,0.25);
      --shadow-md: 0 8px 20px hsla(0,0%,0%,0.35);
      --shadow-lg: 0 16px 32px hsla(0,0%,0%,0.45);

      /* Compatibility aliases (keep existing CSS working) */
      --bg-app: var(--background);
      --bg-surface: var(--card);
      --bg-subtle: var(--secondary);
      --bg-card: var(--card);
      --text-primary: var(--foreground);
      --text-secondary: var(--muted-foreground);
      --text-tertiary: var(--muted-foreground);
      
      /* Sidebar tokens for consistent look */
      --sidebar: var(--card);
      --sidebar-foreground: var(--foreground);
      --sidebar-border: var(--border);
      --sidebar-accent: var(--secondary);
    }

    /* Optional light alias if ever needed */
    .light {
      --background: hsl(0 0% 100%);
      --foreground: hsl(240 10% 3.9%);
      --card: hsl(0 0% 100%);
      --card-foreground: hsl(240 10% 3.9%);
      --popover: hsl(0 0% 100%);
      --popover-foreground: hsl(240 10% 3.9%);
      --primary: hsl(239 84% 59%);
      --primary-foreground: hsl(0 0% 98%);
      --ring: hsl(239 84% 59%);
      --secondary: hsl(240 4.8% 95.9%);
      --secondary-foreground: hsl(240 5.9% 10%);
      --muted: hsl(240 4.8% 95.9%);
      --muted-foreground: hsl(240 3.8% 46.1%);
      --accent: hsl(240 4.8% 95.9%);
      --accent-foreground: hsl(240 5.9% 10%);
      --success: hsl(158 64% 42%);
      --warning: hsl(43 96% 50%);
      --error: hsl(0 84% 60%);
      --destructive: var(--error);
      --destructive-foreground: hsl(0 0% 98%);
      --border: hsl(240 5.9% 90%);
      --input: hsl(240 5.9% 90%);
      --radius: 0.6rem;
      --shadow-sm: 0 1px 2px hsla(0,0%,0%,0.10);
      --shadow-md: 0 8px 20px hsla(0,0%,0%,0.15);
      --shadow-lg: 0 16px 32px hsla(0,0%,0%,0.2);

      /* Aliases */
      --bg-app: var(--background);
      --bg-surface: var(--card);
      --bg-subtle: var(--secondary);
      --bg-card: var(--card);
      --text-primary: var(--foreground);
      --text-secondary: var(--muted-foreground);
      --text-tertiary: var(--muted-foreground);
    }

    /* App background and base text rendering */
    .stApp { background: var(--background); -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }

    /* Main container (comfortable density) */
    .main .block-container {
      max-width: 1200px;
      background: var(--background);
      border-radius: var(--radius);
      box-shadow: var(--shadow-md);
      padding: 1.75rem 1.25rem !important;
      margin: 1rem auto;
      border: 1px solid var(--border);
    }

    .stMainBlockContainer { 
      margin-top: 2rem !important; 
      padding-top: 1rem !important; 
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
      background: var(--sidebar);
      border-right: 1px solid var(--sidebar-border);
      padding: 1.5rem 1.25rem;
      box-shadow: var(--shadow-sm);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
      font-family: Inter, ui-sans-serif, system-ui;
      font-size: 0.95rem !important; font-weight: 600 !important;
      text-transform: none; letter-spacing: 0.01em;
      color: var(--sidebar-foreground) !important; margin-bottom: 0.6rem !important;
    }

    /* Sidebar markdown spacing tweaks */

    /* Sidebar expanders */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
      border: 1px solid var(--sidebar-border);
      border-radius: var(--radius);
      background: var(--sidebar-accent);
      box-shadow: var(--shadow-sm);
      margin-bottom: 0.75rem;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
      font-family: Inter, ui-sans-serif, system-ui;
      font-weight: 600;
      color: var(--sidebar-foreground);
    }
    [data-testid="stSidebar"] .stExpander p { margin-bottom: 0.25rem !important; }
    [data-testid="stSidebar"] ul { margin: 0 0 0.5rem 1.25rem !important; }
    [data-testid="stSidebar"] li { margin-bottom: 0.25rem !important; }

    /* Sidebar Ollama toggle button styling (match secondary/browse files look) */
    [data-testid="stSidebar"] .ollama-status .stButton > button {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      padding: 0.35rem 0.6rem !important;
      height: auto !important;
      line-height: 1.1 !important;
      font-size: 0.9rem !important;
      border-radius: calc(var(--radius) - 0.1rem) !important;
      background: transparent !important;
      color: var(--sidebar-foreground) !important;
      border: 1px solid var(--sidebar-border) !important;
      box-shadow: none !important;
      min-width: auto !important;
      width: auto !important;
      white-space: nowrap !important;
    }
    [data-testid="stSidebar"] .ollama-status .stButton > button:hover {
      background: var(--sidebar-accent) !important;
    }
    /* Also target Streamlit's base button test-id for reliability */
    [data-testid="stSidebar"] .ollama-status [data-testid="stBaseButton-secondary"] {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      padding: 0.35rem 0.6rem !important;
      height: auto !important;
      line-height: 1.1 !important;
      font-size: 0.9rem !important;
      border-radius: calc(var(--radius) - 0.1rem) !important;
      background: transparent !important;
      color: var(--sidebar-foreground) !important;
      border: 1px solid var(--sidebar-border) !important;
      box-shadow: none !important;
      min-width: auto !important;
      width: auto !important;
      white-space: nowrap !important;
    }
    [data-testid="stSidebar"] .ollama-status [data-testid="stBaseButton-secondary"]:hover {
      background: var(--sidebar-accent) !important;
    }
    /* Ensure the button column is right aligned */
    [data-testid="stSidebar"] .ollama-status [data-testid="column"]:last-child {
      text-align: right !important;
    }
    /* Remove extra left padding/margins from the button column inside Ollama status */
    [data-testid="stSidebar"] .ollama-status [data-testid="column"]:last-child {
      padding-left: 0 !important;
      margin-left: 0 !important;
    }
    [data-testid="stSidebar"] .ollama-status .stButton { margin: 0 !important; }

    /* Typography */
    h1, h2, h3, h4 { font-family: Inter, ui-sans-serif, system-ui !important; color: var(--foreground) !important; font-weight: 600 !important; }
    h1 { font-size: 1.75rem !important; line-height: 1.25 !important; margin: 0.25rem 0 0.5rem; }
    h2 { font-size: 1.35rem !important; line-height: 1.3 !important; margin: 0.75rem 0 0.4rem; }
    h3 { font-size: 1.05rem !important; line-height: 1.35 !important; margin: 0.5rem 0 0.3rem; }
    p, .stMarkdown, div[data-testid="stMarkdownContainer"] {
      font-family: Inter, ui-sans-serif, system-ui !important;
      font-size: 0.98rem !important; line-height: 1.7 !important; color: var(--foreground) !important;
    }
    button, input, select, textarea { font-family: Inter, ui-sans-serif, system-ui !important; }

    /* Panels (generic containers) */
    .stContainer { 
      border: 1px solid var(--border) !important; 
      background: var(--card) !important; 
      border-radius: var(--radius) !important;
      box-shadow: var(--shadow-sm) !important;
      padding: 1.5rem !important;
    }

    /* Global expanders (outside sidebar) */
    [data-testid="stExpander"] {
      border: 1px solid var(--border) !important;
      border-radius: var(--radius) !important;
      background: var(--card) !important;
      box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stExpander"] summary {
      font-family: Inter, ui-sans-serif, system-ui !important;
      font-weight: 600 !important;
      color: var(--foreground) !important;
    }

    /* Buttons */
    .stButton > button,
    [data-testid="stBaseButton-primary"] {
      background: var(--primary); 
      color: var(--primary-foreground); 
      border: 1px solid var(--primary);
      border-radius: var(--radius); 
      padding: 0.75rem 1.5rem; 
      font-weight: 600; 
      font-size: 0.95rem;
      transition: all 0.2s ease; 
      box-shadow: var(--shadow-sm);
      min-height: 44px;
    }
    .stButton > button:hover,
    [data-testid="stBaseButton-primary"]:hover { 
      background: var(--primary); 
      border-color: var(--primary); 
      transform: translateY(-2px); 
      box-shadow: var(--shadow-md);
    }
    .stButton > button[kind="secondary"] { 
      background: var(--secondary); 
      color: var(--secondary-foreground); 
      border: 1px solid var(--border); 
    }
    .stButton > button[kind="secondary"]:hover { 
      background: var(--accent); 
      border-color: var(--border);
    }

    /* Text selection highlight */
    ::selection { background: var(--accent); color: #0B0F14; }

    /* Inputs */
    input[type="range"], input[type="checkbox"], input[type="radio"] {
      accent-color: var(--primary) !important;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb] {
      background: var(--secondary) !important; 
      color: var(--foreground) !important;
      border: 1px solid var(--border) !important; 
      border-radius: var(--radius) !important; 
      box-shadow: inset 0 0 0 1px rgba(0,0,0,0.25) !important;
      padding: 0.6rem 0.8rem !important;
      font-size: 0.95rem !important;
      transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb]:focus { 
      outline: none !important; 
      border: 1px solid var(--primary) !important; 
      border-bottom: 1px solid var(--primary) !important;
      box-shadow: 0 0 0 2px var(--ring) !important; 
      background: var(--secondary) !important;
    }

    /* Sidebar variants for inputs/selects */
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stTextArea textarea,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb] {
      background: var(--sidebar) !important;
      border: 1px solid var(--sidebar-border) !important;
      box-shadow: inset 0 0 0 1px rgba(0,0,0,0.25) !important;
    }

    /* Enforce indigo for radios/checkboxes in sidebar */
    [data-testid="stSidebar"] input[type="radio"],
    [data-testid="stSidebar"] input[type="checkbox"] {
      accent-color: var(--primary) !important;
    }
    /* BaseWeb radio (Streamlit) - ensure checked state uses indigo */
    [data-testid="stSidebar"] [data-baseweb="radio"] [role="radio"] svg {
      color: var(--muted-foreground) !important;
      stroke: var(--muted-foreground) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] [role="radio"][aria-checked="true"] svg {
      color: var(--primary) !important;
      fill: var(--primary) !important;
      stroke: var(--primary) !important;
    }

    /* Slider label text tone in sidebar */
    [data-testid="stSidebar"] [data-testid="stSlider"] span {
      color: var(--muted-foreground) !important;
    }
    /* Slider hover/focus value bubble (best-effort) */
    [data-testid="stSlider"] [data-testid*="Value"],
    [data-testid="stSlider"] .value,
    [data-testid="stSlider"] .stSliderValue {
      color: var(--foreground) !important;
      background: transparent !important;
      text-shadow: none !important;
    }
    /* Select dropdown popover */
    .stSelectbox [role="listbox"], .stMultiSelect [role="listbox"] {
      background: var(--card) !important;
      color: var(--foreground) !important;
      border: 1px solid var(--border) !important;
    }
    /* Slider general styles */
    [data-testid="stSlider"] div[role="slider"],
    [data-testid="stSlider"] .stSlider {
      accent-color: var(--primary) !important;
    }
    /* Force BaseWeb slider colors via role attributes */
    [data-testid="stSlider"] div[role="slider"] {
      background: var(--primary) !important;
      border: 2px solid var(--background) !important;
      box-shadow: 0 0 0 2px var(--primary) !important;
    }
    /* Rail and track heuristics */
    [data-testid="stSlider"] div[aria-hidden="true"] {
      background: var(--muted) !important;
    }
    /* Selected (filled) track often uses aria-hidden=true + transform width; bump to primary using inline style matcher */
    [data-testid="stSlider"] div[aria-hidden="true"][style*="background"] {
      background: var(--primary) !important;
    }

    /* Slider cross-browser styling */
    input[type="range"]::-webkit-slider-runnable-track {
      background: var(--muted) !important;
      height: 4px; border-radius: 9999px;
    }
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none; appearance: none;
      margin-top: -6px; /* center on 4px track */
      width: 16px; height: 16px; border-radius: 9999px;
      background: var(--primary) !important;
      border: 2px solid var(--background) !important;
      box-shadow: 0 0 0 2px var(--primary) !important;
    }
    input[type="range"]::-moz-range-track {
      background: var(--muted) !important;
      height: 4px; border-radius: 9999px;
    }
    input[type="range"]::-moz-range-progress {
      background: var(--primary) !important;
      height: 4px; border-radius: 9999px;
    }
    input[type="range"]::-moz-range-thumb {
      width: 16px; height: 16px; border-radius: 9999px;
      background: var(--primary) !important;
      border: 2px solid var(--background) !important;
    }

    /* Multiselect chips match primary button color */
    .stMultiSelect [data-baseweb="tag"] {
      background: var(--primary) !important; 
      color: var(--primary-foreground) !important; 
      border-radius: var(--radius); 
      padding: 4px 12px;
      font-weight: 500;
      box-shadow: var(--shadow-sm);
    }

    /* Textarea focus ring and border (avoid red) */
    .stTextArea textarea { 
      border: 1px solid var(--border) !important; 
      border-radius: var(--radius) !important; 
      background: var(--background) !important; 
    }
    .stTextArea textarea:focus, .stTextArea textarea:focus-visible {
      outline: none !important;
      border-color: var(--primary) !important;
      box-shadow: 0 0 0 2px var(--ring) !important;
    }

    /* File uploader primary action */
    [data-testid="stFileUploader"] {
      background: var(--card) !important;
      border: 1px solid var(--border) !important;
      border-radius: var(--radius) !important;
    }
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] [data-testid^="stBaseButton-"] {
      background: var(--primary) !important;
      color: var(--primary-foreground) !important;
      border: 1px solid var(--primary) !important;
      border-radius: var(--radius) !important;
    }
    [data-testid="stFileUploader"] button:hover,
    [data-testid="stFileUploader"] [data-testid^="stBaseButton-"]:hover {
      box-shadow: var(--shadow-md) !important;
      transform: translateY(-1px);
    }

    /* shadcn-ui component overrides */
    .shadcn-ui-select-trigger {
      background: var(--background) !important;
      color: var(--foreground) !important;
      border: 1px solid var(--border) !important;
      border-radius: var(--radius) !important;
    }
    .shadcn-ui-select-trigger:focus {
      border-color: var(--primary) !important;
      box-shadow: 0 0 0 2px var(--ring) !important;
    }
    .shadcn-ui-select-content, .shadcn-ui-select-viewport {
      background: var(--card) !important;
      color: var(--foreground) !important;
      border: 1px solid var(--border) !important;
    }
    .shadcn-ui-button[data-variant="default"], .shadcn-ui-button.primary {
      background: var(--primary) !important;
      color: var(--primary-foreground) !important;
      border: 1px solid var(--primary) !important;
    }
    .shadcn-ui-button[data-variant="secondary"], .shadcn-ui-button.secondary {
      background: var(--secondary) !important;
      color: var(--secondary-foreground) !important;
      border: 1px solid var(--border) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { 
      gap: 8px; 
      border-bottom: 1px solid var(--border-strong); 
      background: transparent; 
      padding: 0.5rem 0; 
    }
    .stTabs [data-baseweb="tab"] { 
      font-family: Inter; 
      font-size: 0.95rem; 
      color: var(--text-secondary); 
      padding: 0.75rem 1.25rem; 
      border-radius: 12px 12px 0 0; 
      transition: all 0.2s ease;
      font-weight: 500;
    }
    .stTabs [data-baseweb="tab"]:hover { 
      color: var(--text-primary); 
      background: var(--bg-subtle); 
    }
    .stTabs [aria-selected="true"] { 
      color: var(--accent) !important; 
      border-bottom: 3px solid var(--accent); 
      background: var(--bg-subtle);
      font-weight: 600;
    }

    /* Badges (pills) */
    .shadcn-ui-badge { background: var(--bg-subtle) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; }
    .shadcn-ui-badge:hover { background: #141922 !important; }

    /* Lists (installed models) */
    .list-row:hover { background: rgba(255,255,255,0.02); }

    /* Alerts */
    .stAlert { 
      border: 1px solid var(--border); 
      background: var(--card); 
      color: var(--card-foreground); 
      border-radius: var(--radius); 
      box-shadow: var(--shadow-sm);
      padding: 1rem;
    }

    /* Code */
    code { 
      background: var(--card); 
      color: var(--muted-foreground); 
      padding: 0.25rem 0.5rem; 
      border-radius: calc(var(--radius) - 0.1rem); 
      font-size: 0.9em;
      border: 1px solid var(--border);
    }
    pre { 
      background: var(--background); 
      border: 1px solid var(--border); 
      border-radius: var(--radius); 
      padding: 1.5rem; 
      box-shadow: var(--shadow-sm);
      overflow-x: auto;
    }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--secondary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: calc(var(--radius) - 0.1rem); }
    ::-webkit-scrollbar-thumb:hover { background: var(--muted-foreground); }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)


def get_theme_config():
    """Return Streamlit theme configuration"""
    return {
        # Indigo accent on dark background
        "primaryColor": "#6366F1",                # indigo-500
        "backgroundColor": "#0F1220",             # matches hsl(224 14% 12%) approx
        "secondaryBackgroundColor": "#1B2230",    # matches card surface
        "textColor": "#F1F5F9",                   # near slate-50
        "font": "sans serif"
    }
