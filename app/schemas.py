from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class TransactionResponse(BaseModel):
    id: int
    wallet_id: int
    amount: Decimal
    status: TransactionStatus
    parent_transaction_id: Optional[int] = None

    class Config:
        orm_mode = True

class WalletCreate(BaseModel):
    initial_balance: Decimal = Field(default=0)

class WalletResponse(BaseModel):
    id: int
    balance: Decimal

    class Config:
        orm_mode = True

class ChargeRequest(BaseModel):
    wallet_id: int
    amount: Decimal

class RefundRequest(BaseModel):
    """Payload for creating a refund.

    The client only needs to supply the ID of the original COMPLETED transaction.
    """
    transaction_id: int
