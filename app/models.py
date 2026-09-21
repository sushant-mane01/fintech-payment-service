from sqlalchemy import Column, Integer, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

# Assuming Base is defined elsewhere in the project (e.g., app/database.py)
from .database import Base

class TransactionStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"  # <-- new status for refund transactions

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Numeric, default=0)
    transactions = relationship("Transaction", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    amount = Column(Numeric, nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False)
    # New nullable FK to link a refund transaction to the original transaction
    parent_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)

    wallet = relationship("Wallet", back_populates="transactions")
    # Self‑referential relationship for refunds (optional, useful for ORM navigation)
    parent_transaction = relationship("Transaction", remote_side=[id], backref="refunds", uselist=False)
