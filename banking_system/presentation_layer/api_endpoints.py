from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel, constr, confloat
from enum import Enum
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import application services and repository interfaces
from banking_system.application_layer.services import AccountService, TransactionService
from banking_system.application_layer.repository_interfaces import AccountRepositoryInterface, TransactionRepositoryInterface

# Import concrete repository implementations
from banking_system import AccountRepository, TransactionRepository,DictionaryStrategy

app = FastAPI(title="Banking Application API")

# Data Models for API
class account_type(str, Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"

class CreateAccountRequest(BaseModel):
    account_type: account_type
    initialDeposit: confloat(ge=0.0) = 0.0

class AccountResponse(BaseModel):
    account_id: str
    account_type: str
    balance: float
    status: str
    creation_date: str

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
    account_id: str

# FastAPI dependency injection system for repositories and services
def get_account_repository() -> AccountRepositoryInterface:
    """Provides an instance of the account repository."""
    return AccountRepository(strategy= DictionaryStrategy())

def get_transaction_repository() -> TransactionRepositoryInterface:
    """Provides an instance of the transaction repository."""
    return TransactionRepository()

def get_account_service(
    account_repo: AccountRepositoryInterface = Depends(get_account_repository)
) -> AccountService:
    """Provides an instance of the account service with its dependencies."""
    return AccountService(account_repo)

def get_transaction_service(
    account_repo: AccountRepositoryInterface = Depends(get_account_repository),
    transaction_repo: TransactionRepositoryInterface = Depends(get_transaction_repository)
) -> TransactionService:
    """Provides an instance of the transaction service with its dependencies."""
    return TransactionService(account_repo, transaction_repo)

@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: CreateAccountRequest, 
    account_service: AccountService = Depends(get_account_service),
    account_repo: AccountRepositoryInterface = Depends(get_account_repository)
):
    """
    Create a new account with the specified type and optional initial deposit.
    """
    try:
        # Log incoming request for debugging
        logger.info(f"Creating account: {request.dict()}")
        
        account_id = account_service.create_account(request.account_type.value, request.initialDeposit)
        account = account_repo.get_account_by_id(account_id)
        
        logger.info(f"Account created with ID: {account_id}")
        
        return AccountResponse(
            account_id=account.account_id,
            account_type=account.account_type,
            balance=account.balance,
            status=account.status,
            creation_date=account.creation_date.isoformat()
        )
    except ValueError as e:
        # For validation errors like minimum deposit
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the actual exception for debugging
        logger.exception(f"Error creating account: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/accounts/{account_id}/deposit", response_model=TransactionResponse)
async def deposit_funds(
    account_id: str,
    request: DepositRequest,
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Deposit funds into the specified account.
    """
    try:
        logger.info(f"Depositing {request.amount} to account {account_id}")
        transaction = transaction_service.deposit(account_id, request.amount)
        return TransactionResponse(
            transactionId=transaction.transactionId,
            transactionType=transaction.transactionType,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat(),
            account_id=transaction.account_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    except Exception as e:
        logger.exception(f"Error depositing funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/accounts/{account_id}/withdraw", response_model=TransactionResponse)
async def withdraw_funds(
    account_id: str,
    request: WithdrawRequest,
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Withdraw funds from the specified account.
    """
    try:
        logger.info(f"Withdrawing {request.amount} from account {account_id}")
        transaction = transaction_service.withdraw(account_id, request.amount)
        return TransactionResponse(
            transactionId=transaction.transactionId,
            transactionType=transaction.transactionType,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat(),
            account_id=transaction.account_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    except Exception as e:
        logger.exception(f"Error withdrawing funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_balance(
    account_id: str,
    account_repo: AccountRepositoryInterface = Depends(get_account_repository)
):
    """
    Get the current balance of the specified account.
    """
    try:
        logger.info(f"Getting balance for account {account_id}")
        account = account_repo.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # In this simple implementation, available balance equals current balance
        return BalanceResponse(
            balance=account.balance,
            availableBalance=account.balance
        )
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    except Exception as e:
        logger.exception(f"Error getting balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
async def get_transaction_history(
    account_id: str,
    transaction_repo: TransactionRepositoryInterface = Depends(get_transaction_repository)
):
    """
    Get the transaction history for the specified account.
    """
    try:
        logger.info(f"Getting transactions for account {account_id}")
        transactions = transaction_repo.get_transactions_by_account_id(account_id)
        
        return [
            TransactionResponse(
                transactionId=tx.transactionId,
                transactionType=tx.transactionType,
                amount=tx.amount,
                timestamp=tx.timestamp.isoformat(),
                account_id=tx.account_id
            ) for tx in transactions
        ]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    except Exception as e:
        logger.exception(f"Error getting transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api_endpoints:app", host="0.0.0.0", port=8000, reload=True)