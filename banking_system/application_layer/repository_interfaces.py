import os, datetime
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from domain_layer import Transaction


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
    
    # New methods for Week 2
    @abstractmethod
    def update_accounts_atomically(self, source_account, destination_account):
        """
        Updates two accounts atomically as part of a transfer operation.
        
        Args:
            source_account: The source account entity with updated balance
            destination_account: The destination account entity with updated balance
            
        Returns:
            True if both accounts were updated successfully, False otherwise
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
    
    # New methods for Week 2
    @abstractmethod
    def save_transfer_transaction(self, transfer_transaction):
        """
        Saves a transfer transaction to the persistence layer.
        
        Args:
            transfer_transaction: The transfer transaction entity to persist
            
        Returns:
            The ID of the persisted transfer transaction
        """
        pass
    
    @abstractmethod
    def get_transaction_by_id(self, transaction_id)->Transaction:
        """
        Retrieves a transaction by its ID.
        
        Args:
            transaction_id: The ID of the transaction to retrieve
            
        Returns:
            The transaction entity if found, None otherwise
        """
        pass


# New interfaces for Week 2

class NotificationAdapterInterface(ABC):
 
    
    @abstractmethod
    def notify(message):
        pass
    
    @abstractmethod
    def save_notification_preference(self, account_id, notification_type):
        """
        Saves a notification preference for an account.
        
        Args:
            account_id: The ID of the account
            notification_type: The type of notification (e.g., "email", "sms")
            
        Returns:
            True if preference was saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def remove_notification_preference(self, account_id, notification_type):
        """
        Removes a notification preference for an account.
        
        Args:
            account_id: The ID of the account
            notification_type: The type of notification (e.g., "email", "sms")
            
        Returns:
            True if preference was removed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_notification_preferences(self, account_id):
        """
        Gets all notification preferences for an account.
        
        Args:
            account_id: The ID of the account
            
        Returns:
            A list of notification preference objects
        """
        pass


class LoggingRepositoryInterface(ABC):
    """
    Abstract interface for transaction and system logging operations.
    To be implemented by concrete infrastructure classes.
    """
    
    @abstractmethod
    def log_transaction(self, transaction_id, account_id, action, details):
        """
        Logs a transaction-related event.
        
        Args:
            transaction_id: The ID of the transaction
            account_id: The ID of the associated account
            action: The action being performed (e.g., "deposit", "withdraw", "transfer")
            details: Additional details about the transaction
            
        Returns:
            The ID of the log entry
        """
        pass
    
    @abstractmethod
    def log_system_event(self, event_type, details):
        """
        Logs a system-level event.
        
        Args:
            event_type: The type of system event
            details: Additional details about the event
            
        Returns:
            The ID of the log entry
        """
        pass
    
    @abstractmethod
    def get_transaction_logs(self):
        """
        Retrieves all transaction logs.
        
        Returns:
            A list of transaction log entries
        """
        pass
    
    @abstractmethod
    def get_logs_by_account_id(self, account_id):
        """
        Retrieves all logs for a specific account.
        
        Args:
            account_id: The ID of the account
            
        Returns:
            A list of log entries for the specified account
        """
        pass
    
    @abstractmethod
    def get_logs_by_transaction_id(self, transaction_id):
        """
        Retrieves all logs for a specific transaction.
        
        Args:
            transaction_id: The ID of the transaction
            
        Returns:
            A list of log entries for the specified transaction
        """
        pass

class StatementAdapterInterface(ABC):
    def __init__(self, folder_name:str):
        self.folder_name = folder_name
        os.makedirs(folder_name, exist_ok=True)
    """
    Adapter interface to generate account statements in various formats.
    """
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> str:
        """
        Generate a statement from structured data and save to output_path.

        Args:
            data: A dict containing statement details, e.g., {
                'account_id': str,
                'period': 'YYYY-MM',
                'opening_balance': float,
                'closing_balance': float,
                'transactions': List[Dict],
            }
            output_path: File path where the statement will be saved.

        Returns:
            The path to the generated file.
        """
        pass

    def _build_file_path(self, account_id: str, file_extension: str) -> str:
        """
        Helper method to build the file path for the statement.

        Args:
            account_id: The ID of the account.
            file_extension: The file extension (e.g., '.pdf', '.csv').

        Returns:
            The full file path for the statement.
        """
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        return f"{self.folder_name}/statement_{account_id}_{current_date}.{file_extension}"
