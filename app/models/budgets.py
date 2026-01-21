from typing import Any, Optional

from pydantic import BaseModel

from app.utils.enums import BudgetPeriod, Currencies


class CreateBudget(BaseModel):
    category: str
    amount: float
    currency: Currencies = Currencies.USD
    period: BudgetPeriod
    start_date: str
    end_date: str
    description: Optional[str] = None


class UpdateOne(BaseModel):
    update_fields: dict[str, Any]
