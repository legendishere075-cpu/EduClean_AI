"""
data_quality.py
===============
AI-powered data quality analyser for EduClean AI.
Scores datasets across four dimensions and surfaces actionable insights.
"""

import re
import numpy as np
import pandas as pd
from typing import Any


# ---------------------------------------------------------------------------
# Columns expected to hold non-negative values in education datasets
# ---------------------------------------------------------------------------
_POSITIVE_KEYWORDS = {
    "age", "marks", "attendance", "score", "grade",
    "percentage", "gpa", "cgpa",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_quality_score(df: pd.DataFrame) -> dict:
    """Compute a multi-dimensional data quality score.

    Returns
    -------
    dict
        {
          overall_score: float,     # 0–100
          completeness: float,      # % non-missing (0–100)
          uniqueness: float,        # (1 – duplicate_rate) * 100
          consistency: float,       # type uniformity proxy (0–100)
          validity: float,          # based on outlier / invalid prevalence
          breakdown: list[dict]     # {metric, score, description}
        }
    """
    completeness = _score_completeness(df)
    uniqueness = _score_uniqueness(df)
    consistency = _score_consistency(df)
    validity = _score_validity(df)

    overall = round(
        0.35 * completeness + 0.25 * uniqueness + 0.20 * consistency + 0.20 * validity,
        2,
    )

    breakdown = [
        {
            "metric": "Completeness",
            "score": round(completeness, 2),
            "description": "Percentage of non-missing values across all cells.",
        },
        {
            "metric": "Uniqueness",
            "score": round(uniqueness, 2),
            "description": "Proportion of non-duplicate rows (penalised for duplicates).",
        },
        {
            "metric": "Consistency",
            "score": round(consistency, 2),
            "description": "Degree of type uniformity within each column.",
        },
        {
            "metric": "Validity",
            "score": round(validity, 2),
            "description": "Absence of statistical outliers and invalid entries.",
        },
    ]

    return {
        "overall_score": overall,
        "completeness": round(completeness, 2),
        "uniqueness": round(uniqueness, 2),
        "consistency": round(consistency, 2),
        "validity": round(validity, 2),
        "breakdown": breakdown,
    }


def detect_outliers(df: pd.DataFrame) -> dict:
    """Detect outliers in every numeric column using the IQR method.

    Returns
    -------
    dict
        {col_name: {count, pct, lower, upper}, ...}
        Only columns with at least one outlier are included.
    """
    result: dict = {}
    num_df = df.select_dtypes(include="number")

    for col in num_df.columns:
        series = num_df[col].dropna()
        if len(series) < 4:
            continue

        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_mask = (series < lower) | (series > upper)
        count = int(outlier_mask.sum())
        if count > 0:
            result[col] = {
                "count": count,
                "pct": round(count / len(series) * 100, 2),
                "lower": round(lower, 4),
                "upper": round(upper, 4),
            }

    return result


def detect_invalid_entries(df: pd.DataFrame) -> dict:
    """Detect semantically invalid entries in the DataFrame.

    Checks:
    - Negative values in columns that should be non-negative
      (age, marks, attendance, score, grade, percentage, gpa, cgpa)
    - Columns that contain mixed Python types (beyond normal NaN coercion)

    Returns
    -------
    dict
        {col_name: {issue: str, count: int}, ...}
    """
    result: dict = {}

    for col in df.columns:
        col_lower = col.lower().strip()

        # --- Negative-value check for domain-specific columns ---
        if any(kw in col_lower for kw in _POSITIVE_KEYWORDS):
            series = df[col]
            if pd.api.types.is_numeric_dtype(series):
                neg_count = int((series < 0).sum())
                if neg_count > 0:
                    result[col] = {
                        "issue": f"Negative values found in '{col}' (should be ≥ 0)",
                        "count": neg_count,
                    }

        # --- Mixed-type check (object columns with heterogeneous Python types) ---
        if df[col].dtype == object:
            non_null = df[col].dropna()
            if len(non_null) == 0:
                continue
            types_seen = set(type(v).__name__ for v in non_null)
            if len(types_seen) > 1:
                # Only flag if truly mixed (e.g. int and str together)
                result.setdefault(
                    col,
                    {
                        "issue": f"Mixed data types in '{col}': {', '.join(sorted(types_seen))}",
                        "count": len(non_null),
                    },
                )

    return result


def detect_format_inconsistencies(df: pd.DataFrame) -> dict:
    """Detect formatting inconsistencies in string/object columns.

    Checks for:
    - Mixed letter casing (e.g. "male" vs "Male" vs "MALE")
    - Leading / trailing whitespace
    - Mixed date-like formats (e.g. "01/01/2020" vs "2020-01-01")

    Returns
    -------
    dict
        {col_name: {issue: str, examples: list}, ...}
    """
    result: dict = {}

    _date_patterns = [
        re.compile(r"^\d{4}-\d{2}-\d{2}$"),           # ISO  2024-01-15
        re.compile(r"^\d{2}/\d{2}/\d{4}$"),            # US   01/15/2024
        re.compile(r"^\d{2}-\d{2}-\d{4}$"),            # EU   15-01-2024
        re.compile(r"^\d{2}\.\d{2}\.\d{4}$"),          # dot  15.01.2024
        re.compile(r"^\d{1,2} \w+ \d{4}$"),            # long 15 January 2024
    ]

    str_cols = df.select_dtypes(include=["object"]).columns

    for col in str_cols:
        non_null = df[col].dropna().astype(str)
        if len(non_null) == 0:
            continue

        issues = []
        examples: list[Any] = []

        # 1. Leading / trailing whitespace
        has_ws = non_null[non_null != non_null.str.strip()]
        if len(has_ws) > 0:
            issues.append("leading/trailing whitespace")
            examples.extend(has_ws.head(2).tolist())

        # 2. Mixed casing (only for columns that look textual, not numeric-ish)
        unique_vals = non_null.unique()
        lower_vals = {v.lower() for v in unique_vals}
        if len(lower_vals) < len(unique_vals):
            issues.append("mixed casing")
            # Show pairs that differ only by case
            seen: dict = {}
            for v in unique_vals:
                key = v.lower()
                seen.setdefault(key, []).append(v)
            mixed_pairs = [vs for vs in seen.values() if len(vs) > 1]
            for pair in mixed_pairs[:2]:
                examples.extend(pair[:2])

        # 3. Mixed date-like formats
        date_format_counts: dict[int, int] = {}
        for val in non_null.head(500):  # sample for performance
            for idx, pat in enumerate(_date_patterns):
                if pat.match(val.strip()):
                    date_format_counts[idx] = date_format_counts.get(idx, 0) + 1
                    break

        if len(date_format_counts) > 1:
            issues.append("mixed date formats")
            matched = [
                v for v in non_null.head(10)
                if any(p.match(v.strip()) for p in _date_patterns)
            ]
            examples.extend(matched[:4])

        if issues:
            result[col] = {
                "issue": "; ".join(issues),
                "examples": list(dict.fromkeys(examples))[:6],  # deduplicate, cap at 6
            }

    return result


def generate_quality_insights(quality_dict: dict, df: pd.DataFrame) -> list[str]:
    """Generate plain-English insights from quality scores and DataFrame.

    Returns
    -------
    list[str]
        Between 4 and 8 actionable insight strings.
    """
    insights: list[str] = []

    overall = quality_dict.get("overall_score", 0)
    completeness = quality_dict.get("completeness", 100)
    uniqueness = quality_dict.get("uniqueness", 100)
    consistency = quality_dict.get("consistency", 100)
    validity = quality_dict.get("validity", 100)

    n_rows, n_cols = df.shape
    total_cells = n_rows * n_cols

    # --- Overall score ---
    if overall >= 90:
        insights.append(
            f"✅ Overall data quality score is {overall}/100 — excellent quality. "
            "This dataset is well-suited for analysis and modelling."
        )
    elif overall >= 70:
        insights.append(
            f"⚠️ Overall data quality score is {overall}/100 — moderate quality. "
            "Some cleaning steps are recommended before modelling."
        )
    else:
        insights.append(
            f"🚨 Overall data quality score is {overall}/100 — poor quality. "
            "Significant preprocessing is needed to ensure reliable results."
        )

    # --- Completeness ---
    missing_pct = round(100 - completeness, 2)
    if missing_pct > 0:
        missing_cells = int(total_cells * missing_pct / 100)
        worst_cols = (
            df.isna()
            .mean()
            .mul(100)
            .sort_values(ascending=False)
            .head(3)
        )
        col_list = ", ".join(
            f"'{c}' ({v:.1f}%)" for c, v in worst_cols.items() if v > 0
        )
        if col_list:
            insights.append(
                f"📉 {missing_pct}% of all cells are missing ({missing_cells:,} cells). "
                f"Columns most affected: {col_list}."
            )
    else:
        insights.append("✅ No missing values detected — the dataset is complete.")

    # --- Uniqueness / duplicates ---
    dup_pct = round(100 - uniqueness, 2)
    if dup_pct > 0:
        dup_count = int(n_rows * dup_pct / 100)
        insights.append(
            f"🔁 Duplicate records detected: {dup_count:,} rows ({dup_pct}%) are exact duplicates. "
            "Remove them to prevent skewed statistics."
        )
    else:
        insights.append("✅ No duplicate rows found — all records are unique.")

    # --- Consistency ---
    if consistency < 80:
        insights.append(
            f"⚠️ Type consistency score is {consistency:.1f}/100. Some columns contain "
            "mixed data types, which can cause errors in numeric operations. "
            "Consider standardising these columns."
        )
    else:
        insights.append(
            f"✅ Consistency score is {consistency:.1f}/100 — column data types are "
            "uniform across the dataset."
        )

    # --- Validity / outliers ---
    outlier_info = detect_outliers(df)
    if outlier_info:
        col_examples = ", ".join(
            f"'{c}' ({v['pct']}%)" for c, v in list(outlier_info.items())[:3]
        )
        insights.append(
            f"📊 Outliers detected in {len(outlier_info)} numeric column(s): {col_examples}. "
            "Review these values — they may represent data entry errors or genuine extremes."
        )
    if validity < 80:
        insights.append(
            f"⚠️ Validity score is {validity:.1f}/100. High outlier prevalence or invalid "
            "entries were detected. Use the Preprocessing tab to handle them."
        )

    # --- Dataset size note ---
    if n_rows < 100:
        insights.append(
            f"ℹ️ The dataset is small ({n_rows} rows). Statistical findings may not be "
            "generalisable. Consider collecting more data before training models."
        )
    elif n_rows > 100_000:
        insights.append(
            f"ℹ️ Large dataset detected ({n_rows:,} rows). Sampling strategies may be "
            "beneficial to speed up exploratory analysis and model training."
        )

    return insights[:8]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _score_completeness(df: pd.DataFrame) -> float:
    """Return % of non-missing cells (0–100)."""
    total = df.size
    if total == 0:
        return 100.0
    missing = int(df.isna().sum().sum())
    return round((total - missing) / total * 100, 4)


def _score_uniqueness(df: pd.DataFrame) -> float:
    """Return (1 – duplicate_rate) * 100 (0–100)."""
    n = len(df)
    if n == 0:
        return 100.0
    n_dup = int(df.duplicated().sum())
    return round((1 - n_dup / n) * 100, 4)


def _score_consistency(df: pd.DataFrame) -> float:
    """Score based on how uniform the inferred type is within object columns.

    For each object column we check whether values can be consistently
    parsed as a single type.  Columns with fully uniform types score 100,
    mixed columns are penalised proportionally.
    """
    obj_cols = df.select_dtypes(include="object").columns
    if len(obj_cols) == 0:
        return 100.0

    scores = []
    for col in obj_cols:
        non_null = df[col].dropna()
        if len(non_null) == 0:
            scores.append(100.0)
            continue
        types = non_null.apply(lambda x: type(x).__name__)
        dominant_pct = types.value_counts(normalize=True).iloc[0] * 100
        scores.append(dominant_pct)

    return round(float(np.mean(scores)), 4)


def _score_validity(df: pd.DataFrame) -> float:
    """Score based on outlier prevalence across numeric columns (0–100).

    Penalty: each outlier cell reduces the score proportionally.
    """
    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return 100.0

    total_numeric_cells = num_df.count().sum()
    if total_numeric_cells == 0:
        return 100.0

    total_outliers = 0
    for col in num_df.columns:
        series = num_df[col].dropna()
        if len(series) < 4:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        total_outliers += int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())

    outlier_rate = total_outliers / total_numeric_cells
    return round(max(0.0, (1 - outlier_rate) * 100), 4)
