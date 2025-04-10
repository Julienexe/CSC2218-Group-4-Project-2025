# domain/entities/transaction.py

from enum import Enum
import uuid
from datetime import datetime


class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class Transaction:
    """
    Represents a financial transaction within the banking system.
    Attributes:
        transaction_id (str): A unique identifier for the transaction, generated using UUID.
        transaction_type (TransactionType): The type of the transaction (e.g., deposit or withdrawal).
        amount (float): The amount involved in the transaction. Must be a positive value.
        timestamp (datetime): The date and time when the transaction was created, in UTC.
        account_id (str): The identifier of the account associated with the transaction.
    Methods:
        is_deposit() -> bool:
            Checks if the transaction is a deposit.
        is_withdrawal() -> bool:
            Checks if the transaction is a withdrawal.
        __repr__() -> str:
            Returns a string representation of the transaction object.
    """
    def __init__(self, transaction_type: TransactionType, amount: float, account_id: str):
        if amount <= 0:
            raise ValueError("Transaction amount must be positive.")

        self.transaction_id = str(uuid.uuid4())
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now(datetime.UTC)
        self.account_id = account_id

    def is_deposit(self) -> bool:
        return self.transaction_type == TransactionType.DEPOSIT

    def is_withdrawal(self) -> bool:
        return self.transaction_type == TransactionType.WITHDRAW

    def __repr__(self):
        return (
            f"<Transaction(id={self.transaction_id}, "
            f"type={self.transaction_type.value}, "
            f"amount={self.amount}, "
            f"account_id={self.account_id}, "
            f"timestamp={self.timestamp.isoformat()})>"
        )
