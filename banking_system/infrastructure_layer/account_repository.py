# infrastructure/account_repository.py
from banking_system import Account, AccountRepositoryInterface
from .strategies.strategy import StrategyInterface as Strat

from typing import Optional


class AccountRepository(AccountRepositoryInterface):
    def __init__(self, strategy:Strat) -> None:
        """
        Initialize a repository for account operations.
        """
        self._strategy = strategy
    
    def create_account(self, account: 'Account') -> str:
        """
        Store a new account in the repository.
        
        Args:
            account (Account): The account object to store.
            
        Returns:
            str: The account ID.
        """
        account_id = self._strategy.create_account(account)
        return account_id
    
    
    def get_account_by_id(self, account_id: str) -> Optional['Account']:
        """
        Retrieve an account by its ID.
        
        Args:
            account_id (str): The unique identifier of the account.
            
        Returns:
            Optional[Account]: The Account object if found, else None.
        """
        return self._strategy.get_account_by_id(account_id)
    
    def update_account(self, account: 'Account') -> None:
        """
        Update an existing account in the repository.
        
        Args:
            account (Account): The account object with updated information.
            
        Raises:
            ValueError: If the account does not exist.
        """
        self._strategy.update_account(account)
