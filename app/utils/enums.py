from enum import Enum


class BudgetPeriod(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    DAILY = "daily"


class Currencies(Enum):
    USD = "USD"
    INR = "INR"
    EUR = "EUR"
    JPY = "JPY"
    GBP = "GBP"

