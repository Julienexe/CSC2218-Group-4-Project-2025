from fastapi import APIRouter, Path, Body, HTTPException, status
from typing import Optional
from datetime import date
from banking_system.application_layer.services import  InterestService
from banking_system import AccountRepository  
from pydantic import BaseModel

router = APIRouter()

# Response model
class InterestAppliedResponse(BaseModel):
    account_id: str
    message: str
    new_balance: float

# Optional request body
class InterestCalculationRequest(BaseModel):
    calculationDate: Optional[date] = None

# Initialize service
account_repository = AccountRepository()
interest_service = InterestService(account_repository)

@router.post(
    "/accounts/{accountId}/interest/calculate",
    response_model=InterestAppliedResponse,
    status_code=status.HTTP_200_OK
)
def calculate_interest(
    accountId: str = Path(..., description="ID of the account"),
    body: InterestCalculationRequest = Body(default={})
):
    try:
        # Apply interest
        interest_service.apply_interest_to_account(accountId)

        # Fetch updated account (assuming the repository supports this)
        account = account_repository.get_account_by_id(accountId)

        return InterestAppliedResponse(
            account_id=accountId,
            message="Interest successfully applied.",
            new_balance=account.balance
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")
