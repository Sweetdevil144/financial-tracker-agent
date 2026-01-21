from enum import Enum


class BudgetPeriod(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    DAILY = "daily"


class Currencies(Enum):
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    GBP = "GBP"
    CNY = "CNY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    KRW = "KRW"
    INR = "INR"
    SGD = "SGD"
    HKD = "HKD"
    MXN = "MXN"
    BRL = "BRL"
    SEK = "SEK"
    NOK = "NOK"
    NZD = "NZD"
    TRY = "TRY"
    ZAR = "ZAR"
    RUB = "RUB"
    PLN = "PLN"
    THB = "THB"
    IDR = "IDR"
    MYR = "MYR"
    PHP = "PHP"
