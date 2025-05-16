import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import pytest
from unittest.mock import Mock, patch, call, MagicMock
from uuid import uuid4
from datetime import datetime

# Import the services to be tested
from banking_system.application_layer.services import (
    LoggingService,
    NotificationService,
    FundTransferService,
    AccountService, 
    TransactionService, 
    InterestService, 
    StatementService
)

# Import necessary domain classes
from banking_system import Transaction, TransactionType, Account, CheckingAccount, SavingsAccount
from domain_layer import SavingsInterestStrategy, CheckingInterestStrategy, LimitConstraint

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
        
        # check if print was called with a string that starts with "LOG: "
        # and contains the expected transaction information
        mock_print.assert_called_once()
        actual_call = mock_print.call_args[0][0]
        assert actual_call.startswith("LOG: ")
        assert expected_log_message in actual_call

class TestAccountService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_repo = MagicMock()
        self.service = AccountService(self.mock_repo)

    def test_create_checking_account(self):
        self.mock_repo.create_account = MagicMock()
        account_id = self.service.create_account("CHECKING", 200.0)
        self.mock_repo.create_account.assert_called()
        assert account_id is not None

    def test_create_savings_account_minimum_deposit(self):
        self.mock_repo.create_account = MagicMock()
        account_id = self.service.create_account("SAVINGS", 200.0)
        self.mock_repo.create_account.assert_called()
        assert account_id is not None

    def test_create_savings_account_below_minimum(self):
        with pytest.raises(ValueError):
            self.service.create_account("SAVINGS", 50.0)

    def test_create_account_invalid_type(self):
        with pytest.raises(ValueError):
            self.service.create_account("BUSINESS", 100.0)

class TestNotificationServiceNew:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_adapter = MagicMock()
        self.service = NotificationService(self.mock_adapter)

    def test_notify(self):
        transaction = MagicMock()
        transaction.transaction_type = "DEPOSIT"
        transaction.amount = 100.0
        transaction.timestamp = "2024-01-01"
        transaction.account_id = "acc1"
        self.service.notify(transaction)
        self.mock_adapter.notify.assert_called()

    def test_subscribe(self):
        self.service.subscribe("acc1", "EMAIL")
        self.mock_adapter.save_notification_preference.assert_called_with("acc1", "EMAIL")
        self.mock_adapter.notify.assert_called()
        assert self.service.is_subscribed

    def test_unsubscribe(self):
        self.service.unsubscribe("acc1", "EMAIL")
        self.mock_adapter.remove_notification_preference.assert_called_with("acc1", "EMAIL")
        self.mock_adapter.notify.assert_called()
        assert not self.service.is_subscribed

class TestLoggingServiceNew:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = LoggingService()

    def test_log(self):
        with patch("builtins.print") as mock_print:
            self.service.log("test message")
            mock_print.assert_called_with("LOG: test message")

    def test_log_transaction(self):
        transaction = MagicMock()
        transaction.transaction_type = "WITHDRAWAL"
        transaction.amount = 50.0
        transaction.timestamp = "2024-01-01"
        transaction.account_id = "acc1"
        with patch("builtins.print") as mock_print:
            self.service.log_transaction(transaction)
            assert mock_print.called

class TestTransactionService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_account_repo = MagicMock()
        self.mock_transaction_repo = MagicMock()
        self.mock_notification = MagicMock()
        self.mock_logging = MagicMock()
        self.service = TransactionService(
            self.mock_account_repo,
            self.mock_transaction_repo,
            self.mock_notification,
            self.mock_logging
        )
        self.mock_account = MagicMock()
        self.mock_account.deposit.return_value = MagicMock()
        self.mock_account.withdraw.return_value = MagicMock()
        self.mock_account_repo.get_account_by_id.return_value = self.mock_account
        patcher = patch("banking_system.application_layer.services.abstractions.save_transaction")
        self.mock_save_transaction = patcher.start()
        yield
        patcher.stop()

    def test_deposit_success(self):
        transaction = self.service.deposit("acc1", 100.0)
        self.mock_account.deposit.assert_called_with(100.0)
        self.mock_save_transaction.assert_called()
        assert transaction is not None

    def test_deposit_account_not_found(self):
        self.mock_account_repo.get_account_by_id.return_value = None
        with pytest.raises(ValueError):
            self.service.deposit("acc1", 100.0)

    def test_withdraw_success(self):
        transaction = self.service.withdraw("acc1", 50.0)
        self.mock_account.withdraw.assert_called_with(50.0)
        self.mock_save_transaction.assert_called()
        assert transaction is not None

    def test_withdraw_account_not_found(self):
        self.mock_account_repo.get_account_by_id.return_value = None
        with pytest.raises(ValueError):
            self.service.withdraw("acc1", 50.0)

