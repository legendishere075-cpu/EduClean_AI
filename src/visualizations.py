"""
visualizations.py — EduClean AI
All chart-building functions using Plotly with a consistent dark theme.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats as scipy_stats

# ---------------------------------------------------------------------------
# Shared theme applied to every figure
# ---------------------------------------------------------------------------
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,20,36,0.8)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    title_font=dict(color="#f1f5f9", size=16, family="Inter, sans-serif"),
    colorway=["#3b82f6", "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"],
    xaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", tickfont=dict(color="#64748b")),
    yaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", tickfont=dict(color="#64748b")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    margin=dict(l=40, r=20, t=50, b=40),
)


def _apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the shared CHART_THEME to a figure and return it."""
    fig.update_layout(**CHART_THEME)
    return fig


# ---------------------------------------------------------------------------
# 1. Performance Distribution  (Histogram + KDE overlay)
# ---------------------------------------------------------------------------
def plot_performance_distribution(df: pd.DataFrame, col: str) -> go.Figure:
    """Histogram with KDE overlay of a numeric column."""
    series = df[col].dropna()
    fig = go.Figure()

    # Histogram
    fig.add_trace(go.Histogram(
        x=series,
        nbinsx=30,
        name="Count",
        marker_color="#3b82f6",
        opacity=0.75,
        histnorm="probability density",
    ))

    # KDE overlay
    kde_x = np.linspace(series.min(), series.max(), 300)
    kde = scipy_stats.gaussian_kde(series)
    fig.add_trace(go.Scatter(
        x=kde_x,
        y=kde(kde_x),
        mode="lines",
        name="KDE",
        line=dict(color="#06b6d4", width=2),
    ))

    fig.update_layout(
        title=f"Distribution of {col}",
        xaxis_title=col,
        yaxis_title="Density",
        bargap=0.05,
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 2. Subject Averages  (Horizontal bar, sorted descending)
# ---------------------------------------------------------------------------
def plot_subject_averages(df: pd.DataFrame, subject_cols: list) -> go.Figure:
    """Horizontal bar chart of mean per subject column, sorted descending."""
    means = df[subject_cols].mean().sort_values(ascending=True)  # ascending for horizontal bar
    fig = go.Figure(go.Bar(
        x=means.values,
        y=means.index.tolist(),
        orientation="h",
        marker=dict(
            color=means.values,
            colorscale=[[0, "#1e3a5f"], [1, "#3b82f6"]],
            showscale=False,
        ),
        text=[f"{v:.2f}" for v in means.values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Subject-wise Average Scores",
        xaxis_title="Average Score",
        yaxis_title="Subject",
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 3. Attendance vs Performance  (Scatter + trendline, colored by quartile)
# ---------------------------------------------------------------------------
def plot_attendance_vs_performance(
    df: pd.DataFrame, attendance_col: str, performance_col: str
) -> go.Figure:
    """Scatter plot with trendline, colored by performance quartile."""
    data = df[[attendance_col, performance_col]].dropna().copy()
    data["Quartile"] = pd.qcut(data[performance_col], q=4, labels=["Q1", "Q2", "Q3", "Q4"])

    color_map = {"Q1": "#ef4444", "Q2": "#f59e0b", "Q3": "#06b6d4", "Q4": "#10b981"}

    fig = go.Figure()
    for quartile, grp in data.groupby("Quartile", observed=True):
        fig.add_trace(go.Scatter(
            x=grp[attendance_col],
            y=grp[performance_col],
            mode="markers",
            name=str(quartile),
            marker=dict(color=color_map.get(str(quartile), "#3b82f6"), size=6, opacity=0.75),
        ))

    # Trendline (OLS)
    slope, intercept, *_ = scipy_stats.linregress(data[attendance_col], data[performance_col])
    x_range = np.linspace(data[attendance_col].min(), data[attendance_col].max(), 100)
    fig.add_trace(go.Scatter(
        x=x_range,
        y=slope * x_range + intercept,
        mode="lines",
        name="Trendline",
        line=dict(color="#f59e0b", width=2, dash="dash"),
    ))

    fig.update_layout(
        title=f"{attendance_col} vs {performance_col}",
        xaxis_title=attendance_col,
        yaxis_title=performance_col,
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 4. Correlation Heatmap
# ---------------------------------------------------------------------------
def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Correlation matrix heatmap of numeric columns using RdBu colorscale."""
    numeric_df = df.select_dtypes(include="number")
    corr = numeric_df.corr()

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(
            tickfont=dict(color="#94a3b8"),
            title=dict(text="r", font=dict(color="#94a3b8")),
        ),
    ))
    fig.update_layout(
        title="Correlation Matrix",
        xaxis=dict(tickangle=-45),
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 5. Grade / Category Distribution  (Donut chart)
# ---------------------------------------------------------------------------
def plot_grade_distribution(df: pd.DataFrame, grade_col: str) -> go.Figure:
    """Donut chart of grade/category distribution."""
    counts = df[grade_col].value_counts()
    fig = go.Figure(go.Pie(
        labels=counts.index.tolist(),
        values=counts.values.tolist(),
        hole=0.45,
        marker=dict(colors=["#3b82f6", "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(title=f"Distribution of {grade_col}")
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 6. Missing Values Bar Chart
# ---------------------------------------------------------------------------
def plot_missing_values_heatmap(df: pd.DataFrame) -> go.Figure:
    """Bar chart of missing value percentages per column (only cols with > 0 missing)."""
    missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    missing_pct = missing_pct[missing_pct > 0]

    if missing_pct.empty:
        fig = go.Figure()
        fig.update_layout(title="No Missing Values Found 🎉")
        return _apply_theme(fig)

    fig = go.Figure(go.Bar(
        x=missing_pct.index.tolist(),
        y=missing_pct.values,
        marker=dict(
            color=missing_pct.values,
            colorscale=[[0, "#1e3a5f"], [1, "#ef4444"]],
            showscale=False,
        ),
        text=[f"{v:.1f}%" for v in missing_pct.values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Missing Values by Column",
        xaxis_title="Column",
        yaxis_title="Missing %",
        yaxis=dict(range=[0, min(missing_pct.max() * 1.2, 105)]),
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 7. Outlier Box Plots
# ---------------------------------------------------------------------------
def plot_outlier_boxplots(df: pd.DataFrame, columns: list) -> go.Figure:
    """Box plots for each numeric column side by side."""
    fig = go.Figure()
    colors = ["#3b82f6", "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]
    for i, col in enumerate(columns):
        series = df[col].dropna()
        fig.add_trace(go.Box(
            y=series,
            name=col,
            marker_color=colors[i % len(colors)],
            line_color=colors[i % len(colors)],
            boxmean="sd",
        ))
    fig.update_layout(
        title="Outlier Analysis — Box Plots",
        yaxis_title="Value",
        showlegend=False,
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 8. Feature Importance  (Horizontal bar, sorted)
# ---------------------------------------------------------------------------
def plot_feature_importance(feature_names: list, importances: list) -> go.Figure:
    """Horizontal bar chart sorted by importance."""
    pairs = sorted(zip(importances, feature_names), reverse=False)
    imp_sorted, feat_sorted = zip(*pairs) if pairs else ([], [])

    fig = go.Figure(go.Bar(
        x=list(imp_sorted),
        y=list(feat_sorted),
        orientation="h",
        marker=dict(
            color=list(imp_sorted),
            colorscale=[[0, "#1e3a5f"], [1, "#3b82f6"]],
            showscale=False,
        ),
        text=[f"{v:.4f}" for v in imp_sorted],
        textposition="outside",
    ))
    fig.update_layout(
        title="Feature Importance",
        xaxis_title="Importance",
        yaxis_title="Feature",
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 9. Confusion Matrix
# ---------------------------------------------------------------------------
def plot_confusion_matrix(cm: np.ndarray, labels: list) -> go.Figure:
    """Annotated heatmap of confusion matrix."""
    # Normalize for color intensity
    cm_norm = cm.astype(float) / (cm.sum(axis=1, keepdims=True) + 1e-9)

    fig = go.Figure(go.Heatmap(
        z=cm_norm,
        x=[str(l) for l in labels],
        y=[str(l) for l in labels],
        colorscale=[[0, "#0d1424"], [0.5, "#1e40af"], [1, "#3b82f6"]],
        showscale=True,
        text=cm,
        texttemplate="%{text}",
        hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{text}<extra></extra>",
        colorbar=dict(tickfont=dict(color="#94a3b8")),
    ))
    fig.update_layout(
        title="Confusion Matrix",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        xaxis=dict(side="bottom"),
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 10. Model Comparison  (Grouped bar)
# ---------------------------------------------------------------------------
def plot_model_comparison(results: dict) -> go.Figure:
    """
    Grouped bar chart comparing model metrics.

    Parameters
    ----------
    results : dict
        {model_name: {metric: value, ...}, ...}
    """
    model_names = list(results.keys())
    if not model_names:
        fig = go.Figure()
        fig.update_layout(title="No model results to compare")
        return _apply_theme(fig)

    # Collect all metric names
    all_metrics = set()
    for v in results.values():
        all_metrics.update(k for k in v if k not in ("confusion_matrix", "classification_report"))
    all_metrics = sorted(all_metrics)

    colors = ["#3b82f6", "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]
    fig = go.Figure()
    for i, metric in enumerate(all_metrics):
        values = [results[m].get(metric, 0) for m in model_names]
        fig.add_trace(go.Bar(
            name=metric.upper(),
            x=model_names,
            y=values,
            marker_color=colors[i % len(colors)],
            text=[f"{v:.4f}" for v in values],
            textposition="outside",
        ))

    fig.update_layout(
        title="Model Performance Comparison",
        barmode="group",
        xaxis_title="Model",
        yaxis_title="Score",
    )
    return _apply_theme(fig)


# ---------------------------------------------------------------------------
# 11. Actual vs Predicted  (Scatter + identity line)
# ---------------------------------------------------------------------------
def plot_actual_vs_predicted(y_actual, y_predicted) -> go.Figure:
    """Scatter plot with identity line."""
    y_actual = np.array(y_actual)
    y_predicted = np.array(y_predicted)

    fig = go.Figure()

    # Scatter points
    fig.add_trace(go.Scatter(
        x=y_actual,
        y=y_predicted,
        mode="markers",
        name="Predictions",
        marker=dict(color="#3b82f6", size=6, opacity=0.7),
        hovertemplate="Actual: %{x:.3f}<br>Predicted: %{y:.3f}<extra></extra>",
    ))

    # Perfect-prediction identity line
    min_val = min(y_actual.min(), y_predicted.min())
    max_val = max(y_actual.max(), y_predicted.max())
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode="lines",
        name="Ideal (y = x)",
        line=dict(color="#ef4444", width=2, dash="dash"),
    ))

    fig.update_layout(
        title="Actual vs Predicted",
        xaxis_title="Actual",
        yaxis_title="Predicted",
    )
    return _apply_theme(fig)
