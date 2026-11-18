"""
ml_engine.py — EduClean AI
Machine learning module: task detection, feature prep, training, evaluation,
feature importance, and K-Means clustering.
All ML primitives use scikit-learn only.
"""

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# ---------------------------------------------------------------------------
# Task-type detection
# ---------------------------------------------------------------------------

def detect_task_type(df: pd.DataFrame, target_col: str) -> str:
    """
    Heuristic: returns "classification" if the target has <= 10 unique values
    or its dtype is object/category; otherwise "regression".
    """
    series = df[target_col].dropna()
    if series.dtype.name in ("object", "category"):
        return "classification"
    if series.nunique() <= 10:
        return "classification"
    return "regression"


# ---------------------------------------------------------------------------
# Feature preparation
# ---------------------------------------------------------------------------

def prepare_features(
    df: pd.DataFrame,
    target_col: str,
    test_size: float = 0.2,
) -> tuple:
    """
    Prepare features and split into train/test sets.

    Steps:
      1. Drop rows where target is null.
      2. Encode remaining categorical columns with LabelEncoder.
      3. Split X (all cols except target) and y (target).

    Returns
    -------
    X_train, X_test, y_train, y_test, feature_names
    """
    data = df.dropna(subset=[target_col]).copy()

    # Encode categorical columns (excluding target for now)
    for col in data.select_dtypes(include=["object", "category"]).columns:
        if col == target_col:
            continue
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col].astype(str))

    # Encode target if categorical
    if data[target_col].dtype.name in ("object", "category"):
        le = LabelEncoder()
        data[target_col] = le.fit_transform(data[target_col].astype(str))

    feature_names = [c for c in data.columns if c != target_col]
    X = data[feature_names].values
    y = data[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    return X_train, X_test, y_train, y_test, feature_names


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

_REGRESSION_MODELS = {
    "Linear Regression": LinearRegression,
    "Random Forest Regressor": lambda: RandomForestRegressor(n_estimators=100, random_state=42),
    "Decision Tree Regressor": lambda: DecisionTreeRegressor(random_state=42),
}

_CLASSIFICATION_MODELS = {
    "Logistic Regression": lambda: LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest Classifier": lambda: RandomForestClassifier(n_estimators=100, random_state=42),
    "Decision Tree Classifier": lambda: DecisionTreeClassifier(random_state=42),
}


def train_model(X_train, y_train, model_name: str, task_type: str):
    """
    Instantiate and fit the named model.

    Supported models
    ----------------
    Regression : "Linear Regression", "Random Forest Regressor",
                 "Decision Tree Regressor"
    Classification : "Logistic Regression", "Random Forest Classifier",
                     "Decision Tree Classifier"

    Returns
    -------
    Trained sklearn estimator.
    """
    if task_type == "regression":
        registry = _REGRESSION_MODELS
    elif task_type == "classification":
        registry = _CLASSIFICATION_MODELS
    else:
        raise ValueError(f"Unknown task_type: {task_type!r}. Use 'regression' or 'classification'.")

    if model_name not in registry:
        raise ValueError(
            f"Model '{model_name}' not supported for {task_type}. "
            f"Choose from: {list(registry.keys())}"
        )

    factory = registry[model_name]
    model = factory() if callable(factory) else factory
    model.fit(X_train, y_train)
    return model


# ---------------------------------------------------------------------------
# Model evaluation
# ---------------------------------------------------------------------------

def evaluate_model(model, X_test, y_test, task_type: str) -> dict:
    """
    Evaluate a trained model and return a metrics dictionary.

    Regression  → {r2, mae, rmse, mse}
    Classification → {accuracy, precision, recall, f1,
                      confusion_matrix (list), classification_report (str)}
    """
    y_pred = model.predict(X_test)

    if task_type == "regression":
        mse = mean_squared_error(y_test, y_pred)
        return {
            "r2": float(r2_score(y_test, y_pred)),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
        }

    # Classification
    avg = "weighted"
    cm = confusion_matrix(y_test, y_pred)
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average=avg, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average=avg, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average=avg, zero_division=0)),
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(y_test, y_pred, zero_division=0),
    }


# ---------------------------------------------------------------------------
# Feature importance
# ---------------------------------------------------------------------------

def get_feature_importance(model, feature_names: list) -> dict | None:
    """
    Extract feature importances or coefficients from a trained model.

    Returns
    -------
    dict  {feature_name: importance_value}  or None if unavailable.
    """
    if hasattr(model, "feature_importances_"):
        return dict(zip(feature_names, model.feature_importances_.tolist()))

    if hasattr(model, "coef_"):
        coef = model.coef_
        # Multiclass: take mean absolute value across classes
        if coef.ndim > 1:
            coef = np.mean(np.abs(coef), axis=0)
        else:
            coef = np.abs(coef)
        return dict(zip(feature_names, coef.tolist()))

    return None


# ---------------------------------------------------------------------------
# K-Means clustering
# ---------------------------------------------------------------------------

def run_kmeans_clustering(
    df: pd.DataFrame,
    n_clusters: int,
    columns: list,
) -> tuple[pd.DataFrame, dict]:
    """
    StandardScale the specified columns, fit KMeans, and return results.

    Returns
    -------
    (df_with_cluster_col, {"inertia": float, "silhouette_score": float})
    """
    data = df[columns].dropna().copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = km.fit_predict(X_scaled)

    sil = silhouette_score(X_scaled, labels) if n_clusters > 1 else 0.0

    df_out = df.copy()
    # Align cluster labels back (some rows may have been dropped due to NaN)
    df_out["Cluster"] = np.nan
    df_out.loc[data.index, "Cluster"] = labels
    df_out["Cluster"] = df_out["Cluster"].astype("Int64")

    metrics = {
        "inertia": float(km.inertia_),
        "silhouette_score": float(sil),
    }
    return df_out, metrics
