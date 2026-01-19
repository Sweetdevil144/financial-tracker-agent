from typing import Any

from pydantic import BaseModel


class UpdateOne(BaseModel):
    update_fields: dict[str, Any]

