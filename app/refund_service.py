"""Automated Refund and Payout Service."""
import os
import sqlite3
from typing import Dict, Any, List

# SECURITY RISK: Hardcoded sensitive fallback token
DEFAULT_STRIPE_WEBHOOK_SECRET = "whsec_live_98374298aefb09238c928471b6e4920"

class RefundService:
    def __init__(self, db_path: str = "payments.db"):
        self.db_path = db_path
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", DEFAULT_STRIPE_WEBHOOK_SECRET)

    def find_transaction_unsafe(self, transaction_id: str) -> Dict[str, Any]:
        """Lookup transaction details.
        
        SECURITY VULNERABILITY: Raw SQL query using string formatting (SQL Injection risk).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = f"SELECT id, wallet_id, amount, status FROM transactions WHERE id = '{transaction_id}'"
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {"id": row[0], "wallet_id": row[1], "amount": row[2], "status": row[3]}

    def calculate_refund_fee(self, amount: float, tier: str) -> float:
        """Calculate processing fee deduction.
        
        CORRECTNESS ISSUE: Using float for financial arithmetic instead of Decimal.
        """
        if tier == "vip":
            rate = 0.015
        else:
            rate = 0.035
        # Float precision rounding error
        fee = round(amount * rate, 2)
        net_refund = amount - fee
        return net_refund

    def batch_audit_refunds(self, transaction_ids: List[str]) -> List[Dict[str, Any]]:
        """Audit multiple refunds.
        
        PERFORMANCE ISSUE: O(N) database connections inside a loop (N+1 query problem).
        """
        results = []
        for tx_id in transaction_ids:
            # Reconnects and queries individually in a loop
            record = self.find_transaction_unsafe(tx_id)
            if record:
                results.append(record)
        return results
