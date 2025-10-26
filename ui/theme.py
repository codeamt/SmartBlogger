"""
Custom theme configuration inspired by Medium and Substack
"""

import streamlit as st


def apply_custom_theme():
    """Apply custom CSS theme inspired by Medium/Substack"""
    
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@300;400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Root tokens: improved dark theme with better contrast */
    :root {
      --bg-app: #0A0E13;
      --bg-surface: #111827;
      --bg-subtle: #1A202C;
      --bg-card: #2D3748;
      --text-primary: #F9FAFB;  /* gray-50 */
      --text-secondary: #D1D5DB; /* gray-300 */
      --text-tertiary: #9CA3AF;  /* gray-400 */
      --accent: #6B7280;         /* gray-500 */
      --accent-hover: #4B5563;   /* gray-600 */
      --accent-light: #9CA3AF;   /* gray-400 */
      --success: #10B981;        /* emerald-500 */
      --warning: #F59E0B;        /* amber-500 */
      --error: #EF4444;          /* red-500 */
      --border: #1F2937;         /* gray-700 */
      --border-strong: #4B5563;  /* gray-600 */
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.6);
    }

    /* App background and base text rendering */
    .stApp { background: var(--background); -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }

    /* Main container */
    .main .block-container {
      max-width: 1200px;
      background: var(--background);
      border-radius: var(--radius);
      box-shadow: var(--shadow-md);
      padding: 2.5rem 2rem !important;
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
    h1 { font-size: 2.0rem !important; line-height: 1.2 !important; margin: 0.2rem 0 0.4rem; }
    h2 { font-size: 1.5rem !important; line-height: 1.3 !important; margin: 0.8rem 0 0.4rem; }
    h3 { font-size: 1.15rem !important; line-height: 1.35 !important; margin: 0.6rem 0 0.3rem; }
    p, .stMarkdown, div[data-testid="stMarkdownContainer"] {
      font-family: 'Source Serif 4', Georgia, serif !important;
      font-size: 1.0rem !important; line-height: 1.7 !important; color: var(--foreground) !important;
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

    /* Buttons */
    .stButton > button {
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
    .stButton > button:hover { 
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
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb] {
      background: var(--background) !important; 
      color: var(--foreground) !important;
      border: 1px solid transparent !important; 
      border-bottom: 1px solid var(--border) !important;
      border-radius: 0 !important; 
      box-shadow: none !important;
      padding: 0.5rem 0.75rem !important;
      font-size: 0.9rem !important;
      transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb]:focus { 
      outline: none !important; 
      border: 1px solid var(--primary) !important; 
      border-bottom: 1px solid var(--primary) !important;
      box-shadow: 0 0 0 2px var(--ring) !important; 
      background: var(--secondary) !important;
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
        "primaryColor": "#4B5563",   # primary color
        "backgroundColor": "#0A0E13",
        "secondaryBackgroundColor": "#111827",
        "textColor": "#F9FAFB",
        "font": "sans serif"
    }
