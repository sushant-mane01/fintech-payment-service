import uuid
import os
from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional
from app.models import Wallet, Transaction

try:
    import stripe
except ImportError:
    stripe = None

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

    def create_stripe_checkout_session(self, wallet_id: str, amount: float, currency: str, success_url: str, cancel_url: str) -> dict:
        """
        Creates a Stripe Checkout Session for the specified wallet and amount.
        """
        if stripe is None:
            raise RuntimeError("Stripe library not installed.")
            
        api_key = os.getenv('STRIPE_SECRET_KEY')
        if not api_key:
            raise RuntimeError("STRIPE_SECRET_KEY environment variable is not set.")
            
        stripe.api_key = api_key
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'unit_amount': int(amount * 100),
                        'product_data': {
                            'name': 'Wallet Payment',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={'wallet_id': wallet_id},
            )
            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            raise e
