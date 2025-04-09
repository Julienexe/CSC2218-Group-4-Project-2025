# domain/account.py
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Account:
    accountId: str
    accountType: str  # "CHECKING" or "SAVINGS"
    balance: float
    status: str  # "ACTIVE" or "CLOSED"
    creationDate: datetime

# domain/transaction.py
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Transaction:
    transactionId: str
    transactionType: str  # "DEPOSIT" or "WITHDRAW"
    amount: float
    timestamp: datetime
    accountId: str