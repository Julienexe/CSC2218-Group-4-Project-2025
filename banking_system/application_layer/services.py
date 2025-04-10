# application/account_creation_service.py
from uuid import uuid4
from datetime import datetime
from banking_system.domain_layer import Account,Transaction

class AccountCreationService:
    def __init__(self, account_repository):
        self.account_repository = account_repository
    
    def create_account(self, account_type, initial_deposit=0.0):
        """
        Creates a new account with the specified type and initial deposit amount.
        Returns the ID of the newly created account.
        """
        # Check minimum deposit requirements based on account type
        if account_type == "SAVINGS" and initial_deposit < 100.0:
            raise ValueError("Savings accounts require a minimum initial deposit of $100.00")
        
        # Create a new account
        account_id = str(uuid4())
        account = Account(
            accountId=account_id,
            accountType=account_type,
            balance=initial_deposit,
            status="ACTIVE",
            creationDate=datetime.now()
        )
        
        # Save the account
        self.account_repository.create_account(account)
        
        return account_id


class TransactionService:
    def __init__(self, account_repository, transaction_repository):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
    
    def deposit(self, account_id, amount):
        """
        Deposits the specified amount into the account.
        Returns a Transaction object representing the deposit.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # Get the account
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")
        
        # Update the account balance
        account.balance += amount
        self.account_repository.update_account(account)
        
        # Create and save the transaction
        transaction = Transaction(
            transactionId=str(uuid4()),
            transactionType="DEPOSIT",
            amount=amount,
            timestamp=datetime.now(),
            accountId=account_id
        )
        
        self.transaction_repository.save_transaction(transaction)
        
        return transaction
    
    def withdraw(self, account_id, amount):
        """
        Withdraws the specified amount from the account if sufficient funds are available.
        Returns a Transaction object representing the withdrawal.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        # Get the account
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")
        
        # Check for sufficient funds
        if account.balance < amount:
            raise ValueError("Insufficient funds")
        
        # Update the account balance
        account.balance -= amount
        self.account_repository.update_account(account)
        
        # Create and save the transaction
        transaction = Transaction(
            transactionId=str(uuid4()),
            transactionType="WITHDRAW",
            amount=amount,
            timestamp=datetime.now(),
            accountId=account_id
        )
        
        self.transaction_repository.save_transaction(transaction)
        
        return transaction