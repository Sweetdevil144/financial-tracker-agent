from pydantic import BaseModel, Field

from app.models.collections import UserPreferences


class User(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    preferences: UserPreferences
    model_config = {"populate_by_name": True}
