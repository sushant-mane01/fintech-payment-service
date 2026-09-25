from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
import os
import stripe

# Ensure Stripe secret key is available at startup
if not os.getenv("STRIPE_SECRET_KEY"):
    raise RuntimeError("STRIPE_SECRET_KEY environment variable not set")

from app.payment_service import PaymentService

app = FastAPI(
    title="Fintech Payment Service",
    description="High-performance serverless payment and wallet processing engine",
    version="1.0.0"
)
payment_service = PaymentService()

class CreateWalletRequest(BaseModel):
    customer_id: str
    initial_balance: float = 0.0

class ChargeRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str = ""

class StripeCheckoutRequest(BaseModel):
    wallet_id: str
    amount: float
    currency: str = "USD"
    success_url: str
    cancel_url: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "fintech-payment-service",
        "platform": "vercel",
        "version": "1.0.0"
    }

@app.get("/api/v1/wallets/{wallet_id}")
def get_wallet(wallet_id: str):
    wallet = payment_service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_id}' not found.")
    return {
        "wallet_id": wallet.wallet_id,
        "customer_id": wallet.customer_id,
        "balance": float(wallet.balance),
        "currency": wallet.currency,
        "is_active": wallet.is_active
    }

@app.post("/api/v1/wallets")
def create_wallet(req: CreateWalletRequest):
    if not req.customer_id.strip():
        raise HTTPException(status_code=400, detail="Customer ID cannot be empty.")
    if req.initial_balance < 0:
        raise HTTPException(status_code=400, detail="Initial balance cannot be negative.")
    wallet = payment_service.create_wallet(req.customer_id.strip(), Decimal(str(req.initial_balance)))
    return {
        "wallet_id": wallet.wallet_id,
        "customer_id": wallet.customer_id,
        "balance": float(wallet.balance),
        "currency": wallet.currency
    }

@app.post("/api/v1/charges")
def charge_wallet(req: ChargeRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Charge amount must be greater than zero.")
    # The rest of the charge logic would go here (omitted for brevity)
    raise HTTPException(status_code=501, detail="Charge endpoint not fully implemented.")

@app.post("/api/v1/stripe/checkout-session")
def create_stripe_checkout_session(req: StripeCheckoutRequest):
    # Basic payload validation (Pydantic already validates types)
    if not req.wallet_id.strip():
        raise HTTPException(status_code=400, detail="wallet_id cannot be empty.")
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than zero.")
    if not req.success_url.strip() or not req.cancel_url.strip():
        raise HTTPException(status_code=400, detail="Both success_url and cancel_url must be provided.")

    wallet = payment_service.get_wallet(req.wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"Wallet '{req.wallet_id}' not found.")

    # Initialize Stripe client
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    try:
        # Convert amount to the smallest currency unit (e.g., cents)
        unit_amount = int(req.amount * 100)
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": req.currency.lower(),
                    "unit_amount": unit_amount,
                    "product_data": {
                        "name": f"Top‑up for wallet {req.wallet_id}"
                    }
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata={"wallet_id": req.wallet_id},
        )
        return {"session_id": session.id, "url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=502, detail=str(e))
