"""create abstract class to act as template for all strategies"""
from abc import ABC, abstractmethod

class StrategyInterface(ABC):
    """
    Abstract base class for all strategies.
    This class defines the interface for the strategy pattern.
    """
    @abstractmethod
    def create_account(self, account):
        """
        Create a new account in the strategy.
        
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
        Updates an existing account in the strategy.
        
        Args:
            account: The account entity with updated values
        """
        pass