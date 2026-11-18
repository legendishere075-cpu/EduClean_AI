"""
EduClean AI — Theme & Styling Module
Provides CSS custom properties, component overrides, and layout polish
for the full Streamlit dashboard.
"""

import streamlit as st


def get_theme_css() -> str:
    """Return the complete CSS string for the EduClean AI theme."""
    return """
<style>
/* ═══════════════════════════════════════════════
   CSS CUSTOM PROPERTIES
═══════════════════════════════════════════════ */
:root {
    --bg-primary:    #0a0e1a;
    --bg-secondary:  #0d1424;
    --bg-card:       #111827;
    --accent-blue:   #3b82f6;
    --accent-cyan:   #06b6d4;
    --text-primary:  #f1f5f9;
    --text-secondary:#94a3b8;
    --border-color:  #1e293b;
    --radius-card:   14px;
    --shadow-card:   0 4px 24px rgba(0,0,0,0.45);
    --transition:    all 0.22s cubic-bezier(.4,0,.2,1);
}

/* ═══════════════════════════════════════════════
   HIDE DEFAULT STREAMLIT CHROME
═══════════════════════════════════════════════ */
#MainMenu,
header[data-testid="stHeader"],
footer,
[data-testid="stToolbar"],
[data-testid="collapsedControl"] > button:first-child,
.stDeployButton { display: none !important; }

/* ═══════════════════════════════════════════════
   GLOBAL APP BACKGROUND
═══════════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

[data-testid="stAppViewContainer"] > section.main {
    padding-top: 1.2rem;
}

/* ═══════════════════════════════════════════════
   CUSTOM SCROLLBAR
═══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* ═══════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #060b18 !important;
    border-right: 1px solid var(--border-color);
    min-width: 260px !important;
    max-width: 260px !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0;
}

/* Sidebar scrollbar */
[data-testid="stSidebar"] ::-webkit-scrollbar { width: 3px; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: var(--border-color);
}

/* Logo area */
.sidebar-logo {
    padding: 1.4rem 1.2rem 1rem;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 0.6rem;
}
.sidebar-logo-title {
    font-size: 1.35rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.sidebar-logo-tagline {
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
    letter-spacing: 0.03em;
    font-style: italic;
}

/* Nav section header */
.nav-section-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 0.9rem 1.2rem 0.4rem;
}

/* Nav buttons — override Streamlit defaults */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.6rem 1.2rem !important;
    margin: 0.08rem 0 !important;
    transition: var(--transition) !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    border-left: 3px solid transparent !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59, 130, 246, 0.08) !important;
    color: var(--text-primary) !important;
    border-left: 3px solid rgba(59, 130, 246, 0.4) !important;
}

/* Active nav button — applied via a wrapper class .nav-active */
[data-testid="stSidebar"] .nav-active .stButton > button {
    background: rgba(59, 130, 246, 0.12) !important;
    color: var(--accent-blue) !important;
    border-left: 3px solid var(--accent-blue) !important;
    font-weight: 600 !important;
}

/* Sidebar footer */
.sidebar-footer {
    padding: 1rem 1.2rem;
    border-top: 1px solid var(--border-color);
    margin-top: auto;
}
.sidebar-footer-text {
    font-size: 0.7rem;
    color: var(--text-secondary);
    text-align: center;
    opacity: 0.7;
}

/* ═══════════════════════════════════════════════
   KPI / METRIC CARDS
═══════════════════════════════════════════════ */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-card);
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-card);
    transition: var(--transition);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
    border-radius: var(--radius-card) var(--radius-card) 0 0;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.18);
    border-color: rgba(59, 130, 246, 0.3);
}
.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.4rem;
}
.kpi-delta {
    font-size: 0.78rem;
    color: var(--accent-cyan);
    font-weight: 500;
}
.kpi-icon {
    position: absolute;
    top: 1.2rem; right: 1.4rem;
    font-size: 1.8rem;
    opacity: 0.18;
}

/* Glass card variant */
.glass-card {
    background: rgba(17, 24, 39, 0.75);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: var(--radius-card);
    padding: 1.4rem;
    box-shadow: var(--shadow-card);
}

/* ═══════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════ */
/* Primary gradient button */
.stButton > button[kind="primary"],
.stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-cyan) 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: var(--transition) !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35) !important;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
    filter: brightness(1.08) !important;
}

/* Secondary / default button */
.stButton > button:not([kind="primary"]):not([data-testid="stSidebar"] *) {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: var(--transition) !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: var(--accent-blue) !important;
    color: var(--accent-blue) !important;
    background: rgba(59, 130, 246, 0.07) !important;
}

/* ═══════════════════════════════════════════════
   FILE UPLOAD AREA
═══════════════════════════════════════════════ */
[data-testid="stFileUploadDropzone"],
.stFileUploader > div {
    background: rgba(59, 130, 246, 0.04) !important;
    border: 2px dashed var(--accent-blue) !important;
    border-radius: var(--radius-card) !important;
    color: var(--text-secondary) !important;
    transition: var(--transition) !important;
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
}
[data-testid="stFileUploadDropzone"]:hover,
.stFileUploader > div:hover {
    background: rgba(59, 130, 246, 0.08) !important;
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 18px rgba(59, 130, 246, 0.2) !important;
}
[data-testid="stFileUploadDropzone"] p,
.stFileUploader > div p {
    color: var(--text-secondary) !important;
}

/* ═══════════════════════════════════════════════
   PLOTLY CHART CONTAINER
═══════════════════════════════════════════════ */
.plotly-chart-container {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-card);
    padding: 1rem;
    box-shadow: var(--shadow-card);
}

[data-testid="stPlotlyChart"] {
    background: transparent !important;
}

.js-plotly-plot .plotly {
    border-radius: 10px;
    overflow: hidden;
}

/* ═══════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════ */
[data-testid="stTabs"] {
    border-bottom: 1px solid var(--border-color);
}

button[data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.6rem 1.1rem !important;
    transition: var(--transition) !important;
}

button[data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    border-bottom-color: rgba(59, 130, 246, 0.4) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent-blue) !important;
    border-bottom: 2px solid var(--accent-blue) !important;
    background: rgba(59, 130, 246, 0.07) !important;
    border-radius: 6px 6px 0 0 !important;
    font-weight: 700 !important;
}

[data-testid="stTabContent"] {
    padding: 1.2rem 0 !important;
}

/* Tab underline */
[data-baseweb="tab-highlight"] {
    background: var(--accent-blue) !important;
    height: 2px !important;
}

/* ═══════════════════════════════════════════════
   INPUTS & SELECTBOXES
═══════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 0.9rem !important;
    transition: var(--transition) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    outline: none !important;
}

[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

[data-testid="stSelectbox"] > div:hover,
[data-testid="stMultiSelect"] > div:hover {
    border-color: var(--accent-blue) !important;
}

/* Dropdown list */
ul[data-testid="stSelectboxVirtualDropdown"],
ul[role="listbox"] {
    background: #161f35 !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 0.4rem !important;
}

li[role="option"] {
    color: var(--text-secondary) !important;
    border-radius: 6px !important;
    font-size: 0.87rem !important;
    padding: 0.4rem 0.8rem !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background: rgba(59, 130, 246, 0.14) !important;
    color: var(--text-primary) !important;
}

/* Slider */
[data-testid="stSlider"] > div > div > div {
    background: var(--border-color) !important;
}
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)) !important;
}

/* Checkbox & Radio */
[data-testid="stCheckbox"] span,
[data-testid="stRadio"] span {
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
}

/* ═══════════════════════════════════════════════
   DATAFRAME / TABLE
═══════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-card) !important;
    overflow: hidden;
}

.dvn-scroller::-webkit-scrollbar { width: 5px; height: 5px; }
.dvn-scroller::-webkit-scrollbar-thumb {
    background: var(--accent-blue);
    border-radius: 4px;
}

/* ═══════════════════════════════════════════════
   METRIC WIDGETS (native st.metric)
═══════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-card) !important;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow-card) !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ═══════════════════════════════════════════════
   ALERT / STATUS BOXES
═══════════════════════════════════════════════ */
.stAlert {
    border-radius: 10px !important;
    border-left-width: 4px !important;
    font-size: 0.88rem !important;
}

/* Success */
[data-testid="stAlert"][data-baseweb="notification"][kind="positive"],
div.stAlert > div[data-baseweb="notification"] {
    background: rgba(16, 185, 129, 0.1) !important;
    border-left-color: #10b981 !important;
    color: #6ee7b7 !important;
}

/* Warning */
[data-testid="stAlert"][kind="warning"] {
    background: rgba(245, 158, 11, 0.1) !important;
    border-left-color: #f59e0b !important;
    color: #fcd34d !important;
}

/* Error */
[data-testid="stAlert"][kind="error"] {
    background: rgba(239, 68, 68, 0.1) !important;
    border-left-color: #ef4444 !important;
    color: #fca5a5 !important;
}

/* Info */
[data-testid="stAlert"][kind="info"] {
    background: rgba(59, 130, 246, 0.1) !important;
    border-left-color: var(--accent-blue) !important;
    color: #93c5fd !important;
}

/* Custom status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.status-badge.success { background: rgba(16,185,129,0.15); color: #34d399; }
.status-badge.warning { background: rgba(245,158,11,0.15); color: #fbbf24; }
.status-badge.error   { background: rgba(239,68,68,0.15); color: #f87171; }
.status-badge.info    { background: rgba(59,130,246,0.15); color: #60a5fa; }

/* ═══════════════════════════════════════════════
   EXPANDER
═══════════════════════════════════════════════ */
[data-testid="stExpander"] > details {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-card) !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.9rem 1.2rem !important;
}
[data-testid="stExpander"] summary:hover {
    background: rgba(59, 130, 246, 0.05) !important;
}

/* ═══════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div {
    background: var(--border-color) !important;
    border-radius: 999px !important;
    height: 8px !important;
}
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)) !important;
    border-radius: 999px !important;
    transition: width 0.4s ease !important;
}

/* ═══════════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid var(--border-color) !important;
    margin: 1.5rem 0 !important;
}

/* ═══════════════════════════════════════════════
   PAGE TITLE STYLES
═══════════════════════════════════════════════ */
.page-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}
.page-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
}
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
}

/* ═══════════════════════════════════════════════
   COLUMN GAP ADJUSTMENTS
═══════════════════════════════════════════════ */
[data-testid="column"] {
    padding: 0 0.5rem !important;
}

/* ═══════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════ */
[data-testid="stSpinner"] > div {
    border-top-color: var(--accent-blue) !important;
}

/* ═══════════════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════════════ */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        min-width: 220px !important;
        max-width: 220px !important;
    }
    .kpi-value { font-size: 1.5rem; }
    .page-title { font-size: 1.3rem; }
    [data-testid="column"] { padding: 0 0.2rem !important; }
}

@media (max-width: 480px) {
    .kpi-card { padding: 1rem; }
    .kpi-value { font-size: 1.2rem; }
}
</style>
"""


def apply_theme() -> None:
    """Inject the EduClean AI CSS theme into the Streamlit app."""
    st.markdown(get_theme_css(), unsafe_allow_html=True)
