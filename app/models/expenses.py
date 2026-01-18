from typing import Optional

from pydantic import BaseModel


class CreateExpenseRequest(BaseModel):
    text: str
    amount: Optional[float] = None
    category: Optional[str] = None
    currency: Optional[str] = "USD"


class ListExpenseRequest(BaseModel):
    user_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    category: Optional[str] = None
    min_amount: Optional[int] = 0
    max_amount: Optional[int] = int("inf")
    limit: Optional[int] = 100
    sort_by: Optional[str] = "asc"

class ListIndividualExpenseRequest(BaseModel):
    user_id: str
    expense_id: str