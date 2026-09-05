"""Create a reproducible, relationship-driven failed-payment training dataset."""
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT = Path(__file__).with_name("dataset.csv")


def generate_data(rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    reasons = rng.choice(["network", "insufficient_funds", "card_expired", "bank_decline", "technical"], rows, p=[.28, .27, .15, .18, .12])
    methods = rng.choice(["card", "upi", "netbanking"], rows, p=[.62, .25, .13])
    attempts = rng.integers(1, 6, rows)
    successes = rng.integers(0, 14, rows)
    failures = rng.integers(0, 7, rows)
    tenure = rng.integers(10, 1500, rows)
    subscription_age = rng.integers(1, 900, rows)
    amount = rng.choice([299, 499, 799, 999, 1499, 2499, 4999], rows)
    days = rng.integers(0, 22, rows)
    segment = rng.choice(["new", "standard", "loyal", "enterprise"], rows, p=[.2, .5, .23, .07])
    historical = np.clip((successes + 1) / (successes + failures + 3), .05, .98)
    logit = -0.45 + 1.3 * (reasons == "network") + .85 * (reasons == "technical") - 1.25 * (reasons == "card_expired") - .65 * (reasons == "bank_decline") - .45 * (reasons == "insufficient_funds") - .55 * (attempts - 1) + .16 * successes - .23 * failures - .07 * days + .6 * historical + .3 * (segment == "loyal") + .18 * (segment == "enterprise") - .00008 * amount
    probability = 1 / (1 + np.exp(-logit))
    recovered = rng.binomial(1, probability)
    return pd.DataFrame({
        "customer_id": [f"C{1000+i}" for i in range(rows)], "subscription_id": [f"sub_{1000+i}" for i in range(rows)],
        "amount": amount, "payment_method": methods, "failure_reason": reasons, "attempt_number": attempts,
        "previous_successes": successes, "previous_failures": failures, "customer_tenure_days": tenure,
        "subscription_age_days": subscription_age, "plan_value": amount, "days_since_failure": days,
        "historical_recovery_rate": historical.round(3), "customer_segment": segment, "recovered": recovered,
    })


if __name__ == "__main__":
    generate_data().to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT}")
