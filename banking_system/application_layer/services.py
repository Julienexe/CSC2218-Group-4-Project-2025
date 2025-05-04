# banking_system/application_layer/account_creation_service.py
from uuid import uuid4
from datetime import datetime
from banking_system import Transaction, TransactionType, Account, CheckingAccount, SavingsAccount
from banking_system.application_layer.repository_interfaces import AccountRepositoryInterface, TransactionRepositoryInterface
from domain_layer import validate_transaction
from .util import abstractions

class AccountService:
    def __init__(self, account_repository: AccountRepositoryInterface):
        self.account_repository = account_repository
    
    def create_account(self, account_type, initial_deposit=0.0):
        """
        Creates a new account with the specified type and initial deposit amount.
        Returns the ID of the newly created account.
        """
        # Check minimum deposit requirements based on account type
        if account_type == "SAVINGS" and initial_deposit < 100.0:
            raise ValueError("Savings accounts require a minimum initial deposit of $100.00")
        
        # Create a concrete account instance based on the account type
        if account_type == "CHECKING":
            account = CheckingAccount(
                account_type=account_type,
                initial_balance=initial_deposit,
            )
        elif account_type == "SAVINGS":
            account = SavingsAccount(
                account_type=account_type,
                initial_balance=initial_deposit,
            )
        else:
            raise ValueError(f"Unsupported account type: {account_type}")
        
        # Save the account using the repository interface
        self.account_repository.create_account(account)
        
        return account.account_id


class FundTransferService:
    def __init__(self, 
                 account_repository: AccountRepositoryInterface, 
                 transaction_repository: TransactionRepositoryInterface):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository

    def transfer_funds(self, source_account_id, destination_account_id, amount):
        """
        Transfers the specified amount from the source account to the destination account.
        Returns a dictionary containing the withdrawal and deposit transactions.
        """

        # Get the source and destination accounts
        source_account:Account = self.account_repository.get_account_by_id(source_account_id)
        destination_account = self.account_repository.get_account_by_id(destination_account_id)

        if not source_account:
            raise ValueError(f"Source account with ID {source_account_id} not found")
        if not destination_account:
            raise ValueError(f"Destination account with ID {destination_account_id} not found")

        transfer_transaction = source_account.transfer(amount, destination_account)
        abstractions.save_transaction(
            self.account_repository, 
            self.transaction_repository, 
            self.notification_service, 
            self.logging_service, 
            source_account, 
            transfer_transaction
        )

        

class NotificationService:
    def notify(self, transaction):
        """
        Sends a notification (e.g., email/SMS) to the account owner(s) about the transaction.
        """
        # Example notification logic (can be replaced with actual email/SMS integration)
        message = (
            f"Transaction Notification:\n"
            f"Type: {transaction.transaction_type}\n"
            f"Amount: ${transaction.amount:.2f}\n"
            f"Date: {transaction.timestamp}\n"
            f"Account ID: {transaction.account_id}\n"
        )
        print(f"Notification sent: {message}")


class LoggingService:
    def log(self, message):
        """
        Logs a message to the console or a file.
        """
        # Example logging logic 
        print(f"LOG: {message}")

    def log_transaction(self, transaction):
        """
        Logs details of a transaction.
        """
        log_message = (
            f"Transaction Log:\n"
            f"Type: {transaction.transaction_type}\n"
            f"Amount: ${transaction.amount:.2f}\n"
            f"Date: {transaction.timestamp}\n"
            f"Account ID: {transaction.account_id}\n"
        )
        self.log(log_message)


class TransactionService:
    def __init__(self, 
                 account_repository: AccountRepositoryInterface, 
                 transaction_repository: TransactionRepositoryInterface,
                 notification_service: NotificationService,
                 logging_service: LoggingService):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.notification_service = notification_service
        self.logging_service = logging_service

    def deposit(self, account_id, amount):
        """
        Deposits the specified amount into the account.
        Returns a Transaction object representing the deposit.
        """

        # Get the account using the repository interface
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        transaction = account.deposit(amount)

        abstractions.save_transaction(
            self.account_repository, 
            self.transaction_repository, 
            self.notification_service, 
            self.logging_service, 
            account, 
            transaction
        )

        return transaction

    def withdraw(self, account_id, amount):
        """
        Withdraws the specified amount from the account if sufficient funds are available.
        Returns a Transaction object representing the withdrawal.
        """

        # Get the account using the repository interface
        account:Account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")
        
        transaction = account.withdraw(amount)

        abstractions.save_transaction(
            self.account_repository, 
            self.transaction_repository, 
            self.notification_service, 
            self.logging_service, 
            account, 
            transaction
        )

        return transaction


class InterestService:
    def __init__(self, account_repository: AccountRepositoryInterface):
        self.account_repository = account_repository

    def apply_interest_to_account(self, account_id):
        """
        Applies interest to a specific account based on its type and balance.
        """
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        interest_rate = 0.02 if account.account_type == "SAVINGS" else 0.01
        interest = account.balance * interest_rate
        account.balance += interest
        self.account_repository.update_account(account)
        return interest

    def apply_interest_batch(self, account_ids):
        """
        Applies interest to a batch of accounts.
        """
        results = {}
        for account_id in account_ids:
            try:
                interest = self.apply_interest_to_account(account_id)
                results[account_id] = interest
            except ValueError as e:
                results[account_id] = str(e)
        return results


class LimitEnforcementService:
    def __init__(self):
        self.daily_limits = {}
        self.monthly_limits = {}

    def check_limit(self, account_id, transaction_amount):
        """
        Checks if the transaction amount exceeds daily or monthly limits.
        """
        daily_limit = self.daily_limits.get(account_id, 0)
        monthly_limit = self.monthly_limits.get(account_id, 0)

        if daily_limit + transaction_amount > 5000:
            return False  # Exceeds daily limit
        if monthly_limit + transaction_amount > 20000:
            return False  # Exceeds monthly limit

        # Update limits
        self.daily_limits[account_id] = daily_limit + transaction_amount
        self.monthly_limits[account_id] = monthly_limit + transaction_amount
        return True

    def reset_limits_daily(self):
        """
        Resets daily limits for all accounts.
        """
        self.daily_limits = {}

    def reset_limits_monthly(self):
        """
        Resets monthly limits for all accounts.
        """
        self.monthly_limits = {}


class StatementService:
    def __init__(self, transaction_repository: TransactionRepositoryInterface):
        self.transaction_repository = transaction_repository

    def generate_statement(self, account_id, start_date, end_date):
        """