class TestInterestService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_account_repo = MagicMock()
        self.service = InterestService(self.mock_account_repo)
        self.mock_account = MagicMock()
        self.mock_account_repo.get_account_by_id.return_value = self.mock_account

    def test_apply_interest_to_account_success(self):
        self.service.apply_interest_to_account("acc1")
        self.mock_account.calculate_interest.assert_called()
        self.mock_account_repo.update_account.assert_called_with(self.mock_account)

    def test_apply_interest_to_account_not_found(self):
        self.mock_account_repo.get_account_by_id.return_value = None
        with pytest.raises(ValueError):
            self.service.apply_interest_to_account("acc1")

    def test_apply_interest_batch(self):
        self.mock_account_repo.get_account_by_id.return_value = self.mock_account
        self.service.apply_interest_batch(["acc1", "acc2"])
        assert self.mock_account.calculate_interest.called

class TestStatementService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_account_repo = MagicMock()
        self.mock_transaction_repo = MagicMock()
        self.mock_statement_adapter = MagicMock()
        self.service = StatementService(self.mock_account_repo, self.mock_transaction_repo, self.mock_statement_adapter)
        self.mock_account = MagicMock()
        self.mock_account.generate_monthly_statement.return_value = {"statement": "data"}
        self.mock_account_repo.get_account_by_id.return_value = self.mock_account
        self.mock_transaction_repo.get_transactions_by_account_id.return_value = [MagicMock(return_dict=lambda: {"id": 1})]
        self.mock_statement_adapter.generate.return_value = "statement"

    def test_generate_monthly_statement_success(self):
        result = self.service.generate_monthly_statement("acc1")
        assert result == "statement"
        self.mock_statement_adapter.generate.assert_called()

    def test_generate_monthly_statement_account_not_found(self):
        self.mock_account_repo.get_account_by_id.return_value = None
        with pytest.raises(ValueError):
            self.service.generate_monthly_statement("acc1")

    def test_get_transaction_history_success(self):
        result = self.service.get_transaction_history("acc1")
        assert isinstance(result, list)

    def test_get_transaction_history_account_not_found(self):
        self.mock_account_repo.get_account_by_id.return_value = None
        with pytest.raises(ValueError):
            self.service.get_transaction_history("acc1")

class TestFundTransferServiceNew:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_account_repo = MagicMock()
        self.mock_transaction_repo = MagicMock()
        self.mock_notification = MagicMock()
        self.mock_logging = MagicMock()
        self.service = FundTransferService(
            self.mock_account_repo,
            self.mock_transaction_repo,
            self.mock_notification,
            self.mock_logging
        )
        self.mock_source_account = MagicMock()
        self.mock_destination_account = MagicMock()
        self.mock_account_repo.get_account_by_id.side_effect = lambda x: self.mock_source_account if x == "src" else self.mock_destination_account
        patcher = patch("banking_system.application_layer.services.abstractions.save_transaction")
        self.mock_save_transaction = patcher.start()
        yield
        patcher.stop()

    def test_transfer_funds_success(self):
        self.mock_source_account.transfer.return_value = MagicMock()
        result = self.service.transfer_funds("src", "dst", 100.0)
        self.mock_source_account.transfer.assert_called_with(100.0, self.mock_destination_account)
        self.mock_save_transaction.assert_called()
        assert result is not None

    def test_transfer_funds_source_not_found(self):
        self.mock_account_repo.get_account_by_id.side_effect = lambda x: None if x == "src" else self.mock_destination_account
        with pytest.raises(ValueError):
            self.service.transfer_funds("src", "dst", 100.0)

    def test_transfer_funds_destination_not_found(self):
        self.mock_account_repo.get_account_by_id.side_effect = lambda x: self.mock_source_account if x == "src" else None
        with pytest.raises(ValueError):
            self.service.transfer_funds("src", "dst", 100.0)