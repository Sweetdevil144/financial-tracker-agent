from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.utils.enums import Currencies


class ExpenseExtraction(BaseModel):
    amount: float
    currency: Currencies = Currencies.USD
    merchant: str
    category: str
    date: datetime | str
    description: Optional[str] = Field(
        default_factory=str, description="Description of expense"
    )
    note: Optional[str] = Field(
        default_factory=str, description="Additional notes on transaction"
    )


class ExpenseValidation(BaseModel):
    is_valid: bool
    errors: Optional[List[str]] = Field(
        default_factory=list,
        description="List of errors occuring during expense validation",
    )
    warnings: Optional[List[str]] = Field(
        default_factory=list,
        description="List of warnings occuring during expense validation",
    )
    data: Optional[ExpenseExtraction] | dict[str, Any] = Field(
        default_factory=dict[str, Any],
        description="Parsed data. Can be either according to strictly parsed data OR default to dict structure",
    )


class ExpenseResponse(BaseModel):
    success: bool
    message: str
    expense_id: str | None
    errors: Optional[List[str]] = Field(
        default_factory=list,
        description="List of validation errors during expense extraction if any",
    )
    warnings: Optional[List[str]] = Field(
        default_factory=list,
        description="List of validation warnings during expense extraction if any",
    )
