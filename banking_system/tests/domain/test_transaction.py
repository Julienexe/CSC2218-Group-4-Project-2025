

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid
from enum import Enum

sys.path.append(str(Path(__file__).resolve().parents[3]))
from banking_system.domain_layer.entities.transaction import Transaction, TransactionType


# --- Test Transaction Initialization ---

def test_transaction_initialization_deposit():
    """Test successful initialization of a DEPOSIT transaction."""
    account_id = "acc-test-123"
    amount = 150.75
    transaction = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        account_id=account_id
    )

    assert isinstance(transaction.transaction_id, str)
    assert len(str(uuid.UUID(transaction.transaction_id))) == 36 # Check if it's a valid UUID string
    assert transaction.transaction_type == TransactionType.DEPOSIT
    assert transaction.amount == amount
    assert transaction.account_id == account_id
    assert isinstance(transaction.timestamp, datetime)


def test_transaction_initialization_withdraw():
    """Test successful initialization of a WITHDRAW transaction."""
    account_id = "acc-test-456"
    amount = 75.00
    transaction = Transaction(
        transaction_type=TransactionType.WITHDRAW,
        amount=amount,
        account_id=account_id
    )

    assert isinstance(transaction.transaction_id, str)
    assert len(str(uuid.UUID(transaction.transaction_id))) == 36
    assert transaction.transaction_type == TransactionType.WITHDRAW
    assert transaction.amount == amount
    assert transaction.account_id == account_id
    assert isinstance(transaction.timestamp, datetime)


def test_transaction_initialization_zero_amount():
    """Test that initializing with zero amount raises ValueError."""
    with pytest.raises(ValueError, match="Transaction amount must be positive."):
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=0.0,
            account_id="acc-test-789"
        )

def test_transaction_initialization_negative_amount():
    """Test that initializing with a negative amount raises ValueError."""
    with pytest.raises(ValueError, match="Transaction amount must be positive."):
        Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=-50.0,
            account_id="acc-test-101"
        )

# --- Test Transaction Methods ---

def test_is_deposit():
    """Test the is_deposit method."""
    deposit_tx = Transaction(TransactionType.DEPOSIT, 100.0, "acc-dep")
    withdraw_tx = Transaction(TransactionType.WITHDRAW, 50.0, "acc-wdr")

    assert deposit_tx.is_deposit() is True
    assert withdraw_tx.is_deposit() is False

def test_is_withdrawal():
    """Test the is_withdrawal method."""
    deposit_tx = Transaction(TransactionType.DEPOSIT, 100.0, "acc-dep")
    withdraw_tx = Transaction(TransactionType.WITHDRAW, 50.0, "acc-wdr")

    assert deposit_tx.is_withdrawal() is False
    assert withdraw_tx.is_withdrawal() is True

# --- Test Transaction Representation ---

def test_transaction_repr():
    """Test the string representation of a transaction."""
    transaction = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=200.0,
        account_id="acc-repr-test"
    )
    representation = repr(transaction)

    assert f"id={transaction.transaction_id}" in representation
    assert f"type={transaction.transaction_type.value}" in representation
    assert f"amount={transaction.amount}" in representation # Floats don't need .2f here usually
    assert f"account_id={transaction.account_id}" in representation
    assert f"timestamp={transaction.timestamp.isoformat()}" in representation

