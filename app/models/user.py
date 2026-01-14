from pydantic import BaseModel, Field

from app.models.collections import UserPreferences


class User(BaseModel):
    _id: str = Field(alias="_id")
    name: str
    email: str
    preferences: UserPreferences
