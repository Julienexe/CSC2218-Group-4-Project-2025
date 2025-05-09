import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import pytest
from unittest.mock import Mock, patch, call
from uuid import uuid4
from datetime import datetime

# Import the services to be tested
from banking_system.application_layer.services import (
    LoggingService,
    NotificationService,
    FundTransferService
)

# Import necessary domain classes
from banking_system import Transaction, TransactionType

class TestLoggingService:
    def setup_method(self):
        self.logging_service = LoggingService()
    
    @patch('builtins.print')
    def test_log_message(self, mock_print):
        # Test basic logging functionality
        test_message = "Test log message"
        self.logging_service.log(test_message)
        
        # Verify print was called with the correct message
        mock_print.assert_called_once_with(f"LOG: {test_message}")
    
    @patch('builtins.print')
    def test_log_transaction(self, mock_print):
        # Create a mock transaction
        transaction = Mock()
        transaction.transaction_type = TransactionType.DEPOSIT
        transaction.amount = 100.00
        transaction.timestamp = datetime.now()
        transaction.account_id = str(uuid4())
        
        # Log the transaction
        self.logging_service.log_transaction(transaction)
        
        # Verify print was called with the transaction details
        expected_log_message = (
            f"Transaction Log:\n"
            f"Type: {transaction.transaction_type}\n"
            f"Amount: ${transaction.amount:.2f}\n"
            f"Date: {transaction.timestamp}\n"
            f"Account ID: {transaction.account_id}\n"
        )
        
        # We're checking if print was called with a string that starts with "LOG: "
        # and contains the expected transaction information
        mock_print.assert_called_once()
        actual_call = mock_print.call_args[0][0]
        assert actual_call.startswith("LOG: ")
        assert expected_log_message in actual_call

class TestNotificationService:
    def setup_method(self):
        self.notification_service = NotificationService()
    
    @patch('builtins.print')
    def test_notify(self, mock_print):
        # Create a mock transaction
        transaction = Mock()
        transaction.transaction_type = TransactionType.WITHDRAW
        transaction.amount = 50.00
        transaction.timestamp = datetime.now()
        transaction.account_id = str(uuid4())
        
        # Send notification for the transaction
        self.notification_service.notify(transaction)
        
        # Verify print was called with the notification message
        expected_message = (
            f"Transaction Notification:\n"
            f"Type: {transaction.transaction_type}\n"
            f"Amount: ${transaction.amount:.2f}\n"
            f"Date: {transaction.timestamp}\n"
            f"Account ID: {transaction.account_id}\n"
        )
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert call_args.startswith("Notification sent: ")
        assert expected_message in call_args

