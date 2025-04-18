import pytest
from fastapi.testclient import TestClient
from main import app, get_account_service, get_transaction_service
from application_layer import AccountCreationService, TransactionService
from infrastructure_layer import AccountRepository, TransactionRepository

# Create test repositories (mocked or in-memory implementations)
class TestAccountRepository(AccountRepository):
    def __init__(self):
        self.accounts = {}
    
    def create_account(self, account_type, initial_deposit):
        account_id = f"acc_{len(self.accounts) + 1}"
        self.accounts[account_id] = {
            "accountId": account_id,
            "accountType": account_type,
            "balance": initial_deposit,
            "status": "ACTIVE",
            "creationDate": "2025-04-10T12:00:00Z"
        }
        return account_id
    
    def get_account_by_id(self, account_id):
        return self.accounts.get(account_id)

class TestTransactionRepository(TransactionRepository):
    def __init__(self):
        self.transactions = []
    
    def add_transaction(self, account_id, transaction_type, amount):
        transaction_id = f"tx_{len(self.transactions) + 1}"
        transaction = {
            "transactionId": transaction_id,
            "transactionType": transaction_type,
            "amount": amount,
            "timestamp": "2025-04-10T12:30:00Z",
            "accountId": account_id
        }
        self.transactions.append(transaction)
        return transaction
    
    def get_transactions_for_account(self, account_id):
        return [tx for tx in self.transactions if tx["accountId"] == account_id]

# Replace dependencies with test implementations
test_account_repository = TestAccountRepository()
test_transaction_repository = TestTransactionRepository()
test_account_service = AccountCreationService(test_account_repository)
test_transaction_service = TransactionService(test_account_repository, test_transaction_repository)

def override_get_account_service():
    return test_account_service

def override_get_transaction_service():
    return test_transaction_service

app.dependency_overrides[get_account_service] = override_get_account_service
app.dependency_overrides[get_transaction_service] = override_get_transaction_service

client = TestClient(app)

# Test Cases
def test_create_account():
    response = client.post("/accounts", json={"accountType": "CHECKING", "initialDeposit": 100.0})
    assert response.status_code == 201
    data = response.json()
    assert data["accountType"] == "CHECKING"
    assert data["balance"] == 100.0
    assert data["status"] == "ACTIVE"

def test_deposit_funds():
    response = client.post("/accounts/acc_1/deposit", json={"amount": 50.0})
    assert response.status_code == 200
    data = response.json()
    assert data["transactionType"] == "DEPOSIT"
    assert data["amount"] == 50.0

def test_withdraw_funds():
    response = client.post("/accounts/acc_1/withdraw", json={"amount": 30.0})
    assert response.status_code == 200
    data = response.json()
    assert data["transactionType"] == "WITHDRAW"
    assert data["amount"] == 30.0

def test_get_balance():
    response = client.get("/accounts/acc_1/balance")
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "availableBalance" in data

def test_get_transaction_history():
    response = client.get("/accounts/acc_1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
