from pathlib import Path
import sys
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "ml" / "model.pkl"
if str(ROOT / "ml") not in sys.path: sys.path.append(str(ROOT / "ml"))


def predict(features: dict) -> float:
    if not MODEL_PATH.exists():
        from train import train
        train()
    bundle = joblib.load(MODEL_PATH)
    row = {key: features.get(key, 0) for key in bundle["features"]}
    return round(float(bundle["model"].predict_proba(pd.DataFrame([row]))[0][1]), 4)