class TestFundTransferService:
    def setup_method(self):
        # Create mock repositories
        self.mock_account_repo = Mock()
        self.mock_transaction_repo = Mock()
        
        # Create the service with mock repositories
        self.fund_transfer_service = FundTransferService(
            self.mock_account_repo,
            self.mock_transaction_repo
        )
        
        # Create mock accounts
        self.source_account_id = str(uuid4())
        self.destination_account_id = str(uuid4())
        
        self.source_account = Mock()
        self.source_account.account_id = self.source_account_id
        self.source_account.balance = 1000.0
        
        self.destination_account = Mock()
        self.destination_account.account_id = self.destination_account_id
        self.destination_account.balance = 500.0
        
        # Configure mock repositories to return our mock accounts
        self.mock_account_repo.get_account_by_id.side_effect = lambda account_id: {
            self.source_account_id: self.source_account,
            self.destination_account_id: self.destination_account
        }.get(account_id)
    
    def test_successful_transfer(self):
        # Test a successful transfer between two accounts
        transfer_amount = 200.0
        
        # Execute the transfer
        result = self.fund_transfer_service.transfer_funds(
            self.source_account_id, 
            self.destination_account_id, 
            transfer_amount
        )
        
        # Verify accounts were retrieved from the repository
        self.mock_account_repo.get_account_by_id.assert_has_calls([
            call(self.source_account_id),
            call(self.destination_account_id)
        ])
        
        # Verify balances were updated correctly
        assert self.source_account.balance == 800.0  # 1000 - 200
        assert self.destination_account.balance == 700.0  # 500 + 200
        
        # Verify accounts were updated in the repository
        self.mock_account_repo.update_account.assert_has_calls([
            call(self.source_account),
            call(self.destination_account)
        ])
        
        # Verify transactions were saved
        assert self.mock_transaction_repo.save_transaction.call_count == 2
        
        # Verify the return value contains both transactions
        assert "withdrawal" in result
        assert "deposit" in result
        assert result["withdrawal"].transaction_type == TransactionType.WITHDRAW
        assert result["deposit"].transaction_type == TransactionType.DEPOSIT
        assert result["withdrawal"].amount == transfer_amount
        assert result["deposit"].amount == transfer_amount
    
    def test_transfer_insufficient_funds(self):
        # Test a transfer with insufficient funds
        transfer_amount = 1500.0  # More than source account balance
        
        # Execute the transfer and expect a ValueError
        with pytest.raises(ValueError) as exc_info:
            self.fund_transfer_service.transfer_funds(
                self.source_account_id, 
                self.destination_account_id, 
                transfer_amount
            )
        
        # Verify the error message
        assert "Insufficient funds" in str(exc_info.value)
        
        # Verify no account updates or transactions occurred
        self.mock_account_repo.update_account.assert_not_called()
        self.mock_transaction_repo.save_transaction.assert_not_called()
    
    def test_transfer_invalid_amount(self):
        # Test a transfer with a negative amount
        transfer_amount = -100.0
        
        # Execute the transfer and expect a ValueError
        with pytest.raises(ValueError) as exc_info:
            self.fund_transfer_service.transfer_funds(
                self.source_account_id, 
                self.destination_account_id, 
                transfer_amount
            )
        
        # Verify the error message
        assert "Transfer amount must be positive" in str(exc_info.value)
        
        # Verify no account updates or transactions occurred
        self.mock_account_repo.update_account.assert_not_called()
        self.mock_transaction_repo.save_transaction.assert_not_called()
    
    def test_transfer_source_account_not_found(self):
        # Test a transfer with a non-existent source account
        invalid_account_id = str(uuid4())
        
        # Configure mock repository to return None for this account ID
        self.mock_account_repo.get_account_by_id.side_effect = lambda account_id: {
            self.destination_account_id: self.destination_account
        }.get(account_id)
        
        # Execute the transfer and expect a ValueError
        with pytest.raises(ValueError) as exc_info:
            self.fund_transfer_service.transfer_funds(
                invalid_account_id,
                self.destination_account_id, 
                100.0
            )
        
        # Verify the error message
        assert f"Source account with ID {invalid_account_id} not found" in str(exc_info.value)
        
        # Verify no account updates or transactions occurred
        self.mock_account_repo.update_account.assert_not_called()
        self.mock_transaction_repo.save_transaction.assert_not_called()
    
    def test_transfer_destination_account_not_found(self):
        # Test a transfer with a non-existent destination account
        invalid_account_id = str(uuid4())
        
        # Configure mock repository to return None for this account ID
        self.mock_account_repo.get_account_by_id.side_effect = lambda account_id: {
            self.source_account_id: self.source_account
        }.get(account_id)
        
        # Execute the transfer and expect a ValueError
        with pytest.raises(ValueError) as exc_info:
            self.fund_transfer_service.transfer_funds(
                self.source_account_id,
                invalid_account_id, 
                100.0
            )
        
        # Verify the error message
        assert f"Destination account with ID {invalid_account_id} not found" in str(exc_info.value)
        
        # Verify no account updates or transactions occurred
        self.mock_account_repo.update_account.assert_not_called()
        self.mock_transaction_repo.save_transaction.assert_not_called()