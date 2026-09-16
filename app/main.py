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
