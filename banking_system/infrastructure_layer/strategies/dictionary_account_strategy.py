import threading
from typing import Optional
from domain_layer import Account
from banking_system import AccountRepositoryInterface

class DictionaryAccountStrategy(AccountRepositoryInterface):
    def __init__(self) -> None:
        """
        In-memory account storage.
        """
        self._accounts: dict[str, Account] = {}
        self._lock = threading.Lock()

    def create_account(self, account: Account) -> str:
        """
        Persist a new account.
        Returns the account_id for convenience.
        """
        account_id = account.account_id
        self._accounts[account_id] = account
        return account_id

    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """
        Retrieve an account by ID.
        """
        return self._accounts.get(account_id)

    def update_account(self, account: Account) -> bool:
        """
        Update an existing account; returns True if updated, False if not found.
        """
        account_id = account.account_id
        if account_id not in self._accounts:
            return False
        self._accounts[account_id] = account
        return True

    def update_accounts_atomically(
        self, source_account: Account, destination_account: Account
    ) -> bool:
        """
        Atomically update two accounts (e.g. during a transfer).
        Returns True if both were updated, False otherwise.
        """
        with self._lock:
            src_id = source_account.account_id
            dst_id = destination_account.account_id

            # Ensure both accounts exist
            if src_id not in self._accounts or dst_id not in self._accounts:
                return False

            # Perform updates
            self._accounts[src_id] = source_account
            self._accounts[dst_id] = destination_account
            return True
