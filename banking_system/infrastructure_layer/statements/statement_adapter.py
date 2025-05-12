from abc import ABC, abstractmethod
from typing import Dict, Any

class StatementAdapterInterface(ABC):
    """
    Adapter interface to generate account statements in various formats.
    """
    @abstractmethod
    def generate(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Generate a statement from structured data and save to output_path.

        Args:
            data: A dict containing statement details, e.g., {
                'account_id': str,
                'period': 'YYYY-MM',
                'opening_balance': float,
                'closing_balance': float,
                'transactions': List[Dict],
            }
            output_path: File path where the statement will be saved.

        Returns:
            The path to the generated file.
        """
        pass
