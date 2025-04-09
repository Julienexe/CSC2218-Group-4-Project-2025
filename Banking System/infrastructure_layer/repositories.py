# infrastructure/account_repository.py
class AccountRepository:
    def __init__(self):
        """
        Initialize an in-memory account storage.
        In a real implementation, this would connect to a database.
        """
        self.accounts = {}
    
    def create_account(self, account):
        """
        Store a new account in the repository.
        Returns the account ID.
        """
        self.accounts[account.accountId] = account
        return account.accountId
    
    def get_account_by_id(self, account_id):
        """
        Retrieve an account by its ID.
        Returns the Account object or None if not found.
        """
        return self.accounts.get(account_id)
    
    def update_account(self, account):
        """
        Update an existing account in the repository.
        """
        if account.accountId not in self.accounts:
            raise ValueError(f"Account with ID {account.accountId} not found")
        
        self.accounts[account.accountId] = account

# infrastructure/transaction_repository.py
class TransactionRepository:
    def __init__(self):
        """
        Initialize an in-memory transaction storage.
        In a real implementation, this would connect to a database.
        """
        self.transactions = {}
        self.account_transactions = {}
    
    def save_transaction(self, transaction):
        """
        Store a new transaction in the repository.
        Returns the transaction ID.
        """
        self.transactions[transaction.transactionId] = transaction
        
        # Maintain a list of transactions for each account
        if transaction.accountId not in self.account_transactions:
            self.account_transactions[transaction.accountId] = []
        
        self.account_transactions[transaction.accountId].append(transaction)
        
        return transaction.transactionId
    
    def get_transactions_for_account(self, account_id):
        """
        Retrieve all transactions for a specific account.
        Returns a list of Transaction objects.
        """
        return self.account_transactions.get(account_id, [])