"""
data_loader.py
==============
Module for loading and managing datasets for EduClean AI.
Supports CSV (with encoding detection) and Excel formats.
"""

import io
import pandas as pd
import numpy as np
from typing import Union


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_dataset(uploaded_file) -> pd.DataFrame:
    """Load a CSV or Excel file uploaded via Streamlit's file_uploader.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        The file object returned by st.file_uploader().

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame with whitespace stripped from column names.

    Raises
    ------
    ValueError
        If the file format is unsupported or the file cannot be parsed.
    """
    if uploaded_file is None:
        raise ValueError("No file provided. Please upload a CSV or Excel file.")

    filename: str = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            df = _load_csv(uploaded_file)
        elif filename.endswith((".xlsx", ".xls")):
            df = _load_excel(uploaded_file)
        else:
            raise ValueError(
                f"Unsupported file format '{uploaded_file.name}'. "
                "Please upload a CSV (.csv) or Excel (.xlsx / .xls) file."
            )
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            f"Could not read '{uploaded_file.name}': {exc}. "
            "Please ensure the file is not corrupted and try again."
        ) from exc

    # Strip whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]

    return df


def get_dataset_info(df: pd.DataFrame) -> dict:
    """Return structural metadata about a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    dict
        {
          n_rows: int,
          n_cols: int,
          columns: list[dict],   # {name, dtype, non_null, null_count, null_pct}
          memory_mb: float,
          dtypes_summary: {numeric, categorical, datetime, boolean}
        }
    """
    n_rows, n_cols = df.shape
    memory_mb = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 4)

    columns = []
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        non_null = n_rows - null_count
        null_pct = round(null_count / n_rows * 100, 2) if n_rows > 0 else 0.0
        columns.append(
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null": non_null,
                "null_count": null_count,
                "null_pct": null_pct,
            }
        )

    dtypes_summary = _summarise_dtypes(df)

    return {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "columns": columns,
        "memory_mb": memory_mb,
        "dtypes_summary": dtypes_summary,
    }


def detect_duplicates(df: pd.DataFrame) -> dict:
    """Detect exact duplicate rows in the DataFrame.

    Returns
    -------
    dict
        {count: int, percentage: float, duplicate_rows: pd.DataFrame}
    """
    dup_mask = df.duplicated(keep=False)
    dup_df = df[dup_mask]
    count = int(df.duplicated().sum())
    percentage = round(count / len(df) * 100, 2) if len(df) > 0 else 0.0

    return {
        "count": count,
        "percentage": percentage,
        "duplicate_rows": dup_df,
    }


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary of missing values per column.

    Returns
    -------
    pd.DataFrame
        Columns: Column, Missing Count, Missing %, Data Type
        Sorted descending by missing count. Only columns with ≥1 missing value
        are included (all columns are included when there are none missing).
    """
    missing_counts = df.isna().sum()
    missing_pct = (missing_counts / len(df) * 100).round(2)
    dtypes = df.dtypes.astype(str)

    summary = pd.DataFrame(
        {
            "Column": df.columns,
            "Missing Count": missing_counts.values,
            "Missing %": missing_pct.values,
            "Data Type": dtypes.values,
        }
    )

    summary = summary[summary["Missing Count"] >= 0]  # keep all rows
    summary = summary.sort_values("Missing Count", ascending=False).reset_index(drop=True)
    return summary


def generate_dataset_summary(df: pd.DataFrame) -> dict:
    """Generate a comprehensive statistical summary of the DataFrame.

    Returns
    -------
    dict
        {
          basic_stats: dict,            # df.describe() as nested dict
          value_counts_top: dict,       # top-5 value counts per categorical col
          skewness: dict,               # skewness per numeric col
          kurtosis: dict,               # kurtosis per numeric col
        }
    """
    # Basic statistics for all columns (numeric + object where possible)
    try:
        basic_stats = df.describe(include="all").to_dict()
    except Exception:
        basic_stats = df.describe().to_dict()

    # Top-5 value counts for categorical / object columns
    value_counts_top: dict = {}
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        vc = df[col].value_counts(dropna=False).head(5)
        value_counts_top[col] = vc.to_dict()

    # Skewness and kurtosis for numeric columns
    num_cols = df.select_dtypes(include="number").columns
    skewness: dict = {}
    kurtosis_dict: dict = {}
    for col in num_cols:
        try:
            skewness[col] = round(float(df[col].skew()), 4)
            kurtosis_dict[col] = round(float(df[col].kurt()), 4)
        except Exception:
            skewness[col] = None
            kurtosis_dict[col] = None

    return {
        "basic_stats": basic_stats,
        "value_counts_top": value_counts_top,
        "skewness": skewness,
        "kurtosis": kurtosis_dict,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_csv(uploaded_file) -> pd.DataFrame:
    """Try multiple encodings to load a CSV robustly."""
    raw_bytes = uploaded_file.read()
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

    for enc in encodings:
        try:
            df = pd.read_csv(io.BytesIO(raw_bytes), encoding=enc)
            return df
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue

    raise ValueError(
        "Could not decode the CSV file with common encodings (UTF-8, Latin-1, CP1252). "
        "Please re-save the file as UTF-8 and try again."
    )


def _load_excel(uploaded_file) -> pd.DataFrame:
    """Load the first sheet of an Excel workbook."""
    raw_bytes = uploaded_file.read()
    df = pd.read_excel(io.BytesIO(raw_bytes), engine="openpyxl")
    return df


def _summarise_dtypes(df: pd.DataFrame) -> dict:
    """Count columns by high-level dtype category."""
    numeric = 0
    categorical = 0
    datetime = 0
    boolean = 0

    for dtype in df.dtypes:
        if pd.api.types.is_bool_dtype(dtype):
            boolean += 1
        elif pd.api.types.is_numeric_dtype(dtype):
            numeric += 1
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            datetime += 1
        else:
            categorical += 1

    return {
        "numeric": numeric,
        "categorical": categorical,
        "datetime": datetime,
        "boolean": boolean,
    }
