from typing import Dict, List, Optional
from banking_system import Transaction, TransactionRepositoryInterface



class DictionaryTransactionStrategy(TransactionRepositoryInterface):
    def __init__(self) -> None:
        """
        In-memory transaction storage with transfer support.
        """
        self._transactions: Dict[str, Transaction] = {}
        self._account_transactions: Dict[str, List[Transaction]] = {}

    def save_transaction(self, transaction: Transaction) -> str:
        """
        Store a new transaction in memory.
        """
        tid = transaction.transaction_id
        self._transactions[tid] = transaction

        # Index under primary account
        primary = getattr(transaction, 'account_id', None)
        if primary:
            self._account_transactions.setdefault(primary, []).append(transaction)

        # If transfer, index under destination account as well
        dest = getattr(transaction, 'destination_account_id', None)
        if dest:
            self._account_transactions.setdefault(dest, []).append(transaction)

        return tid

    def get_transactions_by_account_id(self, account_id: str) -> List[Transaction]:
        """
        Retrieve all transactions for the specified account.
        Sorted by timestamp.
        """
        txns = self._account_transactions.get(account_id, [])
        ordered = list(txns)
        if ordered and hasattr(ordered[0], "timestamp"):
            ordered.sort(key=lambda t: t.timestamp)
        return ordered

    def save_transfer_transaction(self, transfer_transaction: Transaction) -> str:
        """
        Specifically saves a transfer transaction.
        This is treated the same as a regular transaction in memory.
        """
        return self.save_transaction(transfer_transaction)

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Retrieve a transaction by its ID.
        """
        return self._transactions.get(transaction_id)