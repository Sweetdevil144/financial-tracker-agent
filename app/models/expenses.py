from typing import Any, Optional

from pydantic import BaseModel


class CreateExpense(BaseModel):
    text: str
    amount: Optional[float] = None
    category: Optional[str] = None
    currency: Optional[str] = "USD"

class UpdateOne(BaseModel):
    expense_id: str
    update_fields: dict[str, Any]

class DeleteOne(BaseModel):
    expense_id: str