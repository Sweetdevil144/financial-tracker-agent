from typing import Any

from pydantic import BaseModel


class UpdateOne(BaseModel):
    budget_id: str
    update_fields: dict[str, Any]


class DeleteOne(BaseModel):
    budget_id: str
