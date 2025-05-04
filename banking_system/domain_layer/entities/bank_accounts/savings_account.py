# Example of specialized behavior
from banking_system.domain_layer.entities.bank_accounts.account import Account


class SavingsAccount(Account):
    MINIMUM_BALANCE = 100.0

    def _validate_before_withdraw(self, amount):
        if self.balance - amount < self.MINIMUM_BALANCE:
            raise ValueError("Cannot withdraw: minimum balance requirement not met.")

