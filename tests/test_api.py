import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import stripe

from app.main import app
from app.payment_service import PaymentService

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_service():
    # Reset the service state before each test
    app.state.payment_service = PaymentService()
    # We need to update the reference in main.py
    import app.main
    app.main.payment_service = app.state.payment_service
    yield

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_wallet():
    response = client.post("/api/v1/wallets", json={"customer_id": "cust_123", "initial_balance": 100.0})
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "cust_123"
    assert data["balance"] == 100.0

def test_stripe_checkout_session_success():
    # Create a wallet first
    wallet_res = client.post("/api/v1/wallets", json={"customer_id": "cust_test", "initial_balance": 1000.0})
    wallet_id = wallet_res.json()["wallet_id"]
    
    mock_session = MagicMock()
    mock_session.id = "cs_test_123"
    mock_session.url = "https://checkout.stripe.com/test"
    
    with patch('stripe.checkout.Session.create', return_value=mock_session) as mock_create:
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_123"}):
            response = client.post("/api/v1/stripe/checkout-session", json={
                "wallet_id": wallet_id,
                "amount": 50.0,
                "currency": "USD",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "cs_test_123"
            assert data["url"] == "https://checkout.stripe.com/test"
            mock_create.assert_called_once()

def test_stripe_checkout_session_invalid_wallet():
    response = client.post("/api/v1/stripe/checkout-session", json={
        "wallet_id": "wal_nonexistent",
        "amount": 50.0,
        "currency": "USD",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel"
    })
    assert response.status_code == 404

def test_stripe_checkout_session_invalid_payload():
    # Test missing fields or invalid values
    response = client.post("/api/v1/stripe/checkout-session", json={
        "wallet_id": "",
        "amount": -10.0,
        "currency": "USD",
        "success_url": "invalid-url",
        "cancel_url": "https://example.com/cancel"
    })
    assert response.status_code == 422  # FastAPI validation error

def test_stripe_checkout_session_stripe_error():
    wallet_res = client.post("/api/v1/wallets", json={"customer_id": "cust_test", "initial_balance": 1000.0})
    wallet_id = wallet_res.json()["wallet_id"]
    
    with patch('stripe.checkout.Session.create', side_effect=stripe.error.StripeError("Test Error")):
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_123"}):
            response = client.post("/api/v1/stripe/checkout-session", json={
                "wallet_id": wallet_id,
                "amount": 50.0,
                "currency": "USD",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel"
            })
            assert response.status_code == 502
            assert "Stripe API error" in response.json()["detail"]

def test_stripe_checkout_session_missing_key():
    wallet_res = client.post("/api/v1/wallets", json={"customer_id": "cust_test", "initial_balance": 1000.0})
    wallet_id = wallet_res.json()["wallet_id"]
    
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": ""}):
        response = client.post("/api/v1/stripe/checkout-session", json={
            "wallet_id": wallet_id,
            "amount": 50.0,
            "currency": "USD",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        })
        # Our implementation raises HTTPException 500 for missing key
        assert response.status_code == 500
