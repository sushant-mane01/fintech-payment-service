from app.metrics import get_system_metrics

def test_metrics_payload():
    metrics = get_system_metrics()
    assert metrics["status"] == "healthy"
    assert metrics["service"] == "fintech-payment-service"
    assert metrics["uptime_seconds"] >= 0
