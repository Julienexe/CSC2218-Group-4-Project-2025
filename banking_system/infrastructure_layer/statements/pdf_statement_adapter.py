from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from typing import Dict, Any
from banking_system import StatementAdapterInterface

class PDFStatementAdapter(StatementAdapterInterface):
    """
    Generates a PDF account statement using ReportLab.
    """
    def generate(self, data: Dict[str, Any]) -> str:
        output_path = self._build_file_path(data['account_id'], '.pdf')
        c = canvas.Canvas(output_path, pagesize=LETTER)
        width, height = LETTER
        y = height - 50  # start from top
        # Header
        c.setFont('Helvetica-Bold', 16)
        c.drawString(50, y, f"Account Statement for {data['account_id']}")
        y -= 30
        c.setFont('Helvetica', 12)
        c.drawString(50, y, f"Period: {data['period']}")
        y -= 20
        c.drawString(50, y, f"Opening Balance: {data['opening_balance']}")
        y -= 20
        c.drawString(50, y, f"Closing Balance: {data['closing_balance']}")
        y -= 30
        # Transactions Table Header
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, y, 'Txn ID')
        c.drawString(150, y, 'Type')
        c.drawString(250, y, 'Amount')
        c.drawString(350, y, 'Timestamp')
        y -= 20
        c.setFont('Helvetica', 10)
        # Transactions
        for tx in data.get('transactions', []):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, str(tx['transaction_id']))
            c.drawString(150, y, tx['type'])
            c.drawString(250, y, str(tx['amount']))
            c.drawString(350, y, tx['timestamp'])
            y -= 15
        c.save()
        return output_path
