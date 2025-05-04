"""
Root package initialization for the Banking System project.
Exposes core components for easy access across layers.
"""

# Package metadata
__version__ = "1.0.0"
__author__ = "CSC2218 Group-4-Project-2025"

# Import key classes/functions to simplify external imports
from banking_system.domain_layer.entities.bank_accounts.checking_account import (
    CheckingAccount,
)
from banking_system.domain_layer.entities.bank_accounts.savings_account import (
    SavingsAccount,
)

from banking_system.domain_layer.entities.bank_accounts.account import (
    Account,
    AccountStatus,
    AccountType,
)

from banking_system.domain_layer.entities.transaction import (
    Transaction,
    TransactionType
)

from banking_system.application_layer.services import (
    AccountService,
    TransactionService
)

from banking_system.application_layer.repository_interfaces import(
    AccountRepositoryInterface,TransactionRepositoryInterface
)

from banking_system.infrastructure_layer.account_repository import (
    AccountRepository,
)

from banking_system.infrastructure_layer.transaction_repository import (
    TransactionRepository,
)

from banking_system.infrastructure_layer.strategies.dictionary_strategy import (
    DictionaryStrategy,
)
from banking_system.infrastructure_layer.strategies.dictionary_transaction_strategy import(
    DictionaryTransactionStrategy
)

# Define what gets imported with `from banking_system import *`
__all__ = [
    "CheckingAccount",
    "SavingsAccount",
    "Transaction",
    "TransactionType",
    "AccountService",
    "TransactionService",
    "AccountRepository",
    "TransactionRepository",
    "AccountStatus",
    "AccountType",
    "Account",
    "AccountRepositoryInterface",
    "DictionaryStrategy",
    "TransactionRepositoryInterface",
    "DictionaryTransactionStrategy",
]

# Optional: Initialize package-wide configurations
def _initialize_package():
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info("Banking system package initialized")

_initialize_package()