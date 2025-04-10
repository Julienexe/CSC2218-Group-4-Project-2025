# infrastructure/account_repository.py
from banking_system.domain_layer import Account

from typing import Dict, Optional
# Import your Account class from the domain layer, e.g.:
# from domain.account import Account

class AccountRepository:
    def __init__(self) -> None:
        """
        Initialize an in-memory account storage.
        In a real implementation, this would connect to a database.
        """
        self._accounts: Dict[str, 'Account'] = {}
    
    def create_account(self, account: 'Account') -> str:
        """
        Store a new account in the repository.
        
        Args:
            account (Account): The account object to store.
            
        Returns:
            str: The account ID.
        """
        self._accounts[account.account_id] = account
        return account.account_id
    
    def get_account_by_id(self, account_id: str) -> Optional['Account']:
        """
        Retrieve an account by its ID.
        
        Args:
            account_id (str): The unique identifier of the account.
            
        Returns:
            Optional[Account]: The Account object if found, else None.
        """
        return self._accounts.get(account_id)
    
    def update_account(self, account: 'Account') -> None:
        """
        Update an existing account in the repository.
        
        Args:
            account (Account): The account object with updated information.
            
        Raises:
            ValueError: If the account does not exist.
        """
        if account.account_id not in self._accounts:
            raise ValueError(f"Account with ID {account.account_id} not found")
        self._accounts[account.account_id] = account
