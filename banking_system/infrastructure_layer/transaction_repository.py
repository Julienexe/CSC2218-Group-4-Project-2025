from typing import List
from banking_system import TransactionRepositoryInterface, Transaction
from .strategies.transaction_strategy import TransactionStrategyInterface

class TransactionRepository(TransactionRepositoryInterface):
    def __init__(self, strategy: TransactionStrategyInterface) -> None:
        """
        Repository for transaction operations, using a pluggable strategy.
        """
        self._strategy = strategy

    def save_transaction(self, transaction: Transaction) -> str:
        """
        Persist a transaction and return its ID.
        """
        return self._strategy.save_transaction(transaction)

    def get_transactions_for_account(self, account_id: str) -> List[Transaction]:
        """
        Retrieve all transactions for a specific account.
        """
        return self._strategy.get_transactions_for_account(account_id)
