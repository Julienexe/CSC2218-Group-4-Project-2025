
from typing import List, Optional
from banking_system.application_layer.repository_interfaces import TransactionRepositoryInterface
from banking_system import Transaction

class TransactionRepository(TransactionRepositoryInterface):
    def __init__(self, strategy) -> None:
        """
        Repository for transaction operations with pluggable storage strategy.
        """
        self._strategy:TransactionRepositoryInterface = strategy

    def save_transaction(self, transaction: Transaction) -> str:
        """
        Saves a transaction to the persistence layer.
        """
        return self._strategy.save_transaction(transaction)

    def get_transactions_by_account_id(self, account_id: str) -> List[Transaction]:
        """
        Retrieves all transactions for a specific account.
        """
        return self._strategy.get_transactions_by_account_id(account_id)

    def save_transfer_transaction(self, transfer_transaction: Transaction) -> str:
        """
        Saves a transfer transaction to the persistence layer.
        """
        return self._strategy.save_transaction(transfer_transaction)

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Retrieves a transaction by its ID.
        """
        return self._strategy.get_transaction_by_id(transaction_id)