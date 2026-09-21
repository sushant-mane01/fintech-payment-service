from fastapi import FastAPI, Depends
from fastapi.routing import APIRouter
from .payment_service import PaymentService
from .schemas import (
    WalletCreate,
    WalletResponse,
    ChargeRequest,
    TransactionResponse,
    RefundRequest,
)

app = FastAPI(title="Payment Service")
router = APIRouter()

# ---------------------------------------------------------------------
# Wallet endpoints (unchanged – shown for context only)
# ---------------------------------------------------------------------
@router.post("/api/v1/wallets", response_model=WalletResponse, status_code=201)
async def create_wallet(payload: WalletCreate, service: PaymentService = Depends()):
    return service.create_wallet(payload)

# ---------------------------------------------------------------------
# Charge endpoint (unchanged – shown for context only)
# ---------------------------------------------------------------------
@router.post("/api/v1/charges", response_model=TransactionResponse, status_code=201)
async def create_charge(payload: ChargeRequest, service: PaymentService = Depends()):
    return service.process_charge(payload)

# ---------------------------------------------------------------------
# Refund endpoint – new implementation per SCRUM‑5
# ---------------------------------------------------------------------
@router.post(
    "/api/v1/refunds",
    response_model=TransactionResponse,
    status_code=201,
    summary="Create a refund for a completed transaction",
)
async def create_refund(
    payload: RefundRequest, service: PaymentService = Depends()
) -> TransactionResponse:
    """Refund a previously COMPLETED transaction.

    The endpoint expects a JSON body like ``{"transaction_id": 123}``.
    It returns the newly created refund transaction (status ``REFUNDED``).
    """
    return service.process_refund(payload)

app.include_router(router)
