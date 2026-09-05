from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from app.db.models import AuditLog, Customer, PaymentEvent, RecoveryAction, Subscription
from app.services.diagnosis_service import diagnose
from app.services.ml_service import predict
from app.services.policy_engine import evaluate
from app.services.recovery_service import execute


def audit(db: Session, event_id: str, customer_id: str, event: str, result: str, action: str = "-", policy: str = "N/A", detail: str = ""):
    db.add(AuditLog(id=str(uuid4()), event_id=event_id, customer_id=customer_id, event=event, action=action, result=result, policy_status=policy, detail=detail))


def process_incident(db: Session, data: dict) -> dict:
    event_id = data.get("event_id") or f"evt_demo_{uuid4().hex[:12]}"
    data = data | {"event_id": event_id}
    existing = db.get(PaymentEvent, event_id)
    if existing:
        audit(db, event_id, existing.customer_id, "Duplicate webhook ignored", "IGNORED", detail="Event ID was already processed."); db.commit()
        return {"duplicate": True, "event_id": event_id, "message": "Duplicate event ignored"}
    customer = db.get(Customer, data["customer_id"])
    if not customer:
        db.add(Customer(id=data["customer_id"], segment=data.get("customer_segment", "standard"), opted_out=data.get("opted_out", False)))
    db.merge(Subscription(id=data["subscription_id"], customer_id=data["customer_id"], status="pending"))
    db.add(PaymentEvent(id=event_id, event_type=data.get("event", "subscription.pending"), customer_id=data["customer_id"], subscription_id=data["subscription_id"], amount=float(data["amount"]), failure_reason=data.get("failure_reason", "unknown"), attempt_number=int(data.get("attempt_number", 1)), payload=data))
    audit(db, event_id, data["customer_id"], "Webhook received", "STORED", detail="Simulated failed-payment incident stored.")
    probability = predict(data)
    diagnosis, explanation = diagnose(data, probability)
    audit(db, event_id, data["customer_id"], "ML score generated", "COMPLETE", detail=f"Recovery probability: {probability:.2%}")
    policy = evaluate(data, probability)
    audit(db, event_id, data["customer_id"], "Policy evaluated", policy["status"], policy["action"], policy["status"], policy["reason"])
    result = execute(policy["action"], data, probability)
    action_id = str(uuid4())
    db.add(RecoveryAction(id=action_id, event_id=event_id, customer_id=data["customer_id"], amount=float(data["amount"]), recovery_probability=probability, action=policy["action"], status=result["status"], recovered_amount=result["recovered_amount"], diagnosis=diagnosis, reason=explanation + " " + policy["reason"], policy_status=policy["status"], requires_human=policy["requires_human"]))
    audit(db, event_id, data["customer_id"], "Recovery action executed", result["status"], policy["action"], policy["status"], result["detail"])
    db.commit()
    return {"event_id": event_id, "customer_id": data["customer_id"], "risk_score": round(1 - probability, 4), "recovery_probability": probability, "diagnosis": diagnosis, "recommended_action": policy["action"], "expected_recovery": round(probability * float(data["amount"]), 2), "reason": explanation + " " + policy["reason"], "requires_human": policy["requires_human"], "policy_check": policy["status"], "execution": result, "simulation_mode": True}
