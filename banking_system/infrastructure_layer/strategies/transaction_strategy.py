from abc import ABC, abstractmethod
from typing import List
from banking_system import Transaction

class TransactionStrategyInterface(ABC):
    """
    Abstract base class for transaction storage strategies.
    """
    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> str:
        """
        Persist a transaction and return its ID.
        """
        pass

    @abstractmethod
    def get_transactions_for_account(self, account_id: str) -> List[Transaction]:
        """
        Retrieve all transactions for a given account.
        """
        pass
