import uuid
from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional
from app.models import Wallet, Transaction

class PaymentService:
    def __init__(self):
        self._wallets: Dict[str, Wallet] = {}
        self._transactions: Dict[str, Transaction] = {}

    def create_wallet(self, customer_id: str, initial_balance: Decimal = Decimal("0.00")) -> Wallet:
        wallet_id = f"wal_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id=wallet_id, customer_id=customer_id, balance=initial_balance)
        self._wallets[wallet_id] = wallet
        return wallet

    def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        return self._wallets.get(wallet_id)

    def process_charge(self, wallet_id: str, amount: Decimal, description: str = "") -> Transaction:
        wallet = self.get_wallet(wallet_id)
        if not wallet:
            raise ValueError(f"Wallet {wallet_id} not found.")
        if not wallet.is_active:
            raise ValueError("Wallet is inactive.")
        if wallet.balance < amount:
            raise ValueError("Insufficient balance.")

        wallet.balance -= amount
        tx_id = f"tx_{uuid.uuid4().hex[:12]}"
        tx = Transaction(
            transaction_id=tx_id,
            wallet_id=wallet_id,
            amount=amount,
            currency=wallet.currency,
            status="COMPLETED",
            created_at=datetime.utcnow(),
            description=description,
        )
        self._transactions[tx_id] = tx
        return tx

    def process_vendor_payout(self, wallet_id: str, amount: float, vendor_account: str) -> Dict[str, Any]:
        """Process vendor payout.
        
        CORRECTNESS ISSUE: Unhandled gateway timeout / missing rollback if network fails.
        """
        wallet = self.get_wallet(wallet_id)
        # Type inconsistency: comparing Decimal balance with float amount
        wallet.balance = float(wallet.balance) - amount
        
        # Simulated external payout dispatch without timeout / try-except
        import requests
        resp = requests.post("https://api.partner-bank.internal/v1/payout", json={
            "account": vendor_account,
            "amount": amount
        })
        return {"status": "SUCCESS", "vendor": vendor_account, "transferred": amount}
