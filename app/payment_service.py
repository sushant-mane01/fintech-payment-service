from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from decimal import Decimal

from .models import Wallet, Transaction, TransactionStatus
from .schemas import (
    WalletCreate,
    WalletResponse,
    ChargeRequest,
    TransactionResponse,
    RefundRequest,
)
from .database import get_db

class PaymentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # ---------------------------------------------------------------------
    # Existing wallet & charge logic (unchanged – shown for context only)
    # ---------------------------------------------------------------------
    def create_wallet(self, payload: WalletCreate) -> WalletResponse:
        wallet = Wallet(balance=payload.initial_balance)
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return WalletResponse.from_orm(wallet)

    def process_charge(self, payload: ChargeRequest) -> TransactionResponse:
        wallet = self.db.query(Wallet).filter(Wallet.id == payload.wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        if wallet.balance < payload.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        wallet.balance -= payload.amount
        transaction = Transaction(
            wallet_id=wallet.id,
            amount=payload.amount,
            status=TransactionStatus.COMPLETED,
        )
        self.db.add_all([wallet, transaction])
        self.db.commit()
        self.db.refresh(transaction)
        return TransactionResponse.from_orm(transaction)

    # ---------------------------------------------------------------------
    # New refund logic
    # ---------------------------------------------------------------------
    def process_refund(self, payload: RefundRequest) -> TransactionResponse:
        """Create a refund for a previously COMPLETED transaction.

        Steps:
        1. Retrieve the original transaction; error 404 if missing.
        2. Verify its status is COMPLETED; error 400 otherwise.
        3. Credit the original amount back to the associated wallet.
        4. Record a new Transaction with status REFUNDED and a link to the
           original transaction via ``parent_transaction_id``.
        5. Return the newly created refund transaction.
        """
        # 1. Load original transaction
        original_tx = (
            self.db.query(Transaction)
            .filter(Transaction.id == payload.transaction_id)
            .first()
        )
        if not original_tx:
            raise HTTPException(status_code=404, detail="Original transaction not found")

        # 2. Validate status
        if original_tx.status != TransactionStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Only COMPLETED transactions can be refunded",
            )

        # 3. Credit wallet
        wallet = (
            self.db.query(Wallet)
            .filter(Wallet.id == original_tx.wallet_id)
            .with_for_update()
            .first()
        )
        if not wallet:
            # This should never happen if DB integrity is maintained
            raise HTTPException(status_code=500, detail="Associated wallet not found")

        wallet.balance += original_tx.amount

        # 4. Create refund transaction
        refund_tx = Transaction(
            wallet_id=wallet.id,
            amount=original_tx.amount,
            status=TransactionStatus.REFUNDED,
            parent_transaction_id=original_tx.id,
        )

        # 5. Persist changes atomically
        self.db.add_all([wallet, refund_tx])
        self.db.commit()
        self.db.refresh(refund_tx)

        return TransactionResponse.from_orm(refund_tx)
