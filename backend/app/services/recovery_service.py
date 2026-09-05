def execute(action: str, data: dict, probability: float) -> dict:
    amount = float(data["amount"])
    # Deterministic simulation outcome derived from model likelihood, never a real payment action.
    recovered = action in {"RETRY", "PAYMENT_LINK"} and probability >= .55
    if action == "RETRY": return {"status": "SIMULATED_RECOVERED" if recovered else "SIMULATED_FAILED", "recovered_amount": amount if recovered else 0, "detail": "Demo-mode native retry simulated."}
    if action == "PAYMENT_LINK": return {"status": "SIMULATED_RECOVERED" if recovered else "SIMULATED_PENDING", "recovered_amount": amount if recovered else 0, "detail": f"Demo payment link: demo://recover/{data['event_id']}"}
    if action == "WAIT": return {"status": "PENDING", "recovered_amount": 0, "detail": "Demo-mode intervention scheduled after cooldown."}
    if action == "ESCALATE": return {"status": "HUMAN_REVIEW", "recovered_amount": 0, "detail": "Demo-mode merchant review item created."}
    return {"status": "STOPPED", "recovered_amount": 0, "detail": "Automation safely terminated."}
