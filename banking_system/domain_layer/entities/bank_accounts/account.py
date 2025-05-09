from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import uuid, sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))
from domain_layer import validate_transaction,enforce_limits,float_greater_than_zero,Transaction, TransactionType, InterestStrategy, LimitConstraint





class AccountStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    # You can add more types like FIXED_DEPOSIT later


class Account(ABC):
    """
    The `Account` class serves as an abstract base class for different types of bank accounts. 
    It provides common attributes and methods that are shared across all account types, 
    while allowing specialized behavior to be implemented in subclasses.
    Attributes:
        account_id (str): A unique identifier for the account, generated using UUID.
        account_type (AccountType): The type of the account (e.g., savings, checking).
        balance (float): The current balance of the account. Defaults to 0.0.
        status (AccountStatus): The current status of the account (e.g., active, closed).
        creation_date (datetime): The date and time when the account was created.
    Methods:
        __init__(account_type: AccountType, initial_balance: float = 0.0):
            Initializes a new account with the specified type and initial balance.
            Raises a ValueError if the initial balance is negative.
        withdraw(amount: float):
            Abstract method to withdraw money from the account. 
            Must be implemented by subclasses to define specific withdrawal behavior.
        deposit(amount: float):
            Deposits a specified amount into the account. 
            Raises a ValueError if the deposit amount is not positive.
        close_account():
            Closes the account by setting its status to `CLOSED`.
        is_active() -> bool:
            Checks if the account is currently active.
        __repr__():
            Returns a string representation of the account, including its ID, type, 
            balance, status, and creation date.
    """
    def __init__(self, account_type: AccountType, initial_balance: float = 5.0,interest_strategy:InterestStrategy=None, limit_constraint:LimitConstraint=None):
        # Ensure initial balance is positive
        if not float_greater_than_zero(initial_balance):
            raise ValueError("Initial balance cannot be negative.")
        self.account_id = str(uuid.uuid4())
        self.account_type = account_type
        self.balance = initial_balance
        self.status = AccountStatus.ACTIVE
        self.creation_date = datetime.now()
        self.interest_strategy = interest_strategy
        self.limit_constraint = limit_constraint

    @validate_transaction("withdraw")  
    @enforce_limits
    def withdraw(self, amount: float):
        """Withdraw money from the account. Specialized behavior for different account types."""
        self._validate_before_withdraw(amount)
        
        self.balance -= amount

        #create a record of the transaction
        return Transaction(account_id=self.account_id, amount=amount,transaction_type=TransactionType.WITHDRAW)

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        #create a record of the transaction
        return Transaction(account_id=self.account_id, amount=amount,transaction_type=TransactionType.DEPOSIT)

    def close_account(self):
        self.status = AccountStatus.CLOSED

    def is_active(self) -> bool:
        return self.status == AccountStatus.ACTIVE
    
  
    def _validate_before_withdraw(self, amount: float):
        """Validate conditions before allowing withdrawal. Specialized behavior for different account types."""
        pass

    @validate_transaction("transfer")
    def transfer(self, amount: float, destination_account) -> Transaction:
        """Transfer money to another account."""
           

        # Perform the withdrawal and deposit
        self.withdraw(amount)
        destination_account.deposit(amount)

        #create a record of the transaction
        return Transaction(account_id=self.account_id, destination_account_id=destination_account.account_id,amount=amount,transaction_type=TransactionType.TRANSFER)

    def calculate_interest(self) -> float:
        self.balance = self.interest_strategy.apply_interest(self.balance)
    
    def generate_monthly_statement(self):
        """Generate a monthly statement for the account."""
        return {
            "account_id": self.account_id,
            "balance": self.balance,
            "interest_earned": self.interest_strategy.apply_interest(self.balance),
            "transactions": [],  
        }

    def __repr__(self):
        return (
            f"<Account(id={self.account_id}, "
            f"type={self.account_type.value}, "
            f"balance={self.balance:.2f}, "
            f"status={self.status.value}, "
            f"created={self.creation_date.isoformat()})>"
        )





