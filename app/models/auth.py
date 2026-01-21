from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    token: Optional[str] = None


class User(BaseModel):
    id: str = Field(alias="_id")
    email: str
    name: str
    password_hash: str
    created_at: str
    deleted: bool = False
    model_config = {"populate_by_name": True}


class Token(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    token: str
    created_at: str
    expires_at: str
    revoked: bool = False
    model_config = {"populate_by_name": True}
