"""Print held-out evaluation captured during training; never evaluates training rows."""
from pathlib import Path
import json

if __name__ == "__main__":
    path = Path(__file__).with_name("metrics.json")
    if not path.exists():
        from train import train
        train()
    print(path.read_text())
