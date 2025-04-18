# banking_system/application_layer/interfaces/repositories.py

from abc import ABC, abstractmethod

class AccountRepositoryInterface(ABC):
    """
    Abstract interface for account repository operations.
    To be implemented by concrete infrastructure classes.
    """
    
    @abstractmethod
    def create_account(self, account):
        """
        Creates a new account in the persistence layer.
        
        Args:
            account: The account entity to persist
        """
        pass
    
    @abstractmethod
    def get_account_by_id(self, account_id):
        """
        Retrieves an account by its ID.
        
        Args:
            account_id: The ID of the account to retrieve
            
        Returns:
            The account entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_account(self, account):
        """
        Updates an existing account in the persistence layer.
        
        Args:
            account: The account entity with updated values
        """
        pass


class TransactionRepositoryInterface(ABC):
    """
    Abstract interface for transaction repository operations.
    To be implemented by concrete infrastructure classes.
    """
    
    @abstractmethod
    def save_transaction(self, transaction):
        """
        Saves a transaction to the persistence layer.
        
        Args:
            transaction: The transaction entity to persist
        """
        pass
    
    @abstractmethod
    def get_transactions_by_account_id(self, account_id):
        """
        Retrieves all transactions for a specific account.
        
        Args:
            account_id: The ID of the account
            
        Returns:
            A list of transaction entities
        """
        pass