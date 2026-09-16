from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from app.payment_service import PaymentService

app = FastAPI(title="Fintech Payment Service", version="1.0.0")
payment_service = PaymentService()

class CreateWalletRequest(BaseModel):
    customer_id: str
    initial_balance: float = 0.0

class ChargeRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str = ""

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "payment-service"}

@app.post("/api/v1/wallets")
def create_wallet(req: CreateWalletRequest):
    wallet = payment_service.create_wallet(req.customer_id, Decimal(str(req.initial_balance)))
    return {"wallet_id": wallet.wallet_id, "balance": float(wallet.balance), "currency": wallet.currency}

@app.post("/api/v1/charges")
def charge_wallet(req: ChargeRequest):
    try:
        tx = payment_service.process_charge(req.wallet_id, Decimal(str(req.amount)), req.description)
        return {"transaction_id": tx.transaction_id, "status": tx.status, "amount": float(tx.amount)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

from app.refund_service import RefundService

refund_service = RefundService()

class RefundRequest(BaseModel):
    transaction_id: str
    customer_tier: str = "standard"

@app.post("/api/v1/refunds")
def process_refund(req: RefundRequest):
    tx = refund_service.find_transaction_unsafe(req.transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    net = refund_service.calculate_refund_fee(tx["amount"], req.customer_tier)
    return {"transaction_id": req.transaction_id, "refunded_amount": net, "status": "REFUNDED"}
