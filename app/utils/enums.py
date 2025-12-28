from enum import Enum

class BudgetPeriod(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"

class Currencies(Enum):
    USD = "USD"
    INR = "INR"
    EUR = "EUR"
    DOLLAR = "dollar"
    RUPEE = "rupee"
    POUND = "pound"