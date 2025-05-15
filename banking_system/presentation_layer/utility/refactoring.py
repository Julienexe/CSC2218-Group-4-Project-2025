from application_layer.repository_interfaces import AccountRepositoryInterface, TransactionRepositoryInterface
from application_layer.services import LoggingService
from infrastructure_layer.account_repository import AccountRepository
from infrastructure_layer.strategies.dictionary_account_strategy import DictionaryAccountStrategy
from infrastructure_layer.strategies.dictionary_transaction_strategy import DictionaryTransactionStrategy
from infrastructure_layer.transaction_repository import TransactionRepository

account_repo: AccountRepository = AccountRepository(strategy= DictionaryAccountStrategy())
transaction_repo:TransactionRepository = TransactionRepository(strategy=DictionaryTransactionStrategy())
def get_account_repository() -> AccountRepositoryInterface:
    """Provides an instance of the account repository."""
    return account_repo

def get_transaction_repository() -> TransactionRepositoryInterface:
    """Provides an instance of the transaction repository."""
    return transaction_repo

def get_logging_service():
    return LoggingService()