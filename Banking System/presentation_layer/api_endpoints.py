# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel, constr, confloat
from enum import Enum
import uvicorn

# Import your services and repositories
from application_layer import AccountCreationService, TransactionService
from infrastructure_layer import AccountRepository, TransactionRepository

# Initialize repositories
account_repository = AccountRepository()
transaction_repository = TransactionRepository()

# Initialize services
account_service = AccountCreationService(account_repository)
transaction_service = TransactionService(account_repository, transaction_repository)

app = FastAPI(title="Banking Application API")

# Data Models for API
class AccountType(str, Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"

class CreateAccountRequest(BaseModel):
    accountType: AccountType
    initialDeposit: confloat(ge=0.0) = 0.0

class AccountResponse(BaseModel):
    accountId: str
    accountType: str
    balance: float
    status: str
    creationDate: str

class DepositRequest(BaseModel):
    amount: confloat(gt=0.0)

class WithdrawRequest(BaseModel):
    amount: confloat(gt=0.0)

class BalanceResponse(BaseModel):
    balance: float
    availableBalance: float

class TransactionResponse(BaseModel):
    transactionId: str
    transactionType: str
    amount: float
    timestamp: str
    accountId: str

# Service Dependencies
def get_account_service():
    return account_service

def get_transaction_service():
    return transaction_service

@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: CreateAccountRequest, 
    service: AccountCreationService = Depends(get_account_service)
):
    """
    Create a new account with the specified type and optional initial deposit.
    """
    try:
        account_id = service.create_account(request.accountType, request.initialDeposit)
        account = account_repository.get_account_by_id(account_id)
        
        return AccountResponse(
            accountId=account.accountId,
            accountType=account.accountType,
            balance=account.balance,
            status=account.status,
            creationDate=account.creationDate.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accounts/{account_id}/deposit", response_model=TransactionResponse)
async def deposit_funds(
    account_id: str,
    request: DepositRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    """
    Deposit funds into the specified account.
    """
    try:
        transaction = service.deposit(account_id, request.amount)
        return TransactionResponse(
            transactionId=transaction.transactionId,
            transactionType=transaction.transactionType,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat(),
            accountId=transaction.accountId
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accounts/{account_id}/withdraw", response_model=TransactionResponse)
async def withdraw_funds(
    account_id: str,
    request: WithdrawRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    """
    Withdraw funds from the specified account.
    """
    try:
        transaction = service.withdraw(account_id, request.amount)
        return TransactionResponse(
            transactionId=transaction.transactionId,
            transactionType=transaction.transactionType,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat(),
            accountId=transaction.accountId
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_balance(account_id: str):
    """
    Get the current balance of the specified account.
    """
    try:
        account = account_repository.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # In this simple implementation, available balance equals current balance
        # This could be enhanced later based on account type specific rules
        return BalanceResponse(
            balance=account.balance,
            availableBalance=account.balance
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
async def get_transaction_history(account_id: str):
    """
    Get the transaction history for the specified account.
    """
    try:
        transactions = transaction_repository.get_transactions_for_account(account_id)
        
        return [
            TransactionResponse(
                transactionId=tx.transactionId,
                transactionType=tx.transactionType,
                amount=tx.amount,
                timestamp=tx.timestamp.isoformat(),
                accountId=tx.accountId
            ) for tx in transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)