import csv
from typing import Dict, Any
from .statement_adapter import StatementAdapterInterface

class CSVStatementAdapter(StatementAdapterInterface):
    """
    Generates a CSV account statement using Python's csv module.
    """
    def generate(self, data: Dict[str, Any], output_path: str) -> str:
        # data expected keys: account_id, period, opening_balance, closing_balance, transactions
        with open(output_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Header
            writer.writerow(['Account ID', data['account_id']])
            writer.writerow(['Balance', data['balance']])
            writer.writerow([])
            # Transactions
            writer.writerow(['Transaction ID', 'Type', 'Amount', 'Timestamp'])
            for tx in data.get('transactions', []):
                writer.writerow([tx['transaction_id'], tx['type'], tx['amount'], tx['timestamp']])
        return output_path