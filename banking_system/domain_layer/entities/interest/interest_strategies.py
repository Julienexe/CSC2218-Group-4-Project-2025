from abc import ABC, abstractmethod

class InterestStrategy(ABC):
    @abstractmethod
    def apply_interest(self, balance):
        pass


class SavingsInterestStrategy(InterestStrategy):
    def __init__(self, annual_rate):
        self.annual_rate = annual_rate

    def apply_interest(self, balance, months=1):
        monthly_rate = self.annual_rate / 12
        return balance * ((1 + monthly_rate) ** months)

class CheckingInterestStrategy(InterestStrategy):
    def apply_interest(self, balance):
        flat_interest = 0.001  # 0.1%
        return balance + balance * flat_interest