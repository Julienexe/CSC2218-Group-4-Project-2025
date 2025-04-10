"""
Root package initialization for the Banking System project.
Exposes core components for easy access across layers.
"""

# Package metadata
__version__ = "1.0.0"
__author__ = "CSC2218 Group-4-Project-2025"

# Import key classes/functions to simplify external imports
from banking_system.domain_layer.entities.account import (
    Account,
)

from banking_system.domain_layer.entities.transaction import (
    Transaction,
    TransactionType
)

from banking_system.application_layer.services import (
    AccountCreationService,
    TransactionService
)

from banking_system.infrastructure_layer.repositories import (
    AccountRepository,
    TransactionRepository
)

# Define what gets imported with `from banking_system import *`
__all__ = [
    "AccountCreateService",
    "TransactionService",
    "Account",
    "Transaction",
    "AccountRepository",
    "TransactionRepository"
]

# Optional: Initialize package-wide configurations
def _initialize_package():
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info("Banking system package initialized")

_initialize_package()