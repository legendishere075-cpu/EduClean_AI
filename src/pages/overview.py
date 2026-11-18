"""
overview.py — Overview Dashboard page for EduClean AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

from src.data_loader import load_dataset


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _academic_performance_mean(df: pd.DataFrame) -> str:
    """Return mean of academic-performance-related numeric columns, or all numerics."""
    keywords = ["score", "marks", "grade", "performance", "gpa", "cgpa",
                "percentage", "result"]
    num_cols = df.select_dtypes(include="number").columns.tolist()
    matched = [c for c in num_cols
               if any(kw in c.lower() for kw in keywords)]
    target_cols = matched if matched else num_cols
    if not target_cols:
        return "N/A"
    mean_val = df[target_cols].mean(numeric_only=True).mean()
    return f"{mean_val:.2f}"


def _dtype_pie(df: pd.DataFrame):
    """Return a small plotly pie chart showing dtype distribution."""
    dtype_map = {
        "Numeric": len(df.select_dtypes(include="number").columns),
        "Categorical": len(df.select_dtypes(include=["object", "category"]).columns),
        "DateTime": len(df.select_dtypes(include=["datetime"]).columns),
        "Boolean": len(df.select_dtypes(include=["bool"]).columns),
    }
    dtype_map = {k: v for k, v in dtype_map.items() if v > 0}
    colors = ["#3b82f6", "#06b6d4", "#a855f7", "#f59e0b"]
    fig = px.pie(
        values=list(dtype_map.values()),
        names=list(dtype_map.keys()),
        color_discrete_sequence=colors,
        hole=0.4,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f1f5f9",
        legend=dict(font=dict(color="#94a3b8")),
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
    )
    fig.update_traces(textfont_color="#f1f5f9")
    return fig


# ──────────────────────────────────────────────
# Empty-state upload widget
# ──────────────────────────────────────────────

def _show_empty_state():
    st.markdown(
        """
        <div class="card" style="text-align:center; padding:60px 40px;">
            <div style="font-size:72px; margin-bottom:16px;">📂</div>
            <h2 style="color:#f1f5f9; margin-bottom:8px;">No Dataset Loaded</h2>
            <p style="color:#94a3b8; font-size:16px; margin-bottom:32px;">
                Upload a CSV or Excel file to unlock your analytics dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown(
            '<h2 class="section-header">📤 Quick Upload</h2>',
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Drop your dataset here (CSV or Excel)",
            type=["csv", "xlsx", "xls"],
            key="overview_uploader",
        )
        if uploaded is not None:
            try:
                df = load_dataset(uploaded)
                st.session_state.df_original = df
                st.session_state.df_working = df.copy()
                st.session_state.upload_filename = uploaded.name
                st.session_state.upload_time = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                st.success(
                    f"✅ **{uploaded.name}** loaded successfully — "
                    f"{df.shape[0]:,} rows × {df.shape[1]} columns"
                )
                st.rerun()
            except ValueError as exc:
                st.error(f"⚠️ Could not load file: {exc}")
            except Exception:
                st.error(
                    "⚠️ An unexpected error occurred while reading your file. "
                    "Please check the format and try again."
                )


# ──────────────────────────────────────────────
# Main render
# ──────────────────────────────────────────────

def render():
    # ── Page header ──────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>Welcome to EduClean AI</h1>
            <p>Transforming Student Data into Intelligent Insights</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_original = st.session_state.get("df_original", None)

    # ── No dataset ───────────────────────────────
    if df_original is None:
        _show_empty_state()
        return

    # ── Dataset loaded ───────────────────────────
    df = df_original  # read-only view

    # Compute quality score if not already set
    quality_score = st.session_state.get("quality_score", None)
    if quality_score is None:
        try:
            from src.data_quality import compute_quality_score
            result = compute_quality_score(st.session_state.df_working)
            quality_score = result.get("overall_score", 0)
            st.session_state.quality_score = quality_score
        except Exception:
            quality_score = 0.0

    total_missing = int(df.isnull().sum().sum())
    avg_perf = _academic_performance_mean(df)

    # ── 4 KPI cards ─────────────────────────────
    st.markdown('<h2 class="section-header">📊 Dataset Snapshot</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Students", f"{df.shape[0]:,}")
    with col2:
        qs_display = f"{quality_score:.1f}%" if quality_score is not None else "—"
        st.metric("🏅 Quality Score", qs_display)
    with col3:
        st.metric("❓ Missing Values", f"{total_missing:,}")
    with col4:
        st.metric("📈 Avg Academic Performance", avg_perf)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Info card + dtype pie ────────────────────
    left, right = st.columns(2)

    with left:
        filename = st.session_state.get("upload_filename", "Unknown")
        upload_time = st.session_state.get("upload_time", "—")
        file_ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "Unknown"
        mem_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)

        st.markdown(
            f"""
            <div class="card">
                <h3 style="color:#3b82f6; margin-bottom:16px;">📁 Dataset Info</h3>
                <table style="width:100%; color:#f1f5f9; border-collapse:collapse;">
                    <tr><td style="padding:6px 0; color:#94a3b8;">Filename</td>
                        <td style="padding:6px 0; font-weight:600;">{filename}</td></tr>
                    <tr><td style="padding:6px 0; color:#94a3b8;">Rows</td>
                        <td style="padding:6px 0; font-weight:600;">{df.shape[0]:,}</td></tr>
                    <tr><td style="padding:6px 0; color:#94a3b8;">Columns</td>
                        <td style="padding:6px 0; font-weight:600;">{df.shape[1]}</td></tr>
                    <tr><td style="padding:6px 0; color:#94a3b8;">File Type</td>
                        <td style="padding:6px 0; font-weight:600;">{file_ext}</td></tr>
                    <tr><td style="padding:6px 0; color:#94a3b8;">Memory</td>
                        <td style="padding:6px 0; font-weight:600;">{mem_mb:.2f} MB</td></tr>
                    <tr><td style="padding:6px 0; color:#94a3b8;">Uploaded</td>
                        <td style="padding:6px 0; font-weight:600;">{upload_time}</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="card"><h3 style="color:#3b82f6; margin-bottom:4px;">📐 Data Type Breakdown</h3>',
            unsafe_allow_html=True,
        )
        fig_pie = _dtype_pie(df)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Data preview ────────────────────────────
    st.markdown('<h2 class="section-header">👀 Data Preview (First 10 Rows)</h2>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True)
