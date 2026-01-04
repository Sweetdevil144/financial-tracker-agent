from enum import Enum


class BudgetPeriod(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"


class Currencies(Enum):
    USD = "USD"
    INR = "INR"
    EUR = "EUR"
    JPY = "JPY"
    GBP = "GBP"
