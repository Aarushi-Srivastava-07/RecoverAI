from fastapi.testclient import TestClient
from app.main import app


def test_demo_scenarios_and_guardrails():
    with TestClient(app) as client:
        max_attempts = client.post("/api/demo/simulate?scenario=max_attempts").json()
        assert max_attempts["recommended_action"] == "STOP"
        high_value = client.post("/api/demo/simulate?scenario=high_value_customer").json()
        assert high_value["recommended_action"] == "ESCALATE"
        assert high_value["requires_human"] is True


def test_webhook_is_idempotent():
    payload = {"event": "subscription.pending", "payload": {"event_id":"evt_test_duplicate", "subscription_id":"sub_test", "customer_id":"C_test", "amount":999, "failure_reason":"network", "attempt_number":1}}
    with TestClient(app) as client:
        assert client.post("/api/webhooks/razorpay", json=payload).status_code == 200
        response = client.post("/api/webhooks/razorpay", json=payload)
        assert response.status_code == 200
        assert response.json()["duplicate"] is True
