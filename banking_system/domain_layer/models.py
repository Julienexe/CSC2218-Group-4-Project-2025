# domain/account.py
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Account:
    account_id: str
    account_type: str  # "CHECKING" or "SAVINGS"
    balance: float
    status: str  # "ACTIVE" or "CLOSED"
    creation_date: datetime

# domain/transaction.py
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Transaction:
    transactionId: str
    transactionType: str  # "DEPOSIT" or "WITHDRAW"
    amount: float
    timestamp: datetime
    account_id: str