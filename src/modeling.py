import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.config import load_config
from src.data import Preprocessor, load_dataset


def compute_metrics(y_true, y_pred, labels):
    metrics = {
        "macro_f1": f1_score(y_true, y_pred, labels=labels, average="macro"),
        "macro_precision": precision_score(y_true, y_pred, labels=labels, average="macro"),
        "macro_recall": recall_score(y_true, y_pred, labels=labels, average="macro"),
        "micro_f1": f1_score(y_true, y_pred, labels=labels, average="micro"),
    }

    per_class = {}
    for label in labels:
        per_class[str(label)] = {
            "precision": precision_score(y_true, y_pred, labels=[label], average="macro"),
            "recall": recall_score(y_true, y_pred, labels=[label], average="macro"),
            "f1": f1_score(y_true, y_pred, labels=[label], average="macro"),
        }

    metrics["per_class"] = per_class
    metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    return metrics


def train_logistic(X_train, y_train, config):
    params = config.get("training", {}).get("logistic", {})
    model = LogisticRegression(
        max_iter=params.get("max_iter", 300),
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train, config):
    try:
        from xgboost import XGBClassifier
    except ImportError as exc:
        raise ImportError(
            "xgboost is required. Install with: pip install xgboost"
        ) from exc

    params = config.get("training", {}).get("xgboost", {})
    num_class = int(len(np.unique(y_train)))
    model = XGBClassifier(
        n_estimators=params.get("n_estimators", 200),
        max_depth=params.get("max_depth", 4),
        learning_rate=params.get("learning_rate", 0.1),
        subsample=params.get("subsample", 1.0),
        colsample_bytree=params.get("colsample_bytree", 1.0),
        reg_lambda=params.get("reg_lambda", 1.0),
        objective="multi:softprob",
        num_class=num_class,
        eval_metric="mlogloss",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def train_dbscan(X_train, config):
    params = config.get("training", {}).get("dbscan", {})
    model = DBSCAN(
        eps=params.get("eps", 0.5),
        min_samples=params.get("min_samples", 5),
    )
    model.fit(X_train)
    return model


def _label_name(label_map, class_id):
    if class_id in label_map:
        return label_map[class_id]
    if str(class_id) in label_map:
        return label_map[str(class_id)]
    return str(class_id)


def run_training_pipeline(config_path=None):
    config = load_config(config_path)
    df = load_dataset(config)

    features = config["features"]
    target = config["target"]
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' is missing from dataset")

    df[target] = pd.to_numeric(df[target], errors="coerce").fillna(0).astype(int)

    preprocessor = Preprocessor(features)
    X = preprocessor.fit_transform(df)
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.get("training", {}).get("test_size", 0.2),
        random_state=config.get("training", {}).get("random_state", 42),
        stratify=y if len(set(y)) > 1 else None,
    )

    logistic_model = train_logistic(X_train, y_train, config)
    xgb_model = train_xgboost(X_train, y_train, config)
    dbscan_model = train_dbscan(X_train, config)

    xgb_pred = xgb_model.predict(X_test)
    labels = sorted(set(y))
    metrics = compute_metrics(y_test, xgb_pred, labels)

    model_dir = Path(config["paths"]["model_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(logistic_model, model_dir / "baseline_logistic.joblib")
    joblib.dump(xgb_model, model_dir / "xgboost_risk.joblib")
    joblib.dump(dbscan_model, model_dir / "dbscan_spatial.joblib")
    joblib.dump(preprocessor.scaler, model_dir / "feature_scaler.joblib")

    metrics_path = model_dir / "metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


def load_metrics(config=None, config_path=None):
    if config is None:
        config = load_config(config_path)
    model_dir = Path(config["paths"]["model_dir"])
    metrics_path = model_dir / "metrics.json"
    if metrics_path.exists():
        with metrics_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_artifacts(config=None, config_path=None):
    if config is None:
        config = load_config(config_path)

    model_dir = Path(config["paths"]["model_dir"])
    paths = {
        "logistic": model_dir / "baseline_logistic.joblib",
        "xgboost": model_dir / "xgboost_risk.joblib",
        "dbscan": model_dir / "dbscan_spatial.joblib",
        "scaler": model_dir / "feature_scaler.joblib",
    }

    if not all(path.exists() for path in paths.values()):
        return None

    return {
        "logistic": joblib.load(paths["logistic"]),
        "xgboost": joblib.load(paths["xgboost"]),
        "dbscan": joblib.load(paths["dbscan"]),
        "scaler": joblib.load(paths["scaler"]),
    }


def predict_risk(df_input, config, artifacts):
    features = config["features"]
    X = df_input[features].copy()
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.fillna(X.median(numeric_only=True))

    scaler = artifacts["scaler"]
    X_scaled = scaler.transform(X)

    xgb_model = artifacts["xgboost"]
    probs = xgb_model.predict_proba(X_scaled)
    pred_class = probs.argmax(axis=1)
    pred_prob = probs.max(axis=1)

    logistic_model = artifacts["logistic"]
    baseline_class = logistic_model.predict(X_scaled)

    label_map = config.get("risk_labels", {})
    pred_label = [_label_name(label_map, cls) for cls in pred_class]

    return pd.DataFrame(
        {
            "predicted_class": pred_class,
            "predicted_label": pred_label,
            "predicted_probability": pred_prob,
            "baseline_class": baseline_class,
        }
    )
