HIGH_VALUE_THRESHOLD = 3000


def evaluate(data: dict, probability: float) -> dict:
    if data.get("already_successful"):
        return {"action": "STOP", "status": "BLOCKED", "reason": "Payment already succeeded; no recovery action is permitted.", "requires_human": False}
    if data.get("opted_out"):
        return {"action": "STOP", "status": "BLOCKED", "reason": "Customer opted out of recovery communication.", "requires_human": False}
    if data.get("attempt_number", 1) >= 4:
        return {"action": "STOP", "status": "BLOCKED", "reason": "Maximum of three recovery attempts reached.", "requires_human": False}
    if data.get("amount", 0) > HIGH_VALUE_THRESHOLD:
        return {"action": "ESCALATE", "status": "PASSED", "reason": f"Amount exceeds merchant threshold of ₹{HIGH_VALUE_THRESHOLD:,.0f}.", "requires_human": True}
    if data.get("failure_reason") in {"card_expired", "bank_decline"}:
        return {"action": "PAYMENT_LINK", "status": "PASSED", "reason": "Payment method appears problematic; do not blindly retry.", "requires_human": False}
    if data.get("days_since_failure", 0) > 3:
        return {"action": "WAIT", "status": "PASSED", "reason": "Cooldown window applies before another intervention.", "requires_human": False}
    if probability >= .62 and data.get("failure_reason") in {"network", "technical"}:
        return {"action": "RETRY", "status": "PASSED", "reason": "High recovery probability for a likely transient failure.", "requires_human": False}
    if probability < .30:
        return {"action": "ESCALATE", "status": "PASSED", "reason": "Low recovery probability requires merchant review.", "requires_human": True}
    return {"action": "PAYMENT_LINK", "status": "PASSED", "reason": "A bounded recovery link is preferred to a generic retry.", "requires_human": False}
