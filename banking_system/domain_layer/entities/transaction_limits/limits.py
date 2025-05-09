from datetime import datetime

class LimitConstraint:
    def __init__(self, daily_limit: float = None, monthly_limit: float = None, now_provider:datetime=datetime.now):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.now_provider:datetime = now_provider
        self._daily_total = 0.0
        self._monthly_total = 0.0
        self._last_check:datetime = self.now_provider()

    def _reset_if_needed(self):
        today:datetime = self.now_provider()
        if today.date() != self._last_check.date():
            self._daily_total = 0.0
            if today.month != self._last_check.month:
                self._monthly_total = 0.0
            self._last_check = today

    def validate(self, amount: float):
        self._reset_if_needed()

        if self.daily_limit is not None and (self._daily_total + amount > self.daily_limit):
            raise ValueError("Daily transaction limit exceeded.")

        if self.monthly_limit is not None and (self._monthly_total + amount > self.monthly_limit):
            raise ValueError("Monthly transaction limit exceeded.")

    def record(self, amount: float):
        self._daily_total += amount
        self._monthly_total += amount
