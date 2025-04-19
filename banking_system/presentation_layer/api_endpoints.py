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
from banking_system import AccountRepository, TransactionRepository,DictionaryStrategy, DictionaryTransactionStrategy
# Import Week 2 additional services and repositories
from banking_system.application_layer.services import FundTransferService, NotificationService
from banking_system.application_layer.repository_interfaces import LoggingRepositoryInterface
from banking_system import AccountRepository, TransactionRepository, LoggingRepository
from banking_system.infrastructure_layer.adapters import NotificationAdapter

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

# Week 2 - New Models
class TransferRequest(BaseModel):
    sourceAccountId: str
    destinationAccountId: str
    amount: confloat(gt=0.0)

class TransferResponse(BaseModel):
    transactionId: str
    sourceAccountId: str
    destinationAccountId: str
    amount: float
    timestamp: str
    status: str

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"

class NotificationRequest(BaseModel):
    accountId: str
    notifyType: NotificationType

class NotificationResponse(BaseModel):
    accountId: str
    notifyType: str
    status: str

class LogEntry(BaseModel):
    logId: str
    timestamp: str
    level: str
    message: str
    transactionId: Optional[str] = None
    accountId: Optional[str] = None

# FastAPI dependency injection system for repositories and services
def get_account_repository() -> AccountRepositoryInterface:
    """Provides an instance of the account repository."""
    return AccountRepository(strategy= DictionaryStrategy())

def get_transaction_repository() -> TransactionRepositoryInterface:
    """Provides an instance of the transaction repository."""
    return TransactionRepository(strategy=DictionaryTransactionStrategy())

def get_logging_repository() -> LoggingRepositoryInterface:
    """Provides an instance of the logging repository."""
    return LoggingRepository()

def get_notification_adapter() -> NotificationAdapter:
    """Provides an instance of the notification adapter."""
    return NotificationAdapter()

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

# Week 2 - New service dependencies
def get_fund_transfer_service(
    account_repo: AccountRepositoryInterface = Depends(get_account_repository),
    transaction_repo: TransactionRepositoryInterface = Depends(get_transaction_repository)
) -> FundTransferService:
    """Provides an instance of the fund transfer service with its dependencies."""
    return FundTransferService(account_repo, transaction_repo)

def get_notification_service(
    notification_adapter: NotificationAdapter = Depends(get_notification_adapter)
) -> NotificationService:
    """Provides an instance of the notification service with its dependencies."""
    return NotificationService(notification_adapter)

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

# Week 2 - New API Endpoints

@app.post("/accounts/transfer", response_model=TransferResponse)
async def transfer_funds(
    request: TransferRequest,
    fund_transfer_service: FundTransferService = Depends(get_fund_transfer_service)
):
    """
    Transfer funds from source account to destination account.
    """
    try:
        logger.info(f"Transferring {request.amount} from account {request.sourceAccountId} to account {request.destinationAccountId}")
        transfer = fund_transfer_service.transfer_funds(
            request.sourceAccountId, 
            request.destinationAccountId, 
            request.amount
        )
        
        return TransferResponse(
            transactionId=transfer.transactionId,
            sourceAccountId=request.sourceAccountId,
            destinationAccountId=request.destinationAccountId,
            amount=request.amount,
            timestamp=transfer.timestamp.isoformat(),
            status="completed"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error transferring funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notifications/subscribe", response_model=NotificationResponse)
async def subscribe_to_notifications(
    request: NotificationRequest,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Subscribe to notifications for a specific account.
    """
    try:
        logger.info(f"Subscribing to {request.notifyType} notifications for account {request.accountId}")
        subscription = notification_service.subscribe(request.accountId, request.notifyType)
        
        return NotificationResponse(
            accountId=request.accountId,
            notifyType=request.notifyType,
            status="subscribed"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Account {request.accountId} not found")
    except Exception as e:
        logger.exception(f"Error subscribing to notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notifications/unsubscribe", response_model=NotificationResponse)
async def unsubscribe_from_notifications(
    request: NotificationRequest,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Unsubscribe from notifications for a specific account.
    """
    try:
        logger.info(f"Unsubscribing from {request.notifyType} notifications for account {request.accountId}")
        notification_service.unsubscribe(request.accountId, request.notifyType)
        
        return NotificationResponse(
            accountId=request.accountId,
            notifyType=request.notifyType,
            status="unsubscribed"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Account {request.accountId} not found")
    except Exception as e:
        logger.exception(f"Error unsubscribing from notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/transactions", response_model=List[LogEntry])
async def get_transaction_logs(
    logging_repo: LoggingRepositoryInterface = Depends(get_logging_repository)
):
    """
    Retrieve the transaction logs (primarily for administrative purposes).
    """
    try:
        logger.info("Retrieving transaction logs")
        logs = logging_repo.get_transaction_logs()
        
        return [
            LogEntry(
                logId=log.log_id,
                timestamp=log.timestamp.isoformat(),
                level=log.level,
                message=log.message,
                transactionId=log.transaction_id,
                accountId=log.account_id
            ) for log in logs
        ]
    except Exception as e:
        logger.exception(f"Error retrieving transaction logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/logs", response_model=List[LogEntry])
async def get_account_logs(
    account_id: str,
    logging_repo: LoggingRepositoryInterface = Depends(get_logging_repository)
):
    """
    Retrieve logs for a specific account.
    """
    try:
        logger.info(f"Retrieving logs for account {account_id}")
        logs = logging_repo.get_logs_by_account_id(account_id)
        
        return [
            LogEntry(
                logId=log.log_id,
                timestamp=log.timestamp.isoformat(),
                level=log.level,
                message=log.message,
                transactionId=log.transaction_id,
                accountId=log.account_id
            ) for log in logs
        ]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    except Exception as e:
        logger.exception(f"Error retrieving account logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api_endpoints:app", host="0.0.0.0", port=8000, reload=True)