"""
EduClean AI — Main Entry Point
A premium Streamlit-based educational analytics dashboard.
"""

import importlib
import sys
import os

import streamlit as st

# ── Ensure src/ is importable ──────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Page config — MUST be first Streamlit call ─────────────────────────────
st.set_page_config(
    page_title="EduClean AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ──────────────────────────────────────────────────────────────────
from src.theme import apply_theme  # noqa: E402
apply_theme()

# ── Session state defaults ─────────────────────────────────────────────────
_DEFAULTS = {
    "current_page":         "Overview Dashboard",
    "df_original":          None,
    "df_working":           None,
    "df_cleaned":           None,
    "upload_filename":      None,
    "preprocessing_history": [],
    "model_results":        {},
    "quality_score":        None,
}
for _key, _val in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val

# ── Navigation config ──────────────────────────────────────────────────────
NAV_ITEMS = [
    ("📊", "Overview Dashboard",        "overview"),
    ("🗂️", "Dataset Explorer",          "dataset_explorer"),
    ("🔍", "Data Quality Analysis",      "data_quality"),
    ("🛠️", "Data Preprocessing",         "preprocessing"),
    ("📈", "Exploratory Data Analysis",  "eda"),
    ("🤖", "Performance Prediction",     "prediction"),
    ("👩‍🎓", "Student Insights",          "insights"),
    ("📄", "Reports & Downloads",        "reports"),
    ("⚙️", "Settings",                   "settings"),
]

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo area
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-title">🎓 EduClean AI</div>
            <div class="sidebar-logo-tagline">
                Clean Data. Clear Insights. Smarter Education.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Nav section label
    st.markdown(
        '<div class="nav-section-label">Navigation</div>',
        unsafe_allow_html=True,
    )

    # Nav buttons
    for icon, label, _module in NAV_ITEMS:
        is_active = st.session_state.current_page == label
        # Wrap active button in a div that CSS can target
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"nav_{_module}", use_container_width=True):
            st.session_state.current_page = label
            st.rerun()
        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

    # Spacer + footer
    st.markdown(
        """
        <div style="flex:1; min-height:2rem;"></div>
        <div class="sidebar-footer">
            <div class="sidebar-footer-text">
                EduClean AI &nbsp;·&nbsp; v1.0.0<br>
                © 2025 EduClean Project
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Page routing ───────────────────────────────────────────────────────────
_MODULE_MAP = {label: mod for _, label, mod in NAV_ITEMS}

current = st.session_state.current_page
module_name = _MODULE_MAP.get(current)

if module_name is None:
    st.error(f"Unknown page: {current!r}")
    st.stop()

try:
    page_module = importlib.import_module(f"src.pages.{module_name}")
    page_module.render()
except ModuleNotFoundError:
    # Page not yet implemented — show a friendly placeholder
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;min-height:60vh;gap:1rem;">
            <div style="font-size:3rem;">🚧</div>
            <div style="font-size:1.5rem;font-weight:700;color:#f1f5f9;">
                {current}
            </div>
            <div style="color:#94a3b8;font-size:0.9rem;">
                This page is under construction. Check back soon!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
except Exception as exc:
    st.error(f"Error loading **{current}**: {exc}")
    with st.expander("Traceback"):
        import traceback
        st.code(traceback.format_exc(), language="python")
