import csv
from typing import Dict, Any
from banking_system import StatementAdapterInterface

class CSVStatementAdapter(StatementAdapterInterface):
    """
    Generates a CSV account statement using Python's csv module.
    """
    def generate(self, data: Dict[str, Any]) -> str:
        # data expected keys: account_id, period, opening_balance, closing_balance, transactions
        #create output path with account_id and current date
        output_path = self._build_file_path(data['account_id'], '.csv')
        with open(output_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Header
            writer.writerow(['Account ID', data['account_id']])
            writer.writerow(['Balance', data['balance']])
            writer.writerow([])
            # Transactions
            writer.writerow(['Transaction ID', 'Type', 'Amount', 'Timestamp'])
            for tx in data.get('transactions', []):
                writer.writerow([tx['transaction_id'], tx['transaction_type'], tx['amount'], tx['timestamp']])
        return output_path