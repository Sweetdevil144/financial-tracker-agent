from typing import Any, Optional

from pydantic import BaseModel


class CreateExpense(BaseModel):
    text: str
    amount: Optional[float] = None
    category: Optional[str] = None
    currency: Optional[str] = "USD"


class ListAll(BaseModel):
    user_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    category: Optional[str] = None
    min_amount: Optional[int] = 0
    max_amount: Optional[int] = int("inf")
    limit: Optional[int] = 100
    sort_by: Optional[str] = "asc"

class ListOne(BaseModel):
    expense_id: str

class UpdateOne(BaseModel):
    expense_id: str
    update_fields: dict[str, Any]

class DeleteOne(BaseModel):
    expense_id: str