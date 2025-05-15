

from enum import Enum
import uuid
from datetime import datetime

from ..util.validators import float_greater_than_zero


class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"


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
    def __init__(self, transaction_type: TransactionType, amount: float, account_id: str, destination_account_id: str = None):
        """
        Initializes a new transaction.
        Args:
            transaction_type (TransactionType): The type of the transaction (e.g., deposit, withdrawal).
            amount (float): The amount involved in the transaction. Must be a positive value.
            account_id (str): The identifier of the account associated with the transaction.
            destination_account_id (str, optional): The identifier of the destination account for transfer transactions.
        Raises:
            ValueError: If the transaction amount is not positive.
        """
        #check if the amount is less than zero
        if not float_greater_than_zero(amount):
            raise ValueError("Transaction amount must be positive.")

        self.transaction_id = str(uuid.uuid4())
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now()
        self.account_id = account_id
        self.destination_account_id = destination_account_id  

    def is_deposit(self) -> bool:
        return self.transaction_type == TransactionType.DEPOSIT

    def is_withdrawal(self) -> bool:
        return self.transaction_type == TransactionType.WITHDRAW
    
    def is_transfer(self) -> bool:
        return self.transaction_type == TransactionType.TRANSFER

    def __repr__(self):
        return (
            f"<Transaction(id={self.transaction_id}, "
            f"type={self.transaction_type.value}, "
            f"amount={self.amount}, "
            f"account_id={self.account_id}, "
            f"destination_account_id={self.destination_account_id if self.destination_account_id else None}, "
            f"timestamp={self.timestamp.isoformat()})>"
        )
