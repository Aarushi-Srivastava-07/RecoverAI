"""Fair, reproducible counterfactual benchmark over the fixed synthetic cohort.

The database tracks interactive demo activity. It is intentionally not used for
strategy comparisons because a judge may run a scenario repeatedly. The benchmark
uses every row in ml/dataset.csv exactly once and its `recovered` label as ground
truth for both strategies.
"""
from functools import lru_cache
from pathlib import Path
import sys

import joblib
import pandas as pd

from app.services.policy_engine import evaluate

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "ml" / "dataset.csv"
MODEL = ROOT / "ml" / "model.pkl"
if str(ROOT / "ml") not in sys.path:
    sys.path.append(str(ROOT / "ml"))


@lru_cache
def synthetic_benchmark() -> dict:
    if not DATASET.exists() or not MODEL.exists():
        from train import train
        train()
    frame = pd.read_csv(DATASET)
    bundle = joblib.load(MODEL)
    probabilities = bundle["model"].predict_proba(frame[bundle["features"]])[:, 1]
    total_risk = float(frame["amount"].sum())
    ground_truth = frame["recovered"].astype(bool)
    # ALWAYS_RETRY attempts each event. Both strategies use the exact same target
    # label; no simulated executor status or database row affects this comparison.
    baseline = float(frame.loc[ground_truth, "amount"].sum())
    recoverai = 0.0
    action_counts: dict[str, int] = {}
    for row, probability, recovered in zip(frame.to_dict("records"), probabilities, ground_truth):
        policy = evaluate(row, float(probability))
        action_counts[policy["action"]] = action_counts.get(policy["action"], 0) + 1
        # The dataset records whether the failed payment is recoverable. RecoverAI
        # realizes that outcome only when its policy permits a bounded recovery flow.
        if recovered and policy["action"] in {"RETRY", "PAYMENT_LINK"}:
            recoverai += float(row["amount"])
    return {
        "label": "Synthetic benchmark — fixed 5,000-record cohort; not merchant money.",
        "cohort_size": len(frame),
        "revenue_at_risk": round(total_risk, 2),
        "always_retry_recovered_revenue": round(baseline, 2),
        "recoverai_recovered_revenue": round(recoverai, 2),
        "always_retry_recovery_rate": round(baseline / total_risk * 100, 2),
        "recoverai_recovery_rate": round(recoverai / total_risk * 100, 2),
        "improvement_percentage": round((recoverai - baseline) / baseline * 100, 2) if baseline else 0,
        "policy_action_counts": action_counts,
    }
