# Example of specialized behavior
from banking_system.domain_layer.entities.bank_accounts.account import Account


class SavingsAccount(Account):
    MINIMUM_BALANCE = 100.0

    def withdraw(self, amount: float):
        if not self.is_active():
            raise ValueError("Cannot withdraw from a closed account.")

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")

        if self.balance - amount < self.MINIMUM_BALANCE:
            raise ValueError("Cannot withdraw: minimum balance requirement not met.")

        self.balance -= amount
