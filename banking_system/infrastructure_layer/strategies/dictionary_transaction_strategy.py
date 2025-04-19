from typing import Dict, List
from banking_system import Transaction
from .transaction_strategy import TransactionStrategyInterface

class DictionaryTransactionStrategy(TransactionStrategyInterface):
    def __init__(self) -> None:
        """
        In-memory transaction storage.
        """
        self._transactions: Dict[str, Transaction] = {}
        self._account_transactions: Dict[str, List[Transaction]] = {}

    def save_transaction(self, transaction: Transaction) -> str:
        """
        Store a new transaction in memory.
        """
        self._transactions[transaction.transaction_id] = transaction
        self._account_transactions.setdefault(transaction.account_id, []).append(transaction)
        return transaction.transaction_id

    def get_transactions_for_account(self, account_id: str) -> List[Transaction]:
        """
        Retrieve all transactions for the specified account.
        """
        return self._account_transactions.get(account_id, [])