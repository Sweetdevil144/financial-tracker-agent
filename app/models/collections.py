from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils.enums import BudgetPeriod, Currencies


class Expenses(BaseModel):
    """
    Collection = expenses
    """

    id: str = Field(alias="_id")
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
    model_config = {"populate_by_name": True}


class Budgets(BaseModel):
    """
    Collection = budgets
    """

    id: str = Field(alias="_id")
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
    model_config = {"populate_by_name": True}


class UserPreferences(BaseModel):
    """
    Collection = preferences
    """

    id: str = Field(alias="_id")
    user_id: str
    default_currency: str
    categories_list: List[str]
    timezone: str
    timezone_offset: Optional[str] = None
    model_config = {"populate_by_name": True}
