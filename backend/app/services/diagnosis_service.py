def diagnose(data: dict, probability: float) -> tuple[str, str]:
    reason = data.get("failure_reason", "unknown")
    attempts = data.get("attempt_number", 1)
    if reason in {"network", "technical"} and attempts == 1:
        return "isolated transient payment failure", "A transient failure with an early attempt and payment history suggests retryability."
    if reason in {"card_expired", "bank_decline"}:
        return "payment method requires attention", "The payment method signal makes a fresh payment-link flow safer than repeated retries."
    if attempts >= 4:
        return "repeated collection failure", "Repeated attempts have exhausted safe automation limits."
    return "recoverable payment interruption", f"The model estimates a {probability:.0%} recovery chance from customer and payment context."
