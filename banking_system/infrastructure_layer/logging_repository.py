import uuid
from typing import List, Dict
from banking_system.application_layer.repository_interfaces import LoggingRepositoryInterface

class LoggingRepository(LoggingRepositoryInterface):
    def __init__(self) -> None:
        """
        In-memory storage for transaction and system logs.
        """
        self._transaction_logs: List[Dict] = []
        self._system_logs: List[Dict] = []

    def log_transaction(self, transaction_id: str, account_id: str, action: str, details: str) -> str:
        """
        Logs a transaction-related event.
        """
        log_id = str(uuid.uuid4())
        entry = {
            'id': log_id,
            'transaction_id': transaction_id,
            'account_id': account_id,
            'action': action,
            'details': details
        }
        self._transaction_logs.append(entry)
        return log_id

    def log_system_event(self, event_type: str, details: str) -> str:
        """
        Logs a system-level event.
        """
        log_id = str(uuid.uuid4())
        entry = {
            'id': log_id,
            'event_type': event_type,
            'details': details
        }
        self._system_logs.append(entry)
        return log_id

    def get_transaction_logs(self) -> List[Dict]:
        """
        Retrieves all transaction logs.
        """
        return list(self._transaction_logs)

    def get_logs_by_account_id(self, account_id: str) -> List[Dict]:
        """
        Retrieves all logs for a specific account.
        """
        return [e for e in self._transaction_logs if e['account_id'] == account_id]

    def get_logs_by_transaction_id(self, transaction_id: str) -> List[Dict]:
        """
        Retrieves all logs for a specific transaction.
        """
        return [e for e in self._transaction_logs if e['transaction_id'] == transaction_id]
