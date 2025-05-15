from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import FileResponse
from typing import Literal

from banking_system.infrastructure_layer.account_repository import AccountRepository
from banking_system.infrastructure_layer.transaction_repository import TransactionRepository
from banking_system.application_layer.services import StatementService
from banking_system.infrastructure_layer.statements.pdf_statement_adapter import PDFStatementAdapter
from banking_system.infrastructure_layer.statements.csv_statement_adapter import CSVStatementAdapter

router = APIRouter()

# Shared Repositories (injected into service)
account_repo = AccountRepository()
transaction_repo = TransactionRepository()

@router.get("/accounts/{accountId}/statement")
def get_monthly_statement(
    accountId: str = Path(..., description="ID of the account"),
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    format: Literal["pdf", "csv"] = Query("pdf", description="Format of the output")
):
    try:
        # Choose the adapter based on the format
        if format == "pdf":
            adapter = PDFStatementAdapter()
        elif format == "csv":
            adapter = CSVStatementAdapter()
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

        # Inject the adapter into the service
        statement_service = StatementService(account_repo, transaction_repo, adapter)

        # Generate statement file (this returns a file path)
        file_path = statement_service.generate_monthly_statement(accountId)

        return FileResponse(
            path=file_path,
            filename=file_path.split("/")[-1],
            media_type="application/pdf" if format == "pdf" else "text/csv"
        )

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
