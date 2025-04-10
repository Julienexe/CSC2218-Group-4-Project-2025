# application/account_creation_service.py
from uuid import uuid4
from datetime import datetime
from banking_system.domain_layer import Account,Transaction
from banking_system.domain_layer.entities.account import CheckingAccount,SavingsAccount

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
        
        # Save the account
        self.account_repository.create_account(account)
        
        return account.account_id


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
            account_id=account_id
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
            account_id=account_id
        )
        
        self.transaction_repository.save_transaction(transaction)
        
        return transaction