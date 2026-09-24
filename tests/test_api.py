from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert "Fintech Payment Service" in response.text
    assert "text/html" in response.headers["content-type"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "fintech-payment-service"

def test_api_workflow():
    # 1. Create wallet
    create_res = client.post("/api/v1/wallets", json={
        "customer_id": "cust_test_100",
        "initial_balance": 200.0
    })
    assert create_res.status_code == 200
    wallet_data = create_res.json()
    wallet_id = wallet_data["wallet_id"]
    assert wallet_data["balance"] == 200.0

    # 2. Get wallet
    get_res = client.get(f"/api/v1/wallets/{wallet_id}")
    assert get_res.status_code == 200
    assert get_res.json()["customer_id"] == "cust_test_100"

    # 3. Charge wallet
    charge_res = client.post("/api/v1/charges", json={
        "wallet_id": wallet_id,
        "amount": 75.0,
        "description": "Test subscription"
    })
    assert charge_res.status_code == 200
    charge_data = charge_res.json()
    assert charge_data["status"] == "COMPLETED"
    assert charge_data["remaining_balance"] == 125.0
