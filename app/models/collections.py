from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.utils.enums import BudgetPeriod, Currencies

class Expenses(BaseModel):
    """
    Collection = expenses
    """
    user_id: str
    amount: float
    currency: Currencies
    description: Optional[str] = None
    merchant: str
    category: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class Budgets(BaseModel):
    """
    Collection = budgets
    """
    user_id: str
    category: str
    amount: float
    currency: Currencies
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = None

class UserPreferences(BaseModel):
    """
    Collection = preferences
    """
    user_id: str
    default_currency : str
    categories_list: List[str]
    timezone: str
    timezone_offset: Optional[str] = None
    