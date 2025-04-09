# infrastructure/transaction_repository.py
from domain_layer import Transaction
from typing import Dict, List
# Import your Transaction class from the domain layer, e.g.:
# from domain.transaction import Transaction

class TransactionRepository:
    def __init__(self) -> None:
        """
        Initialize an in-memory transaction storage.
        In a real implementation, this would connect to a database.
        """
        self._transactions: Dict[str, 'Transaction'] = {}
        self._account_transactions: Dict[str, List['Transaction']] = {}
    
    def save_transaction(self, transaction: 'Transaction') -> str:
        """
        Store a new transaction in the repository.
        
        Args:
            transaction (Transaction): The transaction object to store.
            
        Returns:
            str: The transaction ID.
        """
        self._transactions[transaction.transaction_id] = transaction
        
        # Maintain a list of transactions for each account.
        if transaction.account_id not in self._account_transactions:
            self._account_transactions[transaction.account_id] = []
        self._account_transactions[transaction.account_id].append(transaction)
        
        return transaction.transaction_id
    
    def get_transactions_for_account(self, account_id: str) -> List['Transaction']:
        """
        Retrieve all transactions for a specific account.
        
        Args:
            account_id (str): The unique identifier of the account.
            
        Returns:
            List[Transaction]: A list of Transaction objects, or an empty list if none exist.
        """
        return self._account_transactions.get(account_id, [])
