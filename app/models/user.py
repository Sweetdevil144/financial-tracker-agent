from pydantic import BaseModel
from models.collections import UserPreferences

class User(BaseModel):
    id: str
    name: str
    email: str
    preferences: UserPreferences