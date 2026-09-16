from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime

@dataclass
class Wallet:
    wallet_id: str
    customer_id: str
    balance: Decimal
    currency: str = "USD"
    is_active: bool = True

@dataclass
class Transaction:
    transaction_id: str
    wallet_id: str
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
    description: Optional[str] = None
