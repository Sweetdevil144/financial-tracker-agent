from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils.enums import BudgetPeriod, Currencies


class Expenses(BaseModel):
    """
    Collection = expenses
    """

    _id: str = Field(alias="_id")
    user_id: str
    amount: float
    currency: Currencies
    description: Optional[str] = None
    merchant: Optional[str] = None
    category: str
    deleted: bool = False
    date: str
    created_at: str
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class Budgets(BaseModel):
    """
    Collection = budgets
    """

    _id: str = Field(alias="_id")
    user_id: str
    category: str
    amount: float
    currency: Currencies
    deleted: bool = False
    period: BudgetPeriod
    start_date: str
    end_date: str
    created_at: str
    description: Optional[str] = None


class UserPreferences(BaseModel):
    """
    Collection = preferences
    """

    _id: str = Field(alias="_id")
    user_id: str
    default_currency: str
    categories_list: List[str]
    timezone: str
    timezone_offset: Optional[str] = None
