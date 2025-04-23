# banking_system/application_layer/account_creation_service.py
from uuid import uuid4
from datetime import datetime
from banking_system import Transaction
from banking_system import CheckingAccount
from banking_system import SavingsAccount
from banking_system.application_layer.repository_interfaces import AccountRepositoryInterface, TransactionRepositoryInterface

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
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        # Get the source and destination accounts
        source_account = self.account_repository.get_account_by_id(source_account_id)
        destination_account = self.account_repository.get_account_by_id(destination_account_id)

        if not source_account:
            raise ValueError(f"Source account with ID {source_account_id} not found")
        if not destination_account:
            raise ValueError(f"Destination account with ID {destination_account_id} not found")

        # Check for sufficient funds in the source account
        if source_account.balance < amount:
            raise ValueError("Insufficient funds in the source account")

        # Withdraw from the source account
        source_account.balance -= amount
        self.account_repository.update_account(source_account)

        withdrawal_transaction = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            account_id=source_account_id
        )
        self.transaction_repository.save_transaction(withdrawal_transaction)

        # Deposit into the destination account
        destination_account.balance += amount
        self.account_repository.update_account(destination_account)

        deposit_transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            account_id=destination_account_id
        )
        self.transaction_repository.save_transaction(deposit_transaction)

        # Return both transactions for reference
        return {
            "withdrawal": withdrawal_transaction,
            "deposit": deposit_transaction
        }


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
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        # Get the account using the repository interface
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        # Update the account balance
        account.balance += amount
        self.account_repository.update_account(account)

        # Create and save the transaction using the repository interface
        transaction = Transaction(
            transactionId=str(uuid4()),
            transactionType="DEPOSIT",
            amount=amount,
            timestamp=datetime.now(),
            account_id=account_id
        )

        self.transaction_repository.save_transaction(transaction)

        # Notify and log the transaction
        self.notification_service.notify(transaction)
        self.logging_service.log_transaction(transaction)

        return transaction

    def withdraw(self, account_id, amount):
        """
        Withdraws the specified amount from the account if sufficient funds are available.
        Returns a Transaction object representing the withdrawal.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        # Get the account using the repository interface
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        # Check for sufficient funds
        if account.balance < amount:
            raise ValueError("Insufficient funds")

        # Update the account balance
        account.balance -= amount
        self.account_repository.update_account(account)

        # Create and save the transaction using the repository interface
        transaction = Transaction(
            transactionId=str(uuid4()),
            transactionType="WITHDRAW",
            amount=amount,
            timestamp=datetime.now(),
            account_id=account_id
        )

        self.transaction_repository.save_transaction(transaction)

        # Notify and log the transaction
        self.notification_service.notify(transaction)
        self.logging_service.log_transaction(transaction)

        return transaction