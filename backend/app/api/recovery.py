from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import AuditLog, Customer, PaymentEvent, RecoveryAction
from app.db.session import get_db
from app.services.decision_service import process_incident

router = APIRouter(tags=["recovery"])

class Incident(BaseModel):
    event_id: str | None = None
    event: str = "subscription.pending"
    subscription_id: str
    customer_id: str
    amount: float = Field(gt=0)
    failure_reason: str
    attempt_number: int = Field(default=1, ge=1)
    payment_method: str = "card"
    previous_successes: int = 4
    previous_failures: int = 0
    customer_tenure_days: int = 180
    subscription_age_days: int = 90
    plan_value: float | None = None
    days_since_failure: int = 0
    historical_recovery_rate: float = .7
    customer_segment: str = "standard"
    opted_out: bool = False
    already_successful: bool = False

SCENARIOS = {
 "transient_failure": {"amount": 999, "failure_reason":"network", "attempt_number":1, "previous_successes":9, "previous_failures":0, "customer_segment":"loyal"},
 "payment_method_issue": {"amount": 799, "failure_reason":"card_expired", "attempt_number":1, "previous_successes":5, "previous_failures":1},
 "repeated_failure": {"amount": 1499, "failure_reason":"insufficient_funds", "attempt_number":3, "previous_successes":1, "previous_failures":4},
 "high_value_customer": {"amount": 4999, "failure_reason":"network", "attempt_number":1, "previous_successes":10, "customer_segment":"enterprise"},
 "max_attempts": {"amount": 999, "failure_reason":"network", "attempt_number":4, "previous_successes":2, "previous_failures":4},
}

@router.post("/webhooks/razorpay")
def webhook(body: dict, db: Session = Depends(get_db)):
    payload = body.get("payload", body)
    try: incident = Incident(**(payload | {"event": body.get("event", payload.get("event", "subscription.pending"))}))
    except Exception as exc: raise HTTPException(422, f"Invalid simulated webhook payload: {exc}")
    return process_incident(db, incident.model_dump() | {"plan_value": incident.plan_value or incident.amount})

@router.post("/demo/simulate")
def simulate(scenario: str = "transient_failure", db: Session = Depends(get_db)):
    if scenario not in SCENARIOS: raise HTTPException(400, "Unknown demo scenario")
    base = {"event_id": f"evt_{scenario}_{uuid4().hex[:8]}", "subscription_id": f"sub_demo_{uuid4().hex[:6]}", "customer_id": f"C{uuid4().int % 9000 + 1000}", "payment_method":"card", "customer_tenure_days":365, "subscription_age_days":180, "days_since_failure":0, "historical_recovery_rate":.72, "customer_segment":"standard", "plan_value":999}
    data = base | SCENARIOS[scenario]; data["plan_value"] = data["amount"]
    return process_incident(db, data)

@router.get("/recoveries")
def recoveries(db: Session = Depends(get_db)):
    return [{"id": x.id, "customer_id":x.customer_id, "amount":x.amount, "failure_reason": db.get(PaymentEvent, x.event_id).failure_reason if db.get(PaymentEvent, x.event_id) else "unknown", "recovery_probability":x.recovery_probability, "action":x.action, "status":x.status, "diagnosis":x.diagnosis, "reason":x.reason, "policy_status":x.policy_status, "requires_human":x.requires_human, "expected_recovery":round(x.amount*x.recovery_probability,2)} for x in db.query(RecoveryAction).order_by(RecoveryAction.created_at.desc()).all()]

@router.get("/customers")
def customers(db: Session = Depends(get_db)): return [{"id": c.id, "segment": c.segment, "opted_out": c.opted_out} for c in db.query(Customer).all()]

@router.get("/audit")
def audits(db: Session = Depends(get_db)): return [{"id":a.id,"timestamp":a.created_at.isoformat(),"event":a.event,"customer_id":a.customer_id,"action":a.action,"result":a.result,"policy_status":a.policy_status,"detail":a.detail} for a in db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()]

@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    items = db.query(RecoveryAction).all(); total = len(items); risk = sum(x.amount for x in items); recovered = sum(x.recovered_amount for x in items)
    # Baseline replays an uncontextualised generic retry: only high-confidence transient
    # first/second attempts recover; it cannot resolve expired methods or unsafe repeats.
    baseline = 0.0
    for item in items:
        payment = db.get(PaymentEvent, item.event_id)
        if payment and payment.failure_reason in {"network", "technical"} and payment.attempt_number < 3 and item.recovery_probability >= .75:
            baseline += item.amount
    return {"total_failed_payments":total,"revenue_at_risk":risk,"recovered_revenue":recovered,"recovery_rate":round(recovered/risk*100,2) if risk else 0,"pending_actions":sum(x.status in {"PENDING","SIMULATED_PENDING"} for x in items),"escalations":sum(x.action=="ESCALATE" for x in items),"stopped_automations":sum(x.action=="STOP" for x in items),"baseline_recovered_revenue":baseline,"recoverai_recovered_revenue":recovered,"improvement_percentage":round((recovered-baseline)/baseline*100,2) if baseline else 0}
