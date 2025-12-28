from typing import Optional, List, Any
from pydantic import BaseModel, Field
from app.utils.enums import Currencies
from datetime import datetime

class ExpenseExtraction(BaseModel):
    amount: float
    curency: Currencies = Currencies.USD
    merchant: str
    category: str
    date: datetime | str
    description: Optional[str] = Field(default_factory=str, description="Description of expense")
    note: Optional[str] = Field(default_factory=str, description="Additional notes on transaction")

class ExpenseValidation(BaseModel):
    is_valid: bool
    errors: Optional[List[str]] = Field(default_factory=List[str], description="List of errors occuring during expense validation")
    warnings: Optional[List[str]] = Field(default_factory=List[str], description="List of warnings occuring during expense validation")
    data: Optional[ExpenseExtraction] | dict[str, Any] = Field(default_factory=dict[str, Any], description="Parsed data. Can be either according to strictly parsed data OR default to dict structure")

