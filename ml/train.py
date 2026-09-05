"""Train and persist a small explainable recovery-probability model."""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).parent
DATA = ROOT / "dataset.csv"
MODEL = ROOT / "model.pkl"
METRICS = ROOT / "metrics.json"
FEATURES = ["amount", "payment_method", "failure_reason", "attempt_number", "previous_successes", "previous_failures", "customer_tenure_days", "subscription_age_days", "plan_value", "days_since_failure", "historical_recovery_rate", "customer_segment"]
CAT = ["payment_method", "failure_reason", "customer_segment"]
NUM = [f for f in FEATURES if f not in CAT]


def score(model, x_test, y_test):
    p = model.predict_proba(x_test)[:, 1]; y = (p >= .5).astype(int)
    return {"precision": round(precision_score(y_test, y, zero_division=0), 4), "recall": round(recall_score(y_test, y, zero_division=0), 4), "f1": round(f1_score(y_test, y, zero_division=0), 4), "roc_auc": round(roc_auc_score(y_test, p), 4), "confusion_matrix": confusion_matrix(y_test, y).tolist()}


def train():
    if not DATA.exists():
        from generate_data import generate_data
        generate_data().to_csv(DATA, index=False)
    frame = pd.read_csv(DATA); x_train, x_test, y_train, y_test = train_test_split(frame[FEATURES], frame.recovered, test_size=.2, random_state=42, stratify=frame.recovered)
    prep = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT), ("num", StandardScaler(), NUM)])
    candidates = {"logistic_regression": Pipeline([("prep", prep), ("model", LogisticRegression(max_iter=1000))]), "random_forest": Pipeline([("prep", prep), ("model", RandomForestClassifier(n_estimators=180, max_depth=9, min_samples_leaf=6, random_state=42, n_jobs=-1))])}
    results = {}
    for name, model in candidates.items():
        model.fit(x_train, y_train); results[name] = (score(model, x_test, y_test), model)
    best_name = max(results, key=lambda name: results[name][0]["roc_auc"])
    joblib.dump({"model": results[best_name][1], "features": FEATURES, "model_name": best_name}, MODEL)
    output = {name: metrics for name, (metrics, _) in results.items()} | {"best_model": best_name}
    METRICS.write_text(json.dumps(output, indent=2))
    return output


if __name__ == "__main__": print(json.dumps(train(), indent=2))
