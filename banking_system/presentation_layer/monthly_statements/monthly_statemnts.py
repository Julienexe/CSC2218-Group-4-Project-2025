from fastapi import HTTPException, Path, Query
from fastapi.responses import FileResponse
from typing import Literal
from application_layer.repository_interfaces import AccountRepositoryInterface, TransactionRepositoryInterface
from banking_system.infrastructure_layer.account_repository import AccountRepository
from banking_system.infrastructure_layer.transaction_repository import TransactionRepository
from banking_system.application_layer.services import StatementService
from banking_system.infrastructure_layer.statements.pdf_statement_adapter import PDFStatementAdapter
from banking_system.infrastructure_layer.statements.csv_statement_adapter import CSVStatementAdapter
from infrastructure_layer.strategies.dictionary_account_strategy import DictionaryAccountStrategy
from infrastructure_layer.strategies.dictionary_transaction_strategy import DictionaryTransactionStrategy
from main import app # Import your main FastAPI instance
from banking_system.presentation_layer.utility.refactoring import get_account_repository,get_transaction_repository

# Shared Repositories (injected into service)
account_repo = get_account_repository()
transaction_repo = get_transaction_repository()


@app.get("/accounts/{accountId}/statement")
def get_monthly_statement(
    accountId: str = Path(..., description="ID of the account"),
    
    format: Literal["pdf", "csv"] = Query("pdf", description="Format of the output")
):
    """
    Generates a monthly account statement in PDF or CSV format.
    """
    try:
        # Choose the adapter based on the format
        if format == "pdf":
            adapter = PDFStatementAdapter(folder_name="pdfs")
        elif format == "csv":
            adapter = CSVStatementAdapter(folder_name="csvs")
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

        # Inject the adapter into the service
        statement_service = StatementService(account_repo, transaction_repo, adapter)

        # Generate the file
        file_path = statement_service.generate_monthly_statement(accountId)

        return FileResponse(
            path=file_path,
            filename=file_path.split("/")[-1],
            media_type="application/pdf" if format == "pdf" else "text/csv"
        )

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        print(f"Error generating statement: {e}")
        # Log the error
        raise HTTPException(status_code=500, detail=str(e))
