from decimal import Decimal
import pytest
from app.payment_service import PaymentService

def test_wallet_creation():
    service = PaymentService()
    wallet = service.create_wallet("cust_101", Decimal("150.00"))
    assert wallet.customer_id == "cust_101"
    assert wallet.balance == Decimal("150.00")

def test_successful_charge():
    service = PaymentService()
    wallet = service.create_wallet("cust_102", Decimal("100.00"))
    tx = service.process_charge(wallet.wallet_id, Decimal("40.00"), "Groceries")
    assert tx.status == "COMPLETED"
    assert wallet.balance == Decimal("60.00")

def test_insufficient_funds():
    service = PaymentService()
    wallet = service.create_wallet("cust_103", Decimal("20.00"))
    with pytest.raises(ValueError, match="Insufficient balance"):
        service.process_charge(wallet.wallet_id, Decimal("50.00"))
