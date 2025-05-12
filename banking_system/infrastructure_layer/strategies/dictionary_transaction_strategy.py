from typing import Dict, List, Optional
from banking_system import Transaction
from .transaction_strategy import TransactionStrategyInterface

class DictionaryTransactionStrategy(TransactionStrategyInterface):
    def __init__(self) -> None:
        """
        In-memory transaction storage with transfer support.
        """
        self._transactions: Dict[str, Transaction] = {}
        self._account_transactions: Dict[str, List[Transaction]] = {}

    def save_transaction(self, transaction: Transaction) -> str:
        """
        Store a new transaction in memory.
        Supports both simple and transfer transactions by indexing
        under all involved account IDs.
        """
        tid = transaction.transaction_id
        self._transactions[tid] = transaction
        
        # Index transaction under primary account
        primary = getattr(transaction, 'account_id', None)
        if primary:
            self._account_transactions.setdefault(primary, []).append(transaction)

        # If this is a transfer, also index under destination account
        dest = getattr(transaction, 'destination_account_id', None)
        if dest:
            self._account_transactions.setdefault(dest, []).append(transaction)

        return tid

    def get_transactions_for_account(self, account_id: str) -> List[Transaction]:
        """
        Retrieve all transactions for the specified account.
        Returns a **new list** of transactions indexed under that account,
        sorted by (assumed) `timestamp` to give a consistent order.
        """
        # Fetch the list (or empty list if none)
        txns = self._account_transactions.get(account_id, [])
        # Return a shallow copy so caller can’t mutate internal state:
        ordered = list(txns)
        # If Transaction has a timestamp attribute, sort by it:
        if ordered and hasattr(ordered[0], "timestamp"):
            ordered.sort(key=lambda t: t.timestamp)
        return ordered

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Retrieve a single transaction by its ID.
        Returns None if no such transaction exists.
        """
        return self._transactions.get(transaction_id